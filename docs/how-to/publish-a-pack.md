# How to publish a pack

1. Create `packs/<name>/pack.toml` with matching name, SemVer version, and a non-empty description.
2. Add admitted RDF source as root `*.ttl` files or under `ontology/`.
3. If the pack projects files, add `.tmpl` or `.tera` templates under `templates/`. A semantic-only pack may omit templates.
4. Add `gates/*.rq` for native SPARQL refusal or bounded `gates/*.py` verifier programs when the pack's own procedure requires them.
5. Use `ggen.toml` when the pack is a self-contained ggen project rather than a simple imported pack.
6. Run `python3 scripts/marketplace.py validate`.
7. For generation behavior, exercise the pack with the matching ggen runtime and verify a second manufacture is stable.
8. Open a purpose-branch PR describing claim, evidence, provenance, falsifiers, and rollback.

Do not hand-edit a marketplace catalog; derive it with `python3 scripts/marketplace.py catalog`.
