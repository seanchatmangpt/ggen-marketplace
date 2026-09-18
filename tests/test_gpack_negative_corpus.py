#!/usr/bin/env python3
"""Permanent tripwire for the T03 invalid corpus (RFC-GPACK-001 v26.9.17).

Encodes the T03 ticket acceptance falsifiers as repository law:

1. No ``assert/run.sh`` in ``packs/ggen-pack-spec-pack/qualification/negative/``
   exits 0 against the null engine (a silent stub) — a negative test that can
   pass without an engine is vacuous (§77: PASS = AttemptObserved ∧
   ForbiddenOutcomeAbsent ∧ RequiredOutcomeObserved).
2. The D1 falsifier pair exists: ``gate-positive-select/gates/`` and
   ``query-positive-select/queries/`` ship byte-identical SELECT queries on
   opposite surfaces (§96 rows 1-2, §4.4 divergence D1).
3. No symlink is committed anywhere under the corpus (§72; repository law
   "No symlinks under packs/").

Plus the inventory contract: exactly the Appendix D ``invalid/*`` fixtures,
each with a non-empty expected-outcome file drawn from the Appendix C typed
refusal vocabulary (or the documented ``NO_REFUSAL:`` positive-outcome form).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "packs" / "ggen-pack-spec-pack" / "qualification" / "negative"

EXPECTED_FIXTURES = frozenset(
    {
        "manifest-unknown-key",
        "manifest-semantic-identity-mismatch",
        "missing-ontology",
        "gate-positive-select",
        "query-positive-select",
        "path-traversal",
        "symlink",
        "dependency-cycle",
        "ambiguous-capability",
        "target-collision",
        "renderer-mismatch",
    }
)

# RFC-GPACK-001 v26.9.17 Appendix C — Initial Typed Refusal Vocabulary.
TYPED_REFUSAL_VOCABULARY = frozenset(
    {
        "REFUSED:PACK_MANIFEST_MISSING",
        "REFUSED:PACK_MANIFEST_INVALID",
        "REFUSED:PACK_IDENTITY_MISMATCH",
        "REFUSED:PACK_GRAPH_MISSING",
        "REFUSED:PACK_GRAPH_INVALID",
        "REFUSED:PACK_SYMLINK",
        "REFUSED:PACK_PATH_ESCAPE",
        "REFUSED:QUERY_INVALID",
        "REFUSED:GATE_INVALID",
        "REFUSED:GATE_VIOLATION",
        "REFUSED:DEPENDENCY_UNSATISFIED",
        "REFUSED:DEPENDENCY_CYCLE",
        "REFUSED:DEPENDENCY_VERSION_CONFLICT",
        "REFUSED:AMBIGUOUS_CAPABILITY_PROVIDER",
        "REFUSED:DUPLICATE_SEMANTIC_AUTHORITY",
        "REFUSED:TARGET_OWNERSHIP_CONFLICT",
        "REFUSED:AUTHORITY_JOIN_INVALID",
        "REFUSED:RENDERER_AMBIGUOUS",
        "REFUSED:RENDERER_PROFILE_MISMATCH",
        "REFUSED:NONDETERMINISTIC_REPLAY",
        "REFUSED:SOURCE_MUTATED_DURING_MANUFACTURE",
        "REFUSED:RECEIPT_IDENTITY_MISMATCH",
    }
)


def expected_outcome(fixture: str) -> str:
    lines = (CORPUS / fixture / "assert" / "refusal-code.txt").read_text(encoding="utf-8").splitlines()
    return next(line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#"))


def test_corpus_inventory_matches_appendix_d() -> None:
    fixtures = {path.name for path in CORPUS.iterdir() if path.is_dir()}
    assert fixtures == EXPECTED_FIXTURES, "corpus inventory drifted; update this tripwire in the same change"


def test_every_fixture_has_expected_outcome_and_executable_run_sh() -> None:
    for fixture in sorted(EXPECTED_FIXTURES):
        assert expected_outcome(fixture), f"{fixture}: empty expected outcome"
        assert os.access(CORPUS / fixture / "assert" / "run.sh", os.X_OK), f"{fixture}: run.sh not executable"


def test_expected_outcomes_use_typed_vocabulary() -> None:
    for fixture in sorted(EXPECTED_FIXTURES):
        outcome = expected_outcome(fixture)
        assert outcome in TYPED_REFUSAL_VOCABULARY or outcome.startswith("NO_REFUSAL:"), (
            f"{fixture}: {outcome!r} is neither an Appendix C typed refusal nor a NO_REFUSAL positive outcome"
        )


def test_no_symlink_anywhere_in_corpus() -> None:
    assert CORPUS.exists()
    for path in CORPUS.rglob("*"):
        assert not path.is_symlink(), f"symlink committed in corpus: {path}"


def test_d1_pair_queries_are_byte_identical_on_opposite_surfaces() -> None:
    gate = CORPUS / "gate-positive-select" / "gates" / "010_positive_select.rq"
    query = CORPUS / "query-positive-select" / "queries" / "d1_select.rq"
    assert gate.parent.name == "gates", "the attacking half must live on the gate surface (§14)"
    assert query.parent.name == "queries", "the non-attacking half must live on the query surface (§13)"
    assert gate.read_bytes() == query.read_bytes(), (
        "the D1 pair must ship the SAME SELECT; only the surface may differ (§96 rows 1-2)"
    )


def test_null_engine_is_silent_and_successful() -> None:
    """Guard the probe itself: a null engine that failed or chattered would
    make the vacuity test below pass for the wrong reason."""
    proc = subprocess.run(
        ["bash", str(CORPUS / "null-engine.sh")],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0
    assert proc.stdout == "" and proc.stderr == ""


def test_no_assertion_passes_vacuously_against_null_engine() -> None:
    null_stub = CORPUS / "null-engine.sh"
    for fixture in sorted(EXPECTED_FIXTURES):
        run_sh = CORPUS / fixture / "assert" / "run.sh"
        proc = subprocess.run(
            ["bash", str(run_sh), f"{null_stub} {{PACK}}"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert proc.returncode != 0, (
            f"{fixture}: assert/run.sh exited 0 against the null engine — it cannot falsify anything (§77)"
        )
