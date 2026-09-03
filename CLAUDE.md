# CLAUDE.md

This file provides guidance to Claude Code when working in this repository. `AGENTS.md` is the authoritative repository doctrine; when the two differ, follow `AGENTS.md` and repair this file.

## What this repository is

The canonical corpus of reusable **ggen packs** and their marketplace qualification/documentation plane. A pack is an ontology-backed manufacturing contract:

```text
identity + semantic source + admission + projection/project rules
    → bounded manufacture
    → consumer consequence
    → verification / receipt / replay / standing
```

`pack.toml` declares identity, RDF/Turtle carries semantic authority, templates/project rules manufacture consequences, and gates may refuse invalid inputs. Generated consumer files are consequences, not a second source of truth.

The ggen runtime lives elsewhere; this repository owns canonical pack source, marketplace operational law, qualification, and documentation. Marketplace validation/qualification does **not** prove every generated consumer, external system, benchmark, or production actuation boundary.

## Canonical command sequence

Admit marketplace operational configuration first:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
```

Then run repository acceptance:

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

Additional useful courts:

```bash
python3 -m pytest tests/ scripts/
python3 scripts/qualify_packs.py --report /tmp/pack-qualification.json
```

Do not hardcode current ggen release versions, commits, platform asset names/digests, worker counts, or timeout bounds in scripts/docs. `marketplace.toml` is the canonical operational source and becomes executable only after admission.

If pack behavior changes, marketplace CI is insufficient evidence by itself. Exercise the matching real consumer/runtime boundary and replay/idempotency for the exact subject.

## Packaging profiles

Every admitted pack requires `pack.toml` (matching name, SemVer, non-empty description) and at least one Turtle source at the pack root or under `ontology/`.

The marketplace derives packaging shape:

- **project** — `ggen.toml` exists at the pack root;
- **projection** — templates exist;
- **semantic** — no project file/templates required.

A packaging profile is not a maturity level or semantic class.

The real ggen loader may enforce a narrower `[pack]` schema than marketplace cataloging. Do not assume arbitrary lifecycle/class metadata can be inserted inside `[pack]`; use only a surface admitted by the relevant loader.

## Semantic pack classes

Use [`docs/reference/pack-classes.md`](docs/reference/pack-classes.md) when reasoning about composition:

- KernelPack
- CapabilityPack
- ProfilePack
- WorldPack
- CompatibilityPack
- EvidencePack
- ReleaseControlPack
- UmbrellaPack

These classes describe semantic responsibility, not directory shape. Similar names/suffixes are not equivalence proof.

Prefer class closure over copy/paste proliferation: canonicalize shared protocol/lifecycle/maturity/projection truth, keep orthogonal capabilities modular, use umbrellas for common bundles, and preserve non-equivalent runtimes/worlds/compatibility seams.

Before deleting or physically merging packs, follow [`docs/how-to/consolidate-a-pack-family.md`](docs/how-to/consolidate-a-pack-family.md).

## Level 5

Read [`docs/reference/level5-maturity-contract.md`](docs/reference/level5-maturity-contract.md) before making a Level-5 claim.

Level 5 is closure across seven independently evidenced dimensions:

1. semantic source;
2. admission;
3. manufacture;
4. execution;
5. receipt/replay;
6. authority fence;
7. composition/class closure.

Documentation adds a required correspondence surface:

```text
Tutorial ∧ How-to ∧ Reference ∧ Explanation
```

`pack-maturity-pack` supplies reusable mechanical fixed-point, receipt, and Diátaxis infrastructure. It cannot invent domain semantics, domain negative witnesses, native runtime success, external observations, customer outcomes, or DO authority.

## Marketplace control plane vs generation contracts

`marketplace.toml` declares marketplace-wide operational law and is executable only after `star-toml`/`admit-config.sh` admission. Pack-level `ggen.toml` files are generation contracts; they are not the marketplace control plane.

`scripts/marketplace.py` is the local structural/source calculus for validation, deterministic catalog projection, archive manufacture, and corpus fingerprinting. The catalog is derived, not hand-maintained.

`scripts/qualify_packs.py` uses the real admitted ggen runtime to exercise isolated pack manufacture/replay. It proves only that bounded qualification boundary.

## Documentation — Diátaxis and generated navigation

Keep the quadrants distinct:

- `docs/tutorials/` — guided learning journeys;
- `docs/how-to/` — bounded task procedures;
- `docs/reference/` — exact contracts;
- `docs/explanation/` — rationale, fences, exclusions, extension law.

`docs/book.ttl` is the canonical mdBook navigation source. The Pages rail deletes and regenerates `book.toml` and `docs/SUMMARY.md` with ggen before building mdBook. Do not hand-edit generated navigation/control files as source.

When a marketplace contract changes, update all affected quadrants in the same dependency-closed transition. Avoid copying volatile configuration/version values when an executable canonical source exists.

## Authority

Preserve:

```text
SELECT → CONSTRUCT → DO
```

Marketplace admission and ggen manufacture may select/construct powerful artifacts without receiving ambient consequential authority. Generated Terraform, workflows, MCP/API intents, deployment specs, proofs, semantic derivations, hooks, and receipts do not gain DO authority from existence.

Where a consumer uses BRCE, it remains the separately admitted consequential DO path. If required external authority is unavailable, use `BLOCKED:<reason>` rather than mocking execution into ALIVE.

## Standing

Use `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, plus typed `REFUSED:*`.

- inspection is not execution;
- workflow definition is not a successful run;
- generated existence is not correctness;
- historical success at another SHA is not current exact-subject evidence;
- a checkpoint on one maturity dimension is not a Level-5 crown.

## Working rules

- branch before editing; never write directly to `main`;
- never hand-maintain a second catalog;
- no symlinks below `packs/`;
- PR CI is read-only evidence and must not rewrite source;
- preserve exact provenance on migration/consolidation;
- repair canonical RDF/query/template/gate/project source rather than patching generated consequences;
- use the smallest dependency-closed change that preserves semantic ownership, authority fences, receipts/replay, and compatibility.
