class converter:
    def __init__(self):
        self.root = None
        self.workflow_name = None
        self.license = None
        self.readme = None
        self.wf_path = None
        self.workflow_definition = {}
        self.step_maps = {}
        self.ro = None
        self.with_prov = set()
        self.workflow_run = None
        self.roc_engine_run = None
        self.control_actions = {}        
        self.collections = {}
        self.hashes = {}
        self.file_map = {}
        self.manifest = None

    # --------------------------------------------------------------------------
    # Top level functions - called by the build() function

    def add_root_metadata(self, crate):
        """
        Add metadata to the root of the crate.
        """
        raise NotImplementedError("add_root_metadata")

    def add_profiles(self, crate):
        """
        Add profiles to the crate.
        """
        raise NotImplementedError("add_profiles")

    def add_workflow(self, crate):
        """
        Add the workflow to the crate.
        """
        raise NotImplementedError("add_workflow")

    def add_engine_run(self, crate):
        """
        Add the engine run to the crate.
        """
        raise NotImplementedError("add_engine_run")

    def add_action(self, crate, workflow_run):
        """
        Add the action to the crate.
        """
        raise NotImplementedError("add_action")

    def patch_workflow_input_collection(self, crate):
        """
        Patch the workflow input collection.
        """
        raise NotImplementedError("patch_workflow_input_collection")

    def add_inputs_files(self, crate):
        """
        Add input files to the crate.
        """
        raise NotImplementedError("add_inputs_files")

    def add_output_formats(self, crate):
        """
        Add output formats to the crate.
        """
        raise NotImplementedError("add_output_formats")
        
    # --------------------------------------------------------------------------
    # Helper functions - called by the top level functions

    def get_workflow(self, wf_path):
        """
        Get the workflow from the given path.

        Returns a dictionary where tools / workflows are mapped by their ids.
        """
        raise NotImplementedError("get_workflow")

    def get_step_maps(self, wf_defs):
        """
        Get a mapping of step names to their tool names and positions.
        """
        raise NotImplementedError("get_step_maps")

    def build_step_graph(self, wf):
        """
        Build a graph of steps in the workflow.
        """
        raise NotImplementedError("build_step_graph")

    def convert_param(self, prov_param, crate, convert_secondary=True, parent=None):
        """
        Convert a CWLProv parameter to a RO-Crate entity.
        """
        raise NotImplementedError("convert_param")
