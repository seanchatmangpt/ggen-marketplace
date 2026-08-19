# 03 Ticket Consolidation Court Methodology

Standing: PARTIAL_ALIVE. This ticket **gates every family consolidation ticket in this milestone** (05 onward). No pack may be physically merged or deleted until the methodology defined here exists and has been run against the specific family in question.

## Quick reference

- Deliverable: a repeatable, machine-generated procedure that turns a proposed pack family (e.g. TCPS, wasm4pm) from an `INFERRED` grouping into an `ADMITTED` one, or refutes the grouping.
- Output artifact per family: a **family-consolidation proof** — a structured record, not prose, that a family ticket can cite as its acceptance evidence.
- This ticket produces the *court*, not a verdict on any specific family. Family tickets (05+) each still need their own run of this court before physical merge.

## Why this ticket exists

The source audit's own closing requirement, quoted verbatim from `00-PACK-PORTFOLIO-MATURITY-AUDIT.md`'s standing statement (confirmed present word-for-word in that file): "run pairwise graph/query/template correspondence on each proposed family and turn this matrix into a machine-generated pack-consolidation court" before any pack is physically merged or deleted. Every family grouping in the audit is self-labeled `INFERRED`/`PARTIAL_ALIVE` — this ticket is what promotes a grouping to `ADMITTED`.

## What evidence a family-consolidation proof requires

For a proposed family of N member packs claiming to share one kernel ontology, the proof must contain:

1. **Pairwise ontology correspondence.** For every pair of member packs, a diff of their `ontology.ttl` (or `ontology/*.ttl`) graphs against a proposed shared kernel graph — which triples are common (candidate kernel), which are pack-specific (candidate profile parameters), and which conflict (blocks consolidation, must be resolved or the pair excluded from the family).
2. **Pairwise query correspondence.** For every pair, a diff of `.rq` gate/query files — same three-way split (common/parameterized/conflicting).
3. **Pairwise template correspondence.** For packs with a `projection` profile (per `CLAUDE.md`'s `Pack.profile` derivation), a diff of `.tmpl`/`.tera` templates against a proposed shared template set.
4. **Consumer-boundary check.** At least one real consumer project (per `CLAUDE.md`'s qualification guidance: "exercise it with the matching ggen runtime against an isolated consumer project") generated from the *current* member pack and from the *proposed* kernel+profile split, with output diffed. A family is not provably consolidatable on ontology/template text similarity alone if generated consumer artifacts diverge.
5. **Verdict**: `ADMITTED` (proceed to physical merge ticket), `PARTIAL` (some members admitted, others excluded — name them), or `REFUTED` (family claim does not hold — record why, so it isn't re-proposed without new evidence).

## Machine-generation requirement

The court must be runnable as a script (e.g. `scripts/consolidation_court.py family.toml`) that takes a family definition (kernel candidate + member pack paths) and emits items 1-5 above as a structured report (JSON or Markdown table), not a manually-written analysis document. This mirrors `scripts/marketplace.py`'s own determinism discipline: the report for a given family + git commit must be reproducible byte-for-byte on a second run, the same way `catalog` output must a/b/cmp-match.

## Acceptance criteria

1. A script or documented procedure exists that produces items 1-4 above for an arbitrary family definition, without hand-editing per family.
2. Running the court twice on the same family at the same commit produces identical output (determinism, matching this repo's existing catalog-determinism discipline).
3. The court's output format is specified precisely enough that a family ticket (05+) can cite "family-consolidation proof: `ADMITTED`, see `<path-to-report>`" as its acceptance evidence, rather than restating the audit's prose claims.
4. At least one worked run of the court exists against a real family before this ticket is considered done — proves the procedure is executable, not just specified. The TCPS family (`tcps-core-pack`, `tcps-cli-pack`, `tcps-ffi-pack`, `tcps-std-pack`, `tcps-wasm-pack`, `tcps-release-pack`) is a reasonable first candidate given its small, uniformly-named member set, but the implementer may choose any family from `00-PACK-PORTFOLIO-MATURITY-AUDIT.md`.
5. This ticket's PR does not merge or delete any pack directory — it delivers only the court mechanism and its one worked example report.

## Falsifiers

- If a family ticket (05+) is merged/closed citing this court's output but the referenced report file does not exist or does not match the required structure (items 1-5), that family ticket's closure is invalid and must be reopened.
- If two runs of the court on the same family/commit produce different verdicts, the court itself is not fit for purpose — fix forward before trusting any of its verdicts.
- If the court's "proof" turns out to be manually written prose rather than machine-generated from real ontology/query/template diffs, it does not satisfy this ticket.

## See Also

- `00-PACK-PORTFOLIO-MATURITY-AUDIT.md` — standing statement this ticket directly operationalizes
- `02-TICKET-pack-class-taxonomy.md` — the classification this court's `ADMITTED` verdicts would eventually be recorded against (e.g. promoting a kernel candidate to `KernelPack`)
- Family tickets `05-*` through `11-*` — each is `BLOCKED on ticket 03` until it can cite a real report from this court
- `CLAUDE.md` — qualification/consumer-boundary discipline this methodology is built on
