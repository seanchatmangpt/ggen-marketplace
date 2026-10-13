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
- S9 (roadmap slice 9): hardening refusal paths landed —
  `HardenedPeerTable` (eclipse subnet cap 8, `Blacklist` 16-slot terms,
  duplicate/table-full ladder), `SlotRateLimiter` (32/slot, typed
  `SpamFlood`), `Mempool::admit_block` (typed `InvalidBlock`, pool
  untouched on refusal); ontology gains `subnetClass` / `msgsThisSlot` /
  `blacklisted` / `blacklistSlots` + constants `ECLIPSE_SUBNET_CAP` 8
  (consensus-pack parity) / `BLACKLIST_SLOTS` 16 / `MAX_MSGS_PER_SLOT` 32;
  gate `030_hardening_law.rq` (blacklist-term law, constant presence+
  value arms, V7 typed/malformed arms, corpus non-vacuity) proven
  non-vacuous by mutation (eclipse cap → 9 and blacklistSlots → 0 each
  fire).

## Standing
ALIVE (qualification receipt 2026-10-13, L150: sync ×2 byte-identical
(`68f16935…` engine / `8871be7e…` consts), 26/26 Rust tests via
`rustc --test` incl. S9 hardening courts, 4/4 gates 0 rows
(010/020/030/040), pack-scoped qualification ALIVE (qualify_packs.py
--pack strata-net-pack → ALIVE, consequence_sha256 `0435e62c…`);
L150 composition law landed — gate `040_composition_law.rq` makes the
L34 #4 one-way law explicit: mempool admission (`sum_out >= sum_in`
shadow, net_engine.rs.tera:269) is NECESSARY NOT SUFFICIENT for ledger
admission (strict equality valve, strata-ledger-pack
ledger_state.rs.tera:403); ontology `st:CompositionLaw` /
`st:MEMPOOL_LEDGER_ADMISSION` with provenance mfact
`procint/ProcInt/Petri/NetLaws.lean:319 inflation_passes_mempool_shadow`;
gate proven non-vacuous by mutation (drop-individual and
bad-completingGate each fire 1 row). verify.py witness set 040 matches
receipt closure hash `29890c6e…`. No repo-wide qualify attempt from this
lane; S8-lane caveat above no longer re-verified by this lane.
