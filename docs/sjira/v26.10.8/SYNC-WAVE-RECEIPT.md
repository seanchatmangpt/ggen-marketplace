# Strata Hardening Sync Wave Receipt — v26.10.8

**Wave**: strata hardening sync wave, 2026-10-13 (branch `strata-hardening-wave`).
**Subject**: ggen-marketplace @ `strata-hardening-wave` (lane L18, docs-only).
**ggen identity**: local 26.10.11.
**Scope**: `ggen sync run` schedule over the 7 strata packs, coordinator-run.
This lane did NOT execute sync; it mints the receipt skeleton and fills the
preamble + honesty sections. Result columns are EMPTY by design — they are to
be filled from witnessed sync output at integration, not pre-claimed.

## 1. Per-pack results

Status: results pending — the schedule has not been executed by this lane.
Every result cell below is EMPTY until the coordinator's sync run lands
witnessed output for that pack.

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

1. **Legacy `ts_ns:0` genesis records** — not re-derived, not re-hashed; any
   chain computation that touches genesis provenance is unverified here.
2. **Superseded `generated/generated/` path anomaly** (protocol receipt-log
   entry 1) — observed in the log, not reproduced or explained; flagged only.
3. **Upstream ggen pin drift** — repository pins ggen 26.8.11 while the local
   runtime is 26.10.11 (BLOCKED:user-gated). No sync result in §1 is evidence
   under the pinned identity; pin alignment is user-gated, not lane-fixable.
4. **CI-05 compilation evidence not run** — no compilation court was executed
   in this wave; generated-code compile claims carry zero bits until CI-05
   runs.
