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

from pathlib import Path

import click

from . import ProvCrateBuilder


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
def convert(root, output, license, workflow_name):
    """\
    RO_DIR: top-level directory of the CWLProv RO
    """
    if not output:
        output = Path(f"{root.name}.crate.zip")
    builder = ProvCrateBuilder(root, workflow_name, license)
    crate = builder.build()
    if output.suffix == ".zip":
        crate.write_zip(output)
    else:
        crate.write(output)


if __name__ == '__main__':
    cli()
