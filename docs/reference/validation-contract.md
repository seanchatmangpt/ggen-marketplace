# Reference: validation contract

`python3 scripts/marketplace.py validate` is the local acceptance entry point.

It refuses when:

- `packs/` is absent or empty;
- a symlink appears under `packs/`;
- `pack.toml` is missing, malformed, or has a non-canonical top-level shape;
- a pack name is empty, duplicated, or differs from its directory;
- a version is not SemVer;
- a description is empty;
- `ontology.ttl` is missing;
- `templates/` is missing, empty, or contains a non-`.tmpl` file;
- `gates/`, when present, is not a directory or contains a gate source outside the admitted `.rq` native-SPARQL / `.py` verifier-gate allowlist;
- a required Diátaxis document is absent or empty.

Refusals use the prefix `REFUSED:` and exit code `2`. Success prints aggregate pack, manifest, template, native-gate, verifier-gate, and documentation counts and exits `0`.

CI calls this same local command; CI is a wrapper, not a separate acceptance implementation.
