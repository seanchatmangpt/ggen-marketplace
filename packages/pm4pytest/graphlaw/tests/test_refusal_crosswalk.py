"""PM6 port: refusal-crosswalk differential court, engine-verdict half (Rust
tests/refusal_crosswalk_differential.rs) translated to pytest with python
rdflib as the symmetric oracle.

The Rust court runs two independent engines (graphlaw NativeSparqlEngine and
python3 rdflib) against the pinned refusal-vocabulary-pack fixtures and
requires both to agree with the pack's own closure-gate verdicts. This port
holds up the rdflib side of that differential: every verdict the Rust court
extracts from rdflib is re-derived here from the same pinned bytes with
rdflib, and compared against the pack's L101-adjudicated expected verdicts.

Fixtures are byte-identical pinned copies of the marketplace pack
/Users/sac/ggen-marketplace/packs/refusal-vocabulary-pack/ (READ-ONLY),
blake3-pinned in manifest.blake3. The manifest is the pin of record; a drift
meta-test compares pin vs the live sibling and BLOCKS (xfail/skip) when the
sibling checkout is absent.

Sabotage twin included: mutating a mapping must flip the verdict — a court
that cannot fail is not a court.
"""

import os
import sys

import pytest

rdflib = pytest.importorskip("rdflib")
import blake3  # noqa: E402

FIXTURE_ROOT = os.environ.get(
    "PM6_REFUSAL_FIXTURES", "/Users/sac/graphlaw/tests/fixtures/refusal_crosswalk"
)
SIBLING_ROOT = os.environ.get(
    "REFUSAL_VOCAB_PACK",
    os.path.join(os.path.expanduser("~"), "ggen-marketplace/packs/refusal-vocabulary-pack"),
)

PINNED = [
    "ontology.ttl",
    "gates/010_exactly_one_class.rq",
    "gates/020_class_coverage.rq",
    "gates/030_jsonrpc_law.rq",
    "gates/040_totality.rq",
    "gates/050_valve_totality.rq",
    "gates/060_a2a_wire_totality.rq",
    "queries/crosswalk.rq",
]
GATES = PINNED[1:7]

# The 6 strata-valve classes and their L101-adjudicated ash_a2a classes
# (from the pack's own ontology ValveMapping individuals + G5 closure gate).
VALVE_EXPECTED = [
    ("malformed_frame", "refused_structure"),
    ("fuel_exhausted", "refused_bounds"),
    ("parent_discontinuity", "refused_receipt"),
    ("arena_failure", "refused_consequence"),
    ("window_run_capacity", "refused_bounds"),
    ("window_tau_capacity", "refused_bounds"),
]


def _fixture(rel: str) -> str:
    path = os.path.join(FIXTURE_ROOT, rel)
    try:
        with open(path) as f:
            return f.read()
    except OSError as e:
        pytest.skip(f"loud SKIP: pinned fixture missing: {path}: {e}")


def _check_manifest():
    """Verify pinned bytes match manifest.blake3 before any evaluation runs."""
    manifest_path = os.path.join(FIXTURE_ROOT, "manifest.blake3")
    try:
        with open(manifest_path) as f:
            manifest = f.read()
    except OSError as e:
        pytest.skip(f"loud SKIP: manifest.blake3 missing: {manifest_path}: {e}")
    lines = [ln for ln in manifest.splitlines() if ln.strip()]
    assert len(lines) >= 8, f"manifest should pin >= 8 files, got {len(lines)}"
    pinned = 0
    for line in lines:
        hash_, path = line.split("  ", 1)
        rel = path.lstrip("*").lstrip("./") if path.startswith(("*", "./")) else path
        rel = path.removeprefix("*").removeprefix("./")
        with open(os.path.join(FIXTURE_ROOT, rel), "rb") as f:
            data = f.read()
        assert blake3.blake3(data).hexdigest() == hash_, f"pin drift on {rel}"
        pinned += 1
    for rel in PINNED:
        assert f"./{rel}" in manifest, f"pinned file {rel} not in manifest"
    return pinned


