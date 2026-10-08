# Ontology Maturity Mapping — Level 4 / Level 5 and the ggen Bridge

> Source: operator doctrine, 2026-10-08, v26.10.8 campaign. Codified verbatim
> as a reference artifact; the mapping table is the normative content.

## Coverage claim

Across the existing Semantic Web, formal logic, and standardization landscape
(W3C, IETF, OASIS, ISO, IEEE), approximately **50–60% of Level 4** can be
formally expressed using established ontologies today. Only **15–25% of Level
5** can be represented by current ontologies.

Primary constraint: OWL 2 / RDFS / SHACL rest on Description Logics
(SROIQ(D)) — decidable, open-world, static classification. Level 4 enters
confidential execution, process-mining alignment, and zero-knowledge claims
(standard vocabs exist or compose). Level 5 enters dependent types, linear
resource consumption, silicon typestates, and continuous self-modifying
process algebras — beyond first-order Description Logics; requires
constructive type theory or category-theoretic metalanguages.

## Mapping by maturity dimension

| Dimension | Representable today | L4 | L5 | Extension / theoretical limit |
|---|---|---|---|---|
| 1. Wire encoding & lexical safety | xsd:* datatypes, RDF datatypes, DFDL | 30% | 10% | DL limit: no struct offsets, zero-copy layouts, affine ownership. Pi/Sigma types need Coq/Lean/Agda. |
| 2. Execution sandboxing & compute typestates | PROV-O, IETF RATS (RFC 9334), EAT (RFC 9711) | 55% | 15% | Enclave/TEE states representable via RATS claims; silicon typestates need SVA/Chisel formal — no Semantic Web bindings. |
| 3. Ingress topology & inference scheduling | MAPE-K, TOSCA, WSMO/OWL-S | 45% | 15% | Static topology/SLA fully representable; KV-cache affinity and decentralized GPU scheduling are runtime algorithms, not taxonomies. |
| 4. Cryptographic identity & federation | VC 2.0, DID Core, RATS/EAT, NIST FIPS PQC taxonomies | 65% | 25% | VC/DID carry PQC keys + ZKP claims; quantum-secure mesh consensus lacks standard formalization. |
| 5. Receipts, non-repudiation, audit | PROV-O, IETF SCITT, BLONDiE, IEEE OCEL 2.0 | 75% | 40% | Highest maturity: receipts/Merkle derivations/DICE paths are native. L5 entropy binding needs sensor-ontology extensions. |
| 6. Testing, conformance, process mining | OCEL 2.0, ISO/IEC 15909 PNML, Declare/LTL ontologies | 70% | 20% | Replay-vs-Petri-net + LTL-via-SHACL-SPARQL supported; self-evolving algebras need inductive metaprogramming. |
| 7. Statutory governance & fiduciary defense | AIRO, VAIR, DPV, LegalRuleML, LKIF Core | 80% | 35% | EU AI Act Art. 9–15/50 formalized in AIRO/DPV/LegalRuleML; L5 legal-text-to-typestate compilation open. |

## The Level 4 core (compose, don't invent)

1. **Statutory governance (80%)** — AIRO (risk classes, Annex III, oversight),
   DPV (legal bases, processing, measures), LegalRuleML (deontic, defeasible,
   temporal validity). Seam: Article 14(4) oversight as a SHACL shape over an
   AIRO model checking `airo:HumanOversight` linkage before high-risk
   actuation.
2. **Enclaves & attestation (60–75%)** — RATS/EAT roles (Attester/Verifier/
   Relying Party) + PROV-O graph: execution result `prov:Entity`; confidential
   micro-VM `prov:SoftwareAgent`; enclave measurement `prov:HardwareAgent`;
   receipt via `prov:wasGeneratedBy` / `prov:qualifiedDerivation` anchored to
   silicon measurement.
3. **Process conformance (70%)** — OCEL 2.0 metamodel instantiates as OWL
   (events, objects, E2O/O2O); normative lifecycle as PNML; alignment
   diagnostics (model/log moves) as semantic graph diffs.
4. **Cryptographic claims (65%)** — VC 2.0 + DID: FIPS 204 keys and
   selective-disclosure ZK claims as credential-subject graphs.

## Where Description Logic fails (the gap to Level 5)

1. **Typestate / memory geometry.** No physical memory layout, cache
   locality, or affine ownership in OWL/SHACL. `A sqsubseteq B` is permanent;
   typestate consumption destroys state A to yield B — substructural (linear/
   affine) logics and dependent types, not DL.
2. **Autonomic self-modification (Gödel boundary).** OWL is open-world,
   monotonic: new triples never invalidate derived truth. Self-repair needs
   non-monotonic, defeasible, reflective metalogics; LegalRuleML models
   defeasibility but not real-time re-synthesis over distributed meshes.
3. **Complexity.** OWL 2 DL reasoning is N2ExpTime-complete; HermiT/Pellet
   over real-time routing violates sub-15 ms budgets.

## The ggen architectural bridge

1. **Standard ontologies own the Level 4 macro-contract**: statutory law
   (AIRO/DPV), business lifecycles (OCEL 2.0/PNML), cryptographic trust
   (VC/DID, RATS), topology (TOSCA) — RDF/OWL/SHACL.
2. **The compiler owns the Level 5 boundary**: ggen translates the DL graph
   into Rust typestates, WASM linear-memory layouts, and regular-grammar
   DFAs — never forcing OWL to execute affine memory management or enclave
   instruction sets.

Level 4 is deliverable today by this composition; Level 5 (2030 horizon)
requires the constructive-type-theory foundation the compiler boundary
preserves.

## See Also

- `docs/rust-wasm-elixir/CONSOLIDATION_MAP.md` — the pack consolidation this
  doctrine's bridge is implemented by (`rust-wasi-wasmex-pack`).
- `docs/sjira/v26.10.8/_INTEGRATION_RUNBOOK.md` — v26.10.8 campaign runbook.
