# Adversarial Review Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a repo-scoped `/adversarial-review` skill that reviews a diff, a pack,
or the whole marketplace through four named-expert-methodology lenses, adversarially
verifies each finding, and reports a structured findings list.

**Architecture:** A `SKILL.md` (target resolution + invocation instructions) paired
with a `workflow.js` (the actual four-lens parallel review, adversarial verification,
and synthesis, run via the `Workflow` tool). No new runtime code — this is a
prompt/orchestration artifact.

**Tech Stack:** Claude Code skill format (frontmatter + markdown instructions), the
`Workflow` tool's JS scripting surface (`agent()`, `pipeline()`, `parallel()`).

**Spec:** `docs/superpowers/specs/2026-08-15-adversarial-review-design.md`

## Global Constraints

- Lens personas are framed as "review through `<person>`'s documented methodology" —
  never as impersonation, never inventing quotes attributed to the named person.
- Always the deep/adversarial tier — no lightweight mode (per spec's explicit
  non-goal, reaffirmed during design: "ultracode everything").
- Every reported finding must cite `file:line` and a concrete failure scenario;
  findings without both are dropped in synthesis, not reported.
- On-demand invocation only — no CI/PR-gating in this plan (spec non-goal).
- Fixed four-lens roster (RDF/SPARQL correctness, TDD rigor, formal correctness,
  engineering pragmatism) — no generic plug-in lens system.

---

## Task 1: Create the workflow script (four-lens review + adversarial verify + synthesis)

**Files:**
- Create: `.claude/skills/adversarial-review/workflow.js`

**Interfaces:**
- Consumes: `args` — `{ targetDescription: string, targetType: "diff" | "pack" | "all" }`,
  passed in by `SKILL.md` (Task 2) via the `Workflow` tool's `args` parameter.
- Produces: workflow return value — an array of finding objects:
  `{ file, line, lens, summary, failureScenario, verdict }` where `verdict` is
  `"CONFIRMED"` or `"PLAUSIBLE"`. `SKILL.md` reads this to render the final report.

- [ ] **Step 1: Write the workflow script**

```javascript
export const meta = {
  name: 'adversarial-review',
  description: 'Four-lens adversarial review (RDF correctness, TDD rigor, formal correctness, pragmatism) with independent verification per finding',
  phases: [
    { title: 'Review', detail: 'one agent per lens' },
    { title: 'Verify', detail: 'two independent skeptics per finding' },
  ],
}

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'number' },
          summary: { type: 'string' },
          failureScenario: { type: 'string' },
        },
        required: ['file', 'summary', 'failureScenario'],
      },
    },
  },
  required: ['findings'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

const LENSES = [
  {
    key: 'rdf-correctness',
    label: 'Semantic web / RDF correctness',
    prompt: (target) => `Review ${target} through the lens of Tim Berners-Lee's Linked ` +
      `Data principles and SPARQL query-correctness discipline. You are not impersonating ` +
      `him -- apply his documented methodology as a rigor standard. For every SPARQL query ` +
      `in a gate or template: does it actually bind what the template consumes downstream? ` +
      `For every ontology individual/class: does it follow RDF/OWL conventions (no ` +
      `literal-typed subjects, no undeclared predicates used as if declared)? For every ` +
      `template's projected output: does it semantically match the ontology facts it claims ` +
      `to derive from, or does it silently diverge? Report ONLY findings with a real file:line ` +
      `citation and a concrete failure scenario (specific input/state -> wrong output). Do not ` +
      `report style preferences or anything you cannot point to in the actual files.`,
  },
  {
    key: 'tdd-rigor',
    label: 'Testing discipline / TDD rigor',
    prompt: (target) => `Review ${target} through the lens of Kent Beck's Chicago-school ` +
      `classicist testing discipline. You are not impersonating him -- apply his documented ` +
      `methodology as a rigor standard. For every test: does it use real collaborators or ` +
      `does it mock something this codebase owns or could run in-process/locally? Are ` +
      `assertions state-based (real returned/persisted values) or interaction-based ("was X ` +
      `called")? For every claim in a description/README that something is "verified" or ` +
      `"tested": is there an actual citable passing run, or is it asserted without evidence? ` +
      `Report ONLY findings with a real file:line citation and a concrete failure scenario. Do ` +
      `not report style preferences.`,
  },
  {
    key: 'formal-correctness',
    label: 'Formal correctness / interface design',
    prompt: (target) => `Review ${target} through the lens of Barbara Liskov's ` +
      `substitutability principle and strict-schema discipline. You are not impersonating her ` +
      `-- apply her documented methodology as a rigor standard. For every manifest/schema file ` +
      `(pack.toml, ggen.toml, qualification.toml): does every field actually validate against ` +
      `the real parser/tool this repo pins (not just look syntactically plausible on a read-` +
      `through)? Are contracts checked exhaustively, or does the review assume validity from ` +
      `visual inspection alone? Flag any field, table, or key that isn't demonstrably accepted ` +
      `by the real tool. Report ONLY findings with a real file:line citation and a concrete ` +
      `failure scenario (what breaks, and how you'd prove it breaks). Do not report style ` +
      `preferences.`,
  },
  {
    key: 'pragmatism',
    label: 'Software engineering pragmatism',
    prompt: (target) => `Review ${target} through the lens of YAGNI/simplicity discipline and ` +
      `no-overclaiming rigor. For every abstraction, config option, or generalization: is it ` +
      `actually used, or speculative? For every claim of correctness/completeness/verification: ` +
      `is it backed by a citable run, or asserted? Would a simpler design serve the same real, ` +
      `currently-existing requirement? Report ONLY findings with a real file:line citation and ` +
      `a concrete failure scenario or concrete cost (e.g. "this table is read nowhere, dead ` +
      `code"). Do not report generic advice.`,
  },
]

