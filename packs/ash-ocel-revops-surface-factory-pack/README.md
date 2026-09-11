# Ash / OCEL RevOps semantic exploration pack

This pack preserves the ontology and SPARQL candidate-surface corpus produced by the original EXPLORE run. It is intentionally a **semantic** marketplace pack, not an executable project profile.

The removed `ggen.toml` referenced a non-existent `templates/` tree and a non-existent `queries/20-migration-surfaces.rq`. Keeping that file would advertise an executable manufacture path that the pack did not contain.

Executable Ash/RevOps manufacture is owned by `ash-revops-structural-factory-pack`, which carries the current `ggen.toml`, templates, admission gates, deterministic-regeneration tests, and generated-surface tests. This pack remains useful as the broader option/candidate vocabulary and can be composed as ontology input without pretending to own runtime generation.

## Authority boundary

The ontology and queries are SELECT/CONSTRUCT inputs. They do not grant provider or application DO authority. A consumer that needs executable Ash artifacts must select an executable manufacturer and independently qualify the exact generated subject.
