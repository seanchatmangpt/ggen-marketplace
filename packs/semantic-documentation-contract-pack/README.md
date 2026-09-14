# semantic-documentation-contract-pack

Canonical source is `ontology.ttl`. This README is explanatory only.

The pack defines revision-bound semantic documentation where compiler/source evidence and provenance are RDF facts and prose/C4/Diataxis/agent context are non-sovereign projections. It reuses PROV-O for derivation and `semantic-projection-pack` vocabulary for sovereignty instead of creating parallel concepts.

The Rustdoc-specific terms (`RustItem`, `DocFragment`, spans, references, and their properties) are part of this same canonical vocabulary; `deepwiki-rs` PR #1 at exact head `fc0f287ad5b1313965de2df64771af543dcb8a85` emits this namespace directly. `gates/050_core_vocabulary.rq` refuses ontology/emitter drift where a required term is no longer defined.

Qualification is repository-native: `scripts/qualify_packs.py` unions `qualification/consumer.ttl`, executes native gates through the real ggen runtime, runs twice, and requires deterministic filesystem convergence. The pack's own `ggen.toml` additionally projects Open Ontologies community-pack metadata and the default projection bundle; those generated files are consequences and are not source.

Standing is intentionally bounded. The ontology names the exact `deepwiki-rs` semantic-compiler head as `PARTIAL_ALIVE`; `open-ontologies validate` is validation only, while Open Ontologies SHACL is a separate admission boundary and remains `UNKNOWN` until actually executed. Nothing in this pack grants DO authority.
