# Copyright 2023 The University of Manchester
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
from pyshex.evaluate import evaluate
from rdflib import Graph, Dataset, ConjunctiveGraph, Namespace, URIRef, DCTERMS
from arcp import arcp_random
from rocrate.rocrate import ROCrate
import rocrateValidator.validate

from importlib_resources import files
# FIXME: For Python 3.10++, below code is sufficient:
#from importlib.resources import files

import sys

SCHEMA = Namespace("http://schema.org/")

class ValidationError(TypeError):
    """A type of validation"""

class RootEntityError(ValidationError):
    """Can't find the root data entity"""

class CrateValidator():
    def __init__(self, root):
        self.root = isinstance(root, Path) and root or Path(root)
        self.base = URIRef(arcp_random())
        self.debug = False
        # Caches
        self._crate = None
        self._graph = None
        self._rootIRI = None

    @property
    def crate(self):
        if self._crate:
            return self._crate
        self._crate = ROCrate(self.root)
        return self._crate

    def _detect_profiles(self):
        """Auto-detect Run Crate profile based on conformsTo

        Return a tuple (workflow, process_run, workflow_run, provenance_run) with
        the corresponding detected profiles URIs. Profiles not detected are
        represented as ``None`` in the tuple.
        """
        profiles = self.crate.root_dataset.get("conformsTo", [])
        if not isinstance(profiles, list):
            profiles = [profiles]
        
        workflow, process_run, workflow_run, provenance_run = (None,)*4
        for p in profiles:
            if self.debug:
                print("Detected profile {}".format(p.id))
            if p.id.startswith("https://w3id.org/workflowhub/workflow-ro-crate/"):
                workflow = p
            if p.id.startswith("https://w3id.org/ro/wfrun/process/"):
                process_run = p
            if p.id.startswith("https://w3id.org/ro/wfrun/workflow/"):
                workflow_run = p
            if p.id.startswith("https://w3id.org/ro/wfrun/provenance/"):
                provenance_run = p
        return (workflow, process_run, workflow_run, provenance_run)

    def ro_crate_check(self):
        print("Validating RO-Crate {}".format(self.root))
        v = rocrateValidator.validate.validate(self.root)
        # FIXME: Avoid extracted code below from v.validator() 
        # to get programmatic access to results
        for method in v.functions:
            result = method(v.tar_file, v.extension)
            if result.code == 0:
                print("   OK {}".format(result.NAME))
            else:
                print("ERROR {}:\n      {}".format(result.NAME, result.message))
        self.metadata_file_check()

    def metadata_file_check(self):
        try:
            return str(self.rootIRI)
        except IOError as e:
            print(str(e), file=sys.stderr)
            return False
        except RootEntityError:
            print("Can't find Metadata File Descriptor, see https://www.researchobject.org/ro-crate/1.1/root-data-entity.html")
            return False

    @property
    def metadataFile(self) -> Path:
        p = self.root / "ro-crate-metadata.json"
        if not p.is_file():
            raise IOError("Can't find RO-Crate Metadata file {}".format(p))
        return p

    @property
    def graph(self):
        if self._graph:
            return self._graph
        g = Graph() # assuming default graph
        metadataIRI = str(self.base) + "ro-crate-metadata.json"
        if self.debug:
            print("Parsing RDF " + metadataIRI)
        g.parse(self.metadataFile, format="application/ld+json", base=metadataIRI)
        self._graph = g
        if self.debug:
            print("Parsed {} triples, {} subjects".format(len(g), len(set(g.subjects()))))
        return self._graph

    @property
    def rootIRI(self):
        """Identify IRI of the RO-Crate Root entity"""
        if self._rootIRI:
            return self._rootIRI
        # Algorithm for finding root data entity
        # https://www.researchobject.org/ro-crate/1.1/root-data-entity.html#finding-the-root-data-entity
        for metadataFile,_,conformsTo in self.graph.triples((None, DCTERMS.conformsTo, None)):
            if conformsTo.startswith("https://w3id.org/ro/crate/"):
                if (self.debug):
                    print("Checking Metadata File Descriptor {}".format(metadataFile))
                    print("RO-Crate specification {}".format(conformsTo))
                roots = set(self.graph.objects(metadataFile, SCHEMA.about))
                for r in roots:
                    self._rootIRI = r
                    if (self.debug):
                        print("Identified RO-Crate root: {}".format(r))
                    return self._rootIRI
        # Still here? Bad luck..
        raise RootEntityError("Can't find RO-Crate root")

    def _load_shex(self, profile):
        return files('runcrate.shex').joinpath(profile).read_text()

    def _validate_shex(self, profile):
        shex = self._load_shex(profile)
        rslt, reason = evaluate(self.graph, shex, self.rootIRI)
        if rslt:
            print("CONFORMS")
        else:
            print("DOES NOT CONFORM")
            if reason:
                print(reason)
        return rslt

    def process_run_check(self):
        self._validate_shex("process-crate-0.1.shex")

    def workflow_check(self):
        self._validate_shex("workflow-crate-1.0.shex")

    def workflow_run_check(self):
        pass
    
    def provenance_run_check(self):
        pass

