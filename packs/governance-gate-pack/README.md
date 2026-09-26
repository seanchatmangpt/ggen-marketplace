# governance-gate-pack

Manufactures a deterministic, fail-closed governance-gate contract from semantic source.

The pack preserves five distinct states: proposal, admission, authority, prepared consequence, and receipted/replayable outcome. It never treats an approval request as authority and never treats authority alone as permission to cross DO. The generated classifier therefore complements BRCE rather than replacing it.

The pack also emits an executable information-obstruction falsifier: identical permitted observations with disjoint accepted-output sets produce `EVIDENCE_CEILING`. That is an observation-interface failure, not a model failure.

Public vocabulary is reused where it already carries the semantics: PROV-O for observations/consequences, ODRL for permission evidence, and EARL for verification. The `gg:` namespace is restricted to the profile relations not supplied by those standards.

Source order is `ontology.ttl -> SPARQL query -> ggen template -> generated contract`. Generated output is a projection and must not be hand-edited.
