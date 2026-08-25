# Reference: R51 transitive consumer propagation

## Public semantic substrate
PROV-O models plans, activities, derivation, generation, exact generations, and evidence use. DCAT identifies target resources. DQV carries standing and metric values. DCTERMS carries identifiers/types. ODRL prohibits execute authority in the measurement pack.

## R51 domain vocabulary
`PropagationEdge`, `TransitiveTarget`, `PropagationReceipt`, `PropagationCompiler`, and `PropagationStanding` express the software-manufacturing-specific projection. Core properties are `propagatesFrom`, `propagatesTo`, `propagationDepth`, `fanout`, `closureVerified`, and `cycleDetected`.

## Standing rule
A propagation plan is not consumer ALIVE evidence. ALIVE requires observed execution against the exact admitted downstream subject.
