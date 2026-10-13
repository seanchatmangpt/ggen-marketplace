# strata-net-pack

Class: CapabilityPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

Strata P2P wire + mempool (roadmap slice S7,
`docs/sjira/v26.10.8/STRATA-BLOCKCHAIN-ROADMAP.md`): CLAP-PDU message framing
for inv/getdata/tx/block/ping gossip — 8-byte header (magic 4B, kind 1B,
payload length 3B u24 big-endian) — typed decode refusals, a deterministic
`BTreeSet`-backed mempool with lowest-digest-first eviction, and a
capacity-capped peer-admission table, projected as a self-contained
serde-free Rust module.

## Capability surface

```bash
$ ggen pack capabilities strata-net-pack
provides: urn:ggen:pack:strata-net-pack, urn:strata:net:v1
requires: (none — FM-PACK-018, see pack.toml)
```

## Wire format

Fixed-width, big-endian, varint-free (CLAP-PDU conventions; ground truth:
`packs/strata-protocol-pack/ontology.ttl`, cited by comment — no
`owl:imports`; mempool admission semantics ride
`packs/strata-valve-pack`, cited by comment):

```text
header (HEADER_LEN = 8):
  [0..4)   magic "SNET" (NET_MAGIC = 0x5354_4E54)
  [4]      message kind (1-byte kind code: INV=1 GET_DATA=2 TX=3 BLOCK=4 PING=5)
  [5..8)   payload length, u24 big-endian (wire bound: MAX_MSG_LEN = 65536)
body: declared payload bytes
```

Decode refusals, in check order: `Truncated` (short header or short payload)
→ `BadMagic` → `UnknownKind` → `LengthOverMax` → `Truncated`.

## Mempool

`BTreeSet<[u8; 32]>` over entry digests — iteration order is lexical digest
order, so eviction is deterministic: the LOWEST digest is evicted first when
the pool is at `MAX_MEMPOOL` (4096). `admit` evicts; `try_admit` refuses
`Full`. Typed refusals: `Full` / `Duplicate` / `Empty`.

## Peer admission

`HashSet`-backed table capped at `MAX_PEERS` (64); typed refusals
`TableFull` / `Duplicate` / `Unknown` (on remove).

## Gates

- `gates/010_net_layout.rq` — header abutment chain (magic 0..4, kind 4..5,
  len 5..8, ends at HEADER_LEN = 8), offset collisions, NET_CONSTANTS law
  (65536 / 8 / 4096 / 64), kind-code uniqueness + u8 range, constant- and
  kind-presence arms, V7 datatype/malformed-integer fail-closed arms.
- `gates/020_msg_closure.rq` — MessageKind set is EXACTLY 5 (count arm),
  per-kind NetMessage presence, payload-length law (payloadLen > 0 for
  TX/BLOCK, = 0 for INV/PING), presence arms for the four model classes and
  four declared properties, undeclared-property closure over
  `rdfs:domain st:NetMessage`.

## Verification receipt (2026-10-13, this working tree)

- `ggen sync run` ×2 → byte-identical `generated/` (sha256 `69061ffb…`
  net_consts.rs, `669a06bb…` net_engine.rs).
- `rustc --test generated/net_consts.rs` → 4/4 pass; `rustc --test
  generated/net_engine.rs` → 13/13 pass (frame round-trip over all 5 kinds,
  kind-code stability, truncated/garbage-magic/unknown-kind/
  length-over-max decode refusals, over-max encode refusal, mempool
  admit/dup/empty/full/evict-order/freed-slot, peer cap + duplicate +
  unknown-remove, ontology-law defaults).
- Both gates 0 rows via rdflib 7.6.0, non-vacuous: a 10-mutation matrix
  (broken len offset, kind-code collision, TX payloadLen 0, PING
  payloadLen 1, deleted BLOCK message, renamed kind, 6th kind, wrong
  MAX_PEERS, dropped msgKind domain, rogue NetMessage property) fires
  1–2 rows per mutation across the two gates.
- `qualify_packs.qualify_pack(strata-net-pack)` → status ALIVE (consequence
  sha256 `521d6df2…`).

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only.
The generated module is a wire/mempool model: gossip routing, transport
security, rate limits, and eclipse hardening are S9's surface, not this
pack. Mempool digests are a documented deterministic FNV-1a placeholder —
real digest binding is S1/S3's surface.
