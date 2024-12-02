import hashlib
import json
from pathlib import Path

import networkx as nx
import prov.model
from cwl_utils.parser import load_document_by_yaml
from cwlprov.prov import Entity
from cwlprov.utils import first
from rocrate.model.contextentity import ContextEntity

from .base import converter


CWLPROV_NONE = "https://w3id.org/cwl/prov#None"


class cwlConverter(converter):
    hashes = {}
    collections = {}

    def __init__(self):
        pass

    def get_workflow(self, wf_path):
        """\
        Get the workflow from the given path.

        Returns a dictionary where tools / workflows are mapped by their ids.

        Does not use load_document_by_uri, so we can hack the json to work
        around issues.
        """

        wf_path = Path(wf_path)
        with open(wf_path, "rt") as f:
            json_wf = json.load(f)
        graph = json_wf.get("$graph", [json_wf])
        # https://github.com/common-workflow-language/cwltool/pull/1506
        for n in graph:
            ns = n.pop("$namespaces", {})
            if ns:
                json_wf.setdefault("$namespaces", {}).update(ns)
        defs = load_document_by_yaml(json_wf, wf_path.absolute().as_uri(), load_all=True)
        if not isinstance(defs, list):
            defs = [defs]
        def_map = {}
        for d in defs:
            k = _get_fragment(d.id)
            if k == "main":
                k = wf_path.name
            def_map[k] = d
        _normalize_cwl_defs(def_map)
        return def_map

    def get_step_maps(self, cwl_defs):
        rval = {}
        for k, v in cwl_defs.items():
            if hasattr(v, "steps"):
                graph = self.build_step_graph(v)
                pos_map = {f: i for i, f in enumerate(nx.topological_sort(graph))}
                rval[k] = {}
                for s in v.steps:
                    f = _get_fragment(s.id)
                    rval[k][f] = {"tool": _get_fragment(s.run), "pos": pos_map[f]}
        return rval

    def build_step_graph(self, cwl_wf):
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
                      hashes=None,
                      manifest=None,
                      file_map=None
                      ):
        type_names = frozenset(str(_) for _ in prov_param.types())
        secondary_files = [_.generated_entity() for _ in prov_param.derivations()
                           if str(_.type) == "cwlprov:SecondaryFile"]
        if convert_secondary and secondary_files:
            main_entity = self.convert_param(prov_param,
                                             crate,
                                             convert_secondary=False,
                                             manifest=manifest,
                                             file_map=file_map)
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
                                       file_map=file_map
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
                file_map[source_k] = dest
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
                                              file_map=file_map
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
                                       file_map=file_map
                                       ))
                for k, v in _get_dict(prov_param).items()
                if k != "@id"
            )
        if "prov:Collection" in type_names:
            return [self.convert_param(_,
                                       crate,
                                       manifest=manifest,
                                       file_map=file_map
                                       ) for _ in _get_members(prov_param)]
        if prov_param.id.uri == CWLPROV_NONE:
            return None
        raise RuntimeError(f"No value to convert for {prov_param}")

    def get_hashes(self, provenance):
        for r in provenance.prov_doc.get_records(prov.model.ProvEntity):
            self._get_hash(self.hashes, Entity(provenance, r))

    def _get_hash(self, hashes, prov_param):
        k = prov_param.id.localpart
        try:
            return hashes[k]
        except KeyError:
            type_names = frozenset(str(_) for _ in prov_param.types())
            if "wf4ever:File" in type_names:
                hash_ = next(prov_param.specializationOf()).id.localpart
                self.hashes[k] = hash_
                return hash_
            elif "ro:Folder" in type_names:
                m = hashlib.sha1()
                m.update("".join(sorted(
                    self._get_hash(hashes, _) for _ in _get_dict(prov_param).values()
                )).encode())
                self.hashes[k] = hash_ = m.hexdigest()
                return hash_


def _get_members(entity):
    membership = entity.provenance.record_with_attr(
        prov.model.ProvMembership, entity.id, prov.model.PROV_ATTR_COLLECTION
    )
    member_ids = (_.get_attribute(prov.model.PROV_ATTR_ENTITY) for _ in membership)
    return (entity.provenance.entity(first(_)) for _ in member_ids)


def _get_fragment(uri):
    return uri.rsplit("#", 1)[-1]


def _normalize_cwl_defs(cwl_defs):
    inline_tools = {}
    for d in cwl_defs.values():
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
    cwl_defs.update(inline_tools)


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
