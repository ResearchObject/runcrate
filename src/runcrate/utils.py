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


def as_list(value):
    if isinstance(value, list):
        return value
    return [value]


def parse_img_name(img_name):
    parts = img_name.split("/")
    if len(parts) == 3:
        registry = parts[0]
        name = "/".join(parts[1:])
    else:
        registry = "docker.io"
        name = "/".join(parts)
    return registry, name


def parse_img(img_str):
    """\
    Parse image string following the docker pull syntax NAME[:TAG|@DIGEST].
    CWL's DockerRequirement also accepts HTTP URLs for docker load.
    """
    parsed = {}
    if img_str.startswith("http://") or img_str.startswith("https://"):
        return img_str
    parts = img_str.rsplit("@", 1)
    if len(parts) == 2:
        parsed["registry"], parsed["name"] = parse_img_name(parts[0])
        algo, digest = parts[1].split(":", 1)
        assert algo == "sha256"
        parsed[algo] = digest
        return parsed
    parts = img_str.rsplit(":", 1)
    if len(parts) == 2:
        parsed["registry"], parsed["name"] = parse_img_name(parts[0])
        parsed["tag"] = parts[1]
        return parsed
    assert len(parts) == 1
    parsed["registry"], parsed["name"] = parse_img_name(parts[0])
    return parsed
