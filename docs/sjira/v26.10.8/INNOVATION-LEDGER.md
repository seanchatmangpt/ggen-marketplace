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

## Tier 1 addendum — cross-cluster seams (Y6, verified file:line)
28. **FM-CHAIN-009 shared fixture** — golden fixture hand-transcribed in affidavit AND graphlaw; no shared artifact, no pin. Glue: one committed fixture + cross-repo byte-exactness test with tamper falsifier. (Partially addressed by T10's port — pin the fixture itself remains.)
29. **graphlaw RDFC-1.0 → wasm export** — ash_a2a's canonical_graph uses RDF.ex RDFC-1.0; graphlaw has the real RDFC-1.0 unwired (native/graphlaw_host unbuilt, test skips). Glue: wasm export + digest-equality court incl. blank-node relabelings.
30. **affidavit wasm ABI contract test** — available?/0 checks only function_exported?; never consumes abi_meta inventory/ABI version. Glue: contract test pinning assemble→verify round trip.
31. **strata↔affidavit receipt codec** — strata's 3381-byte ML-DSA-65 AttestationReceipt vs affidavit's 352-byte CTRT: unrelated formats, zero cross-refs. Glue: bidirectional codec + tamper falsifiers.
32. **sa2a vocabulary unification** — sa2a triplicated across graphlaw bins, affidavit ontology falsifiers, ash_a2a courts/state machine. Glue: one committed sa2a TTL all three consume; falsifier: receipt-not-success fires against a real standing_receipt.json.

**Cross-cutting pattern (Y6)**: every seam is a one-way hand-maintained
reference — affidavit names graphlaw/strata; ash_a2a names graphlaw/
affidavit; strata names nobody. Rigor exists within each repo, none
between them. Seams 28–32 are the loop's next finishing targets.
