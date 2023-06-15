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

Only CWL is supported for now.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from rocrate.model.entity import Entity
from rocrate.rocrate import ROCrate

from .utils import as_list


CWL_ID = "https://w3id.org/workflowhub/workflow-ro-crate#cwl"
PARAMS_FILENAME = "params.json"
EXECUTABLE = "cwl-runner"
STREAMFLOW_FILE = "streamflow.yml"


def check_runnable(crate):
    wf = crate.mainEntity
    if not wf:
        raise RuntimeError("crate does not have a mainEntity")
    if "ComputationalWorkflow" not in as_list(wf.type):
        raise RuntimeError("mainEntity is not a ComputationalWorkflow")
    lang = wf.get("programmingLanguage")
    if not lang or (getattr(lang, "id", None) != CWL_ID and lang != CWL_ID):
        raise RuntimeError(f"workflow language must be {CWL_ID}")
    actions = [_ for _ in crate.get_entities()
               if "CreateAction" in as_list(_.type) and _.get("instrument") is wf]
    if not actions:
        raise RuntimeError(f"no CreateAction associated to {wf.id}")
    return wf, actions[0]


def auto_convert(value):
    if not isinstance(value, str):  # should not happen
        return value
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def convert_file(fp, obj):
    retval = {"class": "File"}
    alt_name = obj.get("alternateName")
    retval["location"] = alt_name or obj.id
    format_ = fp.get("encodingFormat", obj.get("encodingFormat"))
    if format_:
        retval["format"] = format_
    return retval


def convert_dataset(fp, obj):
    retval = {"class": "Directory"}
    alt_name = obj.get("alternateName")
    retval["location"] = alt_name or obj.id
    return retval


def convert_value(fp, value):
    if fp is None:
        return auto_convert(value)
    type_ = fp.get("additionalType")
    if type_ == "PropertyValue":
        return {_["name"]: convert_value(None, _["value"]) for _ in as_list(value)}
    if isinstance(value, list):
        return [convert_value(fp, _) for _ in value]
    if not type_ or isinstance(type_, list) or type_ == "DataType":
        return auto_convert(value)
    if type_ == "Text":
        return value
    if type_ == "Integer":
        return int(value)
    if type_ == "Float":
        return float(value)
    if type_ == "Boolean":
        return value.lower() == "true"
    if isinstance(value, Entity):
        if "File" in as_list(value.type):
            return convert_file(fp, value)
        elif "Dataset" in as_list(value.type):
            return convert_dataset(fp, value)
        # TODO: support Collection
    raise RuntimeError(f"cannot convert {value!r}")


def convert_obj(fp, obj):
    if "Collection" in as_list(obj.type):
        main_entity = obj.get("mainEntity")
        if not main_entity:
            parts = obj.get("hasPart")
            if not parts:
                raise ValueError(f"collection {obj.id} has no parts")
            main_entity = parts[0]
        if "File" in as_list(main_entity.type):
            return convert_file(fp, main_entity)
        if "Dataset" in as_list(main_entity.type):
            return convert_dataset(fp, main_entity)
        raise ValueError(f"{main_entity.id} should be a File or Dataset")
    elif "File" in as_list(obj.type):
        return convert_file(fp, obj)
    elif "Dataset" in as_list(obj.type):
        return convert_dataset(fp, obj)
    elif "PropertyValue" not in as_list(obj.type):
        raise RuntimeError(f"object {obj.id} should be a File, Dataset, Collection or PropertyValue")
    value = obj.get("value")
    if not value:
        raise RuntimeError(f"object {obj.id} has no value")
    return convert_value(fp, value)


def gen_params(wf, action):
    params = {}
    wf_inputs = set(wf.get("input", []))
    for obj in action.get("object", []):
        sel = [_ for _ in as_list(obj.get("exampleOfWork")) if _ in wf_inputs]
        if not sel:
            continue
        fp = sel[0]  # there should be only one of these
        name = fp.get("name", obj.get("name"))
        if not name:
            continue
        params[name] = convert_obj(fp, obj)
    return params


def rename_data_entities(obj, workdir):
    if "Collection" in as_list(obj.type):
        parts = set(as_list(obj.get("hasPart", [])))
        main_entity = obj.get("mainEntity")
        if main_entity:
            parts.add(main_entity)  # should already be in parts
        for p in parts:
            rename_data_entities(p, workdir)
    alt_name = obj.get("alternateName")
    if alt_name:
        dst_path = workdir / alt_name
        if "Dataset" in as_list(obj.type):
            (dst_path).mkdir(parents=True, exist_ok=True)
            for p in set(as_list(obj.get("hasPart", []))):
                rename_data_entities(p, workdir)
        if "File" in as_list(obj.type):
            (dst_path.parent).mkdir(parents=True, exist_ok=True)
            src_path = workdir / obj.id
            try:
                shutil.copy(src_path, dst_path)
            except shutil.SameFileError:
                pass


def find_streamflow_file(crate):
    for e in crate.get_entities():
        if "File" not in as_list(e.type):
            continue
        candidates = e.id, e.get("alternateName", "")
        for c in candidates:
            if c.lower().rsplit("/", 1)[-1] == STREAMFLOW_FILE:
                return e.id


def run_crate(crate, executable=None, keep_wd=False, dry_run=False):
    if executable is None:
        executable = EXECUTABLE
    if not isinstance(crate, ROCrate):
        crate = ROCrate(crate)
    wf, action = check_runnable(crate)
    sys.stdout.write(f"workflow: {wf.id}; action: {action.id}\n")
    workdir = Path(tempfile.mkdtemp(prefix="runcrate_"))
    sys.stdout.write(f"working dir: {workdir}\n")
    params = gen_params(wf, action)
    crate.write(workdir)
    params_path = Path(workdir / PARAMS_FILENAME)
    with open(params_path, "w") as f:
        json.dump(params, f, indent=4)
    for e in crate.data_entities:
        rename_data_entities(e, workdir)
    if dry_run:
        return
    wf_path = workdir / wf.id
    streamflow_relpath = find_streamflow_file(crate)
    if streamflow_relpath:
        streamflow_file = workdir / streamflow_relpath
        args = [executable, "--streamflow-file", streamflow_file, wf_path, params_path]
    else:
        args = [executable, wf_path, params_path]
    sys.stdout.write(f"running {args}\n")
    try:
        subprocess.check_call(args)
    finally:
        if not keep_wd:
            shutil.rmtree(workdir)
