# ggen-marketplace: commit or clean uncommitted changes

- Standing: OPEN
- Created: 2026-09-19 (v26.9.19 gh survey wave)
- Source: working tree dirty at survey time
- Evidence: `git status --porcelain` → 2 path(s) (tracked-modified: 0, untracked: 2); sample: ?? docs/rfc/;?? packages/marketplace-cli/.ggen_igniter/;

## Work to complete
- For the 2 untracked path(s): add intentional files to git and commit; gitignore or delete build artifacts/temp files.
- Note: this survey's ticket files under docs/jira/v26.9.19/ are intentionally uncommitted; include or exclude them deliberately in the commit plan.

## Acceptance
- `git status --porcelain` is clean (except items deliberately deferred and recorded here).

## History
- 2026-09-19 | OPEN | survey found dirty tree | 2 paths (T0/U2) | commit/clean pending
