from .base import converter

from pathlib import Path
import json
import networkx as nx

from cwl_utils.parser import load_document_by_yaml

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


class cwlConverter(converter):
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

