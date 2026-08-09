# Explanation: source of truth

A pack should answer “what is admitted?” before it answers “what file was emitted?”. RDF is the semantic source, the manifest gives pack identity, templates project admitted facts, and gates reject invalid facts before writes.

This is why the marketplace does not keep a hand-edited `catalog.json`. Such a file would duplicate manifest facts and eventually drift. Instead, `scripts/marketplace.py catalog` computes a deterministic projection whenever a machine or human needs catalog JSON.

The same principle applies to consumer outputs: when an emitted file disagrees with the pack source, fix the ontology/template/gate boundary and regenerate rather than blessing the drift in place.
