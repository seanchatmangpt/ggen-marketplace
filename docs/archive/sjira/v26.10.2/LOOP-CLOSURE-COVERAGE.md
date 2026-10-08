# Loop Closure Coverage — v26.10.2

Projection of the v26.10.2 milestone's per-hop standing (ggen_igniter
`docs/jira/v26.10.2/RECEIPT.md`, "Standing per hop") onto the marketplace pack
surface: which hop has marketplace coverage today, which does not, and what a
`sjira-loop-closure-pack` would close. Read-only documentation lane (F5);
the RDF graphs of the packs cited here are canonical over this page.

## Conserved tuple

Identity conserved across the transport boundary, verbatim from the v26.9.21
closure (`docs/sjira/v26.9.21/ECOSYSTEM-CLOSURE.md:18-26`; the tuple itself is
the text block at lines 20-26 — the dispatch sheet's `:24-30` pointer is off by
three lines against the file on disk):

```text
work_order_iri
+ checkpoint_iri
+ graph_digest
+ repository_identity
+ base_sha
```

No planner, UI, descriptor, lease, model, or workflow status is authority.
Consequential DO remains BRCE-only. Every hop row below preserves this tuple.

## Coverage table

Kernel standings are quoted from ggen_igniter `docs/jira/v26.10.2/RECEIPT.md`
("Standing per hop"), witness commits in parentheses. "—" = hop not on that
repo's path, same convention as the receipt.

| hop | kernel carrier (ggen_igniter) | kernel standing | marketplace pack coverage | gap a `sjira-loop-closure-pack` would close |
|---|---|---|---|---|
| admit | `semantic_jira.admit_candidates` (journaled; authority + `sj:admissionDigest` law, SJ-002) | ALIVE | PARTIAL — `sjira-marketplace-feedback-pack`: residual-to-work-order vocabulary (`mf:residualWorkOrder` -> `req:WorkOrder`, `mf:FeedbackReceipt`, gates `010`/`020`), spot-checked this pass | the admission law itself (`origin_authority` + `sj:admissionDigest`) is kernel-only; a pack would carry it as shapes + gates so consumers admit with the same law |
| order->pack | `GgenIgniter.SemanticJira.TargetPack` + gate `065_target_pack_contract.rq`; refusal registry entry 132 (f0c6f92) | ALIVE | NONE — no marketplace pack carries the `sj:targetPack` contract | the pack->order binding contract as RDF shapes, so a mismatch refuses at admission in any consumer, not only in the kernel |
| generate | pack shapes + gate `055_standing_projection.rq` (81df828) | ALIVE | PARTIAL — `sa2a-bridge-pack` (spot-checked: `s2b:EdgeSpec` chain, templates `sa2a_bridge_edges.ex.eex` etc.) and `semantic-projection-pack` (v26.9.21 PACK-MAP platform law) | one generated-artifact family (loop edges, standing events, receipts) instead of per-repo bridge templates |
| execute | local driver `GgenIgniter.SemanticJira.Execute` | ALIVE (local); fabric via xaas bridge | NONE, by design — `sa2a-bridge-pack` marks exactly one edge `doBoundary true` and generates no actuation; DO stays BRCE/repo-side | nothing: the execute hop's DO boundary is correctly pack-absent; the gap is only that no pack carries the execute-hop *contract* as data (edge names, receipt-before/after) |
| verify | fleet-R v2 validator ADMITTED; digest-pinned vendored schema (134b35c) | ALIVE | PARTIAL — `receipt-provenance-unification-pack` (spot-checked: `rp:Validator`, `rp:FieldBinding`, `qualification_runner.py` templates) and `semantic-gate-witness-court-pack` (PACK-MAP projection/evidence machinery) | the fleet-R v2 schema's promoted home is still open (RECEIPT.md parked item 5); a pack is the projection-of-record candidate the parked decision names |
| receipt | `GgenIgniter.SemanticJira.Bootstrap.Receipts.check/1` (fleet-R v2 + extension namespace) | ALIVE; ash_a2a PARTIAL_ALIVE (RProjection, d58f99f) | PARTIAL — `receipt-provenance-unification-pack` already unifies five hand-maintained receipt contracts plus `dfcm_fleet_v1` | fleet-R v2 as a sixth unified contract with its own generated validator, instead of a vendored schema pinned by digest only |
| promote | bridge suite 101/0 against the hex-published dependency | ALIVE | NONE — the promote hop has no pack and no RDF contract at all | the promote contract (hex/crate/npm floor + 101-test court) as data, so promotion is admittable, not narrated |
| plan-next | frontier projection (`050_frontier.rq`, `055_standing_projection.rq`) + journaled candidate | ALIVE — candidate journaled, not auto-admitted | PARTIAL — `planning-policy-pack` (FOND policy), `planning-federation-pack`, `sjira-marketplace-feedback-pack` (residual -> delta -> requalification) | the journaled-candidate schema (candidate order + standing ladder position + falsifier) as shapes, so a candidate is admittable downstream without re-modeling |