function refutePrompt(finding) {
  return `Try to REFUTE this finding. Read the cited file yourself and check it against the ` +
    `actual content -- do not trust the finding's citation blindly. Default to refuted=true if ` +
    `you cannot confirm the cited file:line actually shows what the finding claims, or if the ` +
    `failure scenario does not actually follow from the code as written.\n\n` +
    `File: ${finding.file}${finding.line ? ':' + finding.line : ''}\n` +
    `Summary: ${finding.summary}\n` +
    `Failure scenario: ${finding.failureScenario}`
}

phase('Review')
const target = args.targetDescription
const lensResults = await pipeline(
  LENSES,
  (lens) => agent(lens.prompt(target), {
    label: `review:${lens.key}`,
    phase: 'Review',
    schema: FINDINGS_SCHEMA,
  }),
  (result, lens) => (result?.findings ?? []).map((f) => ({ ...f, lens: lens.label }))
)

const allFindings = lensResults.flat()
log(`${allFindings.length} raw findings across ${LENSES.length} lenses`)

phase('Verify')
const verified = await parallel(
  allFindings.map((finding) => async () => {
    const votes = await parallel(
      Array.from({ length: 2 }, () => () =>
        agent(refutePrompt(finding), { phase: 'Verify', schema: VERDICT_SCHEMA })
      )
    )
    const refutations = votes.filter(Boolean).filter((v) => v.refuted).length
    const survived = refutations < 2
    return survived ? { ...finding, verdict: refutations === 0 ? 'CONFIRMED' : 'PLAUSIBLE' } : null
  })
)

const confirmed = verified.filter(Boolean)
log(`${confirmed.length}/${allFindings.length} findings survived adversarial verification`)

// Dedupe: same file + overlapping summary text across lenses -> keep the first (sharper
// framing tends to come from the more specific lens, which runs earlier in LENSES order).
const seen = new Set()
const deduped = []
for (const f of confirmed) {
  const key = `${f.file}:${f.line ?? ''}:${f.summary.slice(0, 60)}`
  if (seen.has(key)) continue
  seen.add(key)
  deduped.push(f)
}

return deduped
```

- [ ] **Step 2: Verify the script is syntactically valid**

The `Workflow` tool parses `meta` as a pure literal and validates script shape at
invocation time — there is no standalone syntax-check step available before that. Skip
directly to running it for real once Task 2 (the invoking `SKILL.md`) exists, in Task 3.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/adversarial-review/workflow.js
git commit -m "feat(adversarial-review): four-lens review + adversarial-verify workflow script"
```

---

## Task 2: Create the skill definition (target resolution + invocation)

**Files:**
- Create: `.claude/skills/adversarial-review/SKILL.md`

**Interfaces:**
- Consumes: `.claude/skills/adversarial-review/workflow.js` (Task 1) via
  `Workflow({ scriptPath: ".claude/skills/adversarial-review/workflow.js", args: {...} })`.
- Produces: nothing further downstream — this is the user-facing entry point.

- [ ] **Step 1: Write the skill file**

```markdown
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
following this repo's existing branch-per-fix + PR + CI-verify convention (see this
session's `fix/resync-stale-migrated-packs` and `chore/gitignore-pycache` branches for
the pattern: branch off `origin/main`, commit, push, open a PR, wait for CI, merge).
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/adversarial-review/SKILL.md
git commit -m "feat(adversarial-review): add skill entry point (target resolution + invocation)"
```

---

## Task 3: Acceptance check against a known defect

**Files:**
- None created — this task exercises Tasks 1–2 against real repo history.

**Interfaces:**
- Consumes: the skill from Tasks 1–2.
- Produces: a pass/fail acceptance result, not a new file.

- [ ] **Step 1: Locate the pre-fix commit**

```bash
git log --oneline --all -- packs/mmdio-pack/pack.toml | grep -i "restored the \[semantic_crown\]"
```

Expected: finds `05ea78f` (the commit that introduced the invalid `[semantic_crown]`
table, before it was corrected in `ee1c6cf`).

- [ ] **Step 2: Check out that commit's version of the pack into a scratch worktree**

```bash
git worktree add /tmp/adversarial-review-acceptance-check 05ea78f
```

- [ ] **Step 3: Invoke the skill against that pack**

Run `/adversarial-review /tmp/adversarial-review-acceptance-check/packs/mmdio-pack`
(or the equivalent direct invocation per Task 2's target-resolution logic, pointed at
the scratch worktree's copy of the pack).

Expected: the formal-correctness lens (Barbara Liskov / strict-schema) reports a
CONFIRMED finding on `packs/mmdio-pack/pack.toml` citing the `[semantic_crown]` table
as unvalidated against the real pinned parser.

- [ ] **Step 4: If the defect is NOT found, sharpen the lens prompt**

Edit `.claude/skills/adversarial-review/workflow.js`'s `formal-correctness` lens
prompt (Task 1) to be more explicit that "syntactically plausible" TOML is not
sufficient — the lens must reason about whether each table is actually consumed by
the pinned tool's schema, not just whether the file parses. Re-run Step 3 until the
defect is found.

- [ ] **Step 5: Clean up the scratch worktree**

```bash
git worktree remove /tmp/adversarial-review-acceptance-check
```

- [ ] **Step 6: Commit any lens-prompt fixes from Step 4**

```bash
git add .claude/skills/adversarial-review/workflow.js
git commit -m "fix(adversarial-review): sharpen formal-correctness lens per acceptance check"
```

(Skip this step if Step 3 passed on the first try — nothing to commit.)
