# Packs admitted to main, 2026-09-20..2026-09-27

Snapshot taken as of 2026-09-27. One row per pack whose `packs/*/pack.toml` was added to
`main` in the window. Derived from the admitting commit (the merge or squash commit that
introduced `pack.toml` into `main`'s first-parent history); version and capability text are
taken verbatim from each pack's `pack.toml` (`version`, `description`). Where the
description runs longer than one line, the capability column quotes it verbatim, either in
full or by its opening sentence.

Derivation command:

```bash
git log main --since=2026-09-20 --diff-filter=A --name-only -- 'packs/*/pack.toml'
```

| Pack | Admitted by | Version | Capability |
|---|---|---|---|
| agent-harness-recompilation-pack | bf10f7bf0 | 26.9.25 | Reusable decomposition and replacement routing for external agent harnesses: adapters, security scanners, capability surfaces, learning, planning, verification, memory, hooks, and workflows mapped to existing marketplace/SA2A/planning/GALL/OCEL machinery with no ambient DO authority. |
| aloop-episode-ontology-pack | 8ce26baff | 0.1.0 | The ALOOP episode model as RDF: one ontology for an autonomous-execution episode (multi-agent, multi-provider) and the OCEL 2.0-shaped event/object vocabulary that instruments it. |
| ashdspy-pack | eefc832bb | 0.1.0 | The ash_dspy semantic vocabulary + violation gates as RDF: what a SemanticProgram, a Signature (typed input/output fields), a Metric, a Requirement, an Implementation on the 8-rung intelligence lattice, a CompiledRoute and a CourtVerdict are, such that DSPy generalizes: the IMPLEMENTATION of a Signature is absent from the contract and selected by court over an intelligence lattice (precedence 1..8, lower = lower intelligence = preferred when known). |
| collective-skill-court-pack | 5eb71f7ed | 26.9.24 | Semantic manufacturing contract for provenance-bound procedural skills projected into sJira work orders, SA2A candidates, and Oracle/NOP/mutation-qualified executable court families without DO authority. |
| delegation-admission-pack | 210629600 | 0.1.0 | Reusable semantic contract for judgment evidence derived from arXiv:2609.29473 and generalized into a delegation/admission calculus. |
| ecc-agent-harness-profile-pack | bf10f7bf0 | 26.9.25 | ECC supplier profile for the generic EPR and agent-harness recompilation packs. Pins affaan-m/ECC at exact SHA e482e579415fde18357cafce70f177ae19fd7f03, records the 461-unit census, and maps ECC source paths to the nine reusable harness part classes without granting semantic equivalence, authority, or standing. |
| environment-evolution-pack | 22b62f26a | 26.9.25 | Semantic contract for evidence-linked GymAct environment evolution: fixed-request state variants, counter-default decision points, causal event history, reference/evaluator updates, validation, and failure-feedback recurrence without ambient DO authority. |
| errc-ownership-manifest-pack | 2c2cdc425 | 26.9.25 | Canonical ownership declarations for exact-subject ERRC accounting. |
| evolvable-capability-pack | b130b3c40 | 0.1.0 | Ontology-backed manufacturing contract for evolve -> paired-evidence -> admit -> release -> freeze -> select. |
| external-paradigm-recompilation-pack | bf10f7bf0 | 26.9.25 | Generic External Paradigm Recompilation contract: exact-SHA supplier intake, VENDOR/WRAP/REPLACE/NOVEL_GAP classification, declared-target adjacency without equivalence laundering, novelty falsifiers, bounded authority, and qualification receipts before semantic standing. |
| governance-gate-pack | 8caba56e3 | 26.9.26 | Manufactures fail-closed governance gate contracts: admitted evidence, executable policy, explicit authority, prepared receipt, replayable consequence. Proposal/admission never imply authority. |
| greene-licensing-case-pack | 5942b1f4b | 0.1.0 | Licensing proposal packet for the strategic-doctrine executable lab, modeled as a canonical Semantic Case Study (cs:CaseStudy, semantic-case-study-pack). |
| interchangeable-parts-qualification-pack | bf10f7bf0 | 26.9.25 | Consequence-preserving interchangeable-parts qualification contract with exact immutable subjects, provenance, verifier evidence, replay, and no DO authority. |
| invariant-gate-pack | 96feba8c9 | 0.1.0 | Renders stdlib-only executable invariant gates for RDF-profile repos from declared ivg:InvariantCheck facts: a Python checker (exit 0 = all declared invariants hold, 1 = any violated) plus a positive/negative fixture harness (each mutated fixture copy must refuse, proving the gate is non-vacuous). |
| nist-cyber-resiliency-generational-pack | da24c7110 | 26.9.26 | NIST SP 800-160 Vol. 2 Rev. 1 cyber-resiliency semantic crosswalk plus an explicitly non-NIST generational-remanufacture profile. |
| nist-zero-trust-agentic-data-pack | 6cb77548d | 0.1.0 | NIST-rooted semantic crosswalk for zero-trust agentic data engineering and OLAP: SP 800-207/207A source-law anchors plus paper-derived graph, bounded-recovery, evidence-gating, promotion, provenance, and same-snapshot verification predicates. Semantic only; grants no execution authority. |
| pptx-presentation-pack | 05011be53 | 0.1.0 | Ontology-backed PowerPoint presentation manufacture: RDF presentation/slide/block facts -> ggen_igniter projections -> declarative deck JSON + PptxGenJS renderer with speaker notes. CONSTRUCT-only; generated PPTX bytes have no runtime or external standing by existence. |
| premature-actuation-survival-pack | be4c01716 | 26.9.25 | Declarative contract and refusal gates for long-horizon time-to-first-invalid-DO survival benchmarks: exact subject, authority, admission, receipt, terminal readiness, policy machinery, information topology, and fixed horizon without ambient actuation authority. |
| prior-art-admission-pack | 5ea152e64 | 0.1.0 | Machine-readable anti-reinvention law. Records required semantics, searched public prior art, reuse/compose/extend/novel-gap disposition, failed candidates and falsifier. NOVEL_GAP is invalid unless the prior-art search is discharged. |
| provider-extinction-contract-pack | 8ce26baff | 0.1.0 | The provider-neutral execution contract as RDF + violation-row gates: what an ExecutionRequest, an ExecutionProvider and an ExecutionReceipt are, such that a provider can go EXTINCT (be cancelled, rate-killed, sunset, replaced) while the work order survives unchanged. |
| qualified-capability-ecology-pack | ba3641dee | 0.1.0 | Canonical semantic contract for a qualified capability ecology: discover/classify -> candidate -> qualify -> freeze -> operate -> observe -> propose evolution -> requalify -> substitute -> retire. |
| sa2a-bridge-pack | afc850afc | 26.9.20 | Marketplace-first XaaS outer-control-plane to autofde-lab SA2A (Semantic Agent-to-Agent) BEAM-port bridge with generated contract, edge catalog, proof, SHACL and test projections. |
| sa2a-fastapi-pack | 420bc91e7 | 0.1.0 | Projects protocol-integration Capability semantics into a Python/FastAPI SA2A surface. It reuses the capability semantic definition, carries explicit observation/mutation/authority/receipt metadata, and refuses consequential capabilities that omit authority. |
| semantic-case-study-pack | aa2d67210 | 0.1.0 | Canonical Semantic Case Study vocabulary per engineering-standards RFC-0003: a case is a 9-tuple (Provenance, Claims, Evidence, AuthorityCeiling, Falsifiers, Projections, Receipts, Replay, Standing) as machine-addressable RDF. |
| semantic-parts-pack | cd7e394c9 | 0.1.0 | Evidence-bounded ontology for treating software artifacts as interchangeable semantic parts. Reuses PROV-O, DCTERMS and SKOS; CodeGraph observations may identify algorithms, domains, paradigms and design patterns, but discovery remains SELECT/CONSTRUCT with authority NONE until independent behavioral verification and authorized actuation. |
| semantic-procedural-graph-pack | 5ea152e64 | 0.1.0 | Reusable Semantic Procedural Graph vocabulary and SHACL law: stable procedure identity, typed transitions, projection bindings, prior-art claims, and fail-closed authority/receipt constraints for consequential edges. Structural admission never grants DO authority or execution standing. |
| shacl-to-fastapi-pack | 420bc91e7 | 0.1.0 | Projects admitted SHACL/Pydantic contracts into deterministic FastAPI route modules: real routing tables and typed request/response models whose handler bodies deliberately raise NotImplementedError until an application service supplies execution semantics. |
| shacl-to-zod-jsdoc-pack | 420bc91e7 | 0.1.0 | Projects admitted SHACL shapes into JavaScript Zod runtime schemas plus JSDoc typedefs, providing a no-TypeScript Next.js contract surface while preserving the SHACL graph as the sovereign schema. |
| shacl-to-zod-pack | 7f5621532 | 0.1.0 | Projects an admitted SHACL NodeShape into a JavaScript Zod schema while reusing shacl-projection-pack's sp:derivedFromShape / sp:isPrimaryOutput / sp:nullable law. |
| strategic-doctrine-pack | 6b63d5702 | 0.1.0 | Canonical strategic-doctrine graph (IRI https://ggen.dev/ontology/strategic-doctrine#, Turtle prefix sd:; '33S' is a display name only). One primitive algebra of 14 operators (shape, probe, conceal, reveal, concentrate, disperse, delay, accelerate, commit, withdraw, divide, combine, substitute, transform) with five declared duals; a 33-entry catalog that is this marketplace's own operationalization indexed by ordinal (own paraphrased titles <= 60 chars, own primitive compositions, no excerpts, no sd:quote), with operationalized entries carrying ordered steps and sd:Falsifier (subClassOf do:Falsifier) observations and the rest typed sd:CatalogEntry; world-model alignments to W3C ORG, PROV-O, schema.org, SOSA/SSN and OWL-Time (vendored copies with a sha256 materialization receipt); an explicit cs:NonClaim (not licensed, no endorsement, no text reproduced); SHACL shapes; six fail-closed SPARQL gates with an exact-stem gate-witness court and semantic runner; an entrant-world fixture; and a deterministic generated/catalog.json projection. Authority NONE, ceiling SELECT/CONSTRUCT, never DO. |
| swe-prometheus-governance-pack | e896ac36f | 0.1.0 | Semantic interchange contract for SWE-Prometheus-style repository retrofit evidence. |
| wd-failure-analysis-pack | 420bc91e7 | 0.1.0 | Semantic HDD failure-analysis overlay for exact drive/build/process subjects, evidence, failure-mode applicability, falsifiers, diagnostic actions, dispositions, corrective actions, and KNOWN/PARTIAL/UNKNOWN admission. Reuses public provenance/observation vocabularies and marketplace process/decision/standing semantics instead of redefining them. |

## Addendum: graphlaw packs, 2026-09-29..2026-09-30

Added 2026-09-30 on branch `graphlaw-full-representation`. Same derivation as above with the window
moved, run against this branch rather than `main`:

```bash
git log --since=2026-09-29 --diff-filter=A --name-only -- 'packs/*/pack.toml'
```

`chicago-graphlaw-court-pack`, `graphlaw-ash-capability-pack`, `qri-qualification-profile-pack`
and `wasi-json-abi-pack` carry the rust > wasm > beam/elixir representation of graphlaw v26.9.29;
`sa2a-semantic-evidence-pack` consumes the merged GraphLaw contract. See
[the pipeline reference](graphlaw-rust-wasm-beam-pipeline.md). Version and capability text are
verbatim from `pack.toml`.

| Pack | Admitted by | Version | Capability |
|---|---|---|---|
| chicago-graphlaw-court-pack | d52a79a53 | 26.9.29 | Manufacture Chicago-style GraphLaw ABI court test files (one #[test] per case) from an RDF case ontology. Evidence only: authority NONE. |
| graphlaw-ash-capability-pack | d52a79a53 | 26.9.30 | Projects a typed Elixir capability surface (behaviour, registry, per-operation modules, API, lossless result structs, reference docs, and a pure surface test) from the GraphLaw capability registry (schema graphlaw.capability-registry/1). Also projects typed value models (Lease, SignedLease, Receipt, Attestation, Plan, Action, PolicyEntry, PolicyOutcome) with tolerant :extra-preserving structs, informational enum lists, and a Limits module carrying scope, unit and source. Qualified by deterministic render and SPARQL gates over the registry RDF; not qualified by domain execution against the GraphLaw engine. Grants no execution authority. |
| qri-qualification-profile-pack | 7151ef9dc | 26.9.30 | Qualified Runtime Interchangeability (QRI) profile: a thin qualification/admission/substitution vocabulary over SOSA/SSN, PROV-O, ODRL, SPDX, QUDT and SHACL, with gates, witnesses and a ggen projection to WIT, a core-WASM JSON ABI adapter and a wasmex BEAM host. Grants no execution authority. |
| sa2a-semantic-evidence-pack | cb11b87b9 | 26.9.29 | Manufacture authority-free SA2A semantic evidence envelopes and admission surfaces from the merged GraphLaw v26.9.29 contract. |
| wasi-json-abi-pack | d52a79a53 | 26.9.29 | Generic WASI JSON-ABI module substrate: renders the FFI shell (\<prefix>_abi_version/_alloc/_free/_call with null/oversize guards and typed limit errors), ABI metadata (version, limits, op table, error codes), capability registry, op examples, cargo stack/profile fragments and an artifact-pin skeleton from an ontology of wja:WasmModule / wja:Op / wja:ErrorCode. Project specifics are ontology parameters supplied by the consumer. |

This file is a point-in-time record, not a standing guarantee; it does not claim that the
listed versions are still current.
