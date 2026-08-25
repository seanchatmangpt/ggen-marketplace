# Reference

## Public semantic surface

The pack uses PROV-O for causal lineage, DQV for observations, and DCTERMS for identity/documentation. Its local `cpc:` vocabulary names control-plane-specific predicates while preserving public provenance semantics.

Core classes: `cpc:Request`, `cpc:WorkflowRun`, `cpc:Receipt`, `cpc:MemoryRecord`, `cpc:Observation`.

Identity and correspondence: `cpc:requestId`, `cpc:headSha`, `prov:used`, `prov:wasGeneratedBy`, `cpc:exactSubjectPresent`, `cpc:provenancePresent`.

Currentness and standing: `cpc:current`, `cpc:terminal`, `cpc:standing`, `cpc:archived`, `cpc:contradicted`.

Control quality: `cpc:queuedSeconds`, `cpc:latencySeconds`, `cpc:triggerPathMatched`, `cpc:concurrencyGroup`, `cpc:relevantToRequest`, `cpc:changed`.

Evidence/authority: `cpc:receiptPresent`, `cpc:independentEvidenceRoot`, `cpc:actuationPerformed`.

## Court families

001–012: request/receipt symmetry, latency, stale state, exact identity, provenance, fanout, authority.
013–024: duplicate/currentness/provenance correspondence and exact-head integrity.
025–043: terminal standing, ALIVE validity, metric validity, required identifiers, currentness.
044–049: fanout/receipt density and request↔receipt currentness disagreement.
050: positive clean causal-chain crown.

Authority is `OBSERVE|VERIFY|CONSTRUCT`; consequential DO is excluded from this pack.
