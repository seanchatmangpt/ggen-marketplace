# Ontologies

A curated library of hand-authored domain ontologies pulled in from other Sean Chatman
projects, hosted here so they're discoverable and reusable across `ggen-marketplace` packs.
Copied 2026-08-17.

## Scope and status

This directory is a **reference library, not a pack**. `scripts/marketplace.py` only ever
validates/catalogs `packs/<name>/*.ttl` and `packs/<name>/ontology/**/*.ttl` (see
`docs/reference/pack-contract.md`); it does not scan `ontologies/` and never will — putting
ontologies here does not admit them into the marketplace catalog or qualification pipeline on
its own.

What it does give you:

- A single place to browse hand-authored ontologies by domain instead of hunting across a dozen
  repos.
- A working `ggen.toml` project (`ontologies/ggen.toml`) so `ggen` can be run directly against
  this whole corpus via the umbrella manifest `ontologies.ttl` (an `owl:imports` list of every
  `.ttl`/`.owl` file below). This is a standalone ggen project — the same pattern as the
  repo-root `ggen.toml` that serves `docs/book.ttl` for the mdbook pack — not part of the
  `packs/` qualification pipeline.

## How a pack consumes one of these ontologies

Per-pack ontology loading stays scoped exactly as documented in
`docs/reference/pack-contract.md`: a pack only ever loads its own root `*.ttl` files and its own
`ontology/**` subtree (optionally extended via that pack's `qualification.toml`
`[consumer] extra_ontologies`, which must remain inside the pack directory — no absolute paths,
no traversal).

So to use one of these ontologies in a pack:

1. Copy the specific file(s) you need into `packs/<your-pack>/ontology/` (keep the original
   filename so provenance stays traceable back here).
2. Or, if the pack already has `qualification/`, list it under
   `[consumer] extra_ontologies = ["your-copied-file.ttl"]` — still relative, still inside the
   pack.

`ontologies/` itself is never read directly by pack qualification — treat it as upstream source
material to pull from, not a live dependency.

## Layout and provenance

| Directory | Original source | Domain |
|---|---|---|
| `mechanical-design/` | `~/rocket-craft` (`ontology/`, `.specify/ontology/`, `ontology/source_law/`, `packs/cybernetic-research/ontology/`) | Mecha/robot design-rule ontology: chassis/limb/wing grammars, materials, DFLSS manufacturing rules, TRIZ, FMEA, UE4 projection policy (`source_law/` is ~120 numbered rule files) |
| `cns/domains/` | `~/cns/ontologies/*_core.ttl`, `*_shacl.ttl` | Healthcare, industrial IoT, cybersecurity, smart grid, autonomous vehicle domain ontologies + SHACL shapes |
| `cns/dflss/` | `~/cns/ontologies/dflss*.ttl` | DFLSS / Six Sigma business-process ontology suite |
| `cns/trading/` | `~/cns/ontologies/forex_*.ttl`, `production_forex_trading.ttl` | Forex trading domain ontologies |
| `cns/cli-governance/` | `~/cns/ontologies/{governance,owl_reasoning_rules,unified_cli*,cli_*}.ttl` | CLI/workflow governance and OWL reasoning-rule ontologies |
| `cns/legal/` | `~/cns/jurisdiction-mapping/`, `~/cns/cns-litigation-swarm/` | Legal/jurisdiction ontologies (bar-complaint procedures, CA/federal/NV jurisdiction) and litigation-workflow ontologies (employment misclassification, civil rights, bar complaints) |
| `cns/workflow/` | `~/cns/bitjob/weaver-ontology/`, `~/cns/bitflow/` | BitStar workflow ontology, BitFlow workflow-pattern ontology |
| `open-ontologies/` | `~/open-ontologies/ontology/` | Broad multi-project ontology set: Cell8 manufacturing/conformance, GHF security policy, portfolio/process-mining, and the Zoela church-management domain (`zoela/` subtree) |
| `autofde/` | `~/autofde-lab/ontology/` | AutoFDE lab ontology: architecture (C4/state/flow/class/ER diagrams as RDF), authority, evidence, planning, process, SHACL shapes (`shapes/`) |
| `public/` | Mixed: `~/ggen/ontologies/` (vendored copy) + fetched directly from each publisher's canonical URL (see below) | Standard public vocabularies from W3C and named industry/community groups |

### `public/` — standard and named-industry vocabularies

