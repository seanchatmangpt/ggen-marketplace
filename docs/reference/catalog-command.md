# Reference: catalog command

```bash
python3 scripts/marketplace.py catalog
```

The command emits UTF-8 JSON to stdout with keys sorted deterministically. Records are sorted by pack identity and include:

- `name`, `version`, `description`, and repository-relative `path`;
- derived `profile` (`projection`, `semantic`, or `project`);
- ontology-file count and a deterministic SHA-256 fingerprint over ontology paths+bytes;
- template count;
- native-SPARQL gate count;
- verifier-gate count;
- SHA-256 of `pack.toml`.

The root object identifies schema `https://ggen.dev/marketplace/catalog/v1`.

The JSON is a projection and is intentionally not committed as a second editable catalog. Running the command twice at the same filesystem subject must produce byte-identical stdout.
