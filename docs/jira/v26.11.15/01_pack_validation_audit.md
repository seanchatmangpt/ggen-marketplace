# Marketplace Pack Validation Audit Report: ggen-marketplace (v26.11.15)

- **Audited Target**: `/Users/sac/ggen-marketplace`
- **Audit Agent**: Agent 11 of 20 (`ggen_auditor_packs_validation`)
- **Evaluation Date**: 2026-11-16
- **Audit Standard**: Chicago-style live execution, fail-closed admission, anti-vacuity, W3C RDF/SHACL validation, ambient `ggen 26.11.5` qualification
- **Scope**: All 363 marketplace packs (`packs/*`), RDF/Turtle/SHACL shapes (2,682 `.ttl` files, 112 SHACL files), pack manifests (`pack.toml`, `ggen.toml`), pack qualification harness (`scripts/qualify_packs.py`), workgraph validation (`scripts/validate_workgraphs.py`), and vacuity scanner (`scripts/audit_vacuity.py`)

---

## Executive Summary

A comprehensive, live static and dynamic audit was conducted across all 363 packs in `/Users/sac/ggen-marketplace/packs`. The marketplace repository uses an ontology-first architecture where domain facts are authored in Turtle/RDF, shaped via W3C SHACL, and transformed into software artifacts using the `ggen` code generation engine.

While 340 out of 363 packs qualify as **ALIVE** when evaluated in isolation, the audit identified **critical gating bugs that completely break marketplace admission**, several **corrupted and invalid RDF/SHACL files**, **failing ggen synchronization gates**, and **unresolved Cargo path dependencies** in generated crates.

### Key Audit Metrics
| Category | Evaluated | Conforming / ALIVE | Failing / Blocked | Standing |
|---|---|---|---|---|
| **Marketplace Pack Corpus** | 363 packs | 340 | 8 REFUSED, 14 WARN, 1 SKIPPED | **REFUSED** (blocked at corpus gate) |
| **Marketplace Admission Gate** | Corpus preflight | 0 | 2 gate extension refusals in `xstate-v5-machine-pack` | **REFUSED** |
| **Turtle / RDF Files** | 2,682 `.ttl` files | 2,677 | 5 syntax parse errors (unbound prefix, JSON-LD, 404 text) | **REFUSED** |
| **W3C SHACL Shape Files** | 112 shape files | 110 | 1 spec violation (missing `sh:path`), 1 parse failure | **REFUSED** |
| **Workgraph Conformance** | 6 work orders | 0 | 152 style-mismatch shape violations | **REFUSED** |
| **Pack Manifests (`pack.toml`)** | 363 manifests | 363 valid TOML | 0 missing, 0 invalid TOML | **ALIVE** |
| **Generation Manifests (`ggen.toml`)** | 137 manifests (490 rules) | 490 rules | 0 missing templates, 0 missing queries | **ALIVE** |
| **Scaffolding Harness** | `scripts/check_self_pack_scaffolding.py` | 0 | 1 EA admission gate failure | **REFUSED** |
| **Static Capability Scan** | `scripts/pack_capabilities.py --check` | All allowlisted | 0 unallowlisted network gates | **ALIVE** |

---

## 1. Critical Repository-Level Marketplace Gating Blockers

