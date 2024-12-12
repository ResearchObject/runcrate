from abc import ABC, abstractmethod

from rocrate.model.contextentity import ContextEntity

from ..constants import PROFILES_BASE, PROFILES_VERSION, WROC_PROFILE_VERSION


class Converter(ABC):
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
        Add license and readme to the root of the crate, if provided.
        """
        if self.license:
            crate.root_dataset["license"] = self.license
        if self.readme:
            readme = crate.add_file(self.readme)
            readme["about"] = crate.root_dataset
            if self.readme.suffix.lower() == ".md":
                readme["encodingFormat"] = "text/markdown"

        return

    def add_profiles(self, crate):
        """
        Add profiles to the crate.
        """
        profiles = []
        for p in "process", "workflow", "provenance":
            id_ = f"{PROFILES_BASE}/{p}/{PROFILES_VERSION}"
            profiles.append(crate.add(ContextEntity(crate, id_, properties={
                "@type": "CreativeWork",
                "name": f"{p.title()} Run Crate",
                "version": PROFILES_VERSION,
            })))
        # FIXME: in the future, this could go out of sync with the wroc
        # profile added by ro-crate-py to the metadata descriptor
        wroc_profile_id = f"https://w3id.org/workflowhub/workflow-ro-crate/{WROC_PROFILE_VERSION}"
        profiles.append(crate.add(ContextEntity(crate, wroc_profile_id, properties={
            "@type": "CreativeWork",
            "name": "Workflow RO-Crate",
            "version": WROC_PROFILE_VERSION,
        })))
        crate.root_dataset["conformsTo"] = profiles

        return

    @abstractmethod
    def add_workflow(self, crate):
        """
        Add the workflow to the crate.
        """

    @abstractmethod
    def add_engine_run(self, crate):
        """
        Add the engine run to the crate.
        """

    @abstractmethod
    def add_action(self, crate, workflow_run):
        """
        Add the action to the crate.
        """

    @abstractmethod
    def patch_workflow_input_collection(self, crate):
        """
        Patch the workflow input collection.
        """

    @abstractmethod
    def add_inputs_files(self, crate):
        """
        Add input files to the crate.
        """

    @abstractmethod
    def add_output_formats(self, crate):
        """
        Add output formats to the crate.
        """

    # --------------------------------------------------------------------------
    # Helper functions - called by the top level functions

    @abstractmethod
    def get_workflow(self, wf_path):
        """
        Get the workflow from the given path.

        Returns a dictionary where tools / workflows are mapped by their ids.
        """

    @abstractmethod
    def get_step_maps(self, wf_defs):
        """
        Get a mapping of step names to their tool names and positions.
        """

    @abstractmethod
    def build_step_graph(self, wf):
        """
        Build a graph of steps in the workflow.
        """

    @abstractmethod
    def convert_param(self, prov_param, crate, convert_secondary=True, parent=None):
        """
        Convert a CWLProv parameter to a RO-Crate entity.
        """
