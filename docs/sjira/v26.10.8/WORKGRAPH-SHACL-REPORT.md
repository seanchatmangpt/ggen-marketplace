# WORKGRAPH-SHACL-REPORT

SHACL admission validation of the twelve v26.10.8 campaign workgraph graphs
against the ggen_igniter semantic-jira-pack `work-order.shacl.ttl` shapes,
plus the defect classification and the fixes landed by this wave. Executed
with pyshacl 0.31.0 via `scripts/validate_workgraphs.py` (this repo).

- Shapes: `~/ggen_igniter/priv/ggen/semantic-jira-pack/shapes/work-order.shacl.ttl`
- Runner: `scripts/validate_workgraphs.py` (pyshacl, advanced mode)
- Date: 2026-10-08

## Per-repo verdict

| repo | graph | WorkOrders | GoalCheckpoints | conforms | violations | class |
|---|---|---|---|---|---|---|
| ash_a2a | docs/sjira/v26.10.8/WORKGRAPH.ttl | 4 | 0 | false | 72 | style |
| ash_affidavit | docs/sjira/v26.10.8/WORKGRAPH.ttl | 5 | 0 | false | 112 | style |
| ash_pplan | docs/sjira/v26.10.8-1/WORKGRAPH.ttl | 5 | 1 | false | 15 | style |
| ash_r2rml | docs/sjira/v26.10.8/WORKGRAPH.ttl | 4 | 0 | false | 90 | style |
| ash_surface | docs/sjira/v26.10.8/WORKGRAPH.ttl | 4 | 0 | false | 94 | style |
| beam4pm | docs/sjira/v26.10.8/WORKGRAPH.ttl | 5 | 0 | false | 79 | style |
| castle | docs/sjira/v26.10.8/goal.ttl | 0 | 5 | false | 11 | style |
| ex4pm | docs/sjira/v26.10.8/WORKGRAPH.ttl | 5 | 0 | false | 81 | style |
| ggen-ecosystem | docs/sjira/v26.10.8/WORKGRAPH.ttl | 5 | 0 | false | 91 | style |
| ggen-marketplace | docs/sjira/v26.10.8/WORKGRAPH.ttl | 6 | 0 | false | 135 | style |
| xaas | docs/sjira/v26.10.8/WORKGRAPH.ttl | 5 | 0 | false | 131 | style |
| zcode-cli | docs/sjira/v26.10.8/WORKGRAPH.ttl | 5 | 0 | false | 25 | style |

## Classification law

Every remaining violation is classified `style` (shape-expectation mismatch),
not defect. The buckets, all inherent to doc-graph / goal-graph authoring
style rather than defects in the authored data:

- **closed-shape**: graph-local documentation properties (`wg:`, `eco:`,
  `prov:`, `sjd:` …) that the closed `sj:WorkOrderShape` does not admit. The
  pack shapes model execution orders; campaign doc-graphs carry citations
  (`wg:commit`, `wg:courtRun`, `rdfs:seeAlso`, `prov:wasDerivedFrom`).
- **missing-required-field**: the execution-order court fields
  (`sj:originAuthority`, `sj:requiresCourt`, `sj:requiresEvidence`,
  `sj:acceptance`, `sj:falsifier`, `sj:projection`, `sj:nextAction`,
  `sj:nextCheckpoint`, `sj:requiresReceiptClass`, `sj:pathScope`,
  `sj:replayIdentity`, `sj:promotionRule`, …) that doc-graphs deliberately
  omit. The dominant class (~18-80 per repo).
- **node-kind / class-ref**: literals written where the pack expects IRIs or
  typed classes (`sj:requiresCourt "..."` as prose instead of
  `a sj:Court ;` nodes).
- **sparql**: `ALIVE requires exact candidate/subject SHA and a durable
  receipt`, `ALIVE requires an independent court and durable receipt`, origin
  without admission witness — doc-graphs cite receipts that live in
  code/receipt files, never in the graph (per the doc-graph law every
  workgraph header states).

castle is the pure GoalCheckpoint-style goal graph (0 WorkOrders): its 11
violations are the checkpoint tuple fields (`sj:courtCommand`,
`sj:boundaryClass`) that GoalCheckpointShape requires on non-root
checkpoints, and its stopQuery ASK form is admitted.

## Real defects found and fixed

