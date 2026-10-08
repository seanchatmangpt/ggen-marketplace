# Seed → Generator Convergence Proof (v26.10.8)

Generator: `scripts/gen_workgraph.py` @ lane/workgraph-gen 961e7d7df.
Method: regenerate each seed graph from raw repo state (zero LLM), diff against
the agent-authored seed, classify every difference. Three repos with landed
agent-authored `WORKGRAPH.ttl`:

| repo | seed | generated | base |
|---|---|---|---|
| ggen-marketplace | 6 orders, 6 ALIVE | 12 orders, 6 ALIVE / 6 UNKNOWN | 2ad88900b |
| zcode-cli | 5 orders, 5 ALIVE | 1 order, 1 UNKNOWN | 2cdc58a44 |
| ash_affidavit | 5 orders, standing unasserted | 6 orders, 6 UNKNOWN | a4882d59c |

Feature checklist scored per repo (converged = generator emits it; partial =
emitted in degraded/template form; gap = seed richness the generator lacks).
N/A features (absent from the seed) are excluded from the denominator.

## Per-repo diffs

### ggen-marketplace (seed `docs/sjira/v26.10.8/WORKGRAPH.ttl`)

- Converged: WorkOrder class, titles, commit-body-grounded descriptions,
  `sj:subject`/`sj:baseSha` (generator emits full SHAs where the seed used
  short), `prov:wasDerivedFrom` member-commit links, standing vocabulary,
  witness-gated standing (6/6 seed ALIVE orders map to generator-ALIVE axes
  via on-disk receipt citation), CONSTRUCT ceiling, receipt/evidence citations
  (`sj:requiresEvidence` + `sj:receipt` vs seed `rdfs:seeAlso`), projections,
  milestone PARTIAL_ALIVE, scope-disclaimer header.
