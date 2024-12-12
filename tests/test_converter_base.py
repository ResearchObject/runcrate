# Copyright 2022-2024 CRS4.
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

from runcrate.converters.base import Converter

class TestConverter(Converter):
    def add_workflow(self, workflow):
        raise NotImplementedError

    def add_engine_run(self, engine_run):
        raise NotImplementedError

    def add_action(self, action, step):
        raise NotImplementedError

    def patch_workflow_input_collection(self, input_collection):
        raise NotImplementedError

    def add_inputs_files(self, inputs_files):
        raise NotImplementedError

    def add_output_formats(self, output_formats):
        raise NotImplementedError

    def get_workflow(self, workflow):
        raise NotImplementedError

    def get_step_maps(self, step_maps):
        raise NotImplementedError

    def build_step_graph(self, step_graph):
        raise NotImplementedError

    def convert_param(self, param, step):
        raise NotImplementedError


@pytest.fixture
def converter_instance():
    converter_instance = TestConverter()
    return converter_instance


def test_initialization(converter_instance):
    assert isinstance(converter_instance, Converter)


def test_add_workflow(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.add_workflow(None)


def test_add_engine_run(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.add_engine_run(None)


def test_add_action(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.add_action(None, None)


def test_patch_workflow_input_collection(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.patch_workflow_input_collection(None)


def test_add_inputs_files(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.add_inputs_files(None)


def test_add_output_formats(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.add_output_formats(None)


def test_get_workflow(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.get_workflow(None)


def test_get_step_maps(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.get_step_maps(None)


def test_build_step_graph(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.build_step_graph(None)


def test_convert_param(converter_instance):
    with pytest.raises(NotImplementedError):
        converter_instance.convert_param(None, None)
