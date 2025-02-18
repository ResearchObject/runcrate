# Copyright 2022-2025 CRS4.
# Copyright 2024-2025 Senckenberg Society for Nature Research
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

from pathlib import Path

from click.testing import CliRunner
from rocrate.rocrate import ROCrate

from runcrate import __version__
from runcrate.cli import cli


def test_cli_convert(data_dir, tmpdir, monkeypatch):
    monkeypatch.chdir(str(tmpdir))
    root = data_dir / "revsort-run-1"
    runner = CliRunner()
    args = ["convert", str(root)]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate_zip = tmpdir / f"{root.name}.crate.zip"
    assert crate_zip.is_file()
    crate = ROCrate(crate_zip)
    assert crate.root_dataset.get("license") == "notspecified"
    workflow = crate.mainEntity
    assert workflow["name"] == "packed.cwl"


def test_cli_convert_output(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    # output zipped crate
    crate_zip = tmpdir / "crate.zip"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_zip)]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    assert crate_zip.is_file()
    crate = ROCrate(crate_zip)
    assert crate.root_dataset.get("license") == "notspecified"
    workflow = crate.mainEntity
    assert workflow["name"] == "packed.cwl"
    crate_zip.unlink()
    # output crate dir
    crate_dir = tmpdir / "revsort-run-1-crate"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir)]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    assert crate_dir.is_dir()
    crate = ROCrate(crate_dir)
    assert crate.root_dataset.get("license") == "notspecified"
    workflow = crate.mainEntity
    assert workflow["name"] == "packed.cwl"


def test_cli_convert_license(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    license = "MIT"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "-l", license]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate = ROCrate(crate_dir)
    assert crate.root_dataset["license"] == license


def test_cli_convert_agent(data_dir, tmpdir, monkeypatch):
    monkeypatch.chdir(str(tmpdir))
    root = data_dir / "revsort-no-agent-name-run-1"
    runner = CliRunner()
    args = ["convert", str(root)]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate_zip = tmpdir / f"{root.name}.crate.zip"
    assert crate_zip.is_file()
    crate = ROCrate(crate_zip)
    assert crate.get("https://orcid.org/0000-0001-9447-460X")


def test_cli_convert_workflow_name(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    workflow_name = "RevSort"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "-w", workflow_name]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate = ROCrate(crate_dir)
    workflow = crate.mainEntity
    assert workflow["name"] == workflow_name


def test_cli_convert_crate_name(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    workflow_name = "RevSort"
    crate_name = "name of the crate"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "-w", workflow_name, "-n", crate_name]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate = ROCrate(crate_dir)
    assert crate.root_dataset["name"] == crate_name
    assert crate.root_dataset["description"] == crate_name


def test_cli_convert_crate_desc(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    workflow_name = "RevSort"
    crate_desc = "description of the crate"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "-w", workflow_name, "-d", crate_desc]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate = ROCrate(crate_dir)
    assert crate.root_dataset["name"] == f"run of {workflow_name}"
    assert crate.root_dataset["description"] == crate_desc


def test_cli_convert_readme(data_dir, tmpdir):
    root = data_dir / "revsort-run-1"
    crate_dir = tmpdir / "revsort-run-1-crate"
    readme = data_dir / "README.md"
    runner = CliRunner()
    args = ["convert", str(root), "-o", str(crate_dir), "--readme", readme]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    crate = ROCrate(crate_dir)
    assert crate.get(readme.name)


def test_cli_report_provenance_minimal(data_dir, caplog):
    crate_dir = data_dir / "revsort-provenance-crate-minimal"
    runner = CliRunner()
    args = ["report", str(crate_dir)]
    result = runner.invoke(cli, args)
    assert result.exit_code == 0
    out_lines = result.stdout.splitlines()
    assert sum([_.startswith("action") for _ in out_lines]) == 3
    assert sum(["<-" in _ for _ in out_lines]) == 8


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0, result.exception
    assert result.stdout.strip() == __version__


def test_cli_run(data_dir, tmpdir, monkeypatch):
    crate_dir = data_dir / "type-zoo-run-1-crate"
    runner = CliRunner()
    args = ["run", str(crate_dir)]
    monkeypatch.chdir(str(tmpdir))
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
    out_path = Path("output.txt")
    assert out_path.is_file()
    crate_out_path = crate_dir / "4bd8e7e358488e833bf32cf5028695292cecb05b"
    assert out_path.read_text() == crate_out_path.read_text()


def test_cli_run_dir_array(data_dir, tmpdir, monkeypatch):
    crate_dir = data_dir / "dirarray-run-1-crate"
    runner = CliRunner()
    args = ["run", str(crate_dir)]
    monkeypatch.chdir(str(tmpdir))
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception


def test_cli_run_file_array(data_dir, tmpdir, monkeypatch):
    crate_dir = data_dir / "no-output-run-1-crate"
    runner = CliRunner()
    args = ["run", str(crate_dir)]
    monkeypatch.chdir(str(tmpdir))
    result = runner.invoke(cli, args)
    assert result.exit_code == 0, result.exception
