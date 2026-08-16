---
name: adversarial-review
description: >-
  Adversarial multi-lens review of this marketplace's packs or diffs, through four
  named-expert-methodology lenses (RDF/SPARQL correctness, TDD rigor, formal
  correctness, engineering pragmatism), each finding independently verified before
  reporting. Use for /adversarial-review, or when asked to review packs/diffs
  adversarially, by "the luminaries of the fields", or with named-expert rigor.
---

# Adversarial Review

Runs four independent review lenses in parallel over a target, adversarially verifies
every finding (two independent skeptics must fail to refute it), and reports only what
survives. Always runs the full adversarial-verify tier -- there is no lightweight mode.

## Resolve the target

Parse the invocation argument:

- **No argument** -- target is the current branch's diff against its merge-base with
  the base branch. Run:
  ```bash
  git merge-base HEAD origin/main
  git diff $(git merge-base HEAD origin/main)...HEAD
  ```
  Pass the diff text itself (or, if very large, a summary of changed files plus the
  full diff of each) as `targetDescription`, with `targetType: "diff"`.
- **A path argument** (e.g. `packs/mmdio-pack`) -- target is that pack's full contents.
  Set `targetDescription` to the resolved absolute path, `targetType: "pack"`.
- **`--all`** -- target is every directory under `packs/`. This is the expensive path:
  before starting, tell the user how many packs will be reviewed (four lens agents +
  up to two verify agents per finding, per pack) and ask them to confirm before
  proceeding. Set `targetDescription` to `"every pack under packs/"`,
  `targetType: "all"`.

## Run the review

Invoke the workflow:

```
Workflow({
  scriptPath: ".claude/skills/adversarial-review/workflow.js",
  args: { targetDescription: "<resolved above>", targetType: "<resolved above>" }
})
```

For `targetType: "all"`, run the workflow once per pack directory (loop over
`packs/*`) rather than passing the whole corpus as one target -- this keeps each
lens agent's context focused on one pack instead of diluting it across 115.

## Report

The workflow returns an array of `{ file, line, lens, summary, failureScenario,
verdict }`. Render it as a table, most-severe first (CONFIRMED before PLAUSIBLE), one
row per finding. If the array is empty, say so plainly -- do not pad with unearned
praise or a summary paragraph restating that nothing was found.

If invoked with `--fix`, apply each CONFIRMED finding's fix directly after reporting,
following this repo's existing branch-per-fix + PR + CI-verify convention: branch off
`origin/main`, commit, push, open a PR, wait for CI, merge. Before pushing, verify with
this repo's own qualification pipeline per its root `CLAUDE.md`: `python3
scripts/marketplace.py validate`, `python3 scripts/marketplace.py catalog` (run twice,
must be byte-identical), then `python3 scripts/marketplace.py fingerprint`.
