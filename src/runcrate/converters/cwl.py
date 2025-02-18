import hashlib
import json
import re
from io import StringIO
from pathlib import Path

import networkx as nx
import prov.model
from bdbag.bdbagit import BDBag
from cwl_utils.parser import load_document_by_yaml
from cwlprov.prov import Entity, Provenance
from cwlprov.ro import ResearchObject
from cwlprov.utils import first
from rocrate.model.contextentity import ContextEntity
from rocrate.model.softwareapplication import SoftwareApplication

from ..constants import DOCKER_IMG_TYPE
from ..utils import as_list, parse_img
from .base import Converter


MANIFEST_FILE = "manifest-sha1.txt"

CWLPROV_NONE = "https://w3id.org/cwl/prov#None"

CWL_TYPE_MAP = {
    "string": "Text",
    "int": "Integer",
    "long": "Integer",
    "float": "Float",
    "double": "Float",
    "Any": "DataType",
    "boolean": "Boolean",
    "File": "File",
    "Directory": "Dataset",
    "null": None,
}

INPUTS_FILE_BASENAME = "primary-job.json"
OUTPUTS_FILE_BASENAME = "primary-output.json"

SCATTER_JOB_PATTERN = re.compile(r"^(.+)_\d+$")


class CwlConverter(Converter):

    WORKFLOW_BASENAME = "packed.cwl"

    def populate(self, root, workflow_name=None, license=None, readme=None):
        self.root = Path(root)
        self.workflow_name = workflow_name
        self.license = license
        self.readme = Path(readme) if readme else readme
        self.wf_path = self.root / "workflow" / self.WORKFLOW_BASENAME
        self.workflow_definition = self.get_workflow()
        self.step_maps = self.get_step_maps()
        self.ro = ResearchObject(BDBag(str(root)))
        self.with_prov = set(str(_) for _ in self.ro.resources_with_provenance())
        self.workflow_run = Provenance(self.ro).activity()
        self.roc_engine_run = None
        self.control_actions = {}
        self.collection = {}
        self.hashes = {}
        self.file_map = {}
        self.manifest = self.get_manifest(self.root, MANIFEST_FILE)

    # --------------------------------------------------------------------------
    # Top level methods, called by build()

    def add_workflow(self, crate):
        lang_version = self.workflow_definition[self.WORKFLOW_BASENAME].cwlVersion
        properties = {
            "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow", "HowTo"],
        }
        workflow = crate.add_workflow(
            self.wf_path, self.wf_path.name, main=True, lang="cwl",
            lang_version=lang_version, gen_cwl=False, properties=properties
        )
        cwl_workflow = self.workflow_definition[workflow.id]
        wf_name = self.wf_path.name
        if hasattr(cwl_workflow, "label") and cwl_workflow.label:
            wf_name = cwl_workflow.label
        workflow["name"] = self.workflow_name or wf_name
        if hasattr(cwl_workflow, "doc") and cwl_workflow.doc:
            workflow["description"] = cwl_workflow.doc
        # cannot convert "intent" to featureList: workflow is not a SoftwareApplication
        workflow["input"] = self.add_params(crate, cwl_workflow.inputs)
        workflow["output"] = self.add_params(crate, cwl_workflow.outputs)
        if hasattr(cwl_workflow, "steps"):
            for s in cwl_workflow.steps:
                self.add_step(crate, workflow, s)
            self.add_param_connections(crate, workflow)
        return workflow

    def add_engine_run(self, crate):
        engine = self.workflow_run.start().starter_activity()
        roc_engine = crate.add(SoftwareApplication(crate, properties={
            "name": engine.label or "workflow engine"
        }))
        roc_engine_run = crate.add(ContextEntity(crate, properties={
            "@type": "OrganizeAction",
            "name": f"Run of {roc_engine['name']}",
            "startTime": engine.start().time.isoformat(),
        }))
        roc_engine_run["instrument"] = roc_engine
        self.add_agent(crate, roc_engine_run, engine)
        self.roc_engine_run = roc_engine_run

    def add_action(self, crate, activity, parent_instrument=None):
        workflow = crate.mainEntity
        action = crate.add(ContextEntity(crate, properties={
            "@type": "CreateAction",
            "name": activity.label,
        }))
        plan = _resolve_plan(activity)
        plan_tag = plan.id.localpart
        if plan_tag == "main":
            assert str(activity.type) == "wfprov:WorkflowRun"
            instrument = workflow
            self.roc_engine_run["result"] = action
            crate.root_dataset["mentions"] = [action]

            def to_wf_p(k):
                return k
        else:
            parent_instrument_fragment = _get_fragment(parent_instrument.id)
            if parent_instrument_fragment != self.WORKFLOW_BASENAME:
                parts = plan_tag.split("/", 1)
                if parts[0] == "main":
                    parts[0] = parent_instrument_fragment
                    plan_tag = "/".join(parts)
            tool_name = self.step_maps[parent_instrument_fragment][plan_tag]["tool"]
            instrument = crate.dereference(f"{workflow.id}#{tool_name}")
            control_action = self.control_actions.get(plan_tag)
            if not control_action:
                control_action = crate.add(ContextEntity(crate, properties={
                    "@type": "ControlAction",
                    "name": f"orchestrate {tool_name}",
                }))
                step = crate.dereference(f"{workflow.id}#{plan_tag}")
                control_action["instrument"] = step
                self.roc_engine_run.append_to("object", control_action, compact=True)
                self.control_actions[plan_tag] = control_action
            control_action.append_to("object", action, compact=True)
            if activity.uri in self.with_prov:
                nested_prov = Provenance(self.ro, activity.uri)
                activity = nested_prov.activity()

            def to_wf_p(k):
                return k.replace(activity.plan().localpart, tool_name)
        self.get_hashes(activity.provenance)
        action["instrument"] = instrument
        action["startTime"] = activity.start().time.isoformat()
        action["endTime"] = activity.end().time.isoformat()
        action["object"] = self.add_action_params(crate, activity, to_wf_p, "usage")
        action["result"] = self.add_action_params(crate, activity, to_wf_p, "generation")
        self.add_container_images(crate, action, activity)
        for job in activity.steps():
            self.add_action(crate, job, parent_instrument=instrument)

    def patch_workflow_input_collection(self, crate, wf=None):
        """\
        CWLProv records secondary files only in step runs, not in the workflow
        run. Thus, when the conversion of parameter values is completed,
        workflow-level parameters with secondary files get mapped to the main
        entity of the collection alone (a File). This method fixes the mapping
        by retrieving the correct Collection entity from the relevant tool
        execution.
        """
        if wf is None:
            wf = crate.mainEntity
        sel = [_ for _ in crate.contextual_entities
               if "CreateAction" in as_list(_.type) and _.get("instrument") is wf]
        if not sel:
            return  # skipped subworkflow
        wf_action = sel[0]
        connections = [_ for _ in crate.contextual_entities
                       if "ParameterConnection" in as_list(_.type)]
        for param in wf.get("input", []):
            if param.get("additionalType") == "Collection":
                src_sel = [_ for _ in wf_action.get("object", [])
                           if param in as_list(_.get("exampleOfWork"))]
                if not src_sel:
                    raise RuntimeError(f"object for param {param.id} not found")
                obj = src_sel[0]
                if obj.type != "Collection":
                    param_connections = [_ for _ in connections if _["sourceParameter"] is param]
                    if not param_connections:
                        continue
                    pc = param_connections[0]
                    tgt_param = pc["targetParameter"]
                    tgt_sel = [_ for _ in crate.get_entities()
                               if tgt_param in as_list(_.get("exampleOfWork"))]
                    if not tgt_sel:
                        raise RuntimeError(f"object for param {tgt_param.id} not found")
                    tgt_obj = tgt_sel[0]
                    wf_action["object"] = [
                        _ for _ in as_list(wf_action["object"]) if _ is not obj
                    ] + [tgt_obj]
                    tgt_obj.append_to("exampleOfWork", param)
                    obj["exampleOfWork"] = [_ for _ in as_list(obj["exampleOfWork"])
                                            if _ is not param]
                    if len(obj["exampleOfWork"]) == 1:
                        obj["exampleOfWork"] = obj["exampleOfWork"][0]
                    if len(obj["exampleOfWork"]) == 0:
                        del obj["exampleOfWork"]
        for tool in wf.get("hasPart", []):
            if "ComputationalWorkflow" in as_list(tool.type):
                self.patch_workflow_input_collection(crate, wf=tool)

    def add_inputs_files(self, crate):
        path = self.root / "workflow" / INPUTS_FILE_BASENAME
        if path.is_file():
            with open(path) as f:
                data = json.load(f)
            data = self.map_input_data(crate, data)
            source = StringIO(json.dumps(data, indent=4))
            crate.add_file(source, path.name, properties={
                "name": "input object document",
                "encodingFormat": "application/json",
            })

    def add_output_formats(self, crate):
        path = self.root / "workflow" / OUTPUTS_FILE_BASENAME
        if path.is_file():
            with open(path) as f:
                data = json.load(f)
            self.map_input_data(crate, data)

    # --------------------------------------------------------------------------
    # Internal methods, called by the top level methods

    def add_step(self, crate, workflow, cwl_step):
        step_fragment = _get_fragment(cwl_step.id)
        step_id = f"{self.wf_path.name}#{step_fragment}"
        pos = self.step_maps[_get_fragment(workflow.id)][step_fragment]["pos"]
        step = crate.add(ContextEntity(crate, step_id, properties={
            "@type": "HowToStep",
            "position": str(pos),
        }))
        tool = self.add_tool(crate, workflow, cwl_step.run)
        step["workExample"] = tool
        if hasattr(cwl_step, "label") and cwl_step.label:
            step["name"] = cwl_step.label
        if hasattr(cwl_step, "doc") and cwl_step.doc:
            step["description"] = cwl_step.doc
        workflow.append_to("step", step)

    def add_tool(self, crate, workflow, cwl_tool):
        if isinstance(cwl_tool, str):
            tool_fragment = _get_fragment(cwl_tool)
            cwl_tool = self.workflow_definition[tool_fragment]
        else:
            tool_fragment = _get_fragment(cwl_tool.id)
        if hasattr(cwl_tool, "expression"):
            raise RuntimeError("ExpressionTool not supported yet")
        tool_id = f"{self.wf_path.name}#{tool_fragment}"
        tool = crate.dereference(tool_id)
        if tool:
            return tool
        properties = {"name": tool_fragment}
        if cwl_tool.doc:
            properties["description"] = cwl_tool.doc
        if cwl_tool.label:
            properties["name"] = cwl_tool.label
        if hasattr(cwl_tool, "steps"):
            properties["@type"] = ["SoftwareSourceCode", "ComputationalWorkflow", "HowTo"]
        else:
            properties["@type"] = "SoftwareApplication"
        if hasattr(cwl_tool, "intent") and cwl_tool.intent:
            properties["featureList"] = cwl_tool.intent
        if hasattr(cwl_tool, "requirements") and cwl_tool.requirements:
            for req in cwl_tool.requirements:
                if req.class_ == "ResourceRequirement":
                    ramMin = req.ramMin
                    if ramMin:
                        properties["memoryRequirements"] = f"{int(ramMin)} MiB"
        deps = []
        if hasattr(cwl_tool, "hints") and cwl_tool.hints:
            for req in cwl_tool.hints:
                if hasattr(req, "class_") and req.class_ == "ResourceRequirement":
                    ramMin = req.ramMin
                    if ramMin:
                        properties["memoryRequirements"] = f"{int(ramMin)} MiB"
                if hasattr(req, "class_") and req.class_ == "SoftwareRequirement":
                    for p in req.packages:
                        if hasattr(p, "specs") and p.specs:
                            dep_id = p.specs[0]
                            dep_properties = {
                                "@type": "SoftwareApplication",
                                "name": p.package
                            }
                            if p.version:
                                dep_properties["softwareVersion"] = p.version
                            deps.append(
                                crate.add(ContextEntity(crate, dep_id, properties=dep_properties))
                            )
        tool = crate.add(ContextEntity(crate, tool_id, properties=properties))
        if deps:
            tool["softwareRequirements"] = deps
        if len(deps) == 1:
            tool["mainEntity"] = deps[0]
        tool["input"] = self.add_params(crate, cwl_tool.inputs)
        tool["output"] = self.add_params(crate, cwl_tool.outputs)
        workflow.append_to("hasPart", tool)
        if hasattr(cwl_tool, "steps"):
            tool["programmingLanguage"] = workflow["programmingLanguage"]
            for s in cwl_tool.steps:
                self.add_step(crate, tool, s)
            self.add_param_connections(crate, tool)
        return tool

    def add_params(self, crate, cwl_params):
        params = []
        for cwl_p in cwl_params:
            p_id = _get_relative_uri(cwl_p.id)
            properties = _properties_from_cwl_param(cwl_p)
            properties["name"] = p_id.rsplit("/", 1)[-1]
            p = crate.add(ContextEntity(crate, p_id, properties=properties))
            params.append(p)
        return params

    def add_agent(self, crate, roc_engine_run, engine):
        delegate = engine.start().starter_activity()
        try:
            delegation = next(engine.provenance.record_with_attr(
                prov.model.ProvDelegation, delegate.id, prov.model.PROV_ATTR_DELEGATE
            ))
        except StopIteration:
            return
        responsible = delegation.get_attribute(prov.model.PROV_ATTR_RESPONSIBLE)
        agent = sum((engine.provenance.prov_doc.get_record(_) for _ in responsible), [])
        for a in agent:
            if "prov:Person" not in set(str(_) for _ in a.get_asserted_types()):
                continue
            agent_id = a.identifier.uri
            if not agent_id.startswith("http"):
                agent_id = "#" + agent_id.rsplit(":", 1)[-1]
            properties = {
                "@type": "Person"
            }
            if isinstance(a.label, str):
                properties["name"] = a.label
            ro_a = crate.add(ContextEntity(crate, agent_id, properties=properties))
            roc_engine_run.append_to("agent", ro_a, compact=True)

    def add_container_images(self, crate, action, activity):
        images = set()
        for assoc in activity.association():
            for agent in activity.provenance.prov_doc.get_record(assoc.agent_id):
                images |= agent.get_attribute("cwlprov:image")
        for im in images:
            properties = parse_img(im)
            properties.update({
                "@type": "ContainerImage",
                "additionalType": {"@id": DOCKER_IMG_TYPE}
            })
            roc_img = crate.add(ContextEntity(crate, properties=properties))
            action.append_to("containerImage", roc_img, compact=True)

    def add_action_params(self, crate, activity, to_wf_p, ptype="usage"):
        action_params = []
        all_roles = set()
        for rel in getattr(activity, ptype)():
            k = _get_relative_uri(rel.role.uri)
            if str(activity.type) == "wfprov:WorkflowRun":
                # workflow output roles have a phantom step part
                if ptype == "generation":
                    k = _cut_step_part(k)
                # In the case of a single tool run, cwltool reports one WorkflowRun
                # and no ProcessRun; some parameters are duplicated, appearing both
                # with role main/PARAM_NAME and main/ORIGINAL_WF_NAME/PARAM_NAME
                if not list(activity.steps()):
                    k = _cut_step_part(k)
                    if k in all_roles:
                        continue
                    all_roles.add(k)
            wf_p = crate.dereference(to_wf_p(k))
            k = _get_fragment(k)
            v = rel.entity()
            value = self.convert_param(v,
                                       crate,
                                       manifest=self.manifest
                                       )
            if value is None:
                continue  # param is optional with no default and was not set
            if {"ro:Folder", "wf4ever:File"} & set(str(_) for _ in v.types()):
                action_p = value
            else:
                # FIXME: assuming arrays and records don't have nested structured types
                if isinstance(value, dict):
                    value = [crate.add(ContextEntity(crate, f"#pv-{k}/{nk}", properties={
                        "@type": "PropertyValue",
                        "name": nk,
                        "value": nv,
                    })) for nk, nv in value.items()]
                action_p = crate.add(ContextEntity(crate, f"#pv-{k}", properties={
                    "@type": "PropertyValue",
                    "name": k.rsplit("/", 1)[-1],
                }))
                action_p["value"] = value
            action_p["exampleOfWork"] = list(set(
                as_list(action_p.get("exampleOfWork", [])) + [wf_p]
            ))
            if len(action_p["exampleOfWork"]) == 1:
                action_p["exampleOfWork"] = action_p["exampleOfWork"][0]
            if ptype == "generation":
                action_p["dateCreated"] = rel.time.isoformat()
            action_params.append(action_p)
        return action_params

    def add_param_connections(self, crate, workflow):
        def connect(source, target, entity):
            connection = crate.add(ContextEntity(crate, properties={
                "@type": "ParameterConnection"
            }))
            connection["sourceParameter"] = crate.get(f"{self.WORKFLOW_BASENAME}#{source}")
            connection["targetParameter"] = crate.get(f"{self.WORKFLOW_BASENAME}#{target}")
            entity.append_to("connection", connection)
        wf_name = _get_fragment(workflow.id)
        wf_def = self.workflow_definition[wf_name]
        step_map = self.step_maps[wf_name]
        out_map = {}
        for step in wf_def.steps:
            step_name = _get_fragment(step.id)
            tool_name = step_map[step_name]["tool"]
            for o in step.out:
                o_name = _get_fragment(o)
                out_map[o_name] = o_name.replace(step_name, tool_name)
        for step in wf_def.steps:
            step_name = _get_fragment(step.id)
            ro_step = crate.get(f"{self.wf_path.name}#{step_name}")
            tool_name = step_map[step_name]["tool"]
            for mapping in getattr(step, "in_", []):
                if not mapping.source:
                    continue
                sources = [mapping.source] if not isinstance(
                    mapping.source, list
                ) else mapping.source
                for s in sources:
                    from_param = _get_fragment(s)
                    try:
                        from_param = out_map[from_param]
                    except KeyError:
                        pass  # only needed if source is from another step
                    to_param = _get_fragment(mapping.id).replace(step_name, tool_name)
                    connect(from_param, to_param, ro_step)
        for out in getattr(wf_def, "outputs", []):
            out_sources = [out.outputSource] if not isinstance(
                out.outputSource, list
            ) else out.outputSource
            for out_s in out_sources:
                from_param = _get_fragment(out_s)
                try:
                    from_param = out_map[from_param]
                except KeyError:
                    # assuming this is a passthrough for a workflow input parameter
                    pass
                to_param = _get_fragment(out.id)
                connect(from_param, to_param, workflow)

    def get_manifest(self, root=None, MANIFEST_FILE=None):
        manifest = {}
        with open(root / Path(MANIFEST_FILE)) as f:
            for line in f:
                hash_, relpath = line.strip().split(None, 1)
                manifest[hash_] = root / relpath
            return manifest

    def get_workflow(self):
        """\
        Get the workflow from the given path.

        Returns a dictionary where tools / workflows are mapped by their ids.

        Does not use load_document_by_uri, so we can hack the json to work
        around issues.
        """

        with open(self.wf_path, "rt") as f:
            json_wf = json.load(f)
        graph = json_wf.get("$graph", [json_wf])
        # https://github.com/common-workflow-language/cwltool/pull/1506
        for n in graph:
            ns = n.pop("$namespaces", {})
            if ns:
                json_wf.setdefault("$namespaces", {}).update(ns)
        defs = load_document_by_yaml(json_wf, self.wf_path.absolute().as_uri(), load_all=True)
        if not isinstance(defs, list):
            defs = [defs]
        def_map = {}
        for d in defs:
            k = _get_fragment(d.id)
            if k == "main":
                k = self.wf_path.name
            def_map[k] = d
        self.workflow_definition = _normalize_workflow_definition(def_map)
        return def_map

    def get_step_maps(self):
        """
        Get a mapping of step names to their tool names and positions.
        """

        rval = {}
        for k, v in self.workflow_definition.items():
            if hasattr(v, "steps"):
                graph = self.build_step_graph(v)
                pos_map = {f: i for i, f in enumerate(nx.topological_sort(graph))}
                rval[k] = {}
                for s in v.steps:
                    f = _get_fragment(s.id)
                    rval[k][f] = {"tool": _get_fragment(s.run), "pos": pos_map[f]}
        return rval

    def build_step_graph(self, cwl_wf):
        """
        Build a graph of steps in the workflow.
        """

        out_map = {}
        for s in cwl_wf.steps:
            for o in s.out:
                out_map[o] = _get_fragment(s.id)
        graph = nx.DiGraph()
        for s in cwl_wf.steps:
            fragment = _get_fragment(s.id)
            graph.add_node(fragment)
            for i in s.in_:
                sources = [i.source] if not isinstance(i.source, list) else i.source
                for s in sources:
                    source_fragment = out_map.get(s)
                    if source_fragment:
                        graph.add_edge(source_fragment, fragment)
        return graph

    def convert_param(self,
                      prov_param,
                      crate,
                      convert_secondary=True,
                      parent=None,
                      manifest=None,
                      ):
        type_names = frozenset(str(_) for _ in prov_param.types())
        secondary_files = [_.generated_entity() for _ in prov_param.derivations()
                           if str(_.type) == "cwlprov:SecondaryFile"]
        if convert_secondary and secondary_files:
            main_entity = self.convert_param(prov_param,
                                             crate,
                                             convert_secondary=False,
                                             manifest=manifest)
            action_p = self.collections.get(main_entity.id)
            if not action_p:
                action_p = crate.add(ContextEntity(crate, properties={
                    "@type": "Collection"
                }))
                action_p["mainEntity"] = main_entity
                action_p["hasPart"] = [main_entity] + [
                    self.convert_param(_,
                                       crate,
                                       manifest=manifest,
                                       ) for _ in secondary_files
                ]
                crate.root_dataset.append_to("mentions", action_p)
                self.collections[main_entity.id] = action_p
            return action_p
        if "wf4ever:File" in type_names:
            hash_ = self.hashes[prov_param.id.localpart]
            dest = Path(parent.id if parent else "") / hash_
            action_p = crate.dereference(dest.as_posix())
            if not action_p:
                source = manifest[hash_]
                action_p = crate.add_file(source, dest, properties={
                    "sha1": hash_,
                    "contentSize": str(Path(source).stat().st_size)
                })
                _set_alternate_name(prov_param, action_p, parent=parent)
                try:
                    source_k = str(source.resolve(strict=False))
                except RuntimeError:
                    source_k = str(source)
                self.file_map[source_k] = dest
            return action_p
        if "ro:Folder" in type_names:
            hash_ = self.hashes[prov_param.id.localpart]
            dest = Path(parent.id if parent else "") / hash_
            action_p = crate.dereference(dest.as_posix())
            if not action_p:
                action_p = crate.add_directory(dest_path=dest)
                _set_alternate_name(prov_param, action_p, parent=parent)
                for child in _get_dict(prov_param).values():
                    part = self.convert_param(child,
                                              crate,
                                              parent=action_p,
                                              manifest=manifest,
                                              )
                    action_p.append_to("hasPart", part)
            return action_p
        if prov_param.value is not None:
            return str(prov_param.value)
        if "prov:Dictionary" in type_names:
            return dict(
                (k, self.convert_param(v,
                                       crate,
                                       manifest=manifest,
                                       ))
                for k, v in _get_dict(prov_param).items()
                if k != "@id"
            )
        if "prov:Collection" in type_names:
            return [self.convert_param(_,
                                       crate,
                                       manifest=manifest,
                                       ) for _ in _get_members(prov_param)]
        if prov_param.id.uri == CWLPROV_NONE:
            return None
        raise RuntimeError(f"No value to convert for {prov_param}")

    def get_hashes(self, provenance):
        for r in provenance.prov_doc.get_records(prov.model.ProvEntity):
            self.get_hash(Entity(provenance, r))

    def get_hash(self, prov_param):
        k = prov_param.id.localpart
        try:
            return self.hashes[k]
        except KeyError:
            type_names = frozenset(str(_) for _ in prov_param.types())
            if "wf4ever:File" in type_names:
                hash_ = next(prov_param.specializationOf()).id.localpart
                self.hashes[k] = hash_
                return hash_
            elif "ro:Folder" in type_names:
                m = hashlib.sha1()
                m.update("".join(sorted(
                    self.get_hash(_) for _ in _get_dict(prov_param).values()
                )).encode())
                self.hashes[k] = hash_ = m.hexdigest()
                return hash_

    def map_input_data(self, crate, data):
        if isinstance(data, list):
            return [self.map_input_data(crate, _) for _ in data]
        if isinstance(data, dict):
            rval = {}
            for k, v in data.items():
                if k == "location":
                    source = self.root / "workflow" / v
                    try:
                        source_k = str(source.resolve(strict=False))
                    except RuntimeError:
                        source_k = str(source)
                    dest = self.file_map.get(source_k)
                    rval[k] = str(dest) if dest else v
                    fmt = data.get("format")
                    if fmt:
                        entity = crate.get(str(dest))
                        if entity:
                            entity["encodingFormat"] = fmt
                else:
                    rval[k] = self.map_input_data(crate, v)
            return rval
        return data