## Spot-checks (this pass, 2026-10-02)

Three pack ontologies were opened and read before being cited, per the lane
contract's spot-check rule (two required; three done):

- `packs/sjira-marketplace-feedback-pack/ontology.ttl` — real classes
  (`mf:MarketplaceCapabilityDelta`, `mf:FeedbackReceipt`, `mf:DeltaState`
  OPEN/QUALIFIED/REQUALIFIED) and properties (`mf:residualWorkOrder`,
  `mf:feedsDelta`, `mf:semanticJiraKey`, `mf:workOrderDigest`,
  `mf:authority`, `mf:deltaDigest`); `pack.toml` describes exactly the
  residual-to-work-order closure loop. Gates `010_residual_requires_work_order_and_delta.rq`
  and `020_feedback_requires_counterfactual_and_rank.rq` on disk.
- `packs/receipt-provenance-unification-pack/ontology.ttl` — `rp:ReceiptContract`,
  `rp:FieldBinding`, `rp:ValueForm`, `rp:Validator`,
  `rp:DelimiterDivergence`; explicit AUTHORITY BOUNDARY header (read-only
  validator + contract matrix; no runtime actuation authority); generates
  `unified_receipt_validator.py` + `receipt_contract_matrix.json` +
  `qualification_runner.py`; `dfcm_fleet_v1` contract transcribed with a
  sha256 pin.
- `packs/sa2a-bridge-pack/ontology.ttl` — `s2b:BridgeContract`,
  `s2b:EdgeSpec`, `s2b:ProofObligation`, `s2b:doBoundary`,
  `s2b:receiptBefore/After`; templates under `ggen_igniter/templates/`
  (`sa2a_bridge_edges.ex.eex`, `sa2a_contract.ex.eex`, `sa2a_mcp_descriptor.ex.eex`);
  README states the construct-only boundary (generated data modules vs
  hand-written `Port.open/2` wrapper in xaas). Downstream generated modules
  exist at `~/xaas/lib/xaas/generated/sa2a_bridge_edges.ex` and
  `sa2a_bridge_contract.ex`.

## What the pack would close, in one sentence

Today the eight loop hops are admittable only inside ggen_igniter's own pack
(`priv/ggen/semantic-jira-pack`); every other repo re-models its hop contract
by hand (xaas bridge, ash_a2a HILT, ash_pplan SjBridge). A
`sjira-loop-closure-pack` would carry all eight hop contracts as RDF shapes +
gates + templates once, so each repo projects its carrier module from the
same graph instead of hand-writing its slice — the same delta the v26.9.21
closure named for descriptors, now applied to the loop itself.

## Honest residues

- The dispatch sheet's line pointer for the conserved tuple
  (`ECOSYSTEM-CLOSURE.md:24-30`) does not match the file on disk; verified
  citation is `:18-26` (tuple block `:20-26`). The tuple content is identical.
- Kernel standings are quoted from RECEIPT.md, not re-run this pass; this page
  is a projection of that receipt, and its replay instructions stand.
- Pack coverage column: three ontologies spot-checked; the remaining packs
  named (`semantic-projection-pack`, `semantic-gate-witness-court-pack`,
  `planning-policy-pack`, `planning-federation-pack`) were verified to exist
  on disk at `packs/<name>/` but their ontologies were not opened this pass.

## See Also

- `docs/sjira/v26.9.21/ECOSYSTEM-CLOSURE.md` — conserved tuple source
- `docs/target-architecture.md` section 5 — fleet loop one-pager (same wave)
- ggen_igniter `docs/jira/v26.10.2/RECEIPT.md` — per-hop standing source
