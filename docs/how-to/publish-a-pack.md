# How to publish a pack

1. Create `packs/<name>/` with `pack.toml`, `ontology.ttl`, and at least one `templates/*.tmpl` file. Add `gates/*.rq` when invalid facts must refuse generation.
2. Keep `[pack].name` exactly equal to the directory name and use a SemVer version.
3. Put facts in RDF rather than embedding a second semantic model in generated consumer files.
4. Run `python3 scripts/marketplace.py validate`.
5. Exercise the pack with the matching ggen runtime in an isolated consumer and verify a second sync is stable.
6. Open a purpose-branch PR describing the behavioral claim, verification, provenance, falsifiers, and rollback.

Do not edit or commit a hand-maintained marketplace catalog; the catalog command derives it from pack manifests.