def _get_members(entity):
    membership = entity.provenance.record_with_attr(
        prov.model.ProvMembership, entity.id, prov.model.PROV_ATTR_COLLECTION
    )
    member_ids = (_.get_attribute(prov.model.PROV_ATTR_ENTITY) for _ in membership)
    return (entity.provenance.entity(first(_)) for _ in member_ids)


def _normalize_workflow_definition(workflow_definition):
    inline_tools = {}
    for d in workflow_definition.values():
        if not hasattr(d, "steps") or not d.steps:
            continue
        for s in d.steps:
            if hasattr(s, "run") and s.run:
                if hasattr(s.run, "id"):
                    tool = s.run
                    if tool.id.startswith("_:"):  # CWL > 1.0
                        tool.id = f"{s.id}/run"
                    inline_tools[_get_fragment(tool.id)] = tool
                    s.run = tool.id
    return workflow_definition.update(inline_tools)


def _set_alternate_name(prov_param, action_p, parent=None):
    basename = getattr(prov_param, "basename", None)
    if not basename:
        return
    if not parent:
        action_p["alternateName"] = basename
        return
    if "alternateName" in parent:
        action_p["alternateName"] = (Path(parent["alternateName"]) / basename).as_posix()


def _get_dict(entity):
    d = {}
    for qname in entity.record.get_attribute("prov:hadDictionaryMember"):
        kvp = entity.provenance.entity(qname)
        key = first(kvp.record.get_attribute("prov:pairKey"))
        entity_id = first(kvp.record.get_attribute("prov:pairEntity"))
        d[key] = entity.provenance.entity(entity_id)
    return d


