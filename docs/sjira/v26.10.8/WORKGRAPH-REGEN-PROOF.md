# Workgraph Regeneration Proof — 6-Repo Convergence (v26.10.8)

Generator: `scripts/gen_workgraph.py` @ 68ba8d207 (v3 items 1–9, landed on
`lane/workgraph-gen` and integrated into checkout HEAD b372fd334).
Subject: the six repos with agent-authored v26.10.8 `WORKGRAPH.ttl` seeds.
Method: run the generator over each repo's landed state (read-only), diff
against the agent-authored seed, disposition every delta as **converged**
(the generator caught up), **generator-gap** (successor backlog), or
**agent-over-claim-conservatively-refused** (the generator will not copy it).

## Receipt of runs

- All 6 renders exit 0; double-run byte-identical per repo (selftest
  `double-run IDENTICAL`, sha256 prefixes: ggen-marketplace 488f3204,
  ex4pm 8e0fc400, zcode-cli 90b870d5, ash_affidavit 4f16fab2,
  ash_surface 9153e9e0, ash_r2rml 3e1f12a5).
- A run mid-v3-edit bracketed a live edit (projection catalog changed
  under it); after the v3 lane's HEAD landed, re-runs are stable — the
  determinism gate double-fired on a real concurrent-edit race, which is
  the falsifier working as designed.

## Convergence table

| repo | seed orders | generated orders | order coverage | standing disposition | verdict |
|---|---|---|---|---|---|
| ggen-marketplace | 6 (all ALIVE) | 15 (8 ALIVE / 7 UNKNOWN) | 5/6 | 5/6 ALIVE→ALIVE via witness gate; V8-004 cross-repo emitted only as `sj:crossRepo` note | converged; 1 gap |
| ex4pm | 5 (all ALIVE) | 5 (3 ALIVE / 2 UNKNOWN) | 5/5 | 5/5 ALIVE→ALIVE; acceptance/falsifier indexed nodes converged | fully converged |
| zcode-cli | 5 (all ALIVE, DO ceilings) | 2 (0 ALIVE / 2 UNKNOWN) | 2/5 | 2 seed ALIVE→UNKNOWN (receipt-less); DO→CONSTRUCT on all | gap + refused over-claims |
| ash_affidavit | 5 (no standing asserted; EXECUTED_VERIFIED ceilings) | 6 (0 ALIVE / 6 UNKNOWN) | 5/5 axes | UNKNOWN converged; EXECUTED_VERIFIED refused | converged (conservative) |
| ash_surface | 4 (no standing asserted; EXECUTED_VERIFIED ceilings) | 6 (3 ALIVE / 3 UNKNOWN) | 4/4 axes | witness-gate ALIVE on courts/a2a/docs axes; ceilings refused | converged (conservative) |
| ash_r2rml | 4 (no standing asserted; EXECUTED_VERIFIED ceilings) | 5 (0 ALIVE / 5 UNKNOWN) | 4/4 axes | UNKNOWN converged; EXECUTED_VERIFIED refused | converged (conservative) |
| **overall** | **29 seed orders** | **39 orders** | **25/29 axes (86%)** | — | **converged with 2 gap classes** |

Order coverage counts slug→axis correspondence (seed slug to conventional
scope axis); standing disposition counts per-order standing agreement after
over-claim refusals are dispositioned.

## Per-repo detail

### ggen-marketplace

Converged: 5/6 seed orders map to generator-ALIVE axes (V8-001→pack@928e85887,
V8-002→scripts@9444aa91f, V8-003→doc-hdit@97abea822, V8-005→reference@3d6bd8023,
V8-006→sjira@339d1e757), witness-gated by on-disk receipts citing member SHAs;
acceptance/falsifier as first-class indexed nodes (v3 item 1); pathScope,
replayIdentity, checkpoints, dependency/upstream edges (v3 items 3–4); full
projection catalog declared every render (v3 item 8). Gap: V8-004 (cross-repo
order) emitted only as an `sj:crossRepo` note, not a first-class order.
Generator adds 9 post-seed axes correctly as UNKNOWN where no receipt cites
them.

### ex4pm

Fully converged: 5/5 seed orders map to axes with standing ALIVE both sides
(docs@8915e85, archive@92d480f, sjira@da21f05), acceptance/falsifier indexed
items, pathScope, receipts, prov links. Generator adds 2 post-seed axes
(a2a@50071c4, cards@6758bd7) as UNKNOWN — correct, no on-disk receipt cites
them yet.

### zcode-cli