### Finding 1.1: Invalid Gate Source Extensions in `packs/xstate-v5-machine-pack/gates/` Hard-Blocks Marketplace Admission
- **Subject**: `packs/xstate-v5-machine-pack/gates/baselines.toml` and `packs/xstate-v5-machine-pack/gates/shapes.toml`
- **Classification**: Gating Law Violation (`GATE_SOURCE_EXTENSION`)
- **Gap / Issue**: 
  `scripts/marketplace.py` defines allowable gate extensions as `GATE_SOURCE_SUFFIXES = frozenset({".rq", ".py", ".sh"})` (line 42). In `packs/xstate-v5-machine-pack/gates/`, two configuration files (`baselines.toml` and `shapes.toml`) were placed directly in `gates/`.
  Because `marketplace.inspect_marketplace()` inspects all pack directories unconditionally and raises a refusal on unknown file extensions in `gates/`, calling `require_admitted()` triggers `SystemExit(2)`.
  This single defect hard-refuses and breaks every tool depending on `require_admitted()`, including:
  - `scripts/marketplace.py validate`
  - `scripts/marketplace.py check`
  - `scripts/marketplace.py catalog`
  - `scripts/marketplace.py archive`
  - `scripts/qualify_packs.py` (even when qualifying a single separate pack like `--pack aaif-vanilla-pack`)
  - `scripts/marketplace_scope.py`
  - `scripts/check_cross_pack_references.py`
  - `scripts/qualify-marketplace.sh`
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && uv run --no-project python scripts/marketplace.py validate
  ```
- **Command Output**:
  ```text
  REFUSED:GATE_SOURCE_EXTENSION:packs/xstate-v5-machine-pack/gates/baselines.toml
  REFUSED:GATE_SOURCE_EXTENSION:packs/xstate-v5-machine-pack/gates/shapes.toml
  [exit 2]
  ```
- **Remediation**:
  Move `baselines.toml` and `shapes.toml` into a subfolder (e.g. `packs/xstate-v5-machine-pack/gates/config/` or `fixtures/`) or update `GATE_SOURCE_SUFFIXES` in `scripts/marketplace.py` if `.toml` configuration is an admitted gate metadata format.

---

### Finding 1.2: `scripts/check_self_pack_scaffolding.py` Fails EA Architecture Admission
- **Subject**: `scripts/check_self_pack_scaffolding.py`
- **Classification**: Missing EA Admission Opt-Out Flag Under Ambient `ggen 26.11.5`
- **Gap / Issue**:
  Under ggen 26.11.3+ (law `[FM-LAW-015]`), any `ggen sync run` invocation in an environment without `ea.graph.json` must explicitly pass `--skip-ea-admission`. `scripts/qualify_packs.py` correctly passed `--skip-ea-admission` (per MKT-01), but `scripts/check_self_pack_scaffolding.py` runs `ggen sync run --format json` without this flag, causing it to fail immediately with exit code 1.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && uv run --no-project python scripts/check_self_pack_scaffolding.py
  ```
- **Command Output**:
  ```text
  FAIL: ggen sync run exited 1
  stderr:
  2026-11-16T17:41:52.148124Z  INFO ggen.cli{command=sync run --format json version="26.11.5"}: ggen_cli_lib: close time.busy=10.9ms time.idle=25.2µs
  ERROR: CLI execution failed: Command execution failed: validation error: [FM-LAW-015] EA admission gate: `/Users/sac/.cache/tmp/ggen-self-pack-scaffolding-847d85pm/ea.graph.json` is absent and no admission opt-out was given. Every sync must either admit its candidate SBBs against an EA graph or explicitly skip with `--skip-ea-admission`. Remediation: add ea.graph.json, or pass --skip-ea-admission to run without architecture admission.
  [exit 1]
  ```
- **Remediation**:
  Update `scripts/check_self_pack_scaffolding.py` line running `ggen sync run` to include `--skip-ea-admission`.

---

## 2. Turtle / RDF Syntax and Graph Ingestion Defects

A full scan of all 2,682 `.ttl` files across `packs/` using `rdflib 7.6.0` discovered 5 files that fail Turtle parsing.

### Finding 2.1: Syntax Parse Error in `packs/fortune5-enterprise-architecture-pack/tests/__pycache__/violated.ttl`
- **Subject**: `packs/fortune5-enterprise-architecture-pack/tests/__pycache__/violated.ttl:62`
- **Classification**: Malformed Turtle RDF Syntax
- **Gap / Issue**: Line 62 contains an invalid literal or unquoted character sequence: `...#iamAction> "*" .`. The parser expects a valid URI or literal token and rejects the triple.
- **Exact Command**:
  ```bash
  uv run --no-project --with rdflib python -c '
  import rdflib
  g = rdflib.Graph()
  g.parse("packs/fortune5-enterprise-architecture-pack/tests/__pycache__/violated.ttl", format="turtle")
  '
  ```
- **Command Output**:
  ```text
  rdflib.plugins.parsers.notation3.BadSyntax: at line 62 of <>:
  Bad syntax (objectList expected) at ^ in:
  "...b'.io/ontology/fortune5-enterprise-architecture#iamAction> "*"'^b' .\n'"
  [exit 1]
  ```
