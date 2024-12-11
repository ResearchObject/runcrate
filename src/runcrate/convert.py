# Copyright 2022-2024 CRS4.
# Copyright 2023-2024 Michael R. Crusoe
# Copyright 2024 Senckenberg Society for Nature Research
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""\
Generate a Workflow Run RO-Crate from a CWLProv RO bundle.
"""

from pathlib import Path

from bdbag.bdbagit import BDBag
from cwlprov.prov import Provenance
from cwlprov.ro import ResearchObject
from rocrate.rocrate import ROCrate

from .constants import TERMS_NAMESPACE
from .converters import CONVERTERS

MANIFEST_FILE = "manifest-sha1.txt"


class ProvCrateBuilder:
    def __init__(self,
                 root,
                 converter=CONVERTERS["cwl"],
                 workflow_name=None,
                 license=None,
                 readme=None):
        self.converter = converter
        self.converter.root = Path(root)
        self.converter.workflow_name = workflow_name
        self.converter.license = license
        self.converter.readme = Path(readme) if readme else readme
        self.converter.wf_path = self.converter.root / "workflow" / self.converter.WORKFLOW_BASENAME
        self.converter.workflow_definition = self.converter.get_workflow()
        self.converter.step_maps = self.converter.get_step_maps()
        self.converter.ro = ResearchObject(BDBag(str(root)))
        self.converter.with_prov = set(str(_) for _ in self.converter.ro.resources_with_provenance())
        self.converter.workflow_run = Provenance(self.converter.ro).activity()
        self.converter.roc_engine_run = None
        self.converter.control_actions = {}
        self.converter.collection = {}
        self.converter.hashes = {}
        self.converter.file_map = {}
        self.converter.manifest = self.converter.get_manifest(self.converter.root, MANIFEST_FILE)

    def build(self):
        crate = ROCrate(gen_preview=False)
        crate.metadata.extra_contexts.append(TERMS_NAMESPACE)
        self.converter.add_root_metadata(crate)
        self.converter.add_profiles(crate)
        self.converter.add_workflow(crate)
        self.converter.add_engine_run(crate)
        self.converter.add_action(crate, self.converter.workflow_run)
        self.converter.patch_workflow_input_collection(crate)
        self.converter.add_inputs_file(crate)
        self.converter.add_output_formats(crate)
        return crate
