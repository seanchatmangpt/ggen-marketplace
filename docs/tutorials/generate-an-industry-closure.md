# Tutorial: generate an industry closure

In this tutorial you will watch one requirement move through the whole industry-closure chain on synthetic data, from "no architecture building block" to "covered", then see what happens when evidence turns against it. You will read the computed residual at every step, act as the human who approves a contract, run the growth gates, and finish with an honest statement of what you did and did not prove.

You need a checkout of this repository on a branch (not `main`), `python3` with `rdflib` and `Jinja2` installed (`pip install -r ci/requirements.txt`), and about twenty minutes. You do not need a ggen binary. If you have one, see "With a real ggen" at the end.

Everything here uses synthetic data (`example.invalid` IRIs) from the packs' fixtures. Nothing generated or approved in this tutorial is real, and nothing here can be ALIVE. For exact contracts see [Industry closure contract](../reference/industry-closure-contract.md) and [Enterprise operating model contract](../reference/enterprise-operating-model-contract.md); for the reasoning see [Industry closure as architecture strategy](../explanation/industry-closure-as-architecture-strategy.md).

## What you will build on

Three packs take part:

- `enterprise-operating-model-pack` turns an enterprise's operating-model decision into requirements and pending-approval building-block skeletons (pass 1).
- `industry-closure-ledger-pack` computes the residual (requirements minus what the chain already closes), routes each gap, and proposes the next ledger snapshot (pass 2).
- `industry-closure-retail-lending-profile-pack` is a real industry's data over that vocabulary. It ships no building blocks, so its starting residual is honest and non-empty. You will only look at it.

## 1. Set up a helper

The tests share a small helper that runs SPARQL under rdflib and renders templates through a Jinja2 proxy that accepts only the subset ggen's own template engine also executes. Create a scratch script outside the repository tree, for example `/tmp/closure_tour.py`, starting with:

```python
import sys
sys.path.insert(0, "tests")          # run from the repository root
import ic_support as s

K = s.PACK                           # packs/industry-closure-ledger-pack
stages = sorted((K / "fixtures/closure-growth").glob("stage*.ttl"))
```

The proxy gives partial evidence only. The real manufacture engine runs only under a real ggen; here, manufacture is `BLOCKED:ggen_binary_unavailable` and nothing you render below is a manufacturing claim.

## 2. Watch the residual move

Each stage file is the same synthetic requirement, `REQ-A`, with one more link of the chain filled in. Append this loop to your script and run it from the repository root:

```python
for stage in stages:
    graph = s.world(stage)           # kernel ontology plus the stage
    rows = s.query_rows(graph, K / "queries/10-residual.rq")
    print(stage.stem, [(r["rkey"], r["classCode"]) for r in rows] or "covered")
```

```bash
python3 /tmp/closure_tour.py
```

On the repository as committed, the output is:

```text
stage0-no-abb [('REQ-A--CAP-A', 'DEFICIT_ABB')]
stage1-abb-contract-pending [('REQ-A--CAP-A', 'DEFICIT_CONTRACT')]
stage2-contract-approved-no-sbb [('REQ-A--CAP-A', 'DEFICIT_SBB')]
stage3-sbb-candidate [('REQ-A--CAP-A', 'DEFICIT_QUALIFICATION')]
stage4-sbb-qualified-no-evidence [('REQ-A--CAP-A', 'DEFICIT_EVIDENCE')]
stage5-verified-covered covered
stage6-falsified-stale [('REQ-A--CAP-A', 'DEFICIT_EVIDENCE')]
```

The residual is computed from the graph by `queries/10-residual.rq`; nothing stores it. The first failing link of the chain names the class, in this order: architecture building block (ABB), approved contract, solution building block (SBB), qualification, evidence. Note that the same requirement is reopened at stage 6; you will see why in step 6.

## 3. Read what the residual asks for

Print the full row for stage 0:

```python
graph = s.world(stages[0])
for row in s.query_rows(graph, K / "queries/10-residual.rq"):
    print(row)
```

Look at four columns:

- `classCode` is `DEFICIT_ABB`.
- `targetCode` is `UPSTREAM_ARCHITECTURE`: the lane that owns the next move.
- `acceptanceText` says what done looks like. `falsifierText` says what would show the residual itself was wrong.
- `standing` is `UNKNOWN`. A requirement that needs consequential authority would be `BLOCKED` instead.

With a real ggen these same rows become `residual-ledger.ttl`, `sjira-workorders.ttl` and `feedback-packet.json` under `generated/industry-closure/`. They are candidates: each claims authority `NONE` and standing `UNKNOWN` or `BLOCKED`.

## 4. Act as the human approver

Compare `fixtures/closure-growth/stage1-abb-contract-pending.ttl` with `stage2-contract-approved-no-sbb.ttl`. The only substantive change is on the contract:

