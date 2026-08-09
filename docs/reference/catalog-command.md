# Reference: catalog command

```bash
python3 scripts/marketplace.py catalog
```

The command emits UTF-8 JSON to stdout with keys sorted deterministically. Records are sorted by pack directory/name and include:

- `name`
- `version`
- `description`
- repository-relative `path`
- template count
- gate count
- SHA-256 of `pack.toml`
- SHA-256 of `ontology.ttl`

The root object identifies schema `https://ggen.dev/marketplace/catalog/v1`.

The JSON is a projection and is intentionally not committed as a second editable catalog. Running the command twice at the same filesystem subject must produce byte-identical stdout.
