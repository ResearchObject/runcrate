class converter:
    def __init__(self):
        pass

    def get_workflow(self, wf_path):
        """\
        Get the workflow from the given path.

        Returns a dictionary where tools / workflows are mapped by their ids.
        """
        raise NotImplementedError("get_workflow")

    def get_step_maps(self, wf_defs):
        """\
        Get a mapping of step names to their tool names and positions.
        """
        raise NotImplementedError("get_step_maps")

    def build_step_graph(self, wf):
        """\
        Build a graph of steps in the workflow.
        """
        raise NotImplementedError("build_step_graph")

    def convert_param(self, prov_param, crate, convert_secondary=True, parent=None):
        """\
        Convert a CWLProv parameter to a RO-Crate entity.
        """
        raise NotImplementedError("convert_param")
