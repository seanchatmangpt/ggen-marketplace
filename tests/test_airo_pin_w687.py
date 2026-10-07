"""AIRo pin court for ggen-marketplace (xaas lane W687, 2026-10-07).

Pins the vendored AIRo ontology surface the xaas AIRo-wiring ledger claims:
packs/ggen-platform-pack/ontology/airo.ttl — rdflib-parseable turtle,
558 triples, byte-hash 6274d2d8..., and marketplace validate staying green.
Real rdflib parse + real sha256 + real subprocess validate; no mocks.
"""

import hashlib
import os
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AIRO = os.path.join(REPO_ROOT, "packs", "ggen-platform-pack", "ontology", "airo.ttl")
EXPECTED_SHA256 = "6274d2d8711e046cf38f1b5b2980188094d4aa87b5af79804005a06468fd8469"
EXPECTED_TRIPLES = 558

rdflib = pytest.importorskip("rdflib")


def test_airo_file_exists():
    assert os.path.isfile(AIRO), AIRO


def test_airo_byte_hash_pin():
    with open(AIRO, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    assert digest == EXPECTED_SHA256, digest


def test_airo_rdflib_parse_and_triple_count_pin():
    g = rdflib.Graph()
    g.parse(AIRO, format="turtle")
    assert len(g) == EXPECTED_TRIPLES, len(g)


def test_airo_declares_expected_namespace():
    g = rdflib.Graph()
    g.parse(AIRO, format="turtle")
    subjects = {str(s) for s in g.subjects() if str(s).startswith("https://")}
    assert any("airo" in s.lower() for s in subjects), sorted(subjects)[:5]


def test_marketplace_validate_stays_green():
    r = subprocess.run(
        [sys.executable, os.path.join(REPO_ROOT, "scripts", "marketplace.py"), "validate"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert "validated packs=305" in r.stdout and "ontologies=503" in r.stdout, r.stdout[-300:]
