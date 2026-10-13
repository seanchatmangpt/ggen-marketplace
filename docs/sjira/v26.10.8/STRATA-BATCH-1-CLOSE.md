# STRATA-HARDENING-1 Batch 1 — CLOSED

- **Item**: `docs/sjira/v26.10.8/STRATA-HARDENING-1.md` items P1, P7, P18 —
  the strata pack family (`strata-cas-pack`, `strata-pn64-pack`,
  `strata-protocol-pack`, `strata-signer-pack`, `strata-stratus-pack`,
  `strata-temprun-pack`, `strata-valve-pack`) failing marketplace
  qualification with `FM-PACK-014`/`FM-PACK-018` plus accumulated ontology/
  template hygiene debt.
- **Status**: CLOSED 2026-10-13 (batch 1).
- **Fixing commits** (on `ggen-marketplace` branch `strata-hardening-wave`):
  1. `513a1a64c` — `fix(strata packs): FM-PACK-014/018 — drop unresolvable
     [dependencies], empty requires`. Deleted the five unresolvable
     `[dependencies]` blocks and emptied `requires=[]` so pack sync no longer
     refuses on missing capability URNs.
  2. `11c749278` — `refactor(strata packs): ontology hygiene + delete dead
     clap_frame template`. Deletes the dead `clap_frame.rs.tmpl`; declares
     `pdu:FrameConstant` + `valve:WireFact` in the ontologies; pn64
     `verbOpcode` dead-vocab removal and `pn:` alias drop. Output-neutral
     sync proven: generated template byte count 1852 → 1851 with no
     consumer-output change.
- **Fix shape**: remediation at the pack contract level (ggen.toml
  `[dependencies]`/`requires` surface and ontology vocabulary), not at the
  generated-consumer level. Generated files remain projections; no
  hand-edits to consumer output.
- **Witnesses** (real qualification artifacts on this machine):
  1. `/tmp/wave-baseline-qual.json` (ggen 26.10.11, 315 packs) — pre-fix
     baseline. Strata family split: 3 ALIVE (`strata-pn64-pack`,
     `strata-protocol-pack`, `strata-valve-pack`) / 4
     `REFUSED:GGEN_PACK_SYNC_FAILED` (`strata-cas-pack`, `strata-signer-pack`,
     `strata-stratus-pack`, `strata-temprun-pack`). Whole-corpus:
     264 ALIVE / 41 REFUSED / 9 WARN / 1 SKIPPED.
  2. `/tmp/wave-p1b-qual.json` (ggen 26.10.11, 315 packs) — post-fix court.
     Strata family: **7/7 ALIVE**. Whole-corpus: 268 ALIVE / 37 REFUSED /
     9 WARN / 1 SKIPPED (the 4 remediated strata refusals account for the
     REFUSED delta 41 → 37).
- **Consumer consequence**: all seven strata packs now pass real ggen
  `sync run` qualification on the exact subject; consumers of the strata
  family can admit and project from these packs without the FM-PACK-018
  unresolvable-capability refusal. Remaining corpus refusals (37) are
  outside batch 1 scope and are not affected by this closure.
