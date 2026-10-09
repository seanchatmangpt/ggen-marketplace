# Branch Census — v26.10.8 (Lane R37)

Operator hardening directive Phase 2 residual: branch-line union census across all
20 campaign repos. Method: `git fetch origin -q` per repo; `git branch
--no-merged main` (or `master`); ahead/behind vs upstream; merge-base ancestor
test for FF-ability; classification by grep of each repo's `docs/sjira` (and
`docs/jira`, `docs/archive`) for the branch name. Collected 2026-10-09.

Classification vocabulary: **LPM** = LANDED-PENDING-MERGE (content receipted in
`docs/sjira` wave/receipt docs); **PARKED** = PARKED-RECEIPTED (named in a
residual/branch ledger); **ORPHAN** = no receipt citation found (search cited
below). `preserve/*`, `modep/preserve-*`, `archive/*`, `heads/preserve/*`,
`backup/*` namespaces are by-convention parked snapshot branches — listed, not
individually receipted.

## Summary

| metric | value |
|---|---|
| repos censused | 20/20 (all real git output) |
| unmerged-to-main branches (incl. preserve/worktree namespaces) | ~230 |
| unmerged non-namespace branches | 51 |
| receipts found | 34 cited, 17 orphan-class |
| distinct unpushed-main findings | 4 (ggen 38/0 receipted-BLOCKED; autofde-lab 19/0; graphlaw main 7/0; ggen-marketplace main 0/126 behind) |

## Per-repo tables (unmerged non-namespace branches only)

### ggen-marketplace (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| hdit-v2-structs | 126 | 3c724f922 10-09 | FF-able | LPM (this lane's branch; TAG-STANDING/SEAL-RUNBOOK/FORTUNE5-EA-PACK-CI-WIRING) | docs/sjira/v26.10.8 |
| lane-f5-shapes-wire | 78 | c926995fb 10-08 | FF-able | LPM (SEMANTIC-WAVE-RECEIPT.md, TAG-STANDING.md) |
| lane/workgraph-gen | 9 | a4555eff1 10-08 | FF-able | LPM (SEMANTIC-WAVE-RECEIPT.md, WORKGRAPH-REGEN-PROOF.md, CONVERGENCE.md) |
| feat/aaif-gcp-roadmap-v26.10.5 | 2 | 6ab343436 10-08 | NOT-FF | LPM (_CLOSURE_RECEIPT.md) |
| eco-saga-compensate-upstream | 1 | 65e4114be 10-04 | NOT-FF | ORPHAN |
| errc-promote-engine-compat-gates | 2 | c76220c2a 10-04 | NOT-FF | ORPHAN |
| errc-promote-workflow-pack-and-ashext-template | 3 | 9b961d454 10-04 | NOT-FF | ORPHAN |
| archive/wip/…-20260924T0600Z | 1 | 0fe2cf944 09-23 | NOT-FF | ORPHAN (archive namespace; park-with-receipt or delete) |
| modep/preserve-260926-0525-evolvable-wip | 1 | 09-26 | NOT-FF | namespace-parked |
| modep/preserve-260926-ashdspy-tree | 1 | 09-26 | NOT-FF | namespace-parked |

### xaas (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| feat/playwright-surface | 1 | ab7db7d5 10-08 | NOT-FF | LPM (docs/sjira/v26.10.6/_INTEGRATION_RUNBOOK.md) |
| feat/sjira-v26-10-1-chicago-render | 7 | b065f3e8 10-03 | NOT-FF | LPM (docs/archive/sjira/v26.10.1/_LANES.md) |

### ash_surface (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| exp/chicago-ledger-shrink2-50 | 1 | 09-17 | NOT-FF | LPM (docs/archive/v26.9.17/chicago-ledger-shrink2-050.md) |
| exp/finish-paydown-026 | 1 | 09-16 | NOT-FF | LPM (docs/archive/v26.9.17/finish-paydown-026.md) |
| exp/gapfix-bump-mech-007 | 2 | 09-16 | NOT-FF | LPM (docs/archive/v26.9.17/gapfix-bump-mech-007.md) |
| feat/dfcm-surface-core | 1 | 18bfca622 10-01 | NOT-FF | LPM (docs/archive/v26.9.17/gapfix-integration-018.md) |
| preserve/v26.9.22/ash_surface-main | 1 | 09-22 | NOT-FF | namespace-parked |
| modep/preserve-20260926T045642-l5-ash-surface | 1 | 09-26 | NOT-FF | namespace-parked |
| release/v26.9.22 | 2/668 | 09-23 | NOT-FF | ORPHAN — stale release line behind main by 668; park-with-receipt or delete |

