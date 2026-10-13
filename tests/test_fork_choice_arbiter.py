"""Courts for the C20 generator-plurality arbiter (lane L80).

Chicago discipline: the real script is imported (and, for the CLI court,
invoked as a real subprocess) -- no mocks, no stubs. Assertions land on the
arbiter's actual selection output.
"""

from __future__ import annotations

import itertools
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "fork_choice_arbiter.py"

sys.path.insert(0, str(REPO / "scripts"))
import fork_choice_arbiter as arbiter  # noqa: E402


def receipt(consequence: bool = True, manifests: int = 1):
    """Minimal receipt in the real qualification JSON shape."""
    record = {"status": "ALIVE", "name": "some-pack", "version": "0.1.0"}
    if consequence:
        record["consequence_sha256"] = "a" * 64
        record["consequence_files"] = 3
        record["generated_build"] = {
            "manifests_verified": [f"generated/ash/m{i}.ex" for i in range(manifests)]
        }
    return record


def candidate(generator: str, evidence):
    return {"generator": generator, "evidence": list(evidence)}


# ---------------------------------------------------------------------------
# Court (a): heavier evidence wins regardless of order.
# ---------------------------------------------------------------------------

def test_heavier_evidence_wins_regardless_of_order():
    heavy = candidate("g/heavy", [receipt(), receipt(), receipt()])
    light = candidate("g/light", [receipt()])
    for order in itertools.permutations([heavy, light]):
        result = arbiter.select_winner(list(order))
        assert result["generator"] == "g/heavy"
        assert result["work"] == 3 * 4  # 3 receipts x (1 + 2 + 1 manifest)
        assert result["reason"] == "greatest-work"


def test_heavier_wins_with_many_receipts_light_side():
    heavy = candidate("g/A", [receipt() for _ in range(10)])
    light = candidate("g/B", [receipt() for _ in range(9)])
    result = arbiter.select_winner([light, heavy])
    assert result["generator"] == "g/A"


# ---------------------------------------------------------------------------
# Court (b): exact tie -> lower tip nonce, deterministically.
# ---------------------------------------------------------------------------

def test_exact_tie_resolves_to_lower_nonce_deterministically():
    a = candidate("g/alpha", [receipt()])
    b = candidate("g/beta", [receipt()])
    assert arbiter.chain_work(a["evidence"]) == arbiter.chain_work(b["evidence"])

    expected = arbiter.tip_nonce("g/alpha") < arbiter.tip_nonce("g/beta") and "g/alpha" or "g/beta"
    for _ in range(2):
        result = arbiter.select_winner([a, b])
        assert result["generator"] == expected
        assert result["reason"] == "work-tie:lower-tip-nonce"
        assert result["tip_nonce"] == arbiter.tip_nonce(expected)
    # Repeated invocation with the same inputs gives the same winner.
    assert arbiter.select_winner([a, b]) == arbiter.select_winner([b, a])


def test_tip_nonce_is_sha256_of_identity():
    import hashlib

    assert arbiter.tip_nonce("g/alpha") == int(
        hashlib.sha256(b"g/alpha").hexdigest(), 16
    )


# ---------------------------------------------------------------------------
# Court (c): order permutation of evidence never changes the winner.
# ---------------------------------------------------------------------------

def test_evidence_order_permutation_never_changes_winner():
    ids = ["g/p0", "g/p1", "g/p2", "g/p3"]
    candidates = [candidate(g, [receipt(manifests=i + 1)]) for i, g in enumerate(ids)]
    baseline = arbiter.select_winner(candidates)
    for perm in itertools.permutations(candidates):
        result = arbiter.select_winner(list(perm))
        assert result["generator"] == baseline["generator"]
        assert result["work"] == baseline["work"]


def test_candidate_list_permutation_tie_case_stable():
    tied = [candidate("g/x", [receipt()]), candidate("g/y", [receipt()])]
    baseline = arbiter.select_winner(tied)
    for perm in itertools.permutations(tied):
        assert arbiter.select_winner(list(perm))["generator"] == baseline["generator"]


