# Copyright 2022-2023 CRS4.
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
Read a Workflow Run RO-Crate and report on the actions it describes.
"""

import sys

from rocrate.rocrate import ROCrate

from .utils import as_list


def dump_action(action, control_action=None, f=None):
    if f is None:
        f = sys.stdout
    tool = action["instrument"]
    f.write(f"action: {action.id}\n")
    if control_action:
        f.write(f"  step: {control_action['instrument'].id}\n")
    f.write(f"  instrument: {tool.id} ({tool.type})\n")
    start_time = action.get('startTime')
    if start_time:
        f.write(f"  started: {start_time}\n")
    end_time = action.get('endTime')
    if end_time:
        f.write(f"  ended: {end_time}\n")
    objects = action.get("object", [])
    if objects:
        f.write("  inputs:\n")
        inputs = set(tool.get("input", []))
        for obj in objects:
            f.write(f"    {obj.get('value', obj.id)}")
            for p in as_list(obj.get("exampleOfWork", [])):
                if p in inputs:
                    f.write(f" <- {p.id}")
            f.write("\n")
    results = action.get("result", [])
    if results:
        f.write("  outputs:\n")
        outputs = set(tool.get("output", []))
        for res in results:
            f.write(f"    {res.get('value', res.id)}")
            for p in as_list(res.get("exampleOfWork", [])):
                if p in outputs:
                    f.write(f" <- {p.id}")
            f.write("\n")


def dump_crate_actions(crate, f=None):
    if f is None:
        f = sys.stdout
    if not isinstance(crate, ROCrate):
        crate = ROCrate(crate)
    actions = {}
    for a in crate.contextual_entities:
        if a.type == "CreateAction":
            actions.setdefault(a["instrument"].id, []).append(a)
    wf = crate.mainEntity
    if not wf:  # process run crate
        for action_list in actions.values():
            for a in action_list:
                dump_action(a, f=f)
                f.write("\n")
        return
    assert len(actions[wf.id]) == 1
    wf_action = actions[wf.id][0]
    control_actions = {a: ca for ca in crate.contextual_entities
                       for a in as_list(ca.get("object", []))
                       if ca.type == "ControlAction"}
    dump_action(wf_action, f=f)
    for tool in wf.get("hasPart", []):
        for a in actions.get(tool.id, []):
            f.write("\n")
            dump_action(a, control_actions.get(a), f=f)
