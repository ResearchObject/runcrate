# Copyright 2023 The University of Manchester
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

from pyshex.evaluate import evaluate
from rdflib import Graph, Namespace
from arcp import arcp_random
from rocrate.rocrate import ROCrate
import rocrateValidator.validate

    
class CrateValidator():
    def __init__(self, root):
        self.root = root
        self.base = arcp_random()
        self.crate = ROCrate(root)

    def _detect_profiles(self):
        """Auto-detect Run Crate profile based on conformsTo

        Return a tuple (process_run, workflow_run, provenance_run) with
        the corresponding detected profiles URIs. Profiles not detected are
        represented as ``None`` in the tuple.
        """
        profiles = self.crate.root_dataset.get("conformsTo", [])
        if not isinstance(profiles, list):
            profiles = [profiles]
        
        process_run, workflow_run, provenance_run = (None,)*3
        for p in profiles:
            if p.id.startswith("https://w3id.org/ro/wfrun/process/"):
                process_run = p
            if p.id.startswith("https://w3id.org/ro/wfrun/workflow/"):
                workflow_run = p
            if p.id.startswith("https://w3id.org/ro/wfrun/provenance/"):
                provenance_run = p
            # TODO: Also check for Workflow profile stand-alone
        return (process_run, workflow_run, provenance_run)

    def ro_crate_check(self):
        v = rocrateValidator.validate.validate(self.root)
        # FIXME upstream: This does an ugly JSON print instead of returning 
        # the validation result
        v.validator()

    def process_run_check(self):
        pass
    
    def workflow_run_check(self):
        pass
    
    def provenance_run_check(self):
        pass

