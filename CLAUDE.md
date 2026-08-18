# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

The canonical corpus of reusable **ggen packs**. A pack is an ontology-backed manufacturing bundle:
`pack.toml` declares identity, RDF (Turtle) states admitted facts, templates may project those facts
into consumer artifacts, and gates may refuse invalid inputs or verify pack-specific invariants.
Generated consumer files are consequences of a pack; they are not a second source of truth and are
not committed here.

The ggen runtime itself lives elsewhere; this repo owns pack **source** and marketplace **documentation**
only. `python3 scripts/marketplace.py validate/catalog/fingerprint` proves marketplace admission and
deterministic catalog projection — it does **not** prove generated consumer behavior, external-system
behavior, or live-cloud authority. Read `AGENTS.md` before making structural changes; it is the
authoritative source hierarchy and discipline list.

## Commands

```bash
# Core validation loop (run before any PR)
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json      # catalog projection must be deterministic
python3 scripts/marketplace.py fingerprint

# marketplace.toml must be admitted through star-toml before installer/qualification scripts run
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh /tmp/ggen-marketplace-admitted.json /tmp/ggen-marketplace-qualification.json

# Python test suite (pytest, tests/ + scripts/test_*.py)
python3 -m pytest tests/ scripts/
python3 -m pytest tests/test_marketplace.py -k some_test   # single test

# Per-pack qualification against a real ggen runtime
python3 scripts/qualify_packs.py

# Consume a pack from a local checkout (in a consumer project's ggen.toml):
#   [packs]
#   <pack-name> = { path = "../ggen-marketplace/packs/<pack-name>" }
# then: ggen sync run
```

If a pack's generation behavior changes, marketplace CI is not sufficient evidence — also exercise it
with the matching ggen runtime against an isolated consumer project (replay/idempotency where
applicable).

## Architecture

### Pack profiles (`packs/<name>/`)

Every admitted pack requires `pack.toml` (SemVer, non-empty description), and at least one RDF Turtle
source at the pack root or under `ontology/`. `scripts/marketplace.py`'s `Pack.profile` derives the
profile structurally rather than from a declared field:

- **project** — has `ggen.toml` at its root (a self-contained ggen project: RDF, optional
  templates/rules/queries, pack-owned verification).
- **projection** — has `.tmpl`/`.tera` templates (manifest + RDF + templates projecting facts into
  consumer artifacts).
- **semantic** — everything else (manifest + RDF, optional gates/catalogs, no template requirement).

The directory name must equal `[pack].name`. `[pack]` itself is deserialized by the real ggen loader
with deny-unknown-fields — it admits **only** `name`/`version`/`description`; any additional key or
sub-table (e.g. lifecycle metadata) is refused at pack-load time even though `marketplace.py`'s own
cataloging is more lenient about extension tables. See `packs/clap-noun-verb-pack/pack.toml` for the
documented example of this gap.

Gates (`.rq` SPARQL or `.py`) may refuse invalid facts before generation; they live inside the pack
boundary, not centrally.

### Marketplace control plane vs. generation contracts

`marketplace.toml` declares marketplace-wide operational law (release tag, qualification worker
counts, timeout bounds, ggen release digests) and is executable only after admission through
`star-toml`/`admit-config.sh` — never hand-duplicate these values in shell/Python. Pack-level
`ggen.toml` files are ggen generation contracts; they are not part of the marketplace control plane.

### `scripts/marketplace.py` — local-first acceptance calculus

Single-file CLI (`argparse`, stdlib `tomllib` only — Python 3.11+) with four operations:
`validate`, `catalog`, `archive`, `fingerprint`. `inspect_marketplace()` walks `packs/`, builds a
`Pack` dataclass per directory, and is the shared source for all four commands — the catalog is a
deterministic **projection** over that walk (hence the a/b/cmp determinism check), not a
hand-maintained file. `catalog_record()` also computes a `sha256` digest over a synthesized pack
archive and a `download_url` pointing at this repo's rolling `packs` GitHub Release.

`REQUIRED_DOCS` in that file is the authoritative list of Diátaxis pages that must exist for the
marketplace itself to validate — check it before adding/removing top-level docs.

### Documentation — Diátaxis, strictly separated

- `docs/tutorials/` — learning journeys (start: `docs/tutorials/first-pack.md`)
- `docs/how-to/` — task recipes (e.g. `docs/how-to/publish-a-pack.md`)
- `docs/reference/` — exact contracts (e.g. `docs/reference/pack-contract.md`)
- `docs/explanation/` — architecture/rationale (e.g. `docs/explanation/why-a-separate-marketplace.md`)

Do not collapse these into one README; when the marketplace contract changes, update every affected
page across all four quadrants in the same change.

### Provenance

The initial corpus was imported byte-for-byte from `seanchatmangpt/ggen`; see `MIGRATION.md`.
Preserve exact provenance when moving pack source between repositories, and never commit
consumer-generated corrections as a substitute for fixing a pack's admitted RDF/template/gate/project
source.

## Working rules specific to this repo

- Branch before editing; never write directly to `main`.
- Never hand-maintain a second catalog — regenerate via `scripts/marketplace.py catalog`.
- Never introduce `generated/` as a source namespace for marketplace metadata.
- No symlinks under `packs/` — packs must be self-contained and path-safe.
- PR CI is read-only evidence; it must not rewrite or push pack corrections.
