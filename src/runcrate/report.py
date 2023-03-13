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


def dump_action(tool, action, control_action=None, f=None):
    if f is None:
        f = sys.stdout
    instrument = action["instrument"]
    f.write(f"action {action.id}\n")
    if control_action:
        f.write(f"  step: {control_action['instrument'].id}\n")
    f.write(f"  instrument: {instrument.id} ({instrument.type})\n")
    f.write(f"  started: {action.get('startTime', '???')}\n")
    f.write(f"  ended: {action.get('endTime', '???')}\n")
    objects = {p.id: obj for obj in action.get("object", [])
               for p in as_list(obj.get("exampleOfWork", []))}
    results = {p.id: res for res in action.get("result", [])
               for p in as_list(res.get("exampleOfWork", []))}
    f.write("  inputs:\n")
    for in_ in tool.get("input", []):
        obj = objects.get(in_.id)
        f.write(f"    {in_.id}: {obj.get('value', obj.id) if obj else ''}\n")
    for obj in action.get("object", []):
        if "exampleOfWork" not in obj:
            f.write(f"    ???: {obj.get('value', obj.id)}\n")
    f.write("  outputs:\n")
    for out in tool.get("output", []):
        res = results.get(out.id)
        f.write(f"    {out.id}: {res.get('value', res.id) if res else ''}\n")
    for res in action.get("result", []):
        if "exampleOfWork" not in res:
            f.write(f"    ???: {res.get('value', res.id)}\n")


def dump_crate_actions(crate, f=None):
    if f is None:
        f = sys.stdout
    if not isinstance(crate, ROCrate):
        crate = ROCrate(crate)
    wf = crate.mainEntity
    actions = {}
    for a in crate.contextual_entities:
        if a.type == "CreateAction":
            actions.setdefault(a["instrument"].id, []).append(a)
    assert len(actions[wf.id]) == 1
    wf_action = actions[wf.id][0]
    control_actions = {a: ca for ca in crate.contextual_entities
                       for a in as_list(ca.get("object", []))
                       if ca.type == "ControlAction"}
    dump_action(wf, wf_action, f=f)
    for tool in wf.get("hasPart", []):
        for a in actions.get(tool.id, []):
            f.write("\n")
            dump_action(tool, a, control_actions.get(a), f=f)
