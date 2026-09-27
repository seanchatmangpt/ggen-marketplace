# CS2 Fleet Contract

Reusable cross-repository projection for RFC-CS2-001.

Producer: seanchatmangpt/ggen, examples/cs2-projections.
Consumers: ggen-marketplace (CS2-WRK-003), ash_a2a (CS2-WRK-012), XaaS (CS2-WRK-013).

The ontology in ontology/consumer-map.ttl is the marketplace mapping. Consumer repositories should consume generated projections rather than maintain independent CS2 subject/work mappings.