- **Remediation**: Remove or clean cached/test file or fix escaping of wildcard literal in test fixture.

---

### Finding 2.2: Missing Prefix Declaration in `packs/latency-hazard-radar/shapes.ttl`
- **Subject**: `packs/latency-hazard-radar/shapes.ttl:10`
- **Classification**: Unbound RDF Prefix
- **Gap / Issue**: Line 10 uses `rdfs:label`, but `@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .` is missing from the header of `shapes.ttl`. Any RDF parser or SHACL validator parsing this file crashes.
- **Exact Command**:
  ```bash
  uv run --no-project --with rdflib python -c '
  import rdflib
  g = rdflib.Graph()
  g.parse("packs/latency-hazard-radar/shapes.ttl", format="turtle")
  '
  ```
- **Command Output**:
  ```text
  rdflib.plugins.parsers.notation3.BadSyntax: at line 10 of <>:
  Bad syntax (Prefix "rdfs:" not bound) at ^ in:
  "...b's lhr:ObservationWindow ;\n    sh:property [\n        sh:path '^b'rdfs:label ;\n        sh:minCount 1 ; sh:maxCount 1 ;\n       '..."
  [exit 1]
  ```
- **Remediation**: Add `@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .` to the prefix declarations in `packs/latency-hazard-radar/shapes.ttl`.

---

### Finding 2.3: JSON-LD Content Mislabeled as Turtle in `packs/smalt-core-pack/vendor/security.ttl`
- **Subject**: `packs/smalt-core-pack/vendor/security.ttl:1`
- **Classification**: File Format Mismatch / Parse Failure
- **Gap / Issue**: The file begins with `{\n  "@context": {`. It is a JSON-LD document saved with a `.ttl` extension. When parsed as Turtle by standard tooling, it fails immediately.
- **Exact Command**:
  ```bash
  uv run --no-project --with rdflib python -c '
  import rdflib
  g = rdflib.Graph()
  g.parse("packs/smalt-core-pack/vendor/security.ttl", format="turtle")
  '
  ```
- **Command Output**:
  ```text
  rdflib.plugins.parsers.notation3.BadSyntax: at line 1 of <>:
  Bad syntax (expected directive or statement) at ^ in:
  "b''^b'{\n  "@context": {\n    "id": "@id",\n    "type": "@type",\n\n   '..."
  [exit 1]
  ```
- **Remediation**: Rename to `security.jsonld` or transcode content to valid Turtle RDF format.

---

### Finding 2.4: JSON-LD Content Mislabeled as Turtle in `packs/smalt-core-pack/vendor/security2.ttl`
- **Subject**: `packs/smalt-core-pack/vendor/security2.ttl:1`
- **Classification**: File Format Mismatch / Parse Failure
- **Gap / Issue**: The file begins with `{\n  "@context": [{"@version": 1.1...`. It is a JSON-LD document saved with a `.ttl` extension.
- **Exact Command**:
  ```bash
  uv run --no-project --with rdflib python -c '
  import rdflib
  g = rdflib.Graph()
  g.parse("packs/smalt-core-pack/vendor/security2.ttl", format="turtle")
  '
  ```
- **Command Output**:
  ```text
  rdflib.plugins.parsers.notation3.BadSyntax: at line 1 of <>:
  Bad syntax (expected directive or statement) at ^ in:
  "b''^b'{\n  "@context": [{\n    "@version": 1.1\n  }, "https://w3id.or'..."
  [exit 1]
  ```
- **Remediation**: Rename to `security2.jsonld` or transcode content to valid Turtle RDF format.

---

### Finding 2.5: HTTP 404 HTML Error Stored as Turtle in `packs/smalt-core-pack/vendor/tosca-sodalite.ttl`
- **Subject**: `packs/smalt-core-pack/vendor/tosca-sodalite.ttl:1`
- **Classification**: Corrupted Vendor Artifact / Empty Payload
- **Gap / Issue**: The file content is literally `404: Not Found`. An upstream `curl` or `wget` failed to fetch the remote schema and wrote the HTTP error status into the repository as a `.ttl` file.
- **Exact Command**:
  ```bash
  cat packs/smalt-core-pack/vendor/tosca-sodalite.ttl
  ```