```turtle
ex:kA a ea:ArchitectureContract ;
    ea:hasAuthorityBoundary ex:boundaryA ;
    ic:approvalStatus ic:APPROVED ;
    ic:approvedBy ex:humanApprover ;
    ic:approvalReceipt "receipt:A-approval" ;
    ic:authorityClaim "NONE" .
```

A generated skeleton carries `ic:PENDING_HUMAN_APPROVAL` and nothing else. Approval needs a named human and a receipt, and no template ever emits it. Prove the fence yourself: change `ic:approvedBy` away (delete that line from a scratch copy of the stage 2 file) and run the authority gate.

```python
from pathlib import Path
text = (K / "fixtures/closure-growth/stage2-contract-approved-no-sbb.ttl").read_text()
broken = "\n".join(l for l in text.splitlines() if "ic:approvedBy" not in l)
graph = s.world(broken)
print(s.gate_rows(graph, K / "gates/080_authority_fence.rq"))
```

The gate returns a row with `REFUSED:IC_CONTRACT_APPROVAL_UNATTRIBUTED`. Zero rows would have been a pass; any row is a typed refusal. Putting the line back restores zero rows.

## 5. Watch the chain close, then grow the ledger

Stage 3 adds an SBB with only candidate standing; stage 4 makes it QUALIFIED with a pinned exact subject; stage 5 adds independent VERIFIED evidence at that exact subject. QUALIFIED alone is not evidence, which is why stage 4 still has a residual.

At stage 5 the residual is empty, but the ledger has not yet recorded the closure. Run the frontier gate:

```python
graph = s.world(K / "fixtures/closure-growth/stage5-verified-covered.ttl")
print(s.gate_rows(graph, K / "gates/055_frontier_recorded.rq"))
```

It refuses with `REFUSED:IC_FRONTIER_UNRECORDED`: closure cannot be silently omitted. The pack proposes the repair as `closure-next`, the candidate snapshot for epoch plus one. Render it through the proxy and admit it by merging it into the graph:

```python
rows = s.query_rows(graph, K / "queries/20-closure-frontier.rq")
next_snapshot = s.render(K / "templates/closure-next.ttl.tera", rows)
print(next_snapshot)
grown = s.merged(graph, next_snapshot)
for gate in ("030_snapshot_identity", "040_closure_monotonicity",
             "050_coverage_chain", "055_frontier_recorded"):
    print(gate, s.gate_rows(grown, K / "gates" / f"{gate}.rq") or "pass")
```

The proposed snapshot is epoch 1 superseding epoch 0, with one coverage in state `LIVE` whose standing is the literal `UNKNOWN` (never a stronger claim). All four gates then pass. As committed, the output ends:

```text
030_snapshot_identity pass
040_closure_monotonicity pass
050_coverage_chain pass
055_frontier_recorded pass
```

Gate `040_closure_monotonicity.rq` is the monotonicity court: every (capability, ABB) pair recorded in one snapshot must be present in the next, unless a receipted, reasoned retirement names it. To see it bite, propose an epoch 2 that supersedes epoch 1 and records no coverage:

```python
snap2 = """
@prefix ic: <https://seanchatmangpt.github.io/packs/industry-closure-ledger-pack#> .
<https://example.invalid/synthetic/snapshot/2> a ic:ClosureSnapshot ;
    ic:snapshotOf <https://example.invalid/synthetic/closure> ;
    ic:epoch 2 ;
    ic:supersedes <https://example.invalid/synthetic/snapshot/1> .
"""
print(s.gate_rows(s.merged(grown, snap2), K / "gates/040_closure_monotonicity.rq"))
```

The gate returns one row, `REFUSED:IC_CLOSURE_SHRINK`, for the epoch 1 coverage. Adding a retirement that has a reason and a receipt digest would make it pass; an unreceipted one is refused as `REFUSED:IC_RETIREMENT_UNRECEIPTED`.

## 6. Watch closure regress without disappearing

Now run the same step on `stage6-falsified-stale.ttl`:

```python
graph = s.world(K / "fixtures/closure-growth/stage6-falsified-stale.ttl")
rows = s.query_rows(graph, K / "queries/20-closure-frontier.rq")
print([(r["source"], r["state"], r["staleBecause"]) for r in rows])
for gate in ("050_coverage_chain", "090_standing_evidence"):
    print(gate, s.gate_rows(graph, K / "gates" / f"{gate}.rq"))
```

Here a coverage was recorded LIVE, and then FALSIFIED evidence arrived at the SBB's current exact subject. Three things follow, all visible in the output:

