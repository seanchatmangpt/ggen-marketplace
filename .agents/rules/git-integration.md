# Git Integration and Concurrency Rules

## 1. Concurrency and Mutation Locking

Never allow multiple implementation agents to mutate the same non-isolated working tree concurrently:
- **Same mutable repository/tree**: SERIALIZE.
- **Different repositories or isolated worktrees**: MAY PARALLELIZE.
- Maximum ecosystem concurrency: **5 agents**.

## 2. Repository Authority Discovery

Do not infer repository authority from branch names:
- Always discover the remote default branch and actual commit ancestry.
- Do not assume `main` (some repositories like `ash_r2rml` use `dev`).
- Inspect `git log` and `git status` directly.
- An open PR does not mean unmerged semantics; verify content deltas directly.

## 3. Branch Discipline and Clean Merges

- Never commit directly to default branches (`main`/`dev`).
- Always work on a dedicated purpose branch (e.g. `feat/`, `fix/`, `docs/`).
- Use atomic, intentional commits with clear rationale.
- Non-force push to origin; open draft PR.
- **Documentation Preservation**: A merge is not complete until code AND repository context are checked. Never silently drop contract documentation during merges.