- **Command Output**:
  ```text
  404: Not Found
  ```
- **Remediation**: Re-fetch the genuine TOSCA Sodalite ontology from the authoritative source or remove the placeholder file.

---

## 3. SHACL Shape and Workgraph Validation Defects

Across all 112 SHACL shape files discovered in `packs/`, each file was parsed and validated against the W3C SHACL standard shapes using `pyshacl 0.40.2`.

### Finding 3.1: W3C SHACL Standard Violation in `packs/dfcm-pack/ontology/dd-ui.ttl`
- **Subject**: `packs/dfcm-pack/ontology/dd-ui.ttl:15-20`
- **Classification**: SHACL Metamodel Non-Conformance
- **Gap / Issue**:
  Lines 15-20 declare:
  ```turtle
  ddui:worldDigest a sh:PropertyShape ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 .
  ddui:grammarDigest a sh:PropertyShape ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 .
  ddui:frontierDigest a sh:PropertyShape ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 .
  ddui:screenDigest a sh:PropertyShape ; sh:datatype xsd:string ; sh:minCount 1 ; sh:maxCount 1 .
  ddui:irreversibleSelections a sh:PropertyShape ; sh:datatype xsd:integer ; sh:hasValue 0 .
  ddui:actuation a sh:PropertyShape ; sh:datatype xsd:boolean ; sh:hasValue false .
  ```
  According to section 2.3 of the W3C SHACL specification (*Property Shapes*), a shape defined as `sh:PropertyShape` MUST include exactly one `sh:path` property. These individuals omit `sh:path`, making them invalid PropertyShapes that fail SHACL validation engines.
- **Exact Command**:
  ```bash
  uv run --no-project --with rdflib --with pyshacl python -c '
  import pyshacl, rdflib
  g = rdflib.Graph()
  g.parse("packs/dfcm-pack/ontology/dd-ui.ttl", format="turtle")
  pyshacl.validate(data_graph=g, shacl_graph=g, check_shacl=True)
  '
  ```
- **Command Output**:
  ```text
  pyshacl.errors.ShapeValidationError: A shape defined as a PropertyShape must include one `sh:path` property.
  For reference, see https://www.w3.org/TR/shacl/#property-shapes
  [exit 1]
  ```
- **Remediation**: Add `sh:path ddui:worldDigest ;` etc., to each PropertyShape declaration.

---

### Finding 3.2: Workgraph Validation Fails SHACL Conformance in `scripts/validate_workgraphs.py`
- **Subject**: `scripts/validate_workgraphs.py`
- **Classification**: Work Order Non-Conformance against `work-order.shacl.ttl`
- **Gap / Issue**:
  Running `scripts/validate_workgraphs.py` checks work orders and goal checkpoints in `ggen-marketplace` against `/Users/sac/ggen_igniter/priv/ggen/semantic-jira-pack/shapes/work-order.shacl.ttl`. `ggen-marketplace` fails validation (`conforms: False`) with 152 style-mismatch shape errors.
- **Exact Command**:
  ```bash
  cd /Users/sac/ggen-marketplace && uv run --no-project --with rdflib --with pyshacl python scripts/validate_workgraphs.py
  ```
- **Command Output**:
  ```text
  shapes: /Users/sac/ggen_igniter/priv/ggen/semantic-jira-pack/shapes/work-order.shacl.ttl
  goal-graph shapes: /Users/sac/ggen_igniter/priv/ggen/semantic-jira-pack/shapes/goal-checkpoint.shacl.ttl

  repo               conforms    WO   GC  shape                  classes
  ----------------------------------------------------------------------
  ggen-marketplace   False        6    0  work-order.shacl.ttl   style-mismatch=152
  ```
- **Remediation**: Align work-order graph individuals in `ggen-marketplace` with Semantic Jira work-order SHACL shape constraints.

---

## 4. Static Vacuity and Anti-Cheat Audit Findings

