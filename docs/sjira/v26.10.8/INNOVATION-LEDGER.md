# Innovation Ledger — ERRC cross-product wave (2026-10-13, lanes X1–X20)

20 Explore lanes × ~3 candidates each (~59 total), cross-producting the
portfolio against the landed strata S1–S10 slices. Full candidate files:
/tmp/x{1..20}-innov.md. Ranked below by (leverage × grounding) — falsifiers
are the kill conditions, not implementation plans.

## Tier 1 — highest leverage, grounded in shipped code
1. **RDF-native fork states** (X2) — ledger state IS a graphlaw LawState; reorg = ancestor replay; S6 rollback machinery ELIMINATED structurally. Falsifier: heavier branch refusing under the LawState projection.
2. **Lean conservation witnesses** (X7) — mfact's proved Murata/P-invariant theorems × PN64 masks; `lake build` as a sync gate; `decide`-checkable ledger laws. Falsifier: wrong t05 mask fails admission.
3. **OCEL conformance receipts** (X4) — wasm4pm alignments × consensus behavior per block, chained conformance receipts feeding S10. Falsifier: alignment cost on S4-accepted traces.
4. **Attack-case fuzzing of S9 hardening** (X18) — mutate S10's known-attack seeds into corpus families against the S9 valve paths; sabotage-twin must discriminate. Closes S10's one open surface.
5. **Admission-time conservation pre-check** (X18) — S4 law at the S7 mempool wire boundary; eliminates block-time discovery of doomed txs.

## Tier 2 — strong, moderate integration cost
6. Constitutional-diff gate over consensus constants (X5 castle)
7. OCEL admission-chain log replacing markdown receipts (X5)
8. Config-as-chain-law + layered per-network profiles (X9 star-toml)
9. Hermetic multi-node gVisor network gym (X16 clnrm)
10. Doc-drift courts + living wiki (X15 deepwiki-rs)
11. SPARQL-queryable chain state (X10 unrdf kgc-4d)
12. Advected peer reflex / sync-as-replay (X6 insa; sub-200ns hot path)
13. Roadmap-as-spec-of-specs + consensus-law TTL (X14 spec-kit)

## Tier 3 — novel, higher integration cost
14. Actuated mempool / chain-validating reactor (X1 xaas Ash)
15. Lean fork-choice termination witness (X7)
16. POWL-script tx payloads (X4)
17.BUSL-safe unibit projections: ReceiptGate/BitFenwick/TierEscalation/ConsensusProgram (X3)
18. HTN reorg-recovery synthesis + block building (X8 koala-planner)
19. RedStrata adversarial gym / PartitionGym / ProcessMempool (X12)
20. Admitted peer reflex / attributed proposer identity (X6 insa)
21. TierLaw K8s + shared-query multi-language manufacture (X13 storehouse)
22. Lawful scaffold projection + standards upgrade protocol + release receipt chain (X20 praxis)
23. Gate-stalemate detector (X15)
24. GnoLedger / AdmissionDelta / AdmitOnCommit (X19 gno/gymact)
25. erlmcp strata-MCP server / sup-tree / evidence-reputation (X11)
26. LSP config-authoring courts (X9)
27. Plan-bound chain-state pruning (X17 oclnr)

## Dispositions
Next ticks: finish Tier-1 candidates in order (each is a bounded pack/lane
per the established pattern), re-certify, merge. This ledger is the
candidate pool; candidates die by their falsifiers, not by decree.