- Partial: evidenceCeiling (template text vs seed's per-order bespoke);
  acceptance (commit-title concatenation vs seed's authored semantics).
- Gap: per-order bespoke falsifier commands (seed: `git rev-parse
  v26.10.8^{commit}` expecting e890a55ca; generator: repo-level pytest
  template); cross-repo order (seed V8-004 spans affidavit/ferroplan);
  pre-base consolidation commits (seed V8-001 deprecation chain 92233bdfd /
  d5c7ea045 / 164843b68 not reachable since base 2ad88900b).
- Score: 14/16 features (87.5%); order coverage 12 axes emitted, 5/6 seed
  orders represented (V8-004 cross-repo unrepresentable).

### zcode-cli (seed `docs/sjira/v26.10.8/WORKGRAPH.ttl`)

- Converged: WorkOrder class, titles, subject identity, full-SHA baseSha,
  prov commit links, standing vocabulary, CONSTRUCT ceiling, milestone/epic,
  scope header.
- Partial: descriptions (scopeless commit falls back to default text);
  standing witness gate (refuses seed ALIVE — see refusals); projections
  (2 of seed's 14 ProjectionSpecs); evidenceCeiling (template vs SPECIFIED).
- Gap: order coverage 1/5 (lane commits daaec82e / e416d731 / 23c479aa /
  8cb1d4c8 / 542d2238 landed outside the `docs/sjira/v26.10.8/` commit
  filter and off-axis branch names, so the generator sees only the
  workgraph-landing commit itself); `sj:Court` nodes; acceptance criteria
  and falsifiers as first-class indexed nodes; checkpoints; `pathScope`;
  `replayIdentity`; `requiresReceiptClass`; bespoke acceptance/falsifier
  text; full 14-projection catalog; evidence-requirement catalog breadth.
- Refused over-claims (generator conservatism is the feature): seed
  `sj:authorityCeiling "DO"` on all 5 orders → generator emits CONSTRUCT;
  seed ALIVE standing citing only a campaign receipt narrative → UNKNOWN
  absent a per-commit receipt artifact on disk.
- Score: 11/20 features (55%); order coverage 1/5 (20%).

### ash_affidavit (seed `docs/sjira/v26.10.8/WORKGRAPH.ttl`)

- Converged: WorkOrder class, titles, body-grounded descriptions, subject,
  baseSha, prov links, standing vocabulary, standing conservatism (seed
  explicitly asserts no standing; generator's all-UNKNOWN agrees), authority
  NONE / CONSTRUCT, projections (seed's `"jira","receipt"` strings vs
  generator's typed ProjectionSpecs), scope header.
- Partial: receipt/evidence citations (template evidenceCeiling text);
  evidenceCeiling values (seed "EXECUTED_VERIFIED" — refused, see below).
- Gap: order coverage 4/6 core axes (version-bump 1a80667a and W690 pin
  court 53b64474 commits are non-conventional-message and fall outside the
  scope grouping); acceptance-criterion / falsifier indexed nodes;
  `sj:DependencyEdge` chains (seed encodes a full requiresReceipt chain);
  `requiredCourt` / `requiredEvidence`; `replayIdentity`; `pathScope`.
- Refused over-claims: seed `evidenceCeiling "EXECUTED_VERIFIED"` asserts
  execution without a per-order on-disk receipt → generator emits UNKNOWN
  standing with typed template ceiling.
- Score: 12/17 features (71%); order coverage 4/6 (67%).

## Convergence numbers

| repo | shape convergence | order coverage |
|---|---|---|
| ggen-marketplace | 87.5% (14/16) | 83% (5/6) |
| zcode-cli | 55% (11/20) | 20% (1/5) |
| ash_affidavit | 71% (12/17) | 67% (4/6) |
| **overall** | **69.8% (37/53)** | **~60% (10/17)** |

Refusal ledger (agent over-claims the generator correctly will not copy):
1. `authorityCeiling "DO"` on lane work orders (zcode seed, 5 orders) —
   consequential DO never flows from a graph; CONSTRUCT only.
2. Standing ALIVE / `EXECUTED_VERIFIED` without a receipt artifact on disk
   citing the member commit (zcode 5, ash_affidavit 5) — UNKNOWN instead.
3. Vague ceiling strings ("SPECIFIED") — typed evidence-ceiling text instead.

## v3 gap list

1. Acceptance criteria and falsifiers as first-class indexed nodes, not
   string literals.
2. `sj:Court` individuals bound to orders (`requiresCourt`).
3. `sj:DependencyEdge` chains (requiresReceipt ordering between orders).
4. `pathScope`, `nextCheckpoint`, `replayIdentity`, `requiresReceiptClass`.
5. Per-order bespoke falsifier commands (repo manifest gives the template;
   order-level commands need receipt-file parsing to specialize).
6. Cross-repo work orders (V8-004 class).
7. Commit→order coverage beyond conventional-commit scope grouping: version
   bumps, test/court commits, branch-landed lanes, pre-base consolidation
   chains (use the seed's `landedCommit`/`subjectSha` as the mapping input).
8. Full projection catalog (14 ProjectionSpecs) and evidence-requirement
   catalog breadth.
9. Acceptance-text semantic compression (currently commit-title
   concatenation; body bullets are truncated).

## Doctrine statement

Agent-authored workgraphs are the SEED: hand-authored instances of the
canonical folded `sj:` shape that tell the generator what richness matters.
The generator is the successor format: same shape, derived from repository
state with zero LLM in the loop, byte-identical for the same repo state.
Where the seed and the regeneration disagree, the disagreement is
dispositioned three ways — converged (the generator caught up), gap (v3
backlog above), or over-claim (the generator's conservatism wins; the seed's
DO ceilings and receipt-less ALIVE standings are exactly what the standing
vocabulary forbids). Regeneration without an LLM is the acceptance test: a
campaign is closed when `gen_workgraph.py` over the landed repo state
reproduces the campaign's workgraph and every remaining delta is a
dispositioned gap or a refused over-claim — never a hand-authored fact the
machine cannot re-derive.

## See Also

- `docs/sjira/v26.10.8/WORKGRAPH.ttl` — the seed for this repo
- `scripts/gen_workgraph.py` — the generator
- `~/.claude/rules/dfcm-composition-catalog.md` C10 — retirement compounding