### Finding 4.1: Placeholder Marker in Pack Source (`MARKER_PLACEHOLDER`)
- **Subject**: `packs/natfac-hook-packs/standing-ladder.ttl:54`
- **Classification**: Vacuity Scanner Hard Error
- **Gap / Issue**: Line 54 of `packs/natfac-hook-packs/standing-ladder.ttl` contains a raw placeholder string that triggers the anti-vacuity scanner's `MARKER_PLACEHOLDER` error rule.
- **Exact Command**:
  ```bash
  uv run --no-project python -c '
  import json, subprocess
  res = subprocess.run(["uv", "run", "--no-project", "python", "/Users/sac/ggen-marketplace/scripts/audit_vacuity.py"], capture_output=True, text=True)
  data = json.loads(res.stdout)
  for f in data["subjects"][0]["findings"]:
      if f["path"].startswith("packs/") and f["severity"] == "error":
          print(f)
  '
  ```
- **Command Output**:
  ```text
  {'detail': 'contains PLACEHOLDER', 'line': 54, 'path': 'packs/natfac-hook-packs/standing-ladder.ttl', 'rule': 'MARKER_PLACEHOLDER', 'severity': 'error', 'subject': 'filesystem'}
  ```
- **Remediation**: Replace the placeholder comment/literal with genuine production standing ladder logic.

---

## 5. Pack Qualification Runtime Failures under ambient `ggen 26.11.5`

Dynamic qualification was executed across all 363 packs via `qualify_pack(pack, "ggen", timeout)` using ambient `ggen 26.11.5`.

### Finding 5.1: `ash-a2a-app-pack` Refused by Internal SPARQL Gate Query
- **Subject**: `packs/ash-a2a-app-pack/gates/L30_010_ea_shape.rq`
- **Classification**: Dynamic Qualification Failure (`REFUSED:GGEN_PACK_SYNC_FAILED`)
- **Gap / Issue**: During `ggen sync run --skip-ea-admission`, the internal gate `L30_010_ea_shape.rq` executes against the union graph and refuses because no domain is declared for subject `<app>`.
- **Exact Command**:
  ```bash
  uv run --no-project python -c '
  import sys; sys.path.insert(0, "scripts")
  import marketplace, qualify_packs
  p = [p for p in marketplace.inspect_marketplace()[0] if p.name == "ash-a2a-app-pack"][0]
  print(qualify_packs.qualify_pack(p, "ggen", 15.0)["detail"])
  '
  ```
- **Command Output**:
  ```text
  pass=1 exit=1 output=...
  ERROR: CLI execution failed: Command execution failed: validation error: [FM-PACK-013] pack `ash-a2a-app-pack` gate `L30_010_ea_shape.rq` refused the sync against the union graph: SELECT returned 1 row(s); first row: { ?reason = no-domain-declared, ?subject = <app> }. Remediation: fix the offending facts (in this pack, another pack, or the project ontology — gates run against the UNION, so a violation may come from any graph source), or fix the gate query.
  ```

---

### Finding 5.2: `gh-enterprise-architecture-pack` Generates Malformatted Terraform Manifests
- **Subject**: `packs/gh-enterprise-architecture-pack`
- **Classification**: Generated Build Refusal (`REFUSED:GGEN_PACK_TERRAFORM_FMT_FAILED`)
- **Gap / Issue**: The pack's templates render `repositories.tf` and `variables.tf` into `infra/terraform/github-enterprise/`. The qualification harness runs `terraform fmt -check`, which fails with exit code 3 due to unformatted HCL.
- **Exact Command**:
  ```bash
  uv run --no-project python -c '
  import sys; sys.path.insert(0, "scripts")
  import marketplace, qualify_packs
  p = [p for p in marketplace.inspect_marketplace()[0] if p.name == "gh-enterprise-architecture-pack"][0]
  print(qualify_packs.qualify_pack(p, "ggen", 15.0))
  '
  ```
- **Command Output**:
  ```text
  {'code': 'REFUSED:GGEN_PACK_TERRAFORM_FMT_FAILED', 'detail': 'terraform fmt -check exit=3 tf_root=/Users/sac/.cache/tmp/ggen-marketplace-gh-enterprise-architecture-pack-3ulqrv0z/consumer/infra/terraform/github-enterprise output=repositories.tf\nvariables.tf', 'name': 'gh-enterprise-architecture-pack', 'profile': 'projection', 'status': 'REFUSED', 'version': '0.1.0'}
  ```

---

