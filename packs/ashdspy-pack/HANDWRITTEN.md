# HANDWRITTEN.md — ashdspy-pack

The pack IS the authored surface (法面): every file below is hand-authored
RDF or hand-authored gate SPARQL, manufactured once, so consumers never
hand-write an implementation-lattice contract again. No generated files
ship; nothing here is a projection of another source, so there is no
reconciliation manifest.

| path | what | why hand-authored (once) | date |
|---|---|---|---|
| pack.toml | pack admission record + explicit NOT-claimed authority boundary ("Declarative facts + gates only. No runtime, no actuation authority; compiled routes are candidates until admitted by external machinery (SA2A/BRCE).") | pack authorship is the marketplace's lawful write surface | 2026-09-25 |
| ontology.ttl | SemanticProgram/Signature/Input/Output/Metric/Requirement vocabulary, the 8-rung intelligence lattice (Reuse..LLM with precedence 1..8), CompiledRoute + CourtVerdict (earl:TestResult subclass, prov:Entity route), RetirementRule, Trace, ticket-triage worked fixture | one-time ontology authorship; `ashdspy:` minted only after the failed-edge record against prov / earl / dcterms / oslc_cm / SHACL (recorded in-file) | 2026-09-25 |
| gates/010_closed_lattice.rq | violation-row gate: an Implementation outside the 8 lattice subclasses (bare base typing, or routed with no lattice type) is a violation naming it | gate authorship is pack authorship; fires via FM-PACK-013 in consumers | 2026-09-25 |
| gates/020_court_required_before_select.rq | violation-row gate: a CompiledRoute without a CourtVerdict is a violation | same | 2026-09-25 |
| gates/030_known_implies_no_llm.rq | violation-row gate: an LLM-selected route over a Signature whose non-LLM implementation holds a passing CourtVerdict (KNOWN => Allocation_LLM = 0) | same | 2026-09-25 |
| gates/040_receipt_shape.rq | violation-row gate: CompiledRoute missing evidenceDigest, or verdict missing verdictDigest | same | 2026-09-25 |
| templates/lattice_summary.json.tmpl | projects programs, routes and all four gate verdicts to generated/lattice_summary.json in a consumer sync | pack ships >= 1 template (FM-PACK-005, witnessed by real ggen sync); the render is the consumer-facing projection of the gates | 2026-09-25 |
| qualification/fixtures/pos_ticket_triage_clean.ttl | conforming consumer graph (consumer namespace) — all gates 0 rows | anti-vacuity positive half | 2026-09-25 |
| qualification/fixtures/neg_open_lattice_implementation.ttl | bare-typed + routed-untyped implementations — gate 010 fires 2 rows | anti-vacuity negative half (mutated input must be refused) | 2026-09-25 |
| qualification/fixtures/neg_route_without_verdict.ttl | route with an orphan verdict not attached — gate 020 fires 1 row | same | 2026-09-25 |
| qualification/fixtures/neg_llm_despite_known.ttl | LLM route over a signature with a passing rule rung — gate 030 fires 1 row | same | 2026-09-25 |
| qualification/fixtures/neg_route_missing_digests.ttl | route + verdict without digests — gate 040 fires 2 rows | same | 2026-09-25 |
| QUALIFICATION.md | witnessed evidence: dual-engine clean/violating matrix, real-binary FM-PACK-013 refusals, marketplace validate + catalog determinism | evidence recorded at pack birth, replayable from the scratch run record | 2026-09-25 |

Ledger position: zero 産面 bytes. No consumer repo was touched by authoring
this pack (the falsifier harness lives in the lane scratch dir and runs
read-only against this repo via ggen_igniter's mix, MIX_BUILD_ROOT-isolated).
The ticket-triage individuals are fixture DATA, not authority. NOT claimed
(see pack.toml): court execution, implementation selection policy beyond the
precedence law, lattice extension, metric computation, any actuation.
