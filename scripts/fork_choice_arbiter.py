#!/usr/bin/env python3
"""C20 generator-plurality arbiter (L51 seam 2/3 prototype, lane L80).

Fork choice over candidate generator identities, strata-consensus law:

    greatest total work wins; equal work -> lower tip nonce.

Work is a plain Python int -- deliberately UNBOUNDED. Reason: the strata
chain_work saturation tie flag from L34 showed that a bounded u64 accumulator
can tie two chains whose true work differs, silently corrupting fork choice.
Until the production question is settled (see below), the prototype refuses to
saturate: accumulation is exact, so no two distinct evidence chains can tie
unless their real work is genuinely equal.

Production open question (NOT solved here): a u64-saturating variant --
`work = min(U64_MAX, work + w)` per step -- must decide whether saturation
collisions resolve to the nonce tie-break (deterministic but work-blind) or
carry an explicit saturation flag into the receipt so a saturated fork is
marked PARTIAL/UNKNOWN rather than admitted as a tie. Prototype takes the
unbounded answer; production must pick and receipt one.

Receipts reuse the real qualification JSON shape (scripts/qualify_packs.py):
each record may carry `consequence_sha256`, `consequence_files`,
`generated_build.manifests_verified`, `status`. Work scoring is conservative
and derived only from fields the real runner emits.

Deterministic: sha256-based tip nonce, no wall-clock, no RNG.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List

# Work weights (ints; accumulated unbounded).
WORK_CHAIN_LINK = 1  # a qualification receipt exists at all
WORK_CONSEQUENCE_DIGEST = 2  # consequence_sha256 present (bounded consequence proven)
WORK_MANIFEST_VERIFIED = 1  # per manifest in generated_build.manifests_verified


def receipt_work(record: Dict[str, Any]) -> int:
    """Work contributed by one qualification receipt (real JSON shape)."""
    if not isinstance(record, dict):
        return 0
    work = WORK_CHAIN_LINK
    if record.get("consequence_sha256"):
        work += WORK_CONSEQUENCE_DIGEST
    generated = record.get("generated_build") or {}
    manifests = generated.get("manifests_verified") or []
    if isinstance(manifests, list):
        work += WORK_MANIFEST_VERIFIED * len(manifests)
    return work


def chain_work(evidence: List[Dict[str, Any]]) -> int:
    """Total work of an evidence chain. Unbounded int -- no saturation."""
    return sum(receipt_work(r) for r in evidence)


def tip_nonce(generator_identity: str) -> int:
    """Tip nonce: sha256(identity string) read as a big-endian int."""
    digest = hashlib.sha256(generator_identity.encode("utf-8")).hexdigest()
    return int(digest, 16)


def select_winner(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Select per strata law. candidates: [{generator, evidence: [receipts]}].

    Returns {"generator": ..., "work": int, "tip_nonce": int, "reason": str}.
    Raises ValueError on empty input.
    """
    if not candidates:
        raise ValueError("no candidates: empty fork")

    scored = []
    for cand in candidates:
        scored.append(
            {
                "generator": cand["generator"],
                "work": chain_work(cand.get("evidence", [])),
                "tip_nonce": tip_nonce(cand["generator"]),
            }
        )

    best = max(scored, key=lambda s: (s["work"], -s["tip_nonce"]))
    tied = [s for s in scored if s["work"] == best["work"]]
    if len(tied) == 1:
        best["reason"] = "greatest-work"
    else:
        best["reason"] = "work-tie:lower-tip-nonce"
        best["tied_generators"] = sorted(s["generator"] for s in tied)
    return best


def main(argv: List[str]) -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("candidates_json", help="path to candidates JSON: [{generator, evidence}]")
    args = parser.parse_args(argv)
    with open(args.candidates_json) as handle:
        candidates = json.load(handle)
    print(json.dumps(select_winner(candidates), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
