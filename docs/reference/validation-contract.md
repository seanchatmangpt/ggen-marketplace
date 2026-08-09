# Reference: validation contract

`python3 scripts/marketplace.py validate` is the local acceptance entry point. It scans the complete corpus and prints the complete observed refusal set rather than stopping at the first defect.

It refuses when:

- `packs/` is absent or empty;
- a symlink appears under `packs/`;
- `pack.toml` is missing or malformed, or lacks `[pack]`;
- a pack name is empty, duplicated, or differs from its directory;
- a version is not SemVer;
- a description is empty;
- a pack has no Turtle/RDF source at its root or under `ontology/`;
- a visible template source is not `.tmpl` or `.tera`;
- `gates/`, when present, is not a directory or contains a visible source outside `.rq` / `.py`;
- a required Diátaxis document is absent or empty.

Dotfiles under template/gate directories are treated as scaffolding, not executable source. Refusals use `REFUSED:*` and exit code `2`. Success prints pack, RDF, template, gate, profile, and Diátaxis counts and exits `0`.

CI calls this same local command; CI is a wrapper, not a separate acceptance implementation.
