# Archived branch-pinned workflows

56 workflows moved here from `.github/workflows/` by the CI 80/20 pass. Each one triggered only on
`pull_request` and gated every job on `github.head_ref` (or `github.event.pull_request.head.ref`)
equalling one historic round branch, so on every other pull request it produced a skipped run and no
signal. In a 1000-run window, 886 runs were skipped and only 5 workflows produced a failure.

GitHub only executes files under `.github/workflows/`, so these are inert here. History is preserved
(`git mv`). To revive one for a reopened branch: `git mv archive/workflows/<file> .github/workflows/`.

Selection rule (mechanical, see `docs/reference/workflow-map.md` and `scripts/workflow_census.py`):
trigger set is exactly `pull_request`, every job has an `if:` on the head ref, and no open pull
request head matched any pinned branch at archive time.

## See Also

[Workflow map](../../docs/reference/workflow-map.md)
