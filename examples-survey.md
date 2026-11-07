# Examples Survey: Pack Anatomy + New Industry Pack Recipe

Survey of `/Users/sac/ggen-marketplace` (read-only survey; this file is the only artifact written).

## 1. Pack inventory

`packs/` holds **352 packs**. Structure varies by packaging profile (derived, not declared):
`project` (has `ggen.toml`) > `projection` (has `templates/`) > `semantic` (TTL only).

**sa2a family (the pattern exemplars):**

| Pack | Files | Contents |
|---|---|---|
| `packs/sa2a-governed-process-pack/` | `pack.toml`, `ontology.ttl` | Semantic-only: RDF primitives (DelegationLease, ExecutionCommitment, BRCE consequence boundaries, exact-SHA receipts) for Composition C12; declares SHACL prefix; no templates/gates. Deps: praxis-core-pack, sa2a-spark-dsl-pack |
| `packs/sa2a-spark-dsl-pack/` | `pack.toml`, `README.md`, `ontology.ttl`, `gates/010_verifier_template_completeness.rq`, `gates/020_promise_vs_content.rq`, `gates/030_refusal_code_projection_consistency.rq`, `queries/verifier_refusal_codes.rq`, `templates/spark_{verifier,transformer}_skeleton.ex.tmpl` | Projection pack: ontology models the real landed ash_a2a verifier/transformer surface as RDF with per-individual source citations; Tera templates generate Spark verifier/transformer skeletons; SPARQL gates enforce completeness, promise-vs-content, projection consistency |
| `packs/sa2a-chicago-court-pack/` (v0.2.0) | `pack.toml`, `ggen.toml`, `ontology.ttl`, `shapes.ttl`, `README.md`, `templates/chicago_suite_test.exs.tmpl`, `queries/courts.rq`, `gates/000_no_hardcoded_modules.sh` + `gates/010..060 *.rq`, `generated/chicago_court_suite_test.exs`, `.ggen-v2/receipt.json`, `.ggen/keys/` | Full project pack: ontology→query→template→generated ExUnit court suite; template takes every collaborator module as a `chi:SuiteConfig` binding resolved by SPARQL (never hardcodes module names — gate 000 refuses); SHACL shapes; receipts + signing keys |

Other families among the 332: a2a-conformance/durability/hex-migration, affidavit-*, ash-* (pplan, r2rml, ocel, revops), beam4pm-*, autofde-*, strategic-doctrine, tcps-release, legal-matter, challenger-value-framing, gym-* (biblegym, ww3gym, gym-upper-ontology), qri-*, and the clap-noun-verb-{schema,crate,routing,behavior,boundary,verification}-pack six-pack CLI pipeline family.

## 2. What makes a pack VALID

Contract: `docs/reference/pack-contract.md`.

- `pack.toml` required. `[pack]` = `name` (must equal the directory name), `version` (SemVer), non-empty `description`. Unknown keys inside `[pack]` are refused by the ggen pack loader.
- At least one Turtle source: `*.ttl` at pack root or recursively under `ontology/`. Conventional name is `ontology.ttl`.
- `templates/` optional; non-scaffolding files must end `.tmpl` or `.tera`.
- `gates/` optional; admitted roles: `*.rq` (native SPARQL refusal gates, ASK-true = violation) and `*.py` (pack-owned bounded verifiers). "The existence of a gate is not evidence that its negative witness has executed."
- `qualification/` — bounded synthetic positive fixtures for qualification (see `docs/reference/ggen-qualification-contract.md`).
- `targets.toml` sidecar (`[targets] languages = ["ts","py","rs","ex"]`) — refused if placed in `pack.toml` (`TARGETS_IN_MANIFEST`).
- Packaging profile derived, not declared: `project` if `ggen.toml` exists, else `projection` if templates, else `semantic`.
- Symlinks below `packs/` refused (path safety).
- Dependency caveat (FM-PACK-014, documented in `packs/sa2a-spark-dsl-pack/pack.toml`): ggen refuses a `[dependencies]` entry unless the consumer's own `ggen.toml [packs]` table lists the dependency; qualification loads each pack in isolation — document cross-pack relationships in a comment, not necessarily as a dependency edge.

