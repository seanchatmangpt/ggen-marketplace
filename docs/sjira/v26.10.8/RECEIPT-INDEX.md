# RECEIPT-INDEX — gmp campaign receipt index (cold-start aid)

Lane R102, 2026-10-09. One-table index of every campaign artifact in
`docs/sjira/v26.10.8/`. Complements R99. Every row corresponds to an on-disk
entry; table rows == directory contents (count verified at write time).

Counts: 31 top-level files (30 pre-existing + this index) + 1 `seal/` directory (89 entries: 88 sj-record
JSON / txt / py / tsv artifacts plus `retired/` subdir).

## Index

| File | Role | Group |
|---|---|---|
| `_CLOSURE_RECEIPT.md` | FINAL campaign closure receipt — branch merged to main, tag `v26.10.8` cut/pushed | closure |
| `_INTEGRATION_RUNBOOK.md` | Campaign runbook seed: conventions, lane table, landing addenda | runbook |
| `ADMISSION-CONTEXT.md` | Resolution context for backlog [43]: two ledger refusal rows cite a nonexistent repo path; ledger untouched (append-only) | census/corrections |
| `ADMISSION-LEDGER.jsonl` | 78-row admission ledger (50 admitted / 28 refused, 12 repos), append-only | ledger |
| `BRANCH-CENSUS.md` | Lane R37 branch-line union census across all 20 campaign repos (ahead/behind, unmerged lines) | census/corrections |
| `candidates.jsonl` | Round-1 admission candidates (SJIRA-V8-002..006 shape) | candidates |
| `candidates-v2.jsonl` | Round-2 candidates — per-repo split of SJIRA-V8-004 (004A/004B/004C) | candidates |
| `CONVERGENCE.md` | Seed→generator convergence proof: regenerated seed graphs vs agent-authored, diffs classified | proof/court |
| `DENOMINATOR-SCOPE-DECISION.md` | Lane R64 decision: gated doc-hdit coverage denominator is **module-level** | decision/law doc |
| `DOC-HDIT-BUILD-RECEIPT.md` | Manufacturing receipt for `packs/rust-doc-hdit-pack/` + `scripts/gen_doc_surface.py` | certify receipt |
| `DOC-HDIT-PILOT.md` | End-to-end pilot of the doc-hdit pipeline (extraction + court metrics, replays) | certify receipt |
| `DOCS-DOD-GATE.md` | Documentation-campaign DoD gate receipt (§1–§10); overall verdict GATE PASS with disclosed exceptions | gate receipt |
| `FLEET-COURTS-CRON.md` | Fleet courts continuous wiring receipt — launchd every 6h (`com.sac.fleet-courts`) | CI/cron wiring |
| `FORTUNE5-EA-PACK-CI-WIRING.md` | Fortune-5 EA pack 96-test pytest battery wired into CI (lane R21) | CI/cron wiring |
| `GEN-JSONL-CLOSURE.md` | `gen_workgraph.py --emit jsonl` → `SemanticJira.admit_work_order/1` 16-key closure | proof/court |
| `GIT-TRUST-COURT.md` | Court resolving every 40-hex SHA citation in fleet `WORKGRAPH.ttl` against owning repos' git object stores | proof/court |
| `LANDING-BATCH-1.md` | Landing batch 1 receipt (3 commits) | landing receipt |
| `LANDING-BATCH-2.md` | Landing batch 2 receipt (6 commits: ontology maturity doctrine + wasmex-pack deprecation closure) | landing receipt |
| `LANDING-BATCH-3.md` | Landing batch 3 receipt (2 commits + browser-court evidence + symlink-residue cleanup) | landing receipt |
| `PIN-ROTATION-LEDGER.md` | Fleet extractor pin rotation ledger — three rotations (R43→R61→R64 lineage) | decision/law doc |
| `REFUSAL-TRIAGE.md` | Triage of all 28 refused ledger rows by typed refusal, with re-admissions | census/corrections |
| `RECEIPT-INDEX.md` | This index (lane R102, self-referential row so rows == dir contents) | index |
| `SEAL-RECEIPT.md` | Backlog [81] Phase-4 attestation closure — seal over full 78-row ledger (50/28) | seal |
| `SEAL-RUNBOOK.md` | Design/runbook for fleet workgraph ledger sealing via `sj_record` | seal |
| `SEMANTIC-WAVE-RECEIPT.md` | Semantic a2a + sjira wave manufacturing receipt (§1–§17), subject 7b3146788 | certify receipt (big four) |
| `TAG-STANDING.md` | Final tag audit (backlog [115]): advance `v26.10.8-2` annotated tags where round-5 supersedes tagged state | decision/law doc |
| `TCB-INVENTORY.md` | seL4-doctrine TCB inventory; all footprints re-read from disk 2026-10-08 | decision/law doc |
| `UNIFIED-WASM-PACK.md` | Unified Rust > WASM > Elixir pack receipt @ e987f3717 | certify receipt |
| `WORKGRAPH-REGEN-PROOF.md` | 6-repo workgraph regeneration convergence proof (generator v3 items 1–9) | proof/court |
| `WORKGRAPH-SHACL-REPORT.md` | SHACL admission validation of 12 campaign workgraphs vs `work-order.shacl.ttl`; defect classification + fixes | proof/court |
| `WORKGRAPH.ttl` | ggen-marketplace v26.10.8 workgraph seed graph (RDF) | graph |
| `seal/` | 89-entry seal surface: 88 `*.sj-record.json` (AA/ASHSURF/G1-G4/R2RML/RCERT/SJIRA-V8/XAAS/ZCODE/wo-* orders + `@round2+` reseals), `drafts.jsonl`, `standing-table.tsv`, `CHAIN-HEAD.txt`, `OSXCLNR-SEAL-HEADS.txt`, `build_drafts.py`, `UNSCOPE-*` refusal records, plus `retired/` subdir | seal |

## Big four cross-links

- **SEMANTIC-WAVE-RECEIPT.md** (§1–§17) — wave manufacturing receipt, subject 7b3146788.
- **DOCS-DOD-GATE.md** (§1–§10) — docs DoD gate receipt, GATE PASS with disclosed exceptions.
- **TAG-STANDING.md** — final tag audit / `v26.10.8-2` promotion decision (backlog [115]).
- **SEAL-RECEIPT.md** — backlog [81] Phase-4 attestation closure over the 78-row ledger.

## Cold-start reading order

1. `_INTEGRATION_RUNBOOK.md` (campaign shape) → 2. `ADMISSION-LEDGER.jsonl` +
`REFUSAL-TRIAGE.md` (what was admitted/refused) → 3. big four above →
4. `seal/standing-table.tsv` for per-order standing.
