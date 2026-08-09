# consequence-ir-pack

`consequence-ir-pack` is the protocol-neutral semantic kernel for the Chatman consequence production chain:

`O → O* → Π → μ → E → O' → V → R → promotion`

The pack deliberately owns semantics and refusal laws, not a runtime. `ggen` remains the deterministic manufacturer; BRCE-compatible runtimes remain the exclusive consequential execution boundary.

## Public-ontology grounding

The vocabulary reuses PROV-O for entities, activities, agents, plans, and provenance; SOSA for observations; ODRL for bounded permission; DCTERMS for identity metadata; SKOS for controlled concepts; and QUDT for declared information-loss quantities. `cci:` terms exist only where the consequence calculus needs relationships not supplied directly by those public vocabularies.

## Admission laws

The native SPARQL gates refuse:

1. incomplete execution closure;
2. DO on anything other than an `cci:Execution`, or DO without authority;
3. incomplete authority grants;
4. incomplete receipts and ALIVE without consequence + verification;
5. admitted observations without raw-observation lineage;
6. cognition-to-determinism promotion without capability + prior receipt.

`qualification/consumer.ttl` is a synthetic positive specimen used only by the marketplace ggen court. It is not an authority grant, customer observation, or external execution receipt.

## Intended compositions

This pack is designed to become the common source for later protocol, gym, cloud, formal-proof, enterprise, and receipt projections. Those are separate packs/courts; they should depend on this semantic kernel rather than copy it.
