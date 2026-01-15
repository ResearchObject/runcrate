# Copyright 2023-2026 CRS4.
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

import pytest
from rocrate.model.contextentity import ContextEntity
from rocrate.rocrate import ROCrate

from runcrate.run import check_runnable


CWL_ID = "https://w3id.org/workflowhub/workflow-ro-crate#cwl"


def test_check_runnable(data_dir, tmpdir):
    crate = ROCrate()
    with pytest.raises(RuntimeError):
        check_runnable(crate)  # no wf
    crate.mainEntity = crate.add_file("http://example.org/example.pdf")
    with pytest.raises(RuntimeError):
        check_runnable(crate)  # not a ComputationalWorkflow
    crate.mainEntity = crate.add_file("http://example.org/foo.a", properties={
        "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow"]
    })
    with pytest.raises(RuntimeError):
        check_runnable(crate)  # no programmingLanguage in wf
    crate.mainEntity = crate.add_file("http://example.org/foo.cwl", properties={
        "@type": ["File", "SoftwareSourceCode", "ComputationalWorkflow"],
        "programmingLanguage": CWL_ID
    })
    with pytest.raises(RuntimeError):
        check_runnable(crate)  # no associated action
    action = crate.add(ContextEntity(crate, properties={
        "@type": "CreateAction",
        "instrument": crate.mainEntity,
    }))
    assert check_runnable(crate) == (crate.mainEntity, action)
    crate.add_workflow("http://example.org/bar.cwl", None, main=True, lang="cwl")
    action = crate.add(ContextEntity(crate, properties={
        "@type": "CreateAction",
        "instrument": crate.mainEntity,
    }))
    assert crate.mainEntity.id == "http://example.org/bar.cwl"
    assert check_runnable(crate) == (crate.mainEntity, action)