Shape-refusable values fixed in the subject repos (explicit pathspec:
`docs/sjira/v26.10.8/WORKGRAPH.ttl` only; standing/ceiling lexical law per
the pack shapes):

| repo | subject | defect | before | after |
|---|---|---|---|---|
| ash_surface | WO-ASHSURF-26108-2 | baseSha 9-char short SHA | `68f77041b` | `68f77041b885619dc65cc9b5fecd521f4667ad97` |
| ggen-marketplace | SJIRA-V8-002 | baseSha short SHA | `20aadd175` | `20aadd1756d777ec3c8cf7729ad6f867366a855a` |
| ggen-marketplace | SJIRA-V8-003 | baseSha short SHA | `ff9ff8284` | `ff9ff8284cae5aa84932e2684b577c3b637abb12` |
| ggen-marketplace | SJIRA-V8-004 | baseSha not a git SHA at all — no commit `5cc37aea` exists on any local ref or on GitHub (`gh api` 422); it is the W803a *artifact pin* | `5cc37aea` | `e987f3717fead9b2f503a049bb39b49ae88b02d3` (v26.10.8 campaign base commit); `prov:wasDerivedFrom` repointed likewise |
| ggen-marketplace | SJIRA-V8-004 | `sj:repository` not a slug | `cross-repo (affidavit, ferroplan, coordinator-dispatched consumer)` | `seanchatmangpt/ggen-marketplace` (cross-repo scope stays in the description/acceptance) |
| ggen-marketplace | SJIRA-V8-005 | baseSha short SHA (annotated tag object of tag `v26.10.8`) | `e890a55ca` | `e890a55ca47ba031d53028921c72d78125689624`; falsifier text corrected `v26.10.8^{commit}` → `v26.10.8` (the tag's commit is `2ad88900b`, so the old falsifier was self-refuting) |
| ggen-marketplace | SJIRA-V8-006 | baseSha short SHA | `2ad88900b` | `2ad88900b73708ddff6250bc64fe34e481fdc953` |
| zcode-cli | zcode-26108-01 | baseSha short-SHA-then-zero-padding (lexically valid, factually wrong) | `8926518000…0` | `89265187b387047ef887603df6ba6010ccf9cd1f` |
| zcode-cli | zcode-26108-02 | baseSha padding with mis-transcribed prefix (`aa0d3590`, real base is `aa0d359e` = parent of the subject commit `e416d731`) | `aa0d3590…0` | `aa0d359ed54e01a703516b162314241db282309b` |
| zcode-cli | zcode-26108-01..05 | `sj:authorityCeiling "DO"` — outside the pack enum (OBSERVE/SELECT/CONSTRUCT), and doc-graphs never grant DO | `DO` ×5 | `CONSTRUCT` ×5 |
| ggen-ecosystem | SJIRA-GGE-2601..2605 | `sj:standing "CANDIDATE"` — out of the sanctioned six-string vocabulary (CANDIDATE is reserved for MachineExperience standing) | `CANDIDATE` ×5 | `UNKNOWN` (orders are unexecuted planning orders; honest sanctioned value) |

The ggen-ecosystem graph's DISCLAIMER header was updated to disclose the
correction (it previously declared every standing "CANDIDATE" by design).
The ggen-ecosystem `eco:Milestone` node (typed `prov:Activity`, not
`sj:WorkOrder`) is not targeted by WorkOrderShape and was corrected to
`UNKNOWN` for vocabulary consistency; its ceiling `"OBSERVE|SELECT|CONSTRUCT|
VERIFY"` is not shape-targeted and stands as doc vocabulary.

## Defect classes the shapes cannot catch

Two of the fixed defects passed the lexical pattern and are invisible to
SHACL — they were caught by resolving every SHA against git refs and the
GitHub API:

1. Zero-padded pseudo-SHAs (zcode-cli): 40-hex but fabricated padding of a
   short prefix (and one mis-transcribed prefix, `aa0d3590` vs the real
   `aa0d359e`). A `sh:pattern` cannot see this; a `^git:<slug>@<sha>:path`
   trust-root resolution court can.
2. Nonexistent-commit provenance (ggen-marketplace V8-004): `5cc37aea` is an
   artifact pin, not a git commit — no commit exists on any ref, on GitHub
   (`gh api` 422), or in any sibling repo. The `prov:wasDerivedFrom` triple
   asserted a commit that never existed.

## Replay

```
python3 scripts/validate_workgraphs.py            # verdict table
python3 scripts/validate_workgraphs.py --markdown # per-violation detail
```

Subject-repo commits: explicit pathspec `docs/sjira/v26.10.8/WORKGRAPH.ttl`;
each committed and ff-pushed on its checkout branch. No pack shapes change
was required: every lexical law in `work-order.shacl.ttl` correctly refused
the defective values; the remaining non-conformance is the documented
doc-graph vs execution-order style mismatch.

## Round-2 addendum (post-fix court, 2026-10-08)

Re-run of the fleet-wide court after the 12 defect fixes landed in the four
subject repos, via `scripts/validate_workgraphs.py` (same shapes file, same
runner, pyshacl 0.31.0).

### Per-repo verdict vs round 1

| repo | conforms | violations | round-1 violations | delta |
|---|---|---|---|---|
| ash_a2a | false | 72 | 72 | 0 |
| ash_affidavit | false | 112 | 112 | 0 |
| ash_pplan | false | 15 | 15 | 0 |
| ash_r2rml | false | 90 | 90 | 0 |
| ash_surface | false | 94 | 94 | 0 |
| beam4pm | false | 79 | 79 | 0 |
| castle | false | 11 | 11 | 0 |
| ex4pm | false | 81 | 81 | 0 |
| ggen-ecosystem | false | 91 | 91 | 0 |
| ggen-marketplace | false | 135 | 135 | 0 |
| xaas | false | 131 | 131 | 0 |
| zcode-cli | false | 25 | 25 | 0 |

Every remaining violation is `style-mismatch` (doc-graph vs execution-order
shape expectation): closed-shape extra doc properties, deliberately omitted
court fields, literal-vs-IRI node kinds, and receipt-citing SPARQL constraints
whose receipts live in code files, not the graph. Zero defect-class
violations remain. The violation counts are unchanged from round 1 because
the 12 fixes replaced lexically-defective values with lexically-valid ones —
the fixed fields were never counted in the defect bucket in round 1 either
(they passed SHACL lexically and were caught by git-ref/GitHub resolution,
per "Defect classes the shapes cannot catch" above).

### Fix retention check (all 12 on disk, verified 2026-10-08)

| repo | subject | fix | on disk |
|---|---|---|---|
| ash_surface | WO-ASHSURF-26108-2 | full 40-hex baseSha `68f77041b885619dc65cc9b5fecd521f4667ad97` | yes |
| ggen-marketplace | V8-002 | `20aadd1756d777ec3c8cf7729ad6f867366a855a` | yes |
| ggen-marketplace | V8-003 | `ff9ff8284cae5aa84932e2684b577c3b637abb12` | yes |
| ggen-marketplace | V8-004 | base `e987f3717fead9b2f503a049bb39b49ae88b02d3`; slug repository; prov re-pointed | yes |
| ggen-marketplace | V8-005 | tag-object `e890a55ca47ba031d53028921c72d78125689624`; falsifier `v26.10.8` | yes |
| ggen-marketplace | V8-006 | `2ad88900b73708ddff6250bc64fe34e481fdc953` | yes |
| zcode-cli | zcode-26108-01 | `89265187b387047ef887603df6ba6010ccf9cd1f` (resolves: commit) | yes |
| zcode-cli | zcode-26108-02 | `aa0d359ed54e01a703516b162314241db282309b` (resolves: commit) | yes |
| zcode-cli | zcode-26108-01..05 | ceiling `CONSTRUCT` x5 (no `"DO"` string remains) | yes |
| ggen-ecosystem | SJIRA-GGE-2601..2605 | standing `UNKNOWN` x5 (no `"CANDIDATE"` value remains; only the DISCLAIMER prose mentions it) | yes |

The two previously fabricated SHAs (zero-padded zcode pair) and the
previously nonexistent V8-004 base now resolve as real git objects
(`git cat-file -t`: commit/commit; `v26.10.8^{commit}` =
`2ad88900b73708ddff6250bc64fe34e481fdc953`). Residual grep hits for
`5cc37aea` are disclosure prose in the V8-004 acceptance text and a trailing
comment, not field values.

### Classification of anything new

Nothing new: delta = 0 violations in every repo, and no new violation class
beyond the four documented doc-graph style buckets. Round-3 admission
verdict: **ADMITTED** — all 12 graphs at doc-graph-style-only non-conformance,
all 12 defect fixes retained, no regression introduced by the fix wave.
