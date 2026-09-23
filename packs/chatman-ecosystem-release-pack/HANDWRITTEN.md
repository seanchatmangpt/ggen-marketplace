# HANDWRITTEN.md

Code in this pack that is not ontology, gate, template or generated projection. Every row is
`UNSUPPORTED(generator-capability)` with the reason no generator covers it. Vocabulary,
gates 070-085, the disposition rule and all six templates are pack capital, not residue.

| path | standing | reason | owner |
|---|---|---|---|
| `lift/manifest_to_er.py` | UNSUPPORTED(generator-capability) | ggen renders RDF into text; it does not parse TOML into RDF. No marketplace pack lifts TOML to RDF: star-toml-pack generates Rust config structs, and the tomllib users in autofde-semantic-registry-pack and the xaas public-ontology profile are not RDF importers. 32 lines of stdlib tomllib, deterministic, lifted-observation output only. | this pack (manifest-import step) |
| `bin/run-gates.py` | UNSUPPORTED(generator-capability) | Reused from `packs/gym-autonomic-crown-pack/bin/run-gates.py` and extended to union the consumer's `ggen.toml` imports and apply the templates' `construct:` rules. It is the second, independent executor (rdflib next to ggen's own engine) of the same gates; ggen has no mode that runs a pack's gates outside a consumer sync. | this pack |
| `qualification/qualify.sh` | UNSUPPORTED(generator-capability) | Qualification harness (real ggen, real rdflib, scratch copies; no mocks). The marketplace's `scripts/qualify_packs_r18.py` renders a pack once against `qualification/consumer.ttl` but has no mutant/expected-refusal contract. | this pack |

The fixture inputs under `qualification/` are byte copies or lifted observations of real sources,
not handwritten facts; `qualification/consumer-v26.9.23/SOURCES.md` records each source and sha256.
The two fixture-only choices (the target release's role names and constitutional mappings in
`consumer-v26.9.23/release.ttl`) are qualification data, not v26.9.23 release decisions.
