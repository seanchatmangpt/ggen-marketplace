# Contributing

Contributions should change one coherent marketplace boundary at a time: add or update a pack, improve the marketplace contract, or improve one documentation need.

## Before editing

Read [`docs/reference/pack-contract.md`](docs/reference/pack-contract.md) and the relevant how-to guide. For imported packs, preserve existing semantics unless the purpose of the change is explicitly a behavioral upgrade.

## Pack changes

A pack contribution must keep its manifest, ontology, templates, and optional gates self-contained under `packs/<pack-name>/`. The directory name must equal `[pack].name`; versions use SemVer; descriptions must be non-empty. Never commit consumer-generated corrections as a substitute for fixing the ontology/template/gate source.

Run:

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog.json
```

If generation behavior changes, also validate the pack using the matching ggen runtime in an isolated consumer project. Marketplace CI cannot substitute for that behavioral evidence.

## Documentation changes

Place learning journeys in `docs/tutorials/`, task recipes in `docs/how-to/`, exact contracts in `docs/reference/`, and architecture/rationale in `docs/explanation/`. Do not collapse the quadrants into one giant README.

## Pull requests

Explain what changed, why, the affected packs, provenance for migrated content, commands executed, observed outcomes, residual boundaries, rollback, and the exact head being qualified. PR CI must remain read-only.
