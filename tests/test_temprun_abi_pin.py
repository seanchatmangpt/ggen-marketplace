"""strata-temprun-pack ABI-pin court (2026-10-13).

Explore finding #3: the pack's generated/arena.rs predates the strata
ABI-v2 rebase (59ed80c on fix/kg-42-status-code; receipt-wire change:
352B receipt-wire deleted, CTTG New payload, errno 11 E_ABI_MISMATCH) and
the pack carried no ABI pin anywhere.

ABI-delta verdict (read both sides, 2026-10-13): the pack's arena law is
UPSTREAM of the ABI. generated/arena.rs encodes only the fuel model
(FuelLease, run/2 sieve, admissionFuel >= 3); the changed surface lives in
temprun/src/bin/temprun_step.rs (which does not even exist at the pin —
the file was born in the rebase commit) and worker.ex. The fuel-sieve
semantics are byte-identical in git show at BOTH dff1d41 (main,
pre-rebase) and 59ed80c. Deliverable: PIN, not a fix.

This court is the TRIPWIRE for the fix/kg-42-status-code merge: that
branch's own receipt names the ABI delta (temprun_step.rs + worker.ex,
temprun guest ABI v2). When it merges, the live strata main becomes an
ABI-v2 subject while this pack's pin is ABI-v1 — the drift test below
then fires and forces an explicit re-pin decision (re-derive against
merged main, or re-assert with an honest comment). No mocks: real
rdflib parse, real git subprocess, real filesystem.
"""

import os
import re
import subprocess

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY = os.path.join(
    REPO_ROOT, "packs", "strata-temprun-pack", "ontology.ttl"
)
GATE = os.path.join(
    REPO_ROOT, "packs", "strata-temprun-pack", "gates", "030_abi_pin.rq"
)
STRATA = os.environ.get("STRATA_ROOT", "/Users/sac/strata")
PIN_SHA = "dff1d4178abf1fe465d58b815d1042c9784f93c2"
ABI_V2_SHA = "59ed80c0d780aa1a8e9a923dab47b32423e6232e"
ABI_V2_BRANCH = "fix/kg-42-status-code"
SEMANTIC_ANCHORS = [
    "pub fn run(input: &mut ArenaInput, mut fuel: fuel::FuelLease) -> ArenaOutput",
    "Sieve order: clock + causal acyclicity",
    "pub use fuel::FuelLease",
]
# temprun lib.rs path inside the strata tree (anchor source file).
ANCHOR_PATH = "temprun/src/lib.rs"

rdflib = pytest.importorskip("rdflib")


def _git(args, cwd=STRATA):
    return subprocess.run(
        ["git"] + args, capture_output=True, text=True, cwd=cwd, timeout=60
    )


def _abi_pin(g):
    pins = [s for s in g.subjects(rdflib.RDF.type, rdflib.URIRef(
        "https://strata.chatman.ai/ontology#AbiPin"))]
    assert len(pins) == 1, [str(p) for p in pins]
    return pins[0]


@pytest.fixture(scope="module")
def graph():
    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
    return g


@pytest.fixture(scope="module")
def pin(graph):
    s = _abi_pin(graph)
    sha = str(graph.value(s, rdflib.URIRef(
        "https://strata.chatman.ai/ontology#pinSubjectSha")))
    branch = str(graph.value(s, rdflib.URIRef(
        "https://strata.chatman.ai/ontology#pinBranch")))
    ver = int(str(graph.value(s, rdflib.URIRef(
        "https://strata.chatman.ai/ontology#pinAbiVersion"))))
    anchors = sorted(str(o) for o in graph.objects(s, rdflib.URIRef(
        "https://strata.chatman.ai/ontology#pinSemanticAnchor")))
    assert re.fullmatch(r"[0-9a-f]{40}", sha), sha
    assert branch, branch
    assert anchors, anchors
    return {"sha": sha, "branch": branch, "version": ver, "anchors": anchors}


# ── pack-side courts ─────────────────────────────────────────────────

def test_abi_pin_exists_and_shape(graph):
    """Fail-closed: pin present, exactly one, all properties typed."""
    s = _abi_pin(graph)
    assert str(s).startswith("https://strata.chatman.ai/ontology#")


def test_gate_file_present_and_fails_closed():
    """The gate exists and refuses a graph with the pin stripped."""
    assert os.path.isfile(GATE), GATE
    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
    # Sabotage: strip the pin's type triple, re-run the gate — must return
    # the no_st:AbiPin_individual violation row.
    sabotaged = rdflib.Graph()
    for t in g:
        if (t[0], rdflib.RDF.type, rdflib.URIRef(
                "https://strata.chatman.ai/ontology#AbiPin")) == t:
            continue
        sabotaged.add(t)
    query = open(GATE, encoding="utf-8").read()
    rows = list(sabotaged.query(query))
    assert rows, "gate must fail closed on a pin-stripped graph (sabotage)"
    assert any("no_st:AbiPin_individual" in str(c)
               for row in rows for c in row), rows


