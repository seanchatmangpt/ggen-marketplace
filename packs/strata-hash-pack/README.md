# strata-hash-pack

S1 of the Strata blockchain roadmap
(`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): cryptographic
primitives as an ontology-backed ggen pack. Projects `pub const` hash
algorithm closure {BLAKE3, SHA-256} plus a self-contained SHA-256
(FIPS 180-4) and Merkle tree (root + inclusion proofs) with property
tests — generation over hand-writing per doctrine.

## What it projects

Two generated Rust modules from one RDF ontology
(`https://strata.chatman.ai/ontology#`):

- `generated/hash_consts.rs` — `HASH_ALGOS: [(&str, usize)]` const table
  (name, digest length) plus closure and digest-width courts.
- `generated/hash_merkle.rs` — zero-crate SHA-256 (padding, message
  schedule, 64-round compression) and a Merkle tree over 32-byte digests
  using the duplicate-last (Bitcoin) odd-width rule, with property tests:
  empty-tree refusal, single-leaf, 1..=300-leaf proof sweep (covers every
  2^k up to 256), tampered sibling/leaf/root/index/truncated-proof
  failure courts, FIPS 180-4 test vectors.

## Build

```bash
cd packs/strata-hash-pack
ggen sync run    # regenerates generated/*.rs from ontology.ttl
rustc --test -O generated/hash_merkle.rs -o /tmp/merkle && /tmp/merkle
rustc --test generated/hash_consts.rs -o /tmp/consts && /tmp/consts
```

## Verification ladder (receipted this session)

1. `ggen sync run` x2 -> byte-identical outputs.
2. `rustc --test` — 12/12 tests pass (10 merkle + 2 consts).
3. Gates zero-rows via rdflib (010 digest-length, 020 algorithm-closure).
4. `python3 scripts/marketplace.py validate` — 317 packs validated, exit 0.
5. `scripts/qualify_packs.py` — `strata-hash-pack` status ALIVE.

## Family-canonical BLAKE3 ownership (L167 consolidation)

`generated/hash_merkle.rs` is the family-canonical full BLAKE3 port
(hash mode, unkeyed, 32-byte output; multi-chunk streaming via the
reference Hasher/cv_stack shape), provenance-copied from
strata-tx-pack's tx_model.rs. strata-chain-pack and strata-tx-pack pin
this module by sha256 and carry differential cross-pack KATs over the
shared vectors (512B `b[i]=(i*7+13) mod 256` -> `1dd56407...e0a6`;
2000B `b[i]=(i*11+5) mod 256` -> `6a34306d...12b7`), each pinned
against the independent Python `blake3` reference. One calculus, one
canonical implementation.