def _graph():
    g = rdflib.Graph()
    g.parse(os.path.join(FIXTURE_ROOT, "ontology.ttl"), format="turtle")
    return g


def _rows(g, query: str) -> int:
    return len(list(g.query(query)))


@pytest.fixture(scope="module")
def graph():
    _check_manifest()
    return _graph()


# ---------------------------------------------------------------------------
# Pin drift vs live sibling
# ---------------------------------------------------------------------------


def test_refusal_crosswalk_pin_matches_live_sibling():
    _check_manifest()
    if not os.path.isdir(SIBLING_ROOT):
        pytest.skip(f"BLOCKED: sibling pack absent at {SIBLING_ROOT}; drift check skipped")
    for rel in PINNED:
        with open(os.path.join(FIXTURE_ROOT, rel), "rb") as f:
            pinned = f.read()
        with open(os.path.join(SIBLING_ROOT, rel), "rb") as f:
            live = f.read()
        assert pinned == live, (
            f"pin drift: {FIXTURE_ROOT}/{rel} differs from live {SIBLING_ROOT}/{rel} "
            "(re-copy and re-pin)"
        )


# ---------------------------------------------------------------------------
# Differential court, part 1 — the pack's own closure gates (G1..G6) over the
# pinned canonical graph: rdflib must agree with the pack's verdict CLEAN
# (zero violation rows) on every gate.
# ---------------------------------------------------------------------------


def test_refusal_crosswalk_pack_gates_clean_rdflib(graph):
    for gate in GATES:
        rq = _fixture(gate)
        n = _rows(graph, rq)
        assert n == 0, f"rdflib verdict on {gate}: expected CLEAN, got {n} rows"


# ---------------------------------------------------------------------------
# Differential court, part 2 — for each of the 6 valve classes, rdflib's
# independent evaluation must agree with the pack's L101 adjudication table
# (cross-checked by pinned G5 being CLEAN).
# ---------------------------------------------------------------------------


def test_valve_class_differential_agreement(graph):
    # Pack's own verdict: G5 valve totality CLEAN.
    g5 = _rows(graph, _fixture("gates/050_valve_totality.rq"))
    assert g5 == 0, "pack G5 valve-totality gate must be CLEAN"

    mismatch_q = (
        "PREFIX rv: <urn:refusal-vocabulary:>\n"
        "SELECT ?vm WHERE {\n"
        "  ?vm a rv:ValveMapping ;\n"
        "      rv:valveClass ?vc ;\n"
        "      rv:ashA2aClass ?cls .\n"
        '  ?vc rv:valveName "%s" .\n'
        "  ?cls rv:className ?cn .\n"
        '  FILTER (?cn != "%s")\n'
        "}"
    )
    diverged = 0
    for valve, expected in VALVE_EXPECTED:
        q = mismatch_q % (valve, expected)
        n = _rows(graph, q)
        if n != 0:
            diverged += 1
        assert n == 0, f"valve class {valve}: rdflib disagrees with pack verdict {expected}"
    assert diverged == 0, "valve differential divergence"
    assert len(VALVE_EXPECTED) == 6, (
        "the crosswalk declares exactly 6 valve classes; court must cover all 6"
    )


# ---------------------------------------------------------------------------
# Totality court (fail-closed): all 51 erlmcp codes map to EXACTLY ONE class;
# all 18 classes covered (G2); every present wire code inside the law set (G3).
# Wire coverage is partial BY THE PACK'S OWN DESIGN.
# ---------------------------------------------------------------------------


