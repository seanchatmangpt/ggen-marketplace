# Reference

## Sensor families

- `001-012`: subject identity, currentness, receipts/falsifiers, evidence independence, fanout, relief, reuse, concentration.
- `013-020`: standing, typed refusal, authority partition, ambient-DO refusal, replay.
- `021-031`: generator correspondence/drift, generation law, compatibility, exercised paths, duplication/orphaning, freshness, docs, CI evidence and failure domains.
- `032-036`: false-positive/false-negative pressure, precision, recall, E.
- `037-045`: M and memory ERRC: staleness, contradiction, provenance, reuse, rediscovery, reconstruction latency, provenance density, hypotheses.
- `046-050`: observed multiplier factors, independently receipted 10x thresholds, explicit 1000X proof/shortfall.

## Authority

The pack owns OBSERVE and VERIFY only. It does not SELECT consumers, CONSTRUCT repairs, or perform consequential DO. `actuationPerformed=true` is a detected violation, never an instruction.

## Public semantics

The local replication vocabulary specializes facts around PROV-O, DQV, DCAT, DCTERMS, and ODRL. Public terms carry provenance, measurement, catalog-resource, documentation, and authority semantics; the local namespace is limited to replication-specific measurements.