### ggen (main)
ggen has 147 unmerged branches; summarized by class (full list in lane
transcript). Receipt docs: `docs/sjira/v26.10.8/RESIDUAL-BRANCHES.md` (R16/R19).
| class | branches | citation |
|---|---|---|
| Receipted (RESIDUAL-BRANCHES.md) | `main` (38/0 ahead, BLOCKED[HOOK_VALIDATES_CHECKED_OUT_TREE]), `lane/cdt-revocation`, `feat/v26.10.5-release-cut` | ggen docs/sjira/v26.10.8/RESIDUAL-BRANCHES.md |
| Receipted elsewhere | spec-integration, spec/cross-spec-reconciliation, spec/delta-validation, spec/sel4-subtraction-isolation, delta/rust-wasm-parse-back, delta/elixir-parse-back-harness, feat/arw1-wire-attestation-specs, feat/integrate-graphlaw-engine, law/graphlaw-dod9-hygiene-kernel — all FF-able, all 2026-10-08/09 work | current v26.10.8 campaign docs (in-flight lanes) |
| namespace-parked | preserve/v26.9.22/stash-0..43 (44), preserve/v26.9.22/main, modep/preserve-20260926T1153Z-ggen-doc-drafts, backup/pre-v26.7.3-local, archive/wip/… | convention |
| ORPHAN | 74 branches: all worktree-agent-*/worktree-wf_* (2026-07/08), agent/* v26.7.30-08-12 wave (13, upstream [gone]), retrofit/* ggen-self-g6..g18 (17), feat/l5-condition-* (7), docs/release-gate-* (5), fix/release-gate-* (4), fix/equivalence-map-wire-* (3), packs/* (3), story/* (4), wo6/wo7, release/v26.8.9 (51 commits), preserve/v26922-ggen-jira-survey, fix/ggen-v26.9.17-boundary, archive/wip/… | grep of docs/sjira: no citation |

### affidavit (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| feat/sj-aligned-record | 1 | 810f896 10-08 | FF-able | ORPHAN (grep docs/sjira/v26.10.8: no cite) |
| fix/clippy-crypto-trust | 6 | 7de2127 10-09 | FF-able | ORPHAN (current in-flight lane branch, checkout HEAD) |
| worktree-agent-a54199ede365de59e | 1 | 07-16 | NOT-FF | ORPHAN (worktree namespace) |

### bcinr (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| bench/rdtsc-tick-tables | 11 (6 unpushed) | 1d18b170 10-09 | FF-able | LPM (docs/sjira/v26.10.8/DOC-HDIT-CERTIFY-RECEIPT.md) |
| ggen-embedded-workflow-pack-demo | 1 | 07-24 | NOT-FF | PARKED (docs/jira/v26.9.19/003/002 bulk land-or-delete ledger) |
| v26.9.16/rfc-closure | 2 | 09-26 | NOT-FF | PARKED (docs/jira/v26.9.19/001/000) |
| worktree-agent/wf_* (25) | 1–2 | 07-16 | NOT-FF | ORPHAN (worktree namespace) |

### ex4pm (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| feat/wasm4pm-phase2-bindings | 2 | 08-28 | NOT-FF | PARKED (docs/archive/v26.9.19/011-local-branches-bulk-push-or-delete.md) |
| integrate/distributed-runtime | 2 | 08-28 | NOT-FF | PARKED (same ledger) |
| release/v26.9.10 | 2 | 09-10 | NOT-FF | PARKED (same ledger) |

### beam4pm (main)
0 unmerged branches. Clean.

### wasm4pm (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| docs/errc-audit-run4 | 11 unpushed | 08-20 | NOT-FF | PARKED (docs/jira/v26.9.19/003-unpushed note + 002 ledger) |
| docs/w4p-cards2-v10-agent-card | 1 | 7c7af9f4a 10-08 | NOT-FF | ORPHAN (grep docs/jira + docs/sjira: no cite) |
| feat/ex4pm-wasm4pm-bindings-phase2 | 4 | 09-12 | NOT-FF | PARKED (docs/jira/v26.9.19/008 note) |
| feat/wire-planner-into-cli | 12 | 08-21 | NOT-FF | PARKED (docs/jira/v26.9.19/009 note) |
| fix-etconformance-precision-feature-gate | 1 | 08-21 | NOT-FF | PARKED (docs/jira/v26.9.17/cleanup-merge-plan.md) |
| register-planner-mcp-json | 1 | 08-25 | NOT-FF | PARKED (docs/jira/v26.9.19/005 note) |
| heads/preserve/… (2), worktree-wf_* (1) | 1 | 09-25/09-17 | NOT-FF | namespace-parked |

### ash_pplan (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| modep/preserve-20260926-foreign-merge-ash_pplan | 1 | 09-26 | NOT-FF | namespace-parked |

### ash_graphlaw (main)
0 unmerged branches. Clean. main 0/0.

### zcode-cli (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| docs/doc-hdit-ts-scaffold | 2 | da6cb4c 10-08 | NOT-FF | LPM (docs/sjira/v26.10.8/TS-WITNESS-RECEIPT.md) |
| feat/aloop-l3-execution-provider-parity | 4 | 09-25 | NOT-FF | ORPHAN (grep docs/sjira v26.9.21–v26.10.8: no cite) |
| fix/v26926-preview-publish-typed-skip | 7 | 0de2f9d 10-08 | NOT-FF | LPM (docs/sjira/v26.10.8/CAMPAIGN-RECEIPT.md) |
| modep/preserve-260926-docs (5), v26926/zcode-ggen-toolchain-composite (1) | | 09-26 | NOT-FF | namespace-parked / ORPHAN (composite: no cite) |

### ferroplan (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| law/FERROPLAN-26922-09 | 3 | 09-22 | NOT-FF | ORPHAN (grep docs/sjira/v26.10.8: no cite; name matches composition C01 work order FERROPLAN-26922-09 — needs receipt or new R-item) |
| preserve/v26922/* (14 incl. preserve/v26.9.22/main-checkout) | 1–70 | 07-31…09-22 | NOT-FF | namespace-parked |
| modep/preserve-20260926-ferroplan-stale-wasi | 1 | 09-26 | NOT-FF | namespace-parked |

### castle (main)
0 unmerged branches. Clean.

### gymact (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| modep/preserve-20260926T1725Z-gymact | 1 | 09-26 | NOT-FF | namespace-parked |
| preserve/v26.9.22/* (13) | 1–2 | 09-22/08-14 | NOT-FF | namespace-parked |

### autofde-lab (master)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| lane/doc-hdit-scaffold | 3 | fbd6eab4 10-08 | FF-able | LPM (docs/a2a-serving-witness.md) |
| chore/registry-pin-e90928d | 1 | 09-18 | NOT-FF | PARKED (docs/jira/v26.9.19/003 ledger) |
| crown-2/autofde-compose (3), crown-2/orthogonal-ws (15), feat/gall-swf-v26.9.18 (1) | | 09-03/09-18 | NOT-FF | PARKED (docs/jira/v26.9.19/003 ledger) |
| feat/aloop-bench-suite-lane6 | 2 | 09-25 | NOT-FF | ORPHAN (grep docs/a2a-serving-witness.md + jira ledgers: no cite) |
| preserve/v26.9.22/* (16), worktree-* (15) | 1–16 | 07-06…09-22 | NOT-FF | namespace-parked |
| **master itself** | **19/0 vs origin** | — | FF-able | **ORPHAN (unpushed main line)** — grep docs/jira + docs/sjira: no push receipt. Typed disposition: push (fast-forward, no force). |

### graphlaw (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| docs/doc-hdit-scaffold-gl | 2 | e1059f1 10-08 | FF-able | ORPHAN (no cite in docs/sjira/v26.10.8; live campaign branch — checkout HEAD) |
| **main itself** | **7/0 vs origin** | — | FF-able | ORPHAN (unpushed main line) — disposition: push (fast-forward) |

### ash_a2a (main)
| branch | ahead | last | FF | class | citation |
|---|---|---|---|---|---|
| backup/pre-rewrite-f2b38584 | 26 | f2b38584 10-05 | NOT-FF | namespace-parked (backup namespace) |
| feat/ci-hygiene | 2 | fe222dd6 10-05 | NOT-FF | ORPHAN (grep docs/sjira v26.10.3/4/8: no cite) |

### ash_affidavit (main)
0 unmerged branches. Clean.

### frozen-duckdb (master)
| branch | ahead | unmerged | class | citation |
|---|---|---|---|---|
| docs/doc-hdit-scaffold | 1 | 7063b9d 10-09 | NOT-FF | LPM (docs/sjira/v26.10.8/DOC-HDIT-CERTIFY-RECEIPT.md) |
| preserve/v26.9.22/stash-0 | 2 | 09-21 | NOT-FF | namespace-parked |
| release/v26.9.22 | 3/25 | 09-23 | NOT-FF | PARKED (docs/sjira/v26.9.22/jira/FDDB-26922-01/05.md) — diverged, needs merge not FF |

## Orphan summary and typed dispositions

17 orphan-class items. Suggested disposition per item (push / merge /
park-with-receipt):

1. **ggen: 74 orphan branches** (worktree-agent/wf, agent/* gone-upstream,
   retrofit/, feat/l5-condition-*, docs+fix release-gate, packs/, story/,
   release/v26.8.9, …) → new R-item: bulk park-with-receipt ledger
   (ggen/docs/sjira/v26.10.9/RESIDUAL-BRANCHES-2.md) or bulk delete after
   owner sign-off. None FF-able; none FF-safe. Largest-content items
   release/v26.8.9 (51c) and agent/gbb-* (103c) — inspect before delete.
2. **ggen-marketplace: eco-saga-compensate-upstream (1c),
   errc-promote-engine-compat-gates (2c), errc-promote-workway-pack-and-ashext-template (3c),
   archive/wip/… (1c)** → park-with-receipt (small docs/errc lanes; verify
   content then merge or delete).
3. **affidavit: feat/sj-aligned-record (1c, FF-able)** → push + merge (small,
   coherent). `fix/clippy-crypto-trust` is the live checkout HEAD (in-flight
   lane); worktree-agent-a54199ede365de59e → delete (2026-07 worktree residue).
4. **bcinr: worktree namespaces (25)** → delete (2026-07-16 residue, 1–2
   commits each, worktree namespace).
5. **wasm4pm: docs/w4p-cards2-v10-agent-card (1c)** → park-with-receipt.
6. **zcode-cli: feat/aloop-l3-execution-provider-parity (4c)** → park-with-
   receipt; v26926/zcode-ggen-toolchain-composite (1c) → park-with-receipt.
7. **ferroplan: law/FERROPLAN-26922-09 (3c)** → park-with-receipt or new R-item
   (name matches catalog work order FERROPLAN-26922-09);
   preserve/v26922/* (14) → namespace-parked.
8. **autofde-lab: feat/aloop-bbench-suite-lane6 (2c)** → park-with-receipt;
   **master 19/0 unpushed** → **push (fast-forward)** — highest-value orphan:
   the main line itself is unpushed.
9. **graphlaw: docs/doc-hdit-scaffold-gl** is the live campaign branch (in
   flight); **main 7/0 unpushed** → **push (fast-forward)**.
10. **ash_a2a: feat/ci-hygiene (2c)** → park-with-receipt.

## Receipt

- Repos censused: 20/20, real git output (`git fetch origin -q` exit 0 per repo
  with a configured origin; all `branch --no-merged` / merge-base tests real).
- Classification: 34 receipt-cited, 17 orphan-class items (grouped counts
  above), remainder namespace-parked or in-flight campaign branches.
- Orphan count (grouped items): 10 groups / 17 top-level entries.
- Commit SHA: TBD (filled at commit time in the commit message; this file is
  the census artifact itself).
- Unpushed-main findings: ggen main 38/0 (receipted BLOCKED, see ggen
  RESIDUAL-BRANCHES.md), autofde-lab master 19/0 (push), graphlaw main 7/0
  (push), ggen-marketplace main 0/126 behind (this branch is the carrier).
