# errc-tracker.md — strata-consensus-pack S8 construction lane

ERRC pass over the S8 construction lane (2026-10-13 session). All claims
verified against the working tree at edit time.

## Eliminate

- **No cross-pack require.** `requires = []` with the FM-PACK-018
  documentation-only note — the qualification capsule can never resolve a
  cross-pack dependency (same remediation as S2/S4/S5).
- **No wall-clock, no RNG.** Tip selection, work accounting, and all three
  adversarial guards are pure functions of their inputs; the block slot is
  a monotonic logical slot.
- **No BUSL-1.1 reuse.** S8 is GREENFIELD per the roadmap S5/S8
  precondition outcome; unibit is cited as evaluated-and-rejected, never
  vendored.

## Reduce

- **One query, two rules.** `queries/consensus_constants.rq` is shared by
  consensus-consts and consensus-engine; no duplicate query text.
- **Block shape reduced to the consensus-relevant subset.** No tx set /
  Merkle commitment — the chain layer (S5) validates those before
  consensus ever sees a block; the engine carries only height,
  parent-hash, difficulty, nonce, slot.
- **Work law reduces to one function.** `block_work` = 2^difficulty_target
  (saturating); `chain_work` is a saturating fold over it. Computing work
  from the declared target (not the found digest's actual zero count)
  makes equal-difficulty chains EXACTLY tied, which is what makes the
  tie-break law testable rather than probabilistic.

## Raise

- **Gate 020 is the adversarial-corpus manifest.** Not prose: the gate
  fails closed unless all four named `AdversarialCase` individuals exist
  AND each carries a non-empty `st:refusalPath`; Eclipse/SpamFlood must
  also carry their guard-law properties. The S9 bar is pre-committed in
  the S8 graph.
- **Typed `ConsensusRefusal`** with three named variants carrying
  expected/got payloads — every InvalidBlockGossip rejection is data,
  never a bool.
- **Fail-closed V7 gates both directions**: 010 presence + typed/
  malformed-integer arms + ForkChoice-law presence; 020 presence of all
  four named cases + non-empty refusal paths + guard-law presence.
- **Determinism pinned by test**: `equal_work_tie_resolves_to_lower_nonce`
  proves the tie law over genuinely equal work (see Reduce); mining is
  deterministic (same header ⇒ same nonce).
- **Witness + verifier court**: `witness.ttl` pins the sync graph hash
  (257cb093…); `verify.py` (provenance-copied strata-ledger-pack S4
  pattern) re-runs both gates and cross-checks the witness hash against
  the runtime receipt. Both pass zero-rows on this session's tree.

## Falsifiers (what would refute the standing claim)

- `ggen sync run` twice producing non-byte-identical generated files.
- `rustc --test` failing any of the 10 tests.
- Any gate returning a violation row.
- Qualification returning anything but ALIVE.