### Finding 5.3: `rust-doc-hdit-pack` Query Execution Hangs Indefinitely
- **Subject**: `packs/rust-doc-hdit-pack`
- **Classification**: Ggen Execution Timeout (>30s)
- **Gap / Issue**: When `ggen sync run` executes against `rust-doc-hdit-pack`, the SPARQL query phase executes `marketplace-probe.txt.tmpl`. The ggen process consumes 100% CPU on thread execution and fails to return within the qualification timeout window.
- **Exact Command**:
  ```bash
  uv run --no-project python -c '
  import sys; sys.path.insert(0, "scripts")
  import marketplace, qualify_packs
  p = [p for p in marketplace.inspect_marketplace()[0] if p.name == "rust-doc-hdit-pack"][0]
  print(qualify_packs.qualify_pack(p, "ggen", 30.0))
  '
  ```
- **Command Output**:
  ```text
  {'code': 'REFUSED:GGEN_PACK_PASS_TIMEOUT', 'detail': 'pass=1 timeout_seconds=30', 'name': 'rust-doc-hdit-pack', 'profile': 'projection', 'status': 'REFUSED', 'version': '0.1.0'}
  ```

---

### Finding 5.4: `xstate-v5-machine-pack` Ggen Sync Run Timeout
- **Subject**: `packs/xstate-v5-machine-pack`
- **Classification**: Ggen Execution Timeout (>30s)
- **Gap / Issue**: `xstate-v5-machine-pack` contains large architecture graphs and multiple complex templates (`machine.tera.tmpl`, `conformance-matrix.tera.tmpl`). Sync pass 1 exceeds the 30-second execution bound.
- **Exact Command**:
  ```bash
  uv run --no-project python -c '
  import sys; sys.path.insert(0, "scripts")
  import marketplace, qualify_packs
  p = [p for p in marketplace.inspect_marketplace()[0] if p.name == "xstate-v5-machine-pack"][0]
  print(qualify_packs.qualify_pack(p, "ggen", 30.0))
  '
  ```
- **Command Output**:
  ```text
  {'code': 'REFUSED:GGEN_PACK_PASS_TIMEOUT', 'detail': 'pass=1 timeout_seconds=30', 'name': 'xstate-v5-machine-pack', 'profile': 'projection', 'status': 'REFUSED', 'version': '0.1.0'}
  ```

---

## 6. Generated Cargo Build Defects (CI-05 Backlog)

`scripts/qualify_packs.py` runs `cargo build` and `cargo test` against crates generated by packs (CI-05). Ten packs exhibit compilation or dependency resolution failures:

### Finding 6.1: Missing Monorepo Path Dependency `ggen-graph/Cargo.toml`
- **Packs Affected**:
  - `automatic-autonomic-operations-pack`
  - `certification-assist-evidence-control-pack`
  - `certification-assist-pack`
- **Gap / Issue**: The rendered `Cargo.toml` contains `ggen-graph = { path = "../../crates/ggen-graph" }`, which only resolves inside a checkout of the private `ggen` monorepo. In standalone qualification capsules, `cargo build` exits with 101 (`No such file or directory`).
- **Verbatim Error**:
  ```text
  error: failed to load manifest for dependency `ggen-graph`
  Caused by: failed to read `/Users/sac/.cache/tmp/crates/ggen-graph/Cargo.toml`
  Caused by: No such file or directory (os error 2)
  ```

---

### Finding 6.2: Missing Behavior Module in `clap-noun-verb-crate-pack`
- **Pack Affected**: `clap-noun-verb-crate-pack`
- **Gap / Issue**: The generated Rust crate references `mod generated_behavior;`, but the generation rule for that file did not produce `src/generated_behavior.rs`.
- **Verbatim Error**:
  ```text
  error[E0583]: file not found for module `generated_behavior`
  --> src/main.rs:14:5
  ```

---

### Finding 6.3: Missing Monorepo Path Dependency `miniml-core/Cargo.toml`
- **Pack Affected**: `ex4pm-wasm4pm-bindings-pack`
- **Gap / Issue**: Dependencies on `miniml` rely on local relative paths that are absent from the qualification sandbox.
- **Verbatim Error**:
  ```text
  error: failed to get `miniml` as a dependency for package `wasm4pm-ex4pm-bindings`
  Caused by: failed to load manifest for dependency `miniml-core`
  ```

