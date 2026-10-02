# v26.9.30 Consolidation Execution Wave — Lane Map (2026-10-01)

Operator order: perform the frontier consolidation + delete packs not updated in the
last 7 days (cutoff 2026-09-24, `git log -1 --format=%cs -- packs/<name>/`).
288/396 packs are stale by date; lane 8's conservation court prunes to the lawful set.

Shared-file ownership: **lifecycle.toml, marketplace.active.toml → lane 8 EXCLUSIVELY**
during the wave (consolidation lanes leave stale entries; coordinator sweeps all
merged/deleted pack entries post-wave). git mv / git rm allowed for staging; NO
commit/branch/checkout/push (coordinator owns commits).

| lane | owns (exclusive) | mission |
|---|---|---|
| 1 | dfcm-pack + 14 dfcm satellites | dfcm 15→1 (modules+uniform court; EXCLUDE ggen-combinatorial-maximalism — doctrine-referenced) |
| 2 | forced-top25-* (9 packs) | 9→1; reconcile 3 conflicting 25-target copies (newest head per repo wins, conflicts conserved in record) |
| 3 | adapter-family-matrix/-registry, fleet-* (5) | 7→1+profile (fleet-projection-closure stays profile, bumped) |
| 4 | tcps-cli/core/ffi/std/wasm + tcps-release | 5 crates→1; release stays + vendored reference/ dedup |
| 5 | gym-mcp-surface, ggen-ecosystem-mcp-surface, autofde-lab-mcp-surface, wasm4pm-facts/-cognition/-algorithms/-interview-site/-sandbox | MCP trio→1; wasm4pm facts single-owner + retire 2 prototypes |
| 6 | noun-verb-cli, diataxis-documentation, industry-closure-pack, sa2a-diataxis, clap-noun-verb-specimen, ash-extension-core/-starter/-pack | decided retirements + repoints (incl. marketplace-cli pins) + ash-extension port-then-delete |
| 7 | semantic-gate-witness-court-pack + byte-identical runner quad (affidavit-consumer, affidavit-trust-plane, capability-closure, wasi-json-abi) | canonical court config + shared runner (verify ../-ref mechanics first; NEVER touch packs/affidavit-consumer-pack/generated/ untracked tree) |
| 8 | **all packs not owned by lanes 1-7/9-10** + lifecycle.toml + marketplace.active.toml | 7d deletion with conservation court; hygiene (.pytest_cache/__pycache__); flag-only on .ggen/keys |
| 9 | runtime-evidence-authenticity(-control), ggen-platform, repo-as-found/-intervention/-load-path/-reconciliation, evidence-capital-* (8) | de-redeclaration fixes (rea:/gp:/ret: single-owner) + evidence-capital runner kernel (mechanism-permitting) |
| 10 | projection-matrix-compose/-pack, cs2-projection-matrix, beam4pm-ai-contracts, beam4pm-mcp-contracts | projection-matrix 3→1; beam4pm contracts pair→1 |

Deletion court (lane 8) exclusion rules, in order:
1. Fresh (last commit ≥ 2026-09-24) → keep.
2. On any consolidation lane's own list above → that lane owns it (keep for lane).
3. Referenced from tests/, scripts/, ci/, docs/reference/, docs/context/, docs/book*,
   marketplace*.toml, scaffolds/, packages/, .github/ (grep pack name; docs/jira/**
   historical tickets and CONSOLIDATION-FRONTIER.md do NOT count) → keep.
4. Referenced by another surviving pack (pack.toml, qualification*.toml, ggen.toml,
   gates/, ontology ttl, templates) → keep.
5. Listed in marketplace.active.toml front door → keep.
Everything else stale → `git rm -r`, remove its lifecycle.toml entry (own deletions only).
