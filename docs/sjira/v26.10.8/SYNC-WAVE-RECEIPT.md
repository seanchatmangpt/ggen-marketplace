# Strata Hardening Sync Wave Receipt — v26.10.8

**Wave**: strata hardening sync wave, 2026-10-13 (branch `strata-hardening-wave`).
**Subject**: ggen-marketplace @ `strata-hardening-wave` (lane L18, docs-only).
**ggen identity**: local 26.10.11.
**Scope**: `ggen sync run` schedule over the 7 strata packs, coordinator-run.
This lane did NOT execute sync; it mints the receipt skeleton and fills the
preamble + honesty sections. Result columns were EMPTY by design at mint
time — they were filled from witnessed sync output at integration (see the
Results section below), not pre-claimed.

## 1. Per-pack results

Status: results filled 2026-10-13 — see the "Results (filled 2026-10-13)"
section below (77 records family-wide, all chains valid, counts superseding
the values first written at wave close; this skeleton table is retained as
an empty pre-run artifact). The canonical qualify-marketplace.sh court
remains BLOCKED:ggen-pin-26.8.11 (see §3 item 5).

| pack | sync class (append/first) | records before → after | head chain hash | idempotency | gates |
|---|---|---|---|---|---|
| strata-cas-pack | | | | | |
| strata-pn64-pack | | | | | |
| strata-protocol-pack | | | | | |
| strata-signer-pack | | | | | |
| strata-stratus-pack | | | | | |
| strata-temprun-pack | | | | | |
| strata-valve-pack | | | | | |

## 2. Negative witnesses

(placeholder — to be filled from the coordinator's sync run: any pack where
sync refuses, double-run output drifts, or a gate fails must land here with
the exact command, exit code, and observed output)

## 3. What was NOT verified

Pre-filled from lane L18 findings; each item is a typed boundary of this
receipt, not debt hidden in a result column:

1. **`ts_ns:0` records (all records, family-wide)** — ggen 26.10.11 emits
   zeroed-timestamp receipts, so every record in every pack history carries
   `ts_ns=0`, not just pre-wave genesis entries. This is a runtime property,
   not per-pack drift. Consequence: wall-clock ordering is not recoverable
   from the receipt log; any chain computation touching timestamp provenance
   is unverified here, and sequence order is the only ordering evidence.
2. **Superseded `generated/generated/` path anomaly** (protocol receipt-log
   entry 1) — observed in the log, not reproduced or explained; flagged only.
3. **Upstream ggen pin drift** — repository pins ggen 26.8.11 while the local
   runtime is 26.10.11 (BLOCKED:user-gated). No sync result in §1 is evidence
   under the pinned identity; pin alignment is user-gated, not lane-fixable.
4. **CI-05 compilation evidence not run** — no compilation court was executed
   in this wave; generated-code compile claims carry zero bits until CI-05
   runs.
5. **Canonical qualify-marketplace.sh court BLOCKED:ggen-pin-26.8.11** — the
   repository's frozen-court run (lane R16) is gated by the `marketplace.toml`
   ggen pin 26.8.11 (BLOCKED:user-gated). That run produced ~170 corpus-wide
   refusals dominated by `unknown field build_provenance/capabilities` schema
   drift between the pinned and current runtime — runtime-version skew, NOT
   strata-specific breakage. Canonical strata evidence is `qualify_packs.py`
   on ggen 26.10.11: 7/7 packs ALIVE.

   S14 pin-survey decomposition (postdates this receipt): the ~170 frozen-court
   refusals are 163 FM-PACK-003 (161× `unknown field 'capabilities'` — the
   26.8.11 parser predates the capabilities schema; 1× schema; 1× metadata),
   6 FM-CHAIN-003 (build_provenance receipt field), and 1 FM-GRAPH-003
   (strata-protocol SPARQL parse under the old nom parser). All CI
   qualification surfaces run the PINNED binary via `install-ggen.sh`, so the
   court is self-consistent under the pin. A pin-bump recipe exists at
   `docs/context/ggen-pin-bump.pending.md`; the bump would clear ~163
   refusals but invalidates the frozen-court baselines — user-gated.

## Results (filled 2026-10-13)

| pack | sync class | records | chains valid | idempotency | gates |
|---|---|---|---|---|---|
| strata-protocol-pack | append (genesis pre-wave) | 22 | true (ggen receipt history) | double-sync byte-identical | 2 wired, negative-witnessed |
| strata-pn64-pack | first sync this wave | 9 | true | double-sync byte-identical | 3 wired, negative-witnessed |
| strata-valve-pack | append | 24 | true | double-sync byte-identical | 2 wired, mutation-witnessed |
| strata-temprun-pack | first sync this wave | 4 | true | double-sync byte-identical | 1 wired, negative-witnessed |
| strata-signer-pack | first sync this wave | 6 | true | double-sync byte-identical | 1 wired, negative-witnessed |
| strata-stratus-pack | first sync at wave (lane L3) | 6 | true | double-sync byte-identical | 1 wired, negative-witnessed |
| strata-cas-pack | first sync at wave (lane L4) | 6 | true | double-sync byte-identical | 2 wired (vacuous-pass disclosed: zero individuals) |

Record counts re-read from `ggen receipt history` (ggen 26.10.11) on
2026-10-13 across all 7 packs; family-wide total 77 records, all chains
valid. Counts supersede the values first written at wave close (12/5/15/4/
4/4/4).
