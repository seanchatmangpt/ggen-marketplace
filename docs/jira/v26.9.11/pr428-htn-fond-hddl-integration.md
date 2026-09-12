# Merge PR #428: HTN/FOND/HDDL integration

## Summary

Merge commit for pull request #428
(`seanchatmangpt/integration/htn-fond-hddl` into the target branch), carrying
in `fix/engine-template-force-flag`. The merge adds a force-flag line to five
`beam4pm-process-model-pack` engine template files.

## Status

Done — already merged/committed (commit `8bbb2999c`).

## Commits

- `8bbb2999c` Merge pull request #428 from seanchatmangpt/integration/htn-fond-hddl

## Changes

Per `git show --stat 8bbb2999c`, the merge changed 5 files, each with a single
line insertion (5 insertions total, 0 deletions):

- `packs/beam4pm-process-model-pack/templates/beam4pm_engine.erl.tmpl` (+1)
- `packs/beam4pm-process-model-pack/templates/beam4pm_engine.ex.tmpl` (+1)
- `packs/beam4pm-process-model-pack/templates/beam4pm_engine.gleam.tmpl` (+1)
- `packs/beam4pm-process-model-pack/templates/beam4pm_engine_dispatch_gate_test.exs.tmpl` (+1)
- `packs/beam4pm-process-model-pack/templates/beam4pm_engine_ops.tsv.tmpl` (+1)

Commit message states this merge integrates `fix/engine-template-force-flag`
into the `integration/htn-fond-hddl` line.

## Verification

None stated — the commit message contains no test/lint/CI evidence.

## Related

- PR #428
- Branch: `integration/htn-fond-hddl`
- Merged branch: `fix/engine-template-force-flag`
