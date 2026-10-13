# Home-Directory Project Survey — 2026-10-13 (waves HS1–HS14)

162 git repositories under `~/` surveyed read-only by 14 Explore lanes
(+ HS14's straggler sweep: `cargo-cicd` [most recently touched repo on the
machine, 2026-10-10], `expo-supabase-ai-template`, and 3 timestamped backup
dirs). Per-repo tables live in the wave transcript; this receipt records the
aggregate.

## Standing distribution (approx.)
- **Active (commit ≤ 2 wks)**: ~40 — ggen (flagship, v26.10.11), strata
  (ground-truth runtime, most active, all components ALIVE per its own
  standing table), graphlaw, chicago-tdd-tools (254 commits unpushed),
  affidavit, cargo-cicd, dfcm-autonomous, praxis, process-intelligence,
  mfact, mfw, xaas, zcode-cli, wasm4pm (72 unpushed), osx-clnr,
  scikit-decide-wasm, unrdf (feature branch), open-ontologies (307 ahead).
- **Stale (1–13 mo)**: ~75 — incl. cns (behind 265), doctester (behind 392),
  clawdbot (behind 91,720 — frozen fork), full-stack-rubric/fgn (dead).
- **Backup/scaffold/never-committed**: ~15 — clnrm-backup-*, cre-pre-reset-*,
  universe-chain (0 commits), nuxt-layer/nuxt-ui-pro-landing (0 commits),
  clawd (docs-only).

## Hygiene flags (cross-repo patterns)
1. **Unpushed backlogs**: chicago-tdd-tools (254), wasm4pm (72),
   open-ontologies (307/50 diverged), lsp-types-max (13), un-test-utils (75).
2. **Huge dirty trees**: zoela (597), ai (1,328), A2A (157), erlmcp (622,
   8-mo-old commit), speckit-ralph (305), tower-lsp-composition (230).
3. **Recurring `.claude/.gemini` agent-file deletion churn** across many
   repos — looks like one unfinished harness-cleanup sweep.
4. **Detached HEAD**: oxigraph-local. **Orphaned upstream**: dtr.
5. **Prior blockchain-adjacent capital**: `unibit` (bit-native L1 execution
   substrate) + `universe-chain` (chain crate over unibit-kernel) — evaluate
   for reuse in STRATA-BLOCKCHAIN-ROADMAP S5/S8 before greenfield.

## Freshness highlights
- Most recent: cargo-cicd (10-10), chicago-tdd-tools + affidavit (10-12),
  strata + graphlaw + scikit-decide-wasm (10-12), dfcm-autonomous (today).
- Coordinated same-day work clusters: xaas + zcode-cli (R132);
  ggen + ggen-ecosystem (v26.10.11).

## Method
14 Explore lanes (HS1–HS14), disjoint repo batches, read-only git
(status/log/branch only), per-repo one-line purpose + language + git state +
standing guess. Full per-repo tables in the session transcript; this file is
the durable aggregate. No repo was modified.
