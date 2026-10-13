# strata-consensus-pack

S8 of the Strata blockchain roadmap
(`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): the consensus kernel
as an ontology-backed ggen pack. Projects the consensus constants and a
self-contained engine — heaviest-chain fork choice over the chain layer's
block shapes (formalized conceptually as the PN64-style transition lattice),
the valid-extension law, and the adversarial guards — generation over
hand-writing per doctrine. GREENFIELD per the roadmap S5/S8 precondition
outcome: no nonce, difficulty, or fork-choice code exists anywhere to reuse,
and the BUSL-1.1 unibit tree is off-limits (its "TruthBlock" is a memory
region, not a blockchain block).

## What it projects

Two generated Rust modules from one RDF ontology
(`https://strata.chatman.ai/ontology#`):

- `generated/consensus_consts.rs` — `WORK_UNIT` ("sha256-double-tick"),
  `TIE_BREAK` ("lower-nonce"), `ECLIPSE_MAX_PEERS_PER_SUBNET` (8),
  `SPAM_LIMIT` (32).
- `generated/consensus_engine.rs` — zero-crate SHA-256 (FIPS 180-4,
  provenance-copied strata-hash-pack pattern with the published FIPS
  vectors as tests), the consensus-relevant `Block` shape
  (provenance-copied PATTERN from strata-chain-pack — no cross-pack
  imports, FM-PACK-018), `block_work` / `chain_work` (work =
  2^(difficulty leading zeros), the transition-lattice accumulated
  weight), `select_tip` (heaviest total work wins; exact equal-work tie →
  lower tip nonce), `is_valid_extension(parent, candidate)` (typed
  `ConsensusRefusal`: `HeightContinuity`, `ParentHashMismatch`,
  `PoWTargetNotMet` — the InvalidBlockGossip refusal path), and the
  adversarial module: `selfish_mining_detected` (withhold-then-release
  report pattern, run threshold 2), `eclipse_guard` (per-subnet peer cap,
  returns refused peers deterministically), `spam_limit` (per-slot gossip
  cap).

## Gates

- `gates/010_consensus_layout.rq` — CONSENSUS_CONSTANTS presence + typed/
  malformed-integer arms plus the HEAVIEST_CHAIN ForkChoice law presence
  (V7 fail-closed pattern).
- `gates/020_adversarial_closure.rq` — the adversarial-corpus manifest:
  all four `AdversarialCase` individuals (SelfishMining, Eclipse,
  SpamFlood, InvalidBlockGossip) present, each with a non-empty refusal
  path; Eclipse/SpamFlood must also carry their guard laws. Zero rows is
  the pass bar (S9 hardening bar pre-committed at S8).

## Verify

```bash
cd packs/strata-consensus-pack
ggen sync run    # regenerates generated/*.rs from ontology.ttl (×2 byte-identical)
rustc --test -O generated/consensus_engine.rs -o /tmp/consensus_engine && /tmp/consensus_engine
rustc --test generated/consensus_consts.rs -o /tmp/consensus_consts && /tmp/consensus_consts
python3 verify.py                       # gates zero-rows + witness-hash court
python3 scripts/qualify_packs.py --pack strata-consensus-pack
```

## Standing

`ALIVE` (qualification 2026-10-13, ggen 26.10.11): isolated-pack sync,
compile, full test suite, zero-rows gates, deterministic catalog. The pack
projects a specification + reference kernel under the house
SELECT/CONSTRUCT fence — it projects code and grants no DO authority.
