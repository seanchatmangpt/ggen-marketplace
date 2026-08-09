# Contributing

Contributions should change one coherent marketplace boundary at a time: add or update a pack, improve the marketplace contract, or improve one documentation need.

## Before editing

Read [`docs/reference/pack-contract.md`](docs/reference/pack-contract.md) and the relevant how-to guide. For imported packs, preserve existing semantics unless the purpose of the change is explicitly a behavioral upgrade.

## Pack changes

Every admitted pack must keep its manifest and RDF authority self-contained under `packs/<pack-name>/`. Projection packs additionally carry templates; semantic packs may intentionally omit templates; project packs may carry `ggen.toml`, split RDF under `ontology/`, templates, queries, rules, fixtures, and pack-owned verification surfaces. Optional gates remain inside the pack boundary.

The directory name must equal `[pack].name`; versions use SemVer; descriptions must be non-empty. Never commit consumer-generated corrections as a substitute for fixing the pack's admitted RDF, template, gate, or project source.

Run:

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
```

If generation behavior changes, also validate the pack using the matching ggen runtime in an isolated consumer project and verify replay/idempotency where applicable. Marketplace CI cannot substitute for that behavioral evidence.

## Documentation changes

Place learning journeys in `docs/tutorials/`, task recipes in `docs/how-to/`, exact contracts in `docs/reference/`, and architecture/rationale in `docs/explanation/`. Do not collapse the quadrants into one giant README.

When the marketplace contract changes, update every affected Diátaxis page and governance surface in the same transition so tutorial convenience never silently contradicts reference law.

## Pull requests

Explain what changed, why, the affected packs, provenance for migrated content, commands executed, observed outcomes, residual boundaries, rollback, and the exact head being qualified. PR CI must remain read-only.
