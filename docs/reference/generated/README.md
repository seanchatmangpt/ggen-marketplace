# GENERATED — doc-hdit reference skeletons

<!-- GENERATED-BANNER: every file in this directory except this README is   -->
<!-- rendered by the rust-doc-hdit-pack's `doc-hdit scaffold` verb from a    -->
<!-- deterministic code-surface extraction. Do NOT hand-edit. Regenerate:    -->
<!--                                                                         -->
<!--   python3 scripts/gen_doc_surface.py code /Users/sac/ggen-marketplace \  -->
<!--     > /tmp/hdit/ggen-marketplace.code.v3.json                           -->
<!--   packs/rust-doc-hdit-pack/target/release/doc-hdit scaffold \           -->
<!--     --code /tmp/hdit/ggen-marketplace.code.v3.json \                    -->
<!--     --templates packs/rust-doc-hdit-pack/templates \                    -->
<!--     --out docs/reference/generated                                      -->
<!--                                                                         -->
<!-- Court: packs/rust-doc-hdit-pack/courts/doc_quality.court                -->

## What this directory is

Deterministic reference skeletons for the ggen-marketplace code surface
(912 modules / 6,903 public items), rendered by `doc-hdit scaffold` from
`scripts/gen_doc_surface.py code` output. `reference.md` is entirely
AGENT-FORBIDDEN (rigid tables); `how_to.md` and `explanation.md` carry a
bounded `AGENT-COMMENTARY` slot as the only hand-writable region.

## Files

| file | content |
|---|---|
| reference.md | AGENT-FORBIDDEN reference tables from the code surface |
| how_to.md | prerequisite verbs (pack scripts/bin surface) |
| explanation.md | summary + verified-snippet + bounded commentary slot |
| README.md | this provenance banner (hand-maintained; this file only) |

## Coverage audit (2026-10-08, lane scaffold-mp)

`doc-hdit audit <inputs.json> packs/rust-doc-hdit-pack/courts/doc_quality.court`
over the repo's doc claims, before vs after landing these skeletons:

| gate | before | after | threshold |
|---|---|---|---|
| S_coverage (gated) | 0.1166 | 0.1205 | >= 0.9000 |
| S_coverage_raw (report-only) | 0.4880 | 0.4960 | — |
| Phi_halluc | 0.0745 | 0.0726 | <= 0.0010 |
| Q_density | 0.9255 | 0.9274 | >= 0.6500 |

S_coverage rises (+0.0039) but remains below the 0.90 gate: the scaffold
lands real code-fact coverage (coverage_raw +0.0080) without overclaiming
admission — the court verdict for this repo stays FAIL-coverage, honestly
reported. Remediation continues by extending doc claims toward the
scaffold's uncovered-public-module lists.