`public/` now spans general-purpose W3C vocabularies, named industry-consortium ontologies
across cybersecurity, DevOps, energy/IoT, government, telecom, retail, HR, real estate, media,
agriculture, manufacturing, and scientific research, plus two full external corpora (FIBO,
OBO Foundry) and one full compressed dataset (AGROVOC). **See `STATUS.md` for the complete,
authoritative per-ontology table** — publisher, status, and exact file location for every named
ontology researched across three `deep-research` passes this session. This section only
summarizes; `STATUS.md` is the source of truth for what's added vs. blocked vs. not-found vs.
still unresearched.

**851 files, 2.8G total.** Large corpora are kept in their own subdirectories rather than
flattened: `public/fibo/` (EDM Council's full OWL corpus, 287 files/13M, preserving FIBO's own
domain layout), `public/obo/` (170/190 active OBO Foundry member ontologies fetched by PURL,
2.7G — by far the largest single component), `public/agrovoc/` (FAO's full AGROVOC LOD dump,
kept as the 96MB compressed `.nt.zip` rather than exploded to its ~1.5GB uncompressed size), and
modular multi-file ontologies (`public/uco/`, `public/case/`, `public/realestatecore/`,
`public/hrm/`, `public/saref-extensions/`) each with their own manifest/module files as published
upstream.

**Important usage-fit note:** a check of every `packs/*/ontology.ttl` in this repo shows PROV-O
referenced 149 times, Dublin Core terms 143 times, SKOS 47 times, DCAT 22 times, and
SOSA/ORG/schema.org a handful of times each — against **zero** references anywhere in `packs/`
to OBO Foundry, FIBO, AGROVOC, UCO/CASE, GS1, HR-Open, RealEstateCore, EBUCorePlus, SAREF,
D3FEND, IOF, or any other industry-vertical ontology added this session. The general-purpose
W3C core plus the personal-repo domain ontologies remain the load-bearing 20% of this directory
for *this marketplace's current packs*; the large industry corpora are a reference library for
future work, not something any pack consumes today. Fetching was stopped short of 100% OBO
Foundry coverage once this became clear — see `STATUS.md`'s Summary for exactly what's missing
and why.

**Excluded from this copy** (noise, not domain modeling): W3C RDF conformance test-suite
fixtures (`oxigraph-local/testsuite`), the 3,281-file auto-generated
`~/ggen/ontology_catalogue`, git-worktree duplicates, stale `backup_*` directories, and
generated/derived RDF output directories. SNOMED CT is excluded on license grounds (see
`STATUS.md`) — the only deliberate non-technical exclusion.

## Known caveats

- Files were copied as-is; any `owl:imports` or relative paths inside them that assumed their
  original repo's layout (e.g. sibling files that weren't copied here) may not resolve from this
  new location. Treat any such file as needing path adjustment before relying on it standalone —
  this was not rewritten file-by-file during the copy.
- `cns/legal/` contains real jurisdiction/litigation-workflow ontology content (not synthetic
  test data) — included per explicit request; be mindful of that when re-sharing this directory.
- 276 of 284 `.ttl`/`.owl` files parse cleanly with `rdflib`. 8 have pre-existing Turtle syntax
  errors carried over from their source repos (unbound prefixes, malformed literals) — not
  introduced by this copy:
  - `cns/cli-governance/governance.ttl` — `:` prefix used but not bound
  - `cns/legal/cns-litigation-swarm/schemas/yawl_workflow_patterns.ttl` — parser error
  - `cns/legal/cns-litigation-swarm/telemetry/opentelemetry_config.ttl` — parser error
  - `cns/legal/cns-litigation-swarm/workflows/employment_misclassification_detector.ttl` — parser error
  - `cns/legal/jurisdiction-mapping/federal-jurisdiction-comprehensive.ttl` — unescaped newline in a string literal (line 340)
  - `cns/legal/jurisdiction-mapping/timeline-contradiction-validation-system.ttl` — malformed object list (line 606)
  - `mechanical-design/source_law/104_reference_fabric.ttl` — `xsd:` prefix used but not bound (line 107)
  - `open-ontologies/public-shapes.ttl` — `xsd:` prefix used but not bound (line 17)
- `public/skos.rdf` and `public/skos-xl.rdf` are RDF/XML despite what their source repo's naming
  implied — they were copied in as `skos.ttl`/`skos-xl.ttl` from `~/ggen/ontologies/core/` and
  renamed to `.rdf` here since parsing them as Turtle fails; parsing as RDF/XML succeeds cleanly
  (252 and 60 triples respectively).
