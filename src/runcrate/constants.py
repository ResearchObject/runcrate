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

PROFILES_BASE = "https://w3id.org/ro/wfrun"
PROFILES_VERSION = "0.1"

PROCESS_PROFILE_BASE = f"{PROFILES_BASE}/process"
WORKFLOW_PROFILE_BASE = f"{PROFILES_BASE}/workflow"
PROVENANCE_PROFILE_BASE = f"{PROFILES_BASE}/provenance"

PROCESS_PROFILE = f"{PROCESS_PROFILE_BASE}/{PROFILES_VERSION}"
WORKFLOW_PROFILE = f"{WORKFLOW_PROFILE_BASE}/{PROFILES_VERSION}"
PROVENANCE_PROFILE = f"{PROVENANCE_PROFILE_BASE}/{PROFILES_VERSION}"

TERMS_NAMESPACE = "https://w3id.org/ro/terms/workflow-run"
EXTRA_TERMS = {t: f"{TERMS_NAMESPACE}#t" for t in [
    "ParameterConnection",
    "connection",
    "sourceParameter",
    "targetParameter",
    "sha1",
]}
