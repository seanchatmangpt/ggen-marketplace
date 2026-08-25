# How to extend the sensor factory

Add a new sensor specification only when it exposes a distinct failure or opportunity class. Reuse PROV-O for lineage, DQV for measurement, DCTERMS/DCAT for resource semantics, and ODRL for authority. Keep the specification in `ontology.ttl`; change templates only when the projection contract itself changes. Regenerate consequences with ggen and run `python3 tests/test_contract.py` before publication.