- The frontier query carries the coverage forward in state `STALE` with the reason `EVIDENCE_NOT_CURRENT`. It is kept, not deleted, so the ledger does not shrink.
- Gate `050_coverage_chain.rq` refuses the LIVE record with `REFUSED:IC_COVERAGE_EVIDENCE_FALSIFIED`. The fix is to mark it STALE with a reason, which is what `closure-next` proposes.
- Gate `090_standing_evidence.rq` refuses the evidence with `REFUSED:IC_EVIDENCE_FALSIFICATION_UNFED` until an OPEN residual exists to receive it. The derived residual (stage 6 in step 2) is that residual.

Evidence at an old subject is never joined, so history cannot rescue the current subject.

## 7. See where the requirements come from

Pass 1 is the enterprise side. Run its queries and templates over the synthetic enterprise supplied with the pack:

```python
E = s.PACKS / "enterprise-operating-model-pack"
ind = K / "qualification/project/ontology/industry-input.ttl"
ent = E / "qualification/project/ontology/enterprise-input.ttl"
graph = s.world(ind, ent, E / "ontology.ttl")
reqs = s.query_rows(graph, E / "queries/10-requirements.rq")
abbs = s.query_rows(graph, E / "queries/20-abb-skeletons.rq")
print(len(reqs), "requirement rows;", len(abbs), "skeleton rows")
print(s.render(E / "templates/abb-skeletons.ttl.tera", abbs))
```

The synthetic enterprise has chosen an operating model with high integration and high standardization. Each foundation element (a core process, a shared data domain, a linking automation) supports a capability, so the pack emits one requirement per element (three here) whose origin is the strategy, not prose. It emits a skeleton for each capability that has no building block yet (two here). Read the skeleton: the contract is `PENDING_HUMAN_APPROVAL`, claims authority `NONE`, stands `UNKNOWN`, and carries compliance criteria chosen from the two axes. Once a human merges the skeletons, the next run emits none: that is the fixed point.

## 8. Look at a real industry

The retail-lending profile packs real, pinned public sources. Compute its residual the same way:

```python
L = s.PACKS / "industry-closure-retail-lending-profile-pack"
graph = s.world(L / "ontology.ttl")
for row in s.query_rows(graph, K / "queries/10-residual.rq"):
    print(row["rid"], row["capabilityKey"], row["classCode"], row["standing"])
```

Nine in-scope requirements are `DEFICIT_ABB`. One, which asks for funds to be released autonomously with no human gate, is `DEFICIT_AUTHORITY` with standing `BLOCKED`. It will stay that way: a need for DO authority is a need, never a grant, and no pack here can close it. An out-of-scope requirement is absent from the residual but keeps its justification. This is the honest starting point: there are no building blocks, so nothing is covered.

## 9. Run the courts that guard all of this

```bash
python3 -m pytest tests/test_industry_closure_pack.py \
  tests/test_enterprise_operating_model_pack.py \
  tests/test_industry_closure_profile.py -q
```

Each gate runs under rdflib against a passing witness (zero rows) and a failing witness whose reasons must equal exactly the codes the gate declares. A code that no witness can trigger fails the court.

## With a real ggen

If you have installed the admitted ggen (`scripts/install-ggen.sh`), build a scratch consumer, run pass 1 (`enterprise-operating-model-pack`) then pass 2 (`industry-closure-ledger-pack`), run `ggen sync run` twice for each, and byte-compare `generated/**`. To try the real profile of step 8, copy the profile's `ontology.ttl` over the kernel's `ontology/industry-input.ttl` in the scratch consumer first; the exact commands, and the three checks to make afterwards, are in section 8 of [Add an industry to a closure](../how-to/add-an-industry-to-closure.md). Confirm the generated residual ledger agrees with the rdflib result above. The residual in step 8 is rdflib-only evidence: no overlay builds that profile through ggen, so until it is done on the exact subject, manufacture, execution and replay stay `UNKNOWN` or `BLOCKED:ggen_binary_unavailable`.

## Standing

State exactly what you did.

- You ran the gates and queries under rdflib on synthetic data and a real pinned profile. Semantic source, admission and the authority fence are `PARTIAL_ALIVE` for the packs, and the evidence for that is local rdflib courts.
- You rendered templates through a restricted Jinja2 proxy. That is partial evidence about template shape, not manufacture.
- The evidence in the fixtures is synthetic. Synthetic evidence can make the calculus show a capability as covered, but it can never support ALIVE for a real capability.
- Manufacture, execution and receipt or replay: `UNKNOWN`, or `BLOCKED:ggen_binary_unavailable` without a binary.
- Nothing here is ALIVE, no authority was granted, and no Level-5 claim is made. See [Standing](../reference/standing.md) and [Level-5 maturity contract](../reference/level5-maturity-contract.md).

## Next

- Triage a real residual: [Triage an industry-closure residual](../how-to/triage-an-industry-closure-residual.md).
- Bring a new industry in: [Add an industry to a closure](../how-to/add-an-industry-to-closure.md).
