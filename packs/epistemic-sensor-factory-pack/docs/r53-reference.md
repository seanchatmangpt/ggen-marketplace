# Reference — R53 causal propagation observability

## Classes
`PropagationSeed`, `PropagationEdge`, `DownstreamOpportunity`, `CausalWitness`, `CounterfactualWitness`, `PropagationReceipt`.

## Required law
- exact source subject;
- returned receipt provenance;
- replay evidence before strong admission;
- independent target evidence root for causal witness;
- no transitive standing;
- no transitive authority;
- zero ambient consequential DO.

## Sensor tranche
`queries/r53/551_propagation_seed_census.rq` through `600_1000x_causal_admission_surface.rq`.

## Public semantics
PROV-O carries activity/entity/generation/influence provenance; DQV carries measurements; DCAT identifies repository resources; DCTERMS carries identifiers/types; ODRL fences execute authority.
