from .base import converter

from pathlib import Path
import json

from cwl_utils.parser import load_document_by_yaml


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
            k = self._get_fragment(d.id)
            if k == "main":
                k = wf_path.name
            def_map[k] = d
        self._normalize_cwl_defs(def_map)
        return def_map

    def _get_fragment(self, uri):
        return uri.rsplit("#", 1)[-1]

    def _normalize_cwl_defs(self, cwl_defs):
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
                        inline_tools[self._get_fragment(tool.id)] = tool
                        s.run = tool.id
        cwl_defs.update(inline_tools)