**Validation/qualification commands** (from `CONTRIBUTING.md`):

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json   # determinism check
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

Deeper machinery: `scripts/qualify_packs.py` — qualifies every admitted pack through the **real ggen runtime**, loading each pack twice in an isolated capsule and requiring identical filesystem consequence within a 5s per-pass bound (opt-in-by-artifact-presence `cargo build`/`cargo test` of generated Cargo.tomls, CI-05). Supports pack-owned `qualification/consumer.ttl`, `qualification/project/**` overlays, and `qualification.toml` extra ontologies. Scaffolding: `python3 scripts/new_pack.py <name> --profile semantic|projection|project` builds from `scaffolds/pack-skeleton/{common,<profile>}/` and "passes `marketplace.py check <name>` on first run"; the skeleton includes `witnesses/pass/` and `witnesses/fail/` TTL fixtures for the gate's negative witness. `scripts/bootstrap_pack.sh` generates a whole pack from a bootstrap input ontology via ggen_igniter. CI: `.github/workflows/ci.yml` plus specialized workflows (`gate-witness-courts.yml`, `package-contract.yml`, `vacuity-audit.yml`, `publish.yml`) and `ci/courts/`.

## 3. How packs reference standard vocabularies

- **schema.org + FOAF (vendored)**: `packs/strategic-doctrine-pack/sources/vendor/schema-org/source.ttl` — `@prefix foaf: <http://xmlns.com/foaf/0.1/>` (line 32), `@prefix schema: <https://schema.org/>` (line 45). Also `sources/vendor/org/source.ttl` (W3C ORG).
- **SHACL**: `packs/strategic-doctrine-pack/ontology/shapes.ttl` — `@prefix sh: <http://www.w3.org/ns/shacl#>` with `sdsh:StrategyShape a sh:NodeShape`. Also `packs/sa2a-governed-process-pack/ontology.ttl` (`@prefix sh: <http://www.w3.org/ns/shacl#>`) and `packs/sa2a-chicago-court-pack/shapes.ttl`.
- **PROV-O**: PROV vocabulary terms appear in `packs/tcps-release-pack/ontology.ttl` (supply-chain provenance/evidence workflow classes, e.g. around lines 615-625) and in `packs/portfolio-epistemic-observability-pack/ontology*.ttl`.
- **XSD/RDFS/OWL**: every pack ontology uses `xsd:`/`rdfs:`/`owl:` standard prefixes as baseline (e.g. `packs/sa2a-chicago-court-pack/ontology.ttl`).