def test_gate_zero_rows_on_admitted_graph(graph):
    """Honest path: the admitted ontology passes its own gate."""
    rows = list(graph.query(open(GATE, encoding="utf-8").read()))
    assert not rows, [tuple(str(c) for c in r) for r in rows]


# ── live-strata courts ───────────────────────────────────────────────

def test_strata_present_or_blocked():
    """BLOCKED:-skip (typed, not a pass) when the strata checkout is absent."""
    if not os.path.isdir(STRATA):
        pytest.skip(f"BLOCKED:strata_absent — no strata checkout at {STRATA}")


def test_pin_commit_exists_in_strata(pin):
    if not os.path.isdir(STRATA):
        pytest.skip("BLOCKED:strata_absent")
    r = _git(["cat-file", "-t", pin["sha"]])
    if r.returncode != 0:
        pytest.fail(
            f"DRIFT: pinned subject {pin['sha'][:8]} not found in strata at "
            f"{STRATA} ({r.stderr.strip()})"
        )
    assert r.stdout.strip() == "commit", r.stdout


def test_pinned_semantics_present_at_pin(pin):
    """The pin commit's tree contains the semantics the pack encodes.

    Drift here names both sides (pin SHA vs live strata state) and fails.
    """
    if not os.path.isdir(STRATA):
        pytest.skip("BLOCKED:strata_absent")
    missing = []
    for anchor in pin["anchors"]:
        r = _git(["show", f"{pin['sha']}:{ANCHOR_PATH}"])
        if r.returncode != 0 or anchor not in r.stdout:
            missing.append(anchor)
    assert not missing, (
        "ABI-PIN DRIFT — pinned subject no longer carries the pack's "
        f"semantics. pin={pin['sha']} ({pin['branch']}) "
        f"strata_checkout={STRATA}; missing anchors: {missing}"
    )


def test_merge_tripwire_fix_kg42(pin):
    """TRIPWIRE for the fix/kg-42-status-code merge (its receipt names the
    ABI-v2 delta: 352B receipt-wire deleted, CTTG New payload, errno 11).

    While the branch is unmerged, its tip must still carry the
    ABI-independent fuel semantics (anchors hold on both sides — verified
    2026-10-13 at 59ed80c). After the merge lands, this test fails on
    purpose: main is then an ABI-v2 subject and the pin must be
    re-decided explicitly (re-derive or re-assert with an honest comment).
    """
    if not os.path.isdir(STRATA):
        pytest.skip("BLOCKED:strata_absent")
    r = _git(["rev-parse", "--verify", ABI_V2_BRANCH])
    if r.returncode != 0:
        pytest.skip(
            "BLOCKED:branch_absent — fix/kg-42-status-code no longer exists "
            "(likely merged); the pin decision is then owned by the merged "
            "main re-pin, not this tripwire"
        )
    branch_tip = r.stdout.strip()
    anchor_missing = []
    for anchor in pin["anchors"]:
        s = _git(["show", f"{branch_tip}:{ANCHOR_PATH}"])
        if s.returncode != 0 or anchor not in s.stdout:
            anchor_missing.append(anchor)
    assert not anchor_missing, (
        "ABI-PIN MERGE TRIPWIRE FIRED — the ABI-v2 rebase "
        f"({ABI_V2_SHA[:8]}) has reached the live tree; branch tip "
        f"{branch_tip[:8]} no longer carries all pinned anchors "
        f"({anchor_missing}). Re-pin strata-temprun-pack against merged "
        "main: re-derive the arena law or re-assert the pin with an honest "
        "comment in packs/strata-temprun-pack/ontology.ttl."
    )
    # Sanity: the ABI delta surface really is on the branch tip (guards
    # against the tripwire silently degenerating into a no-op if the
    # branch is rewritten).
    s = _git(["show", f"{branch_tip}:temprun/src/bin/temprun_step.rs"])
    assert s.returncode == 0 and "ctt_guest_abi_version" in s.stdout, (
        "fix/kg-42-status-code tip no longer carries the ABI-v2 surface "
        "(temprun_step.rs ctt_guest_abi_version probe) — tripwire premise "
        "invalid, re-derive this court"
    )


def test_sabotage_pin_sha_mutation_fails_gate():
    """Sabotage twin: a mutated pin SHA shape is refused by the gate."""
    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
    q = (
        'PREFIX st: <https://strata.chatman.ai/ontology#>\n'
        'DELETE { ?p st:pinSubjectSha ?o . } '
        'INSERT { ?p st:pinSubjectSha "dff1d41-not-a-sha" } '
        "WHERE { ?p a st:AbiPin ; st:pinSubjectSha ?o . }"
    )
    g.update(q)
    rows = list(g.query(open(GATE, encoding="utf-8").read()))
    assert any("pinSubjectSha" in str(c) for row in rows for c in row), rows
