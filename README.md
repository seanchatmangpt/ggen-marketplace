# ggen Marketplace

Reusable deterministic capability packs for ggen.

## Vision 2030 Capability Generator

`packages/vision-2030-capability-generator` compiles an admitted RDF capability graph into a Vision 2030 architecture, a machine-readable capability index, and a Mermaid capability graph.

```text
ontology.ttl -> SPARQL -> ggen -> generated/VISION_2030.md
                               -> generated/capability-index.json
                               -> generated/capability-graph.mmd
```

The initial ontology contains 50 non-trivial capabilities across 10 families. The pack is CONSTRUCT-only: it manufactures architecture artifacts and never grants runtime DO authority. Generated output does not receive standing merely by existing.

Validation:

```bash
python packages/vision-2030-capability-generator/scripts/verify.py
cd packages/vision-2030-capability-generator
ggen sync run
```

The Python verifier is an independent structural admission court. `ggen sync run` remains the production manufacture boundary.