---

### Finding 6.4: Missing Monorepo Path Dependency `ggen-architecture/Cargo.toml`
- **Packs Affected**:
  - `ontostar-mustar-powlv2-agent-pack`
  - `speedrun-talent-network-pack`
- **Gap / Issue**: The rendered `Cargo.toml` relies on `path = "../../../crates/ggen-architecture"`, which does not exist outside the authoring environment.
- **Verbatim Error**:
  ```text
  error: failed to load manifest for dependency `ggen-architecture`
  Caused by: failed to read `/Users/sac/.cache/tmp/crates/ggen-architecture/Cargo.toml`
  ```

---

### Finding 6.5: Unstable Nightly Feature `#![feature]` on Stable Rust Channel
- **Pack Affected**: `otel-weaver-ocel-pack`
- **Gap / Issue**: `packs/otel-weaver-ocel-pack` templates inject `#![feature(...)]` into generated Rust source files. Under the standard Rust stable compiler, `cargo build` fails with `E0554`.
- **Verbatim Error**:
  ```text
  error[E0554]: `#![feature]` may not be used on the stable release channel
  ```

---

### Finding 6.6: Missing Workspace Member in `tcps-release-pack`
- **Pack Affected**: `tcps-release-pack`
- **Gap / Issue**: The rendered manifest declares workspace members including `tcps-core`, but the member crate directory is absent from the rendered capsule.
- **Verbatim Error**:
  ```text
  error: failed to load manifest for workspace member `tcps-core`
  ```

---

### Finding 6.7: Missing Workspace Root Encapsulation in `tcps-pack`
- **Pack Affected**: `tcps-pack`
- **Gap / Issue**: The generated crate `crates/tcps-cli/Cargo.toml` relies on workspace inheritance (`[package] edition.workspace = true`), but no enclosing workspace `Cargo.toml` is provisioned during single-pack qualification. The qualification harness marks this status as **SKIPPED**.

---

## 7. Pack Manifest & Completeness Verification

### Pack Manifest Verification
- All 363 directories under `packs/` have a valid `pack.toml` file.
- No syntax or TOML parsing errors were found across `pack.toml` files.
- All declared pack names match their directory names.

### Generation Manifest (`ggen.toml`) Verification
- 137 packs define `ggen.toml` files containing a total of 490 generation rules.
- 100% of referenced template files (`templates/*.tera`, `templates/*.tmpl`) and query files (`queries/*.rq`) exist on disk.
- Zero broken file references exist across the 490 generation rules.

### Static Capability Allowlist Scan
- `scripts/pack_capabilities.py --check` was executed to verify that no unauthorized network-enabled gates were introduced.
- Status: **ALIVE** (`ok: 0 network gate(s), all allowlisted`).

---

## 8. Remediation and Action Plan

1. **Immediate P0 Blockers**:
   - Relocate `baselines.toml` and `shapes.toml` out of `packs/xstate-v5-machine-pack/gates/` to unblock `scripts/marketplace.py validate` and `scripts/qualify_packs.py`.
   - Add `--skip-ea-admission` to `scripts/check_self_pack_scaffolding.py` line 77 to conform with ambient `ggen 26.11.5`.
2. **RDF / SHACL Fixes**:
   - Add `@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .` to `packs/latency-hazard-radar/shapes.ttl`.
   - Add `sh:path` declarations to `ddui:worldDigest` and sibling PropertyShapes in `packs/dfcm-pack/ontology/dd-ui.ttl`.
   - Clean/transcode JSON-LD and corrupted 404 files in `packs/smalt-core-pack/vendor/`.
3. **CI-05 Cargo Dependency Backlog**:
   - For crates in `automatic-autonomic-operations-pack`, `certification-assist-pack`, `ontostar-mustar-powlv2-agent-pack`, and `speedrun-talent-network-pack`, publish crates to crates.io or vendor the required interface definitions instead of using local relative paths into `crates/`.
4. **SPARQL Performance Tuning**:
   - Optimize queries in `rust-doc-hdit-pack` and `xstate-v5-machine-pack` to prevent runaway sync evaluation under oxigraph.
