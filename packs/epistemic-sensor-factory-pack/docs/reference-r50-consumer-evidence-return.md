# Reference: R50 consumer evidence-return protocol

## Identity fields

`consumer_repo`, `consumer_head`, `producer_court_head`, `receipt_digest`, `return_source`, and `returned_at` identify the returned evidence subject.

## Standing fields

`consumerStandingValue` is evidence about the consumer only. `producerStandingValue` records the producer's assimilation result and must not be inferred from consumer authority. `evidenceRootCount` and `replayVerified` constrain admissibility.

## Sensor range

Queries `350`–`399` cover receipt/standing censuses, missing assimilation, replay gaps, evidence-root independence, exact identity, duplicate/orphan evidence, return provenance, producer-court fanout, standing conversion, clean-current frontier, unresolved opportunities, ambient actuation, and the observed independent-consumer 10x shortfall.

## Authority

The ontology reuses PROV-O, DQV, DCAT, DCTERMS, and ODRL. ODRL permits read/derive and prohibits execute. Returned evidence is OBSERVE/VERIFY material; it conveys no ambient SELECT, CONSTRUCT, or DO authority.

## Generated consequence

`ggen.toml` projects the ontology-defined return protocol through query `400_evidence_return_protocol.rq` and `templates/evidence-return-protocol.json.tera`. Generated output is a consequence, not an editing surface.
