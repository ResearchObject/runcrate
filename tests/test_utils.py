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

from runcrate.utils import parse_img


def test_parse_img():
    assert parse_img("python") == {
        "registry": "docker.io",
        "name": "python"
    }
    assert parse_img("python:3.12") == {
        "registry": "docker.io",
        "name": "python",
        "tag": "3.12"
    }
    assert parse_img("josiah/python:3.11") == {
        "registry": "docker.io",
        "name": "josiah/python",
        "tag": "3.11"
    }
    assert parse_img("quay.io/josiah/python:3.11") == {
        "registry": "quay.io",
        "name": "josiah/python",
        "tag": "3.11"
    }
    assert parse_img("python@sha256:7b8d65a924f596eb65306214f559253c468336bcae09fd575429774563460caf") == {
        "registry": "docker.io",
        "name": "python",
        "sha256": "7b8d65a924f596eb65306214f559253c468336bcae09fd575429774563460caf"
    }
