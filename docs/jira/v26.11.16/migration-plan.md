# ggen-marketplace migration plan v26.11.16

Standing: UNVERIFIED

## Identity
- path: /Users/sac/ggen-marketplace
- remote: https://github.com/seanchatmangpt/ggen-marketplace
- branch@sha: main@4bc81db7c (tracks origin/main)
- last commit: 2026-11-14; commits: 14507; size: 9400 MB
- languages/build: Python (pyproject.toml, pyrightconfig), ggen packs (ggen.toml, 352 packs),
  mdbook (book.toml), ci/courts
- nested repos: none (no worktrees registered)

## Observed state
- dirty: 66; untracked: 48. Grouped: `packs/` 58, `packages/` 26 (incl. ` D
  packages/pm4pytest/README.md`), `scripts/` 5, `ci/` 2 (`courts.json`, shim-azure-terraform.sh),
  `docs/` 2, root receipts `_CDBR_*`, `_CHICAGO_*`, `_GGEN_*`, `_PQC_*`, `.gitignore`
- ahead/behind: 0/0; stash: 0
- unpushed local branches: 26 (`archive/wip/...20260924`, `blake3-digest-keys`,
  `chore/ci-pareto`, `eco-saga-*`, `errc-promote-*` x2, `exp/invariant-gate-pack`, `feat/*` x6,
  `fix/evolvable-gates-v2`, `graphlaw-full-representation`, `manufacture/v26.9.30-qri-profile`,
  `modep/preserve-*` x2, `mp23/*` x4, `release-prep/v26.9.22`, `release/v26.9.23-int`,
  `strata-hardening-wave`, `v26926/...`)
- bulk: `.git` 2.8 GB, `ontologies/` 2.7 GB, `packs/` 1.9 GB, `vendors/` 852 MB, `bin/` 643 MB,
  `tools/` 341 MB; `.venv` 76 KB (empty)
- submodules: none

## What it is
Canonical corpus of reusable ggen packs (352) plus the marketplace qualification/documentation
plane; AGENTS.md is the authoritative doctrine.

## Classification
ACTIVE (census agrees; v26.11.14 release two days before census).

## Migration risk
- 66 dirty + 48 untracked files (packs/packages WIP post-v26.11.14)
- 26 local-only branches, several explicitly named `preserve`/`archive`/`wip`
- `vendors/`, `bin/`, `tools/`, `ontologies/` may contain untracked or ignored large data
Rate: HIGH

## Recommended action
COMMIT-PUSH
1. `cd /Users/sac/ggen-marketplace && git status --porcelain | head -120` — triage WIP.
2. `git add -A && git commit -m "wip: post-v26.11.14 packs/packages state (pre-migration)"`
3. `git push origin main`
4. `git push origin --all` — pushes all 26 local branches (DECISION: prune `modep/preserve-*`,
   `mp23/*`, `archive/wip/*` afterwards on GitHub).
5. `git status --ignored --porcelain | grep '^!!' | head -40` — DECISION: which of
   `ontologies/`, `vendors/`, `bin/`, `tools/` are ignored data that must RSYNC-COPY.
6. `rm -rf .venv` (empty). Do not copy `.git` (2.8 GB) — reclone.

## First commands on the new machine
`git clone https://github.com/seanchatmangpt/ggen-marketplace && cd ggen-marketplace && uv sync && uv run pytest -q`

## See Also
- ../v26.9.30/
- /Users/sac/docs/jira/v26.11.16/README.md