Order coverage 2/5: only reference@542d223 and sjira@4a1ff83 are reachable.
The four runtime lane commits (daaec82e, e416d731, 23c479aa, 8cb1d4c8) landed
on `fix/v26926-preview-publish-typed-skip` and are reachable from HEAD but
outside the generator's campaign commit filter (tag range + `docs/sjira/`
path filter), so the generator's scope grouping never sees them. Standing:
the seed's receipt-less ALIVE is refused (UNKNOWN); the seed's
`authorityCeiling "DO"` is refused (CONSTRUCT) on all 5 orders.

### ash_affidavit

5/5 seed slugs map to generator axes (changelog-v26108→changelog@6dfb218,
signature-envelope-how-to→diataxis@+signing@, generated-reference-skeletons→reference@56d5fb5,
version-bump/pin-court→sjira/docs axes). All seed orders assert
`sj:evidenceCeiling "EXECUTED_VERIFIED"` with no `sj:standing`; the generator
emits UNKNOWN standing and a typed evidence ceiling — the ceilings are
refused over-claims, the standing stance converges exactly.

### ash_surface

4/4 seed slugs map to generator axes (fixture-backed-court-battery→courts@68f77041b
ALIVE, a2a-agent-card→a2a@8bc9b7509 ALIVE, diataxis-nav-court→diataxis@008f0d775,
v26108-calver-bump→sjira@80bbfd5af). Witness-gate ALIVE on courts/a2a/docs
matches the on-disk court receipts; the seed's four EXECUTED_VERIFIED
ceilings are refused (no per-order receipt artifact).

### ash_r2rml

4/4 seed slugs map to generator axes (v26108-version-bump→sjira@37ce7e0,
changelog-backfill→docs@0cb5eb3 family,
livemd-pin-sync→livemd@6249d5d, doc-hdit-skeletons→reference@ce947d4/how-to@11da8e6).
Seed asserts EXECUTED_VERIFIED ×3 + PARTIAL_ALIVE ×1 with no standing; the
generator refuses the ceilings and emits UNKNOWN — conservative convergence.

## Doctrine statement (closing form)

Agent-authored workgraphs are the SEED; the generator is the successor
format. Regeneration without an LLM is the acceptance test: a campaign is
closed when `gen_workgraph.py` over the landed repo state reproduces the
campaign's workgraph and every remaining delta is a dispositioned gap or a
refused over-claim — never a hand-authored fact the machine cannot re-derive.
This proof shows that condition holding at 86% order coverage across 6 repos,
with 2 remaining gap classes (branch-landed lane discovery; first-class
cross-repo orders), and every standing disagreement resolving to a refusal
of an over-claim the standing vocabulary already forbids. Hand-authoring
retires when the successor closes the gap list below — the seeds did their
job: they told the generator which richness matters, and the generator
absorbed it (v3 items 1–9).

## Successor gap list (v4 backlog)

1. Branch-landed lane discovery: campaign commits on `fix/*` lanes outside
   the tag-range + `docs/sjira/` commit filter (zcode-cli 2/5 coverage root
   cause). Use `--seed-commits` binding with the seed's `subjectSha` as
   mapping input across branches, not just the checked-out branch.
2. First-class cross-repo work orders (V8-004 class) — currently a
   `sj:crossRepo` note, not an order.
3. `sj:Court` individuals + `requiresCourt` binding (still seed-only in the
   zcode/ash seed families).
4. Per-order `requiredEvidence` catalog breadth and bespoke per-order
   evidenceCeiling text.
5. Non-conventional commit mapping: version-bump/changelog commits land on
   axes by keyword heuristics, producing axis-name drift (r2rml
   version-bump→sjira). Seed-slug binding closes this.
6. `sj:dependency` chains are order-order only; the ash seeds' campaign-level
   dependency graphs are not reproduced.

## Replay

```
cd /Users/sac/ggen-marketplace
git checkout 68ba8d207 -- scripts/gen_workgraph.py   # or any tree containing it
for r in ggen-marketplace ex4pm zcode-cli ash_affidavit ash_surface ash_r2rml; do
  python3 scripts/gen_workgraph.py --repo /Users/sac/$r --version v26.10.8 \
    --out /tmp/$r.ttl && git diff --no-index /tmp/$r.ttl /dev/null | head -1
done
python3 scripts/gen_workgraph.py --selftest --repo /Users/sac/ggen-marketplace \
  --repo /Users/sac/ex4pm --repo /Users/sac/zcode-cli --repo /Users/sac/ash_affidavit \
  --repo /Users/sac/ash_surface --repo /Users/sac/ash_r2rml
```

## See Also

- `docs/sjira/v26.10.8/CONVERGENCE.md` — the v2 3-repo proof this closes
- `scripts/gen_workgraph.py` — the generator (68ba8d207)
- `docs/sjira/v26.10.8/WORKGRAPH.ttl` — this repo's seed
- `~/.claude/rules/dfcm-composition-catalog.md` C10 — retirement compounding