def _resolve_plan(activity):
    job_qname = activity.plan()
    plan = activity.provenance.entity(job_qname)
    if not plan:
        m = SCATTER_JOB_PATTERN.match(str(job_qname))
        if m:
            plan = activity.provenance.entity(m.groups()[0])
    return plan


def _get_relative_uri(uri):
    doc, fragment = uri.rsplit("#", 1)
    return f"{doc.rsplit('/', 1)[-1]}#{fragment}"


def _properties_from_cwl_param(cwl_p):
    def is_structured(cwl_type):
        return getattr(cwl_type, "type_", None) in ("array", "record")
    additional_type = "Collection" if cwl_p.secondaryFiles else _convert_cwl_type(cwl_p.type_)
    properties = {
        "@type": "FormalParameter",
        "additionalType": additional_type
    }
    if hasattr(cwl_p, "doc") and cwl_p.doc:
        properties["description"] = cwl_p.doc
    elif hasattr(cwl_p, "label") and cwl_p.label:
        # name is used for the parameter's id to support reproducibility
        properties["description"] = cwl_p.label
    if cwl_p.format:
        properties["encodingFormat"] = cwl_p.format
    if isinstance(cwl_p.type_, list) and "null" in cwl_p.type_:
        properties["valueRequired"] = "False"
    if is_structured(cwl_p.type_):
        properties["multipleValues"] = "True"
    if hasattr(cwl_p, "default"):
        if isinstance(cwl_p.default, dict):
            if cwl_p.default.get("class") in ("File", "Directory"):
                default = cwl_p.default.get("location", cwl_p.default.get("path"))
            if default:
                properties["defaultValue"] = default
        elif not is_structured(cwl_p.type_) and cwl_p.default is not None:
            properties["defaultValue"] = str(cwl_p.default)
        # TODO: support more cases
    if getattr(cwl_p.type_, "type_", None) == "enum":
        properties["valuePattern"] = "|".join(_.rsplit("/", 1)[-1] for _ in cwl_p.type_.symbols)
    return properties


def _convert_cwl_type(cwl_type):
    if isinstance(cwl_type, list):
        s = set(_convert_cwl_type(_) for _ in cwl_type)
        s.discard(None)
        return s.pop() if len(s) == 1 else sorted(s)
    if isinstance(cwl_type, str):
        return CWL_TYPE_MAP[cwl_type]
    if cwl_type.type_ == "enum":
        return "Text"  # use actionOption to represent choices?
    if cwl_type.type_ == "array":
        return _convert_cwl_type(cwl_type.items)
    if cwl_type.type_ == "record":
        return "PropertyValue"


def _get_fragment(uri):
    return uri.rsplit("#", 1)[-1]


def _cut_step_part(relative_uri):
    parts = relative_uri.split("/", 2)
    if len(parts) > 2:
        relative_uri = parts[0] + "/" + parts[2]
    return relative_uri
