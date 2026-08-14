# Public semantic source materialization

This directory closes the `PublicSemanticSource -> retrieved bytes` edge for the AutoFDE semantic registry.

## Contract

`../ontology/*.ttl` is the canonical ggen semantic registry. External authorities remain external authorities. This directory records how an exact public source is acquired without silently turning a schema, taxonomy, protocol, or knowledge base into an ontology.

Each source is one of:

- `vendor`: redistribution is permitted and a stable machine-readable payload can be pinned in `vendor/<id>/`.
- `project`: a machine-readable public source is transformed into an RDF projection; the raw provider source is versioned separately and the generated projection is a consequence, not authority.
- `reference`: the source is publicly readable but redistribution/version/license is not yet sufficiently established for vendoring; only identity and retrieval metadata are stored until admitted.

A source may not become `ALIVE` merely because its URL resolves. `ALIVE` requires exact bytes, digest, version/identity, license standing, parser/validation result, and replay evidence.

## Replay

```bash
python3 materialize.py --manifest sources.lock.toml --dest vendor
```

The materializer is fail-closed: it refuses unpinned or non-vendorable entries rather than copying public-but-not-redistributable material.

## Sony/FDE scope

The corpus is intended to ground the complete Principal Forward Deployed Engineer surface: organization/stakeholders, enterprise architecture, SDLC/Secure-SDLC/AI-DLC, software/full-stack, APIs, cloud/IaC/Kubernetes, security/privacy/governance, telemetry/SRE, process/decision, data/lineage, AI/ML/LLM/RAG/agents/evaluation, software supply chain, media creation, audiovisual assets, production/post/distribution, intellectual-property/rights, preservation, accessibility, skills/certifications, cost/FinOps, and provenance/receipts.
