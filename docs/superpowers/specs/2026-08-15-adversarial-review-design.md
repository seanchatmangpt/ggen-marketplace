# Adversarial Review by Named-Expert Lenses — Design

## Purpose

A reusable, repo-scoped review skill (`/adversarial-review`) that audits marketplace
content — pack diffs, whole packs, or the entire corpus — through four rigor lenses,
each anchored to a real, publicly documented methodology. It exists because this
session found real defects (`ggen-release-pack`/`mmdio-pack` content drift, an invalid
`[semantic_crown]` TOML table that only the real pinned `ggen` binary caught) that a
single-pass, single-perspective review missed. The goal is to make that kind of
adversarial, multi-angle scrutiny repeatable on demand rather than ad hoc.

## Persona framing (must be preserved in implementation)

Lenses are framed as **"review through `<person>`'s documented methodology,"** never
as impersonation. A lens supplies a rigor standard and a fixed list of concrete
questions — not a voice, an opinion attributed to the named person, or invented
quotes. This is a load-bearing constraint, not a nicety: it keeps the skill's output
grounded in checkable facts about the code, and avoids misattributing views to real
people.

## The four lenses

| Lens | Framework anchor | Concrete questions |
|---|---|---|
| Semantic web / RDF correctness | Tim Berners-Lee's Linked Data principles + SPARQL query-correctness discipline | Does every SPARQL query in a gate/template actually bind what the template consumes? Do ontology individuals/classes follow RDF/OWL conventions (no literal-typed subjects, no undeclared predicates)? Does the projected artifact (template output) semantically match the ontology facts it claims to derive from? |
| Testing discipline / TDD rigor | Kent Beck's Chicago-school classicist testing | Real collaborators or mocks? State-based or interaction-based assertions? Does a claimed "verified" artifact cite an actual passing run, not just an assertion? |
| Formal correctness / interface design | Barbara Liskov's substitutability + strict-schema discipline | Does every manifest/schema field actually validate against the real parser (the pinned `ggen` binary), not just look syntactically plausible? Are contracts (`pack.toml`, `ggen.toml`) exhaustively checked against the real tool, not assumed from reading the file? |
| Software engineering pragmatism | YAGNI/simplicity, no-overclaiming discipline | Is there unused complexity or speculative generality? Is any claim unsupported by a citable run? Would a simpler design serve the same real requirement? |

The lens roster is fixed at these four for this repo (RDF/SPARQL ontologies, SHACL,
Rust tooling, Tera templates, TOML manifests, TDD-disciplined testing) — it is not a
generic plug-in system. Extending it is a future decision, not built speculatively now
(pragmatism lens applies to the skill's own design).

## Execution flow

Single path, always the deep/adversarial tier — no lightweight mode:

1. **Target resolution.** No argument → current branch's diff against its merge-base
   with the base branch (mirrors `/code-review`'s no-arg behavior). A path argument
   (`packs/<name>`) → that pack's full contents. `--all` → every pack in `packs/`; this
   path warns about token cost before starting (many packs × 4 lenses × verification
   is a real spend) and requires explicit confirmation.
2. **Parallel lens review.** Four `agent()` calls in parallel (one per lens from the
   table above), each given: the resolved target, that lens's concrete question list,
   and instruction to cite `file:line` and a concrete failure scenario for every
   finding — no vague "could be improved" findings.
3. **Adversarial verification.** Each finding gets checked by 2 independent skeptic
   agents instructed to try to refute it. Majority-refute (2/2 or ambiguous-defaults-
   to-refuted) drops the finding. This mirrors the "adversarial verify" pattern already
   used by this environment's `/code-review` and the ERRC reconciliation done earlier
   this session.
4. **Synthesis.** Dedupe overlapping findings across lenses (the same defect can surface
   from two angles — e.g. a bad SPARQL query is both an RDF-correctness finding and a
   pragmatism finding); keep the sharper framing, drop the duplicate.
5. **Report.** Structured list, most-severe first: file, line, lens/category, one-sentence
   defect summary, concrete failure scenario, verdict (CONFIRMED/PLAUSIBLE). No prose
   padding, no unearned praise, no summary paragraph restating the table.

Implementation mechanics: a `Workflow` script (`workflow.js` alongside the skill) does
steps 2–4 via `pipeline()`/`parallel()`, matching this repo's existing workflow
conventions (see this session's ERRC reconciliation workflow for the pattern). The
skill's `SKILL.md` handles target resolution (step 1) and invokes the workflow.

## File structure

- `.claude/skills/adversarial-review/SKILL.md` — command definition, target resolution,
  invokes the workflow. Repo-scoped (not `~/.claude`) because the lens roster is
  specific to this marketplace's actual content (RDF/SPARQL/Rust/TDD) — it would not
  make sense unmodified in an unrelated repo.
- `.claude/skills/adversarial-review/workflow.js` — the four-lens parallel review +
  adversarial verify + synthesis, as a `Workflow` script per the tool's script format
  (`export const meta = {...}` header, `pipeline()`/`parallel()`/`agent()` calls).

## Non-goals

- No CI/PR-gating integration (explicitly deferred — on-demand only, per this design's
  approval).
- No generic/pluggable lens system — four fixed lenses matched to this repo's content.
- No lightweight/fast tier — every invocation runs the full adversarial-verify path,
  per explicit direction during design (`ultracode everything`).

## Testing

The skill itself is a prompt/workflow artifact, not code with a unit-test surface. Its
correctness is verified by running it against a known-defect target and confirming it
finds the defect: re-run `/adversarial-review packs/mmdio-pack` against the pre-fix
commit (`85d6b95`, before the `[semantic_crown]` fix) as an acceptance check — the
formal-correctness lens should surface the invalid-table defect that this session only
caught via CI. If it doesn't, the lens's question list needs sharpening before the
skill is considered done.