Pattern: packs either (a) declare standard-namespace prefixes inline in their own ontology.ttl, or (b) vendor the full external vocabulary TTL under `sources/vendor/<vocab>/` when they need the real class/property definitions (strategic-doctrine-pack's schema-org/org vendoring is the exemplar). ggen's frozen manifest schema accepts only `source`/`prefixes` in `[ontology]` — `imports` is refused on older ggen (FM-CONFIG-002, noted in `packs/qri-consumer-binding-pack/ggen.toml`), so cross-vocabulary union is done by concatenation/qualification fixtures rather than OWL imports.

## 4. Publish / consume flow

**Discovery (marketplace side)**: `marketplace.toml` is the registry root — `[marketplace] version` (registry snapshot, currently v26.10.8), `[source_authority]` (canonical repo `seanchatmangpt/ggen-marketplace`, `mirrors_are_provenance_only = true`), `[qualification]` workers/timeout, and a pinned upstream ggen binary. `scripts/marketplace.py` validates, projects a deterministic catalog (`marketplace.py catalog`), and fingerprints pack bytes. `scripts/gen_pack_index.py` and `pack_capabilities.py`/`pack_dependency_order.py` handle capability edges and topological order (README: `capabilities.requires` edges are order-only and never refuse; cycles are dropped deterministically). Releases are immutable versioned GitHub Releases plus a rolling "packs" release (`scripts/publish.yml`-adjacent workflows; `scripts/fetch_pack.py` fetches).

**Consumption (consumer side)**: a consumer project's `ggen.toml` lists packs in a `[packs]` table, by path for sibling packs:

```toml
[packs]
"sa2a-chicago-court-pack" = { path = "../ggen-marketplace/packs/sa2a-chicago-court-pack" }
```

e.g. the repo-root `ggen.toml` does `"mdbook-pattern-language-pack" = { path = "packs/mdbook-pattern-language-pack" }`, and `packs/clap-noun-verb-zeroconfig-pack/ggen.toml` composes six sibling packs by relative path. The consumer (or the pack itself, for self-verification — `packs/sa2a-chicago-court-pack/ggen.toml` is explicitly "pack-local self-verification... Consumers copy this manifest into their own project") then runs `ggen sync run`, which executes the 5-stage pipeline: load manifest → load/union RDF (`[ontology] source` + prefixes) → evaluate gates (SPARQL ASK violations refuse; ggen emits no file on refusal) → run `[[generation.rules]]` (each rule = SPARQL query file + Tera template file + `output_file`, `skip_empty`, `mode = "Overwrite"`) → emit files + receipts (`.ggen-v2/receipt.json`, receipt logs). Generated consumer files are consequences, not a second source of truth (`CLAUDE.md`).

## 5. Minimal recipe: a new industry pack

Fastest guaranteed-valid path:

```bash
cd /Users/sac/ggen-marketplace
python3 scripts/new_pack.py acme-insurance-pack --profile projection
# fills scaffolds/pack-skeleton/{common,projection} with __NAME__/__PROFILE__/__IRI__
# (IRI base https://seanchatmangpt.github.io/packs/<name>)
```

Then fill in, following the sa2a exemplars:

1. **`pack.toml`** — `[pack]` name == directory name, SemVer version, real description; `[capabilities] provides = ["urn:ggen:pack:<name>"]`. Declare `[dependencies]` only if consumers will list the dependency in their own `[packs]` table (FM-PACK-014); otherwise document the relationship in a comment.
2. **`ontology.ttl`** — owl:Ontology header + domain classes/properties with `rdfs:label`/`rdfs:comment`. Bind standard vocabularies by inline prefix (`xsd:`, `sh:`, `schema:`) or vendor the full vocab TTL under `sources/vendor/<vocab>/source.ttl` (strategic-doctrine-pack pattern). Model each individual with a grounded citation (file path) into the real source it mirrors — the sa2a-spark-dsl-pack pattern.
3. **`templates/*.tmpl`** — Tera templates that take every module/name from ontology bindings via SPARQL; never hardcode module names.
4. **`queries/*.rq`** — SELECT queries joining ontology individuals to template variables.
5. **`gates/010_*.rq`** — ASK-true-means-violate refusal gates over your own ontology (completeness, hardcoded-name refusal, projection consistency). Copy the negative-witness convention: `witnesses/pass/*.ttl` + `witnesses/fail/*.ttl` from the skeleton.
6. **(project profile only) `ggen.toml`** — `[ontology] source = "ontology.ttl"` + `[ontology.prefixes]`; `[[generation.rules]]` per artifact (query file + template file + `output_file`); use it for pack-local self-verification, writing only under `generated/`.
7. **`qualification/consumer.ttl`** — synthetic consumer facts so qualification can drive your projection without a real customer event.
8. **Validate**: `python3 scripts/marketplace.py validate`, double-`catalog` + `cmp`, then `scripts/qualify-marketplace.sh` (which runs `scripts/qualify_packs.py` → two isolated real-ggen loads must converge byte-identically within 5s).
