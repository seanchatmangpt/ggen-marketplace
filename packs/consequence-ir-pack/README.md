# consequence-ir-pack

`consequence-ir-pack` is the protocol-neutral semantic kernel for the Chatman consequence production chain:

`O → O* → Π → μ → E → O' → V → R → replay/promotion`

It owns semantic distinctions and fail-closed laws, not a runtime. `ggen` remains the deterministic manufacturer; BRCE-compatible runtimes remain the exclusive consequential DO boundary.

## Why this kernel is small

The pack intentionally contains orthogonal primitives that recur across protocol, planner, gym, cloud, enterprise, formal-proof, and physical-world designs. Domain-specific vocabulary belongs in downstream packs. The kernel preserves the distinctions that must survive every projection:

- raw observation versus admitted observation;
- intent versus authority;
- SELECT / CONSTRUCT / DO;
- Knowledge Hook intent manufacture versus actuation;
- principal × action × subject × scope × policy authority;
- execution versus independent consequence observation and verification;
- receipt identity, parentage, standing ceiling, and replay;
- explicit reversibility / snapshot / compensation semantics;
- candidate cognition versus promoted deterministic machinery.

## Public-ontology grounding

The vocabulary reuses PROV-O for entities, activities, agents, plans, and provenance; SOSA for observations; ODRL for bounded permission; DCTERMS for identity metadata; SKOS for controlled concepts; and QUDT for declared information-loss quantities. `cci:` terms exist only where the consequence calculus needs relationships not supplied directly by those public vocabularies.

## Admission laws

The native SPARQL gates refuse:

1. incomplete execution closure;
2. DO on anything other than an `cci:Execution`, or DO without authority;
3. incomplete baseline authority grants;
4. incomplete receipts and ALIVE without consequence + verification;
5. admitted observations without raw-observation lineage;
6. promotions missing capability/evidence;
7. Knowledge Hooks that DO, masquerade as execution, or fail to manufacture intent;
8. replay that does not preserve receipt-bound intent or re-enter authorized DO;
9. authority missing principal/action/subject/scope/policy/evidence;
10. receipt parentage or standing-ceiling escalation;
11. missing or incomplete reversibility/recovery semantics;
12. promotion without two distinct ALIVE receipts, a falsifier, and promoted artifact;
13. unknown or multiple primary standing values.

`qualification/consumer.ttl` is a synthetic positive specimen used only by the marketplace ggen court. It is not an authority grant, customer observation, or external execution receipt.

## Combinatorial contract

Downstream packs should compose this kernel rather than clone it. Intended projections include MCP, A2A, LSP/LSIF, REST/gRPC, POWL/PDDL, GymAct gyms, AutoFDE cloud/runtime bundles, Lean/mfact proof obligations, OCEL evidence, digital twins, enterprise policy, and receipt/replay surfaces.

The kernel does not assert those projections are equivalent merely because they share vocabulary. Each composition needs its own verifier and receipt.
