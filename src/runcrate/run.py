# Copyright 2023 CRS4.
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
Run the workflow from a Workflow Run RO-Crate.
"""

import sys

from rocrate.rocrate import ROCrate

from .utils import as_list


CWL_ID = "https://w3id.org/workflowhub/workflow-ro-crate#cwl"


def check_runnable(crate):
    wf = crate.mainEntity
    if not wf:
        raise RuntimeError("crate does not have a mainEntity")
    if "ComputationalWorkflow" not in as_list(wf.type):
        raise RuntimeError("mainEntity is not a ComputationalWorkflow")
    lang = wf.get("programmingLanguage")
    if not lang or getattr(lang, "id", None) != CWL_ID:
        raise RuntimeError(f"workflow language must be {CWL_ID}")
    actions = [_ for _ in crate.get_entities()
               if "CreateAction" in as_list(_.type) and _.get("instrument") is wf]
    if not actions:
        raise RuntimeError(f"no CreateAction associated to {wf.id}")
    return wf, actions[0]


def run_crate(crate):
    if not isinstance(crate, ROCrate):
        crate = ROCrate(crate)
    wf, action = check_runnable(crate)
    sys.stdout.write(f"workflow: {wf.id}; action: {action.id}\n")
