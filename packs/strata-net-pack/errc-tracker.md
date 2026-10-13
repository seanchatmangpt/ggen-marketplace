# errc-tracker.md — strata-net-pack (roadmap slice S7)

## Eliminate
- No serde/allocator/async dependencies in the generated module — manual
  fixed-width framing over `Vec<u8>`/slices only (a transport or gossip
  routing layer would be unearned capability until S9 demands it).
- No reserved byte in the header: magic(4)+kind(1)+len(3 u24) fills exactly
  8 bytes, so the u24 length field actually bounds MAX_MSG_LEN (a u16 len
  field would have made LengthOverMax unreachable — caught during this
  build).

## Reduce
- `requires = []` with the FM-PACK-018 documentation-only relationship note
  (same remediation as strata-tx-pack): the CLAP-PDU derivation and valve
  semantics are cited by ontology comment, never an unresolvable cross-pack
  dependency.
- Mempool digests reduced to a documented deterministic FNV-1a placeholder
  so the eviction-order court has a real ordering check without faking
  S1/S3's digest.

## Raise
- Gates carry fail-closed datatype + malformed-integer arms (V7 pattern).
- Gate 020 is bidirectional closure + count arm: the kind set is EXACTLY 5
  (a 6th MessageKind fires), per-kind NetMessage presence (a deleted BLOCK
  message fires), and any property claiming
  `rdfs:domain st:NetMessage` outside {msgKind, payloadLen} fires.
- Gate non-vacuity proven live: a 10-mutation matrix fires 1–2 rows per
  mutation across the two gates; clean graph is 0/0.
- Generated module compiles edition-agnostically (`rustc --test`, default
  edition) — no cargo required for the test court.

## Create
- `urn:strata:net:v1` capability URN minted (S9 hardening and S8 consensus
  gossip consume this framing).
- Deterministic eviction law: lowest-digest-first via `BTreeSet` order;
  `admit` evicts, `try_admit` refuses `Full` — both surfaces tested.

## Standing
ALIVE (qualification receipt 2026-10-13: sync ×2 byte-identical, 17/17 Rust
tests, 2/2 gates 0 rows non-vacuous, pack-scoped qualification ALIVE;
repo-wide `qualify_packs.py` run is BLOCKED:ONTOLOGY_SOURCE_MISSING by the
in-flight uncommitted strata-consensus-pack of the S8 lane, not by this
pack).
