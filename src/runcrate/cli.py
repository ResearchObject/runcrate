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

import sys
from pathlib import Path
import click

from . import __version__
from .validator import CrateValidator
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
def convert(root, output, license, workflow_name, readme):
    """Convert a CWLProv RO bundle into a Workflow Run RO-Crate.

    RO_DIR: top-level directory of the CWLProv RO
    """
    if not output:
        output = Path(f"{root.name}.crate.zip")
    builder = ProvCrateBuilder(root, workflow_name, license, readme)
    crate = builder.build()
    if output.suffix == ".zip":
        crate.write_zip(output)
    else:
        crate.write(output)


@cli.command()
@click.option("-s", "--skip-ro-crate-check", is_flag=True, help="Skip general RO-Crate validation")
@click.option("-p", "--process-run", is_flag=True, help="Validate against the Process Run Crate profile")
@click.option("-w", "--workflow-run", is_flag=True, help="Validate against the Workflow Run Crate profile")
@click.option("-P", "--provenance-run", is_flag=True, help="Validate against the Provenance Run Crate profile")
@click.option("-W", "--workflow", is_flag=True, help="Validate against the Workflow RO-Crate profile")
@click.option("-b", "--bioschemas", is_flag=True, help="Validate against Bioschemas profiles (ComputationalWorkflow FormalParameter)")
@click.option("-d", "--debug", is_flag=True, help="Enable debug output")

@click.argument(
    "crate",
    metavar="CRATE",
    type=click.Path(exists=True, file_okay=False, readable=True, path_type=Path),
)

def validate(crate, skip_ro_crate_check, workflow, process_run, workflow_run, provenance_run, bioschemas, debug):
    """Validate a Process/Workflow/Provenance Run Crate (experimental)
    
    CRATE: RO-Crate Root directory

    Unless forced (e.g. --workflow-run), the validation will use
    the crate's profile(s) as indicated with conformsTo.
    """
    validator = CrateValidator(crate)
    if debug:
        validator.debug = True
    if not skip_ro_crate_check:
        validator.ro_crate_check()
        # TODO: Check output

    # Make sure Metadata File is readable and described
    if not validator.metadata_file_check():
        return -2

    guess_profile = not workflow and not process_run and not workflow_run and not process_run and not bioschemas
    if guess_profile:
        # Detect profile from conformsTo
        (workflow,process_run,workflow_run,provenance_run,bioschemas) = validator._detect_profiles()

    if not workflow and not process_run and not workflow_run and not process_run:
        print("Could not detect profile, check \"conformsTo\" or force profile check (e.g. --workflow-run)", file=sys.stderr)
        return -1

    if workflow:
        print("Validating against Workflow profile")
        validator.workflow_check()
    if bioschemas:
        print("Validating against Bioschemas ComputationalWorkflow profile")
        validator.computationalworkflow_check()
    if process_run:
        print("Validating against Process Run profile")
        validator.process_run_check()
    if workflow_run:
        print("Validating against Workflow Run profile")
        validator.workflow_run_check()
    if provenance_run:
        print("Validating against Provenance Run profile")
        validator.provenance_run_check()
        return
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
