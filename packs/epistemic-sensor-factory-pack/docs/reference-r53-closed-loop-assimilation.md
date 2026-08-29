# Reference: R53 closed-loop assimilation

## Public semantic substrate

R53 reuses PROV-O for activity/provenance, DQV for standing/quality measurements, DCAT for repository targets, DCTERMS for identifiers/types, and ODRL for the read/derive/no-execute authority policy.

## Source surfaces

- `ontology.ttl`: `QualifiedConsumerReceipt`, `StandingTransition`, `ReplicationWave`, `WaveCandidate`, `ClosedLoopAssimilationCompiler`.
- `queries/451_*` through `queries/500_*`: receipt qualification, transition, wave, multiplier, and falsifier sensors.
- `queries/501_*` and `queries/502_*`: deterministic ggen projection inputs.
- templates `closed-loop-assimilation-plan.json.tera` and `next-wave-plan.json.tera`: generated consequence schemas.
- `fixtures/r53-closed-loop-consumer-assimilation.ttl`: exact grounded subject evidence.

## Standing law

`ALIVE` requires exact executed consumer evidence plus replay and merge containment. Producer observation alone is insufficient. Generated plans grant no consequential authority.
