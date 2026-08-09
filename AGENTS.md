# Agent instructions — ggen Marketplace

## Mission

Preserve this repository as the canonical, reviewable corpus of reusable ggen pack source. Prefer deterministic manufacture and fail-closed validation over duplicated metadata or generated-output ownership.

## Source hierarchy

1. `marketplace.toml` declares marketplace operational law and must be admitted through `star-toml` before installer/qualification execution.
2. `packs/<name>/pack.toml` declares pack identity.
3. `packs/<name>/ontology.ttl` carries admitted RDF facts.
4. `templates/` projects those facts.
5. `gates/` may refuse invalid facts before generation.
6. Pack/project `ggen.toml` files remain ggen generation contracts; they are not the marketplace control plane.
7. Consumer outputs are generated consequences and do not belong here unless they are themselves explicit pack source fixtures.

## Required discipline

- Work on a purpose branch; do not write directly to `main`.
- Keep pack directory name identical to `[pack].name`.
- Do not hand-maintain a second catalog. Use `python3 scripts/marketplace.py catalog`.
- Do not introduce `generated/` as a source namespace for marketplace metadata.
- Do not use symlinks under `packs/`; marketplace packs must be self-contained and path-safe.
- Do not let CI rewrite or push pack corrections. PR CI is read-only evidence.
- Do not duplicate ggen release versions, platform asset names, SHA-256 digests, qualification worker counts, or timeout bounds in shell/Python. They belong in `marketplace.toml` and are executable only after `star-toml` admission.
- Keep Diátaxis categories distinct: tutorials teach, how-to guides solve tasks, reference specifies, explanation develops understanding.
- Preserve exact provenance when moving pack source between repositories.

## Validation

Run before publication:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh /tmp/ggen-marketplace-admitted.json /tmp/ggen-marketplace-qualification.json
```

`marketplace.toml` is raw observation until `star-toml` returns `q_config=1` with a witness. A green marketplace validator proves the repository contract only. Consequential pack behavior should additionally be exercised with the matching ggen runtime and a real consumer boundary when that behavior is changed.
