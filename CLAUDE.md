# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

The canonical repository of reusable **ggen packs** — ontology-backed manufacturing/semantic
bundles consumed by the [ggen](https://github.com/seanchatmangpt/ggen) code-generation runtime.
A pack's manifest declares identity, RDF (`.ttl`) states admitted facts, templates (`.tmpl`/
`.tera`) may project those facts into consumer artifacts, and gates (`.rq` SPARQL / `.py`) may
refuse invalid inputs or verify pack-specific invariants. **Generated consumer files are
consequences of a pack; they are not a second source of truth and do not belong in this repo.**

`packs/` (82 packs) is the canonical, admitted corpus. There is also a `packages/` directory
(currently just `vision-2030-capability-generator`) from a separate branch of work — it does
**not** conform to the `packs/` contract and is not read by `scripts/marketplace.py`; treat it as
a distinct, not-yet-integrated surface rather than assuming marketplace tooling covers it.

## Commands

Validate/qualify a pack change (run in this order, from repo root, Python 3.11+):

```bash
python3 scripts/marketplace.py validate                        # schema + Diátaxis doc presence
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json    # deterministic catalog projection
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json    # run twice, must be byte-identical
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint                      # content fingerprint of admitted corpus
```

Full qualification (admits `marketplace.toml` through `star-toml`, installs the pinned ggen
binary, and runs every pack through it — mirrors CI):

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh /tmp/ggen-marketplace-admitted.json /tmp/ggen-marketplace-qualification.json
```

`admit-config.sh` builds `tools/marketplace-config` (a Rust binary depending on a pinned
`star-toml` git revision) to parse and admit `marketplace.toml` — that crate is the only Rust
code in the repo and exists solely to gate the marketplace's own config, not to run packs.

There is no single test suite to invoke with a test runner; correctness is proven by the
validate → catalog(x2) → fingerprint → qualify pipeline above, plus (when generation behavior
changes) exercising the affected pack with a real ggen runtime against an isolated consumer
project — CI/marketplace validation alone does not prove that.

## Architecture

- **`marketplace.toml`** — marketplace operational law (qualification worker/timeout bounds, the
  pinned ggen release + per-platform archive SHA-256s). Treated as raw/untrusted until
  `star-toml` admits it (`q_config=1` + witness); values here must never be duplicated by hand in
  shell/Python.
- **`packs/<name>/`** — one pack per directory, directory name must equal `[pack].name` in
  `pack.toml` (SemVer `version`, non-empty `description`). No symlinks are permitted anywhere
  under `packs/` (path-safety refusal in the validator).
  - `pack.toml` — identity manifest (required).
  - `*.ttl` at pack root, or recursively under `ontology/` — admitted RDF facts (at least one
    required). Simple packs use one `ontology.ttl`; larger project packs split RDF under
    `ontology/`.
  - `templates/*.tmpl` / `*.tera` — optional projection templates.
  - `gates/*.rq` — optional native SPARQL refusal gates; `gates/*.py` — optional pack-owned
    verifier gates for checks a SPARQL gate can't express.
  - `ggen.toml` — its presence marks a **project**-profile pack (self-contained ggen project).
- **Pack profile** is derived, not declared: `project` if `ggen.toml` exists, else `projection`
  if templates exist, else `semantic`. Profile is packaging shape only, not execution standing.
- **`scripts/marketplace.py`** — the local-first acceptance calculus: walks `packs/`, validates
  every manifest/RDF/template/gate against the contract above plus required Diátaxis doc
  presence, and derives (never hand-maintains) the catalog and a content fingerprint.
- **`docs/`** — strict [Diátaxis](https://diataxis.fr/) quadrants, each with a required-file list
  enforced by `marketplace.py validate` (`REQUIRED_DOCS`): `tutorials/` (learning), `how-to/`
  (task recipes), `reference/` (exact contracts — start with `docs/reference/pack-contract.md`
  and `docs/reference/repository-layout.md`), `explanation/` (rationale). Never collapse these
  into the README.
- **`.github/workflows/ci.yml`** — a read-only wrapper around the exact local commands above; it
  asserts it's qualifying the exact PR head SHA and refuses if qualification mutates the
  checkout. It cannot rewrite or push pack corrections.

## Working discipline (from AGENTS.md / CONTRIBUTING.md)

- Work on a purpose branch; never commit directly to `main`.
- One coherent change per contribution: add/update a pack, improve the marketplace contract, or
  improve one documentation need — not a mix.
- Never hand-maintain a second pack catalog; it is always `scripts/marketplace.py catalog`
  output.
- Never introduce `generated/` as a source namespace for marketplace metadata — generated
  consumer output is not pack source.
- When a pack's generation behavior changes, marketplace CI passing is not sufficient evidence;
  additionally validate with the matching ggen runtime against an isolated consumer project.
- When the marketplace contract changes, update every affected Diátaxis page and governance
  surface (`AGENTS.md`, `CONTRIBUTING.md`, `SECURITY.md`, relevant `docs/reference/*.md`) in the
  same change.
- Preserve exact provenance when moving pack source between repositories (see `MIGRATION.md`
  and `docs/reference/provenance.md` — the initial corpus was imported byte-for-byte from
  `seanchatmangpt/ggen` at a pinned commit).
