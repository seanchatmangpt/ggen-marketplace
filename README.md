# ggen Marketplace

The canonical repository of reusable **ggen packs**: admitted semantic source for deterministic manufacture, bounded verification, receipts/replay, and composable capability distribution.

A pack is not merely a template directory. Its manifest establishes identity, RDF carries semantic authority, gates may refuse inadmissible subjects, templates or project rules manufacture consequences, and consumer courts establish whatever runtime behavior is actually claimed. Generated files are consequences of admitted source; they are never a second source of truth.

## Canonical local acceptance

Marketplace operational law is declared in `marketplace.toml`. Admit it before running qualification:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
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

These commands prove different boundaries. Structural validation is not runtime qualification, qualification is not consumer correctness, and neither grants consequential DO authority.

## Consume a pack

For a local checkout, reference an admitted pack from the consumer's `ggen.toml`:

```toml
[packs]
ggen-combinatorial-maximalism-pack = { path = "../ggen-marketplace/packs/ggen-combinatorial-maximalism-pack" }
```

Then execute the consumer's admitted manufacturing path with the matching ggen runtime, verify the native consequence, run deterministic replay, and verify any receipt the consumer contract requires.

## Pack profiles

The marketplace preserves legitimate pack diversity instead of forcing every pack into one scaffold:

- **projection** — manifest + RDF + `.tmpl`/`.tera` projections;
- **semantic** — manifest + RDF, optionally with gates/catalogs and no required template;
- **project** — a self-contained `ggen.toml` project with RDF and optional templates/rules/queries.

Every admitted profile still requires `pack.toml`, a SemVer identity, a non-empty description, and at least one Turtle source at the pack root or under `ontology/`. A profile describes packaging shape, not maturity or standing.

The permanent catalog is the set of admitted manifests under `packs/`. `scripts/marketplace.py catalog` is a deterministic projection; this repository deliberately does not maintain a second hand-edited catalog.

## Level 5

Level 5 is **closure**, not a badge attached to a directory. The marketplace evaluates maturity across seven dimensions:

1. semantic source;
2. admission;
3. manufacture;
4. execution;
5. receipt/replay;
6. authority fencing;
7. composition.

A Level-5 claim also requires Diátaxis closure: **Tutorial + How-to + Reference + Explanation**, with documentation corresponding to the same admitted subject and execution boundaries as the implementation.

`pack-maturity-pack` provides reusable mechanical infrastructure for deterministic regeneration, fixed-point convergence, receipt verification, and the Level-5 Diátaxis shape. It deliberately does **not** invent domain semantics, domain negative witnesses, consumer behavior, benchmark results, or runtime authority on behalf of a composing pack.

Start here:

- [Tutorial: promote a pack toward Level 5](docs/tutorials/level5-promotion.md)
- [How to promote a pack to Level 5](docs/how-to/promote-a-pack-to-level5.md)
- [Level-5 maturity contract](docs/reference/level5-maturity-contract.md)
- [Why Level 5 requires Diátaxis](docs/explanation/level5-diataxis.md)
- [Pack classes](docs/reference/pack-classes.md)
- [Class closure and consolidation](docs/explanation/class-closure-and-consolidation.md)

## Documentation — Diátaxis

The repository documentation itself follows Diátaxis:

- **Tutorials** — guided, executable learning journeys in [`docs/tutorials/`](docs/tutorials/first-pack.md)
- **How-to guides** — bounded operational tasks in [`docs/how-to/`](docs/how-to/publish-a-pack.md)
- **Reference** — exact contracts and refusal boundaries in [`docs/reference/`](docs/reference/pack-contract.md)
- **Explanation** — architecture, fences, exclusions, and extension calculus in [`docs/explanation/`](docs/explanation/why-a-separate-marketplace.md)

Navigation is semantic source: `docs/book.ttl` is projected by `mdbook-pattern-language-pack`. `docs/SUMMARY.md` is generated during the Pages build and is not an editing surface.

Start at [`docs/index.md`](docs/index.md).

## Consolidation law

The marketplace may contain many pack instances without treating each as an independent semantic authority. Prefer class closure:

```text
canonical class/kernel
        + orthogonal capability modules
        + parameterized profiles/worlds
        -> many reusable pack instances
```

Consolidate duplicated protocol truth, lifecycle law, maturity law, authority law, or projection grammar. Preserve domain-specific facts, world semantics, implementation runtimes, and compatibility seams unless equivalence has been proved. Deprecation must name a successor and preserve migration/compatibility evidence rather than silently deleting historical consumers.

## Provenance

The initial corpus was imported byte-for-byte from `seanchatmangpt/ggen` at commit `c37b46015b8e5ab40be771d61aafe3d7c7af084c`; source and destination initially shared `packs/` tree `4d70ae027004db829a8c334d201ad8e4f5b75ce1`. After that receipt was established, marketplace admission removed source directories that explicitly documented themselves as orphaned/non-pack research artifacts and repaired incomplete manifest metadata. See [`MIGRATION.md`](MIGRATION.md).

## Scope and standing

This repository owns reusable pack source and marketplace documentation. The ggen runtime remains responsible for interpreting and executing packs. Marketplace validation proves only the contract it actually executes. Exact-head all-pack qualification may prove bounded ggen load/manufacture/replay for that marketplace subject. Consumer runtime behavior, external APIs/clouds, benchmarks, business outcomes, and BRCE DO authority require their own exact-subject courts.

Use standing precisely: `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, plus typed `REFUSED:*`. A workflow declaration is not a successful run, a generated artifact is not authority, and historical success at another SHA does not transfer automatically.

See [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md), and [`SECURITY.md`](SECURITY.md).

## Vision 2030 Capability Generator

`packages/vision-2030-capability-generator` compiles an admitted RDF capability graph into a Vision 2030 architecture, a machine-readable capability index, and a Mermaid capability graph.

```text
ontology.ttl -> SPARQL -> ggen -> generated/VISION_2030.md
                               -> generated/capability-index.json
                               -> generated/capability-graph.mmd
```

Its structural verifier is an admission court; `ggen sync run` remains the manufacture boundary. The package is CONSTRUCT-only: generated architecture does not receive standing or DO authority merely by existing.
