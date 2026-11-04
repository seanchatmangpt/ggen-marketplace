# ZD-12: baseline-to-disk reconcile (qualification/baseline.json)

XA-3 drift finding: 2 baseline entries with no pack dir, 37 pack dirs with no
baseline entry (36 real packs + 1 dot-dir runtime cache). Resolution: full
mechanical re-run of the qualification court and re-projection via
`scripts/warn_ratchet.py baseline` — no hand-written JSON.

## Lawful direction per entry (from the court, not hand-judged)

- **Removed (2)**: `a2a-security-pack`, `a2a-v1-protocol-pack` — pack dirs do
  not exist on disk (phantom entries from the 2026-10-04 wave, see
  `marketplace.active.toml:36-41`: "manifests not yet on disk"). Dropped by
  re-projection; recorded here rather than silently deleted.
- **Added (36 packs)**: court-qualified this run — 29 ALIVE, 7 REFUSED:
  court-kit-pack, fortune5-enterprise-architecture-pack, pack-bootstrap-pack,
  rust-doc-hdit-pack, smalt-semconv-pack, smalt-substrate-pack,
  typer-azure-pack. The 7 REFUSED are real FM-PACK-005 / FM-GEN-008 defects
  (zero templates; template variable `row.kind` missing), not baseline noise.
  (The 37th dir, `.clap-noun-verb`, is runtime cache, correctly not a pack.)
- **Changed (14 existing)**: 7 regressions under ggen 26.10.11 —
  a2a-hex-migration-pack, ash-extension-pack, chicago-tdd-tools-pack,
  cnv-any-manifest-pack, graphlaw-ash-capability-pack,
  greene-licensing-case-pack (ALIVE->REFUSED); clap-noun-verb-schema-pack
  (ALIVE->WARN). 7 improvements (REFUSED->ALIVE): aaif-profile-tailoring-pack,
  aaif-vanilla-pack, ash-pplan-{igniter,protocol-court,store-conformance}-pack,
  gcp-marketplace-saas-pack, tokyo-depeg-burn-in-pack. Recorded honestly;
  the 7 regressions are unfixed pack defects for the pack-owner lanes
  (packs/ dirs not in this lane's file ownership — not touched here).

## Counts (recomputed mechanically by warn_ratchet.project())

Old: ALIVE 295 / REFUSED 8 / SKIPPED 1 / WARN 9 (313 entries)
New: ALIVE 322 / REFUSED 14 / SKIPPED 1 / WARN 10 (347 entries)

## Commands / exits

- `python3 scripts/qualify_packs.py --workers 16 --report /tmp/xa3_qual_report.json`
  -> exit 2 (REFUSED:GGEN_PACK_QUALIFICATION_FAILED:failed=14 total=347;
  report still written — the court's honest output, per script semantics)
- `python3 scripts/warn_ratchet.py baseline /tmp/xa3_qual_report.json`
  -> exit 0, "baseline written packs=347 counts={ALIVE: 322, REFUSED: 14, SKIPPED: 1, WARN: 10}"
- `python3 scripts/warn_ratchet.py check /tmp/xa3_qual_report.json`
  -> exit 0 "ratchet ok counts=..." (new baseline self-consistent with report)
- `python3 -c json.load` -> valid; `jq -c .counts` -> `{"ALIVE":322,"REFUSED":14,"SKIPPED":1,"WARN":10}`

## Standing

ALIVE for the reconcile; ALIVE-with-findings for the corpus: the court now
covers 347 packs (was 313). 7 pre-existing packs regressed to REFUSED under
ggen 26.10.11 — real defects, owned by pack lanes, not this receipt.