def test_erlmcp_code_totality_fail_closed(graph):
    codes_q = (
        "PREFIX rv: <urn:refusal-vocabulary:>\n"
        "SELECT DISTINCT ?code WHERE {\n"
        "  ?m a rv:RefusalMapping ; rv:erlmcpCode ?code .\n"
        "}"
    )
    codes = _rows(graph, codes_q)
    assert codes == 51, f"crosswalk must place all 51 erlmcp codes, got {codes}"

    multi_q = (
        "PREFIX rv: <urn:refusal-vocabulary:>\n"
        "SELECT ?code ?n WHERE {\n"
        "  { SELECT ?code (COUNT(DISTINCT ?c) AS ?n) WHERE {\n"
        "      ?m a rv:RefusalMapping ; rv:erlmcpCode ?code ; rv:ashA2aClass ?c .\n"
        "    } GROUP BY ?code }\n"
        "  FILTER (?n != 1)\n"
        "}"
    )
    assert _rows(graph, multi_q) == 0, "some code lacks exactly-one class"

    assert _rows(graph, _fixture("gates/020_class_coverage.rq")) == 0, (
        "class-coverage gate must be CLEAN"
    )
    assert _rows(graph, _fixture("gates/030_jsonrpc_law.rq")) == 0, (
        "jsonrpc law-set gate must be CLEAN"
    )

    wire_q = (
        "PREFIX rv: <urn:refusal-vocabulary:>\n"
        "SELECT DISTINCT ?code WHERE {\n"
        "  ?m a rv:RefusalMapping ; rv:erlmcpCode ?code ; rv:jsonRpcCode ?c .\n"
        "}"
    )
    wired = _rows(graph, wire_q)
    assert wired <= codes, "wire coverage cannot exceed the code universe"


# ---------------------------------------------------------------------------
# Sabotage twin: mutate the pinned graph (second ValveMapping onto
# vc-fuel-exhausted pointing at a different class) and the court MUST fail.
# ---------------------------------------------------------------------------


def test_sabotage_twin_mutated_verdict_fails_court():
    ont = _fixture("ontology.ttl")
    sabotage = (
        "\nrv:vm-sabotage a rv:ValveMapping ;\n"
        "    rv:valveClass rv:vc-fuel-exhausted ;\n"
        "    rv:ashA2aClass rv:cls-refused-rule .\n"
    )
    mutated = ont + sabotage
    assert mutated != ont, "sabotage mutation applied"

    g = rdflib.Graph()
    g.parse(data=mutated, format="turtle")

    # 1. Pack's own gate verdict flips: G5 fires (double-mapped valve class).
    g5 = _rows(g, _fixture("gates/050_valve_totality.rq"))
    assert g5 >= 1, f"G5 must FIRE on the sabotaged graph, got {g5}"

    # 2. Differential evaluation flips: fuel_exhausted no longer maps solely
    #    to refused_bounds.
    mismatch_q = (
        "PREFIX rv: <urn:refusal-vocabulary:>\n"
        "SELECT ?vm WHERE {\n"
        "  ?vm a rv:ValveMapping ;\n"
        "      rv:valveClass ?vc ;\n"
        "      rv:ashA2aClass ?cls .\n"
        '  ?vc rv:valveName "fuel_exhausted" .\n'
        "  ?cls rv:className ?cn .\n"
        '  FILTER (?cn != "refused_bounds")\n'
        "}"
    )
    n = _rows(g, mismatch_q)
    assert n >= 1, f"differential evaluation must detect the sabotaged mapping, got {n}"

    # 3. Exactly-one-class per CODE totality untouched (negative control).
    codes_q = (
        "PREFIX rv: <urn:refusal-vocabulary:>\n"
        "SELECT DISTINCT ?code WHERE {\n"
        "  ?m a rv:RefusalMapping ; rv:erlmcpCode ?code .\n"
        "}"
    )
    codes = _rows(g, codes_q)
    assert codes == 51, "erlmcp column untouched by valve sabotage"


# ---------------------------------------------------------------------------
# Crosswalk projection (queries/crosswalk.rq) evaluates cleanly in rdflib —
# the fourth differential surface beyond the 6 gates.
# ---------------------------------------------------------------------------


def test_crosswalk_projection_query_agrees(graph):
    rq = _fixture("queries/crosswalk.rq")
    n = _rows(graph, rq)
    expected_rows = 51 + 6 + 18 + 2  # 51 code + 6 valve + 18 class + 2 wire rows
    assert n == expected_rows, f"rdflib projection row count: expected {expected_rows}, got {n}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
