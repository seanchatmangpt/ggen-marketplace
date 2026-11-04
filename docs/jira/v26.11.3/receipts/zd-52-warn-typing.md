# ZD-52: WARN/SKIPPED baseline typing (MKT-03)

Base: f5d5aea77+ (main). Owned file: `qualification/baseline.json` only
(WARN/SKIPPED entries typed; statuses untouched). Each entry was typed by
reading the pack + its on-disk qualification evidence
(`qualification.toml` / `pack.toml` annotations), not from the warn text
alone.

## Per-pack typing table

| pack | status | class | annotation | evidence |
|---|---|---|---|---|
| automatic-autonomic-operations-pack | WARN | ratchet-residue | `ACCEPTED-WARN:missing-external-path-dependency` | `packs/automatic-autonomic-operations-pack/qualification.toml:1-8` (AE8 2026-10-05) |
| certification-assist-evidence-control-pack | WARN | ratchet-residue | `ACCEPTED-WARN:missing-external-path-dependency` | `packs/certification-assist-evidence-control-pack/qualification.toml:1-8` |
| certification-assist-pack | WARN | ratchet-residue | `ACCEPTED-WARN:missing-external-path-dependency` | `packs/certification-assist-pack/qualification.toml:1-8` |
| clap-noun-verb-crate-pack | WARN | ratchet-residue | `ACCEPTED-WARN:solo-capsule-missing-composed-sibling-pack-outputs` | `packs/clap-noun-verb-crate-pack/qualification.toml` (modules manufactured by behavior/boundary/routing sibling packs) |
| clap-noun-verb-schema-pack | WARN | **real-signal** | `REPAIR-LANE:composition-closure-claim-unwitnessed-by-court` | `packs/clap-noun-verb-schema-pack/pack.toml:8-14` (zd-28) claims requiring behavior/boundary/routing sibling packs "makes the generated crate complete and the WARN's honest ceiling ALIVE"; the ggen 26.10.11 court still reports `error[E0583]: file not found for module 'generated_behavior'` (baseline warn_reason) — the composition-closure claim is not witnessed by the court. Gap for the repair lane: composed sibling-pack outputs are still absent from the solo qualification capsule, or the requires-closure claim is wrong. |
| ex4pm-wasm4pm-bindings-pack | WARN | ratchet-residue | `ACCEPTED-WARN:missing-external-path-dependency` | `packs/ex4pm-wasm4pm-bindings-pack/qualification.toml:1-7` (deps live in sibling wasm4pm repo; correct in intended consumer workspace) |
| ontostar-mustar-powlv2-agent-pack | WARN | ratchet-residue | `ACCEPTED-WARN:missing-external-path-dependency` | `packs/ontostar-mustar-powlv2-agent-pack/qualification.toml:1-7` |
| otel-weaver-ocel-pack | WARN | ratchet-residue | `ACCEPTED-WARN:dependency-requires-nightly` | `packs/otel-weaver-ocel-pack/qualification.toml:1-6` (git dep wasm4pm-compat enables `#![feature]` unconditionally; dep-crate constraint, documented in pack's own template header) |
| speedrun-talent-network-pack | WARN | ratchet-residue | `ACCEPTED-WARN:missing-external-path-dependency` | `packs/speedrun-talent-network-pack/qualification.toml:1-7` |
| tcps-pack | SKIPPED | skipped (harness limitation) | `SKIPPED:GGEN_PACK_GENERATED_BUILD_NEEDS_WORKSPACE_ROOT` | `scripts/qualify_packs.py:609-641` — generated workspace Cargo.toml uses workspace-field inheritance; the scratch capsule is deliberately a bare non-workspace project, so this is a harness limitation, "not evidence of a portability defect" (the code's own docstring), skipped rather than refused |
| tcps-release-pack | WARN | ratchet-residue | `ACCEPTED-WARN:workspace-members-not-pack-outputs` | `packs/tcps-release-pack/qualification.toml:1-7` (workspace member crate bodies are not pack generation-rule outputs; correct in real tcps consumer workspace) |

Tally: 9 ratchet-residue, 1 real-signal, 1 skipped (harness limitation).

The annotation vocabulary reuses each pack's own existing vocabulary
(`ACCEPTED-WARN:<slug>` in the AE8 2026-10-05 qualification.toml
annotations; the SKIPPED machine code from `qualify_packs.py`), extended
with `REPAIR-LANE:<slug>` for the one real-signal entry. The baseline had
no annotation field before this task; `warn_class` + `annotation` were
added uniformly to all 11 WARN/SKIPPED entries via mechanical script
(`/tmp/mkt03_type_baseline.py`, python3 json round-trip preserving the
file's sort_keys/indent=2 format) — no hand-edited JSON.

## Counts (recomputed mechanically post-edit)

ALIVE 327 / REFUSED 9 / SKIPPED 1 / WARN 10 — identical to pre-edit
(annotations only; no status changed).

## Verify commands / exits

- `python3 /tmp/mkt03_type_baseline.py` -> exit 0
  (`typed 11 entries; counts: {"ALIVE": 327, "REFUSED": 9, "SKIPPED": 1, "WARN": 10}`)
- `python3 -m json.tool qualification/baseline.json` -> exit 0 (jq-valid equivalent)
- `python3 scripts/warn_ratchet.py check /tmp/mkt03_report.json` (report
  projected from the post-edit baseline itself, so the court compares
  identical statuses) -> exit 0,
  `ratchet ok counts={"ALIVE": 327, "REFUSED": 9, "SKIPPED": 1, "WARN": 10}`

## Standing

ALIVE (ran this session, exits above). The one real-signal entry
(clap-noun-verb-schema-pack) is staged for a repair lane: either the
qualification court must stage composed sibling-pack outputs, or the
zd-28 pack.toml claim must be corrected.
