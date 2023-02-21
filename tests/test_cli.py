# Copyright 2022 CRS4.
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

from click.testing import CliRunner
from rocrate.rocrate import ROCrate

from runcrate.cli import cli


def test_cli_convert(data_dir, tmpdir, monkeypatch):
    monkeypatch.chdir(str(tmpdir))
    root = data_dir / "revsort-run-1"
    runner = CliRunner()
    args = ["convert", str(root)]
    assert runner.invoke(cli, args).exit_code == 0
    crate_zip = tmpdir / f"{root.name}.crate.zip"
    assert crate_zip.is_file()
    crate = ROCrate(crate_zip)
    assert not crate.root_dataset.get("license")
    workflow = crate.mainEntity
    assert workflow["name"] == "packed.cwl"


def test_cli_convert_output(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    # output zipped crate
    crate_zip = tmpdir / "crate.zip"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_zip)]
    assert runner.invoke(cli, args).exit_code == 0
    assert crate_zip.is_file()
    crate = ROCrate(crate_zip)
    assert not crate.root_dataset.get("license")
    workflow = crate.mainEntity
    assert workflow["name"] == "packed.cwl"
    crate_zip.unlink()
    # output crate dir
    crate_dir = tmpdir / "revsort-run-1-crate"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir)]
    assert runner.invoke(cli, args).exit_code == 0
    assert crate_dir.is_dir()
    crate = ROCrate(crate_dir)
    assert not crate.root_dataset.get("license")
    workflow = crate.mainEntity
    assert workflow["name"] == "packed.cwl"


def test_cli_convert_license(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    license = "MIT"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "-l", license]
    assert runner.invoke(cli, args).exit_code == 0
    crate = ROCrate(crate_dir)
    assert crate.root_dataset["license"] == license


def test_cli_convert_workflow_name(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    workflow_name = "RevSort"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "-w", workflow_name]
    assert runner.invoke(cli, args).exit_code == 0
    crate = ROCrate(crate_dir)
    workflow = crate.mainEntity
    assert workflow["name"] == workflow_name


def test_cli_convert_readme(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    readme = data_dir / "README.md"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "--readme", readme]
    assert runner.invoke(cli, args).exit_code == 0
    crate = ROCrate(crate_dir)
    assert crate.get(readme.name)