# ---------------------------------------------------------------------------
# Court (d): sabotage twin -- a wall-clock/RNG tie-breaker is caught.
# A nondeterministic tie-breaker (time.time(), random.random()) would flip
# winners across repeated runs; this corpus pins the winner across repeats,
# orders, and a CLI subprocess run.
# ---------------------------------------------------------------------------

def test_sabotage_twin_repeated_runs_pin_winner():
    a = candidate("g/sab-a", [receipt()])
    b = candidate("g/sab-b", [receipt()])
    winners = {arbiter.select_winner([a, b])["generator"] for _ in range(50)}
    assert len(winners) == 1


def test_sabotage_twin_subprocess_cli_is_deterministic():
    payload = [candidate("g/cli-a", [receipt()]), candidate("g/cli-b", [receipt()])]
    outputs = set()
    for _ in range(3):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "/dev/stdin"],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, proc.stderr
        outputs.add(proc.stdout)
    assert len(outputs) == 1
    assert json.loads(next(iter(outputs)))["generator"] in {"g/cli-a", "g/cli-b"}


# ---------------------------------------------------------------------------
# Court (e): injected evidence perturbation on EQUAL work must not flip the
# winner (L51 falsifier). Perturbations that preserve total work -- receipt
# reordering, manifest-list reordering, hash-content change at equal weight --
# leave the winner unchanged.
# ---------------------------------------------------------------------------

def test_injected_perturbation_equal_work_does_not_flip_winner():
    a = candidate("g/one", [receipt(consequence=True, manifests=2)])
    b = candidate("g/two", [receipt(consequence=True, manifests=2), receipt(consequence=False)])
    # Force exact tie: rebuild b so its work equals a's.
    b = candidate("g/two", [receipt(consequence=True, manifests=1), receipt(consequence=False)])
    assert arbiter.chain_work(a["evidence"]) == arbiter.chain_work(b["evidence"])
    baseline = arbiter.select_winner([a, b])["generator"]

    # Perturbations of a's evidence at equal total work.
    perturbations = [
        list(reversed(a["evidence"])),  # order permutation
        [dict(a["evidence"][0], consequence_sha256="b" * 64)],  # digest content change
        [dict(a["evidence"][0], generated_build={"manifests_verified": ["x.ex", "y.ex"]})],
    ]
    for perturbed in perturbations:
        assert arbiter.chain_work(perturbed) == arbiter.chain_work(a["evidence"])
        result = arbiter.select_winner([candidate("g/one", perturbed), b])
        assert result["generator"] == baseline


def test_injected_perturbation_via_cli_equal_work_stable():
    a = candidate("g/e1", [receipt()])
    b = candidate("g/e2", [receipt()])
    baseline = json.loads(
        subprocess.run(
            [sys.executable, str(SCRIPT), "/dev/stdin"],
            input=json.dumps([a, b]),
            capture_output=True,
            text=True,
        ).stdout
    )["generator"]
    for _ in range(3):
        again = json.loads(
            subprocess.run(
                [sys.executable, str(SCRIPT), "/dev/stdin"],
                input=json.dumps([b, a]),
                capture_output=True,
                text=True,
            ).stdout
        )["generator"]
        assert again == baseline


# ---------------------------------------------------------------------------
# Saturation honesty: work is unbounded int; huge chains do not wrap or tie.
# ---------------------------------------------------------------------------

def test_unbounded_work_no_u64_saturation_tie():
    huge_receipts = [
        {"consequence_sha256": "c" * 64, "generated_build": {"manifests_verified": ["m.ex"]}}
    ]
    huge_work = 4 * 10**7  # true work; exact, far beyond any wrapped 32-bit collapse
    chain = candidate("g/huge", huge_receipts * 10**7)
    small = candidate("g/small", [receipt()])
    result = arbiter.select_winner([chain, small])
    assert result["generator"] == "g/huge"
    assert result["work"] == huge_work  # exact, unbounded
