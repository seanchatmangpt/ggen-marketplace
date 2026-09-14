# semantic-documentation-contract-pack

Canonical source is `ontology.ttl`. This README is explanatory only.

The pack defines revision-bound semantic documentation where compiler/source evidence and provenance are RDF facts and prose/C4/Diataxis/agent context are non-sovereign projections. It reuses PROV-O for derivation and `semantic-projection-pack` vocabulary for sovereignty instead of creating parallel concepts.

Qualification is repository-native: `scripts/qualify_packs.py` unions `qualification/consumer.ttl`, executes native gates through the real ggen runtime, runs twice, and requires deterministic filesystem convergence. The pack's own `ggen.toml` additionally projects Open Ontologies community-pack metadata and the default projection bundle; those generated files are consequences and are not source.

Standing is intentionally bounded. The ontology names the exact `deepwiki-rs` semantic-compiler head as `PARTIAL_ALIVE`; Open Ontologies validation remains `UNKNOWN` until a real `open-ontologies validate` execution receipt exists. Nothing in this pack grants DO authority.
