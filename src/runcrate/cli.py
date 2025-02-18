# Copyright 2022-2025 CRS4.
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

import sys
from pathlib import Path

import click

from . import __version__
from .convert import ProvCrateBuilder
from .report import dump_crate_actions
from .run import run_crate


@click.group()
def cli():
    pass


@cli.command()
@click.argument(
    "root",
    metavar="RO_DIR",
    type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    help="output RO-Crate directory or zip file",
)
@click.option(
    "-l",
    "--license",
    help="license URL (or WorkflowHub-accepted id)",
)
@click.option(
    "-w",
    "--workflow-name",
    metavar="STRING",
    help="original workflow name",
)
@click.option(
    "--readme",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    help="path to a README file (should be README.md in Markdown format)",
)
@click.option(
    "-n",
    "--crate-name",
    metavar="STRING",
    help="crate name",
)
@click.option(
    "-d",
    "--crate-desc",
    metavar="STRING",
    help="crate description",
)
def convert(root, output, license, workflow_name, readme, crate_name, crate_desc):
    """\
    Convert a CWLProv RO bundle into a Workflow Run RO-Crate.

    RO_DIR: top-level directory of the CWLProv RO
    """
    if not output:
        output = Path(f"{root.name}.crate.zip")
    builder = ProvCrateBuilder(root, workflow_name, license, readme, crate_name, crate_desc)
    crate = builder.build()
    if output.suffix == ".zip":
        crate.write_zip(output)
    else:
        crate.write(output)


@cli.command()
@click.argument(
    "crate",
    metavar="RO_CRATE",
    type=click.Path(exists=True, readable=True, path_type=Path),
)
def report(crate):
    """\
    Read a Workflow Run RO-Crate and report on the actions it describes.

    RO_CRATE: RO-Crate directory or zip file.
    """
    dump_crate_actions(crate)


@cli.command()
@click.argument(
    "crate",
    metavar="RO_CRATE",
    type=click.Path(exists=True, readable=True, path_type=Path),
)
@click.option("--executable", help="workflow runner executable")
@click.option("--keep-wd", help="keep working directory", is_flag=True)
@click.option(
    "--dry-run",
    help="do not actually run the workflow (implies --keep-wd)",
    is_flag=True
)
def run(crate, executable, keep_wd, dry_run):
    """\
    Run the workflow from a Workflow Run RO-Crate.

    RO_CRATE: RO-Crate directory or zip file.
    """
    run_crate(crate, executable=executable, keep_wd=keep_wd, dry_run=dry_run)


@cli.command()
def version():
    """\
    Print version string and exit.
    """
    sys.stdout.write(f"{__version__}\n")


if __name__ == '__main__':
    cli()
