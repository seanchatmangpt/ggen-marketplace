# Explanation: the ggen ecosystem map

This document records what six sibling repositories are, how they relate, and what state each was
observed in during a single working session on 2026-08-15. Every claim here is sourced from a
first-hand pass in which an agent read and built that repository. Where something was not
verified, this document says so instead of guessing.

Read the health section as a **point-in-time observation, not a standing guarantee**. Build
status, test counts, and branch sync all change with the next commit.

## What the ecosystem is

`ggen` is a deterministic manufacturing engine: an RDF/Turtle ontology supplies a domain model,
Tera templates carry SPARQL frontmatter, and `ggen sync run` resolves the graph, extracts
bindings, renders outputs, applies write semantics, and emits a BLAKE3-chained receipt. Its
README states the pipeline as `ontology + templates + policy → admitted graph → deterministic
artifacts → receipt`.

The other five repositories sit around that engine in distinct roles:

| Repository | Role |
|---|---|
| `ggen` | The engine and its front ends (CLI, LSP, MCP server) |
| `ggen-marketplace` | The canonical pack corpus consumed by the engine (this repository) |
| `ggen-create` | Turns existing working examples into ggen manufacturing packages |
| `ggen-legacy` | Verification/retirement machinery over legacy estates and over `ggen` itself |
| `ggen-mcp` | A spreadsheet MCP server fork extended into a ggen codegen host |
| `ggen-spec-kit` | An RDF-first spec-driven-development CLI that shells out to the engine |

## Repository roles in detail

### ggen — the engine

Rust, edition 2021, Cargo workspace at version `26.8.12`, MIT licensed. Root package `ggen` plus
16 declared workspace members; `crates/` holds 14 real crates. Front ends: `ggen-cli`,
`ggen-lsp`, `ggen-mcp`. Substrate: `ggen-graph` (oxigraph store, OCEL, coherence, its own
authoritative SHACL), `ggen-engine` (a vendored, renamed replacement for the old `ggen-core`,
`publish = false`), and `praxis-core` / `praxis-graphlaw` (the law/lifecycle/receipt substrate).

Coupling to `~/praxis` is by **vendoring, not linking**: `ggen-engine`, `praxis-core`, and
`praxis-graphlaw` are in-tree copies so migration-specific edits land here rather than upstream.
There are no git submodules and no cross-repo path dependencies in any crate manifest, so `ggen`
builds standalone.

### ggen-marketplace — the pack corpus

Python 3.12 is the operational language (all of `scripts/`, run directly, no packaging manifest).
One small Rust crate, `tools/marketplace-config`, is built with a pinned `nightly-2026-04-15`
toolchain. `packs/` holds 120 packs — 162 ontologies, 877 templates, 396 native gates, 4 verifier
gates.

It consumes `ggen` as a **prebuilt release binary**: `marketplace.toml [ggen]` pins
`version = "v26.8.11"`, `release_commit = 402cecd`, with per-platform asset SHA-256 digests. CI
installs that binary and qualifies every pack through the real runtime — no Rust compile of the
engine. It also consumes `seanchatmangpt/star-toml` at rev `8395515c` and, transitively,
`wasm4pm-compat =26.6.28` from crates.io.

Source authority is asserted in `marketplace.toml [source_authority]` and enforced by
`verify_source_authority.py`: this repository's `main` is canonical after admission, other
repositories are provenance or mirrors only. See [source-of-truth.md](source-of-truth.md).

### ggen-create — the exemplar-to-pack compiler

Dual-stack. Python 3.11+ is primary (`ggen_create` v26.8.7, sole runtime dep `fastmcp[tasks]`,
entry points `ggen-create`, `ggen-create-mcp`, `ggen-create-a2a`). Rust is secondary:
`crates/ggen-dspy` v5.1.0, toolchain pinned to 1.85.1, `publish = false`,
`#![forbid(unsafe_code)]`, zero runtime dependencies.

It consumes `ggen` two ways: CI downloads a pinned, checksum-verified release binary to run its
parity crown, and `crates/ggen-dspy` is a source-provenance descendant of
`seanchatmangpt/ggen@39c5d11d…/crates/ggen-dspy`, recorded as `provenance_commit` in
`architecture/enterprise.toml`. The historical `ggen-ai` workspace dependency was deliberately
severed in favour of a local `LanguageModel` trait boundary. It also consumes the external
`ronp001/hygen-create` as a pinned git submodule, used as a byte-for-byte parity oracle.

Its authority boundary matters ecosystem-wide: SELECT/CONSTRUCT allowed, ambient DO forbidden.
Reasoning modules emit intents; a host broker is the exclusive DO path owning policy,
credentials, actuation, receipts, replay, and standing.

### ggen-legacy — verification and retirement machinery

Primarily Rust (edition 2021, `rust-version = 1.82.0`) with a substantial Python tooling layer
under `tools/v26.8.1/`. Task runner is `just`. It is **not** a single Cargo workspace — the root
crate and each `tools/*` crate are independent manifests, so a plain root `cargo test` verifies
only the LSP crate.

The root crate is `ggen-legacy-lsp` v26.8.5, an independent ggen language-server contract
receiver built on `lsp-max`. The repository's stated purpose is broader: reconstruct a legacy
repository's observable contract, admit it, manufacture a replacement, verify behavioural
closure, replay, and compute whether the predecessor may be retired.

It consumes `lsp-max` from `github.com/seanchatmangpt/lsp-max` as a **git rev pin on an unmerged
branch**, with an explicit `PROVISIONAL PIN` comment in `Cargo.toml`. It consumes
`chicago-tdd-tools` v26.8.3 as a dev-dependency. `docs/v26.8.1/manifest.toml` references
`seanchatmangpt/ggen` — the v26.8.1 tooling is the observer/crown verifier for ggen v26.8.1 and
for the ggen-legacy sunset. This repository therefore both provides verification machinery over
`ggen` and is itself the artifact scheduled for retirement.

### ggen-mcp — MCP server and codegen host

Rust, **edition 2024**, task runner `cargo-make`. There is an identity split: the crate is
`spreadsheet-mcp` v1.0.0 (upstream `PSU3D0/spreadsheet-mcp`, Apache-2.0) while the repository is
`seanchatmangpt/ggen-mcp`, a fork extended into an ontology-driven codegen host. `src/` holds 18
modules; `tests/` holds 100 integration test files.

Unlike every other consumer here, it consumes `ggen` **by path dependency through a git
submodule**: `ggen-ontology-core`, `ggen-core`, `ggen-domain`, and `ggen-config` are all
`{ path = "ggen/crates/…" }` against the `ggen` submodule pinned at `aa51b00e9`. It also consumes
`ggen` as a code generator — `ggen.toml` drives `ggen sync` into `src/generated/**`, and its
`sync_ggen` MCP tool re-runs that pipeline in-process.

Its `chicago-tdd-tools` dev-dependency points at `../chicago-tdd-tools` (a sibling directory on
disk), **not** the in-repo submodule of the same name. Both exist; only the sibling is wired into
the build.

### ggen-spec-kit — spec-driven-development CLI

Python ≥3.11 (observed running 3.13.9), `hatchling` backend, `uv` for env and lock. Package
`specify-cli` v0.0.25, MIT, console entry point `specify`. `src/specify_cli/` holds 263 Python
files in a three-tier `commands/` → `ops/` → `runtime/` architecture, plus `core/`,
`hyperdimensional/`, `agi/`, `ml/`, `mcp/`, `db/`, and others.

It consumes `ggen` as an **external binary only** — no Python dependency on it. `runtime/ggen.py`
and `runtime/tools.py` shell out to `ggen --version` and `ggen sync`; `ggen` is in
`OPTIONAL_TOOLS` with graceful degradation when absent. `pyproject.toml` comments pin ggen v5.0.2
(that pin was **not** verified against a registry this session). Two git submodules:
`vendors/uvmgr` and third-party `fastmcp`. It provides no library surface to other ggen
repositories — it is a leaf consumer and an end-user CLI.

## How the repositories relate

Every dependency edge observed this session flows toward `ggen`; nothing in the ecosystem was
found depending on `ggen-mcp`, `ggen-create`, or `ggen-spec-kit` in-tree.

```text
ggen-marketplace  --pinned release binary + asset digests-->  ggen
ggen-create       --pinned release binary (CI parity crown)-->  ggen
ggen-create       --source provenance of crates/ggen-dspy-->  ggen
ggen-spec-kit     --external binary, shell-out only------->  ggen
ggen-mcp          --git submodule + path dependencies----->  ggen
ggen-mcp          --ggen sync generates src/generated/**-->  ggen
ggen-legacy       --observes / verifies / crowns----------->  ggen
ggen             --vendored in-tree copies----------------->  ~/praxis (not one of the six)
```

Four distinct coupling styles are in play, and they fail differently:

- **Digest-pinned release binary** (`ggen-marketplace`, `ggen-create`) — reproducible, but goes
  stale silently when `ggen` releases move.
- **Shell-out to whatever binary is on `PATH`** (`ggen-spec-kit`) — degrades gracefully, but the
  version actually used is unpinned at runtime.
- **Submodule plus path dependency** (`ggen-mcp`) — compiles against real engine source, so it
  breaks immediately on upstream API change.
- **Vendored copy with no sync mechanism** (`ggen`'s own `praxis-*` crates, and `ggen-create`'s
  DSPy kernel) — insulated from upstream churn, and silently divergent from it.

`ggen-marketplace` packs also model *other* ecosystem repositories as subjects (wasm4pm,
clap-noun-verb, cargo-cicd, dflss, chatman-*), so pack facts drift when those repositories change.

## Observed health as of 2026-08-15

Point-in-time only. Each row reflects one agent's actual command output during this session.

**`ggen`** — `cargo check --workspace --all-targets` clean. `ggen-graph` 129/129 pass;
`praxis-core` 137/137 pass (3 ignored). Branch `agent/lifecycle-boundary-doc-comment` in sync.

**`ggen-marketplace`** — Rust tool `cargo check` clean. 115/115 pytest pass; `marketplace.py
validate` admits 120 packs; cross-pack gate exits 0 with zero violations; catalog projection
byte-identical across runs. Branch `main` in sync.

**`ggen-create`** — builds clean, `cargo fmt --check` clean. 45/45 Rust tests pass; 110/110
Python tests pass (1 skipped). Branch `feat/rust-dspy-kernel-20260812` in sync.

**`ggen-legacy`** — builds. Root crate 17/17 pass; `tools/v26.8.1/` crate 15/15 pass.
Branch `agent/add-dsrust-groq-disposition-proposer` in sync.

**`ggen-mcp`** — `cargo build` passes (0 errors, 135 warnings); the binary builds and runs.
Test count **UNKNOWN** — test targets do not compile. Branch `main` in sync.

**`ggen-spec-kit`** — imports and CLI work. 2263 passed, 16 failed, 126 skipped, 10 xfailed,
77 xpassed; 2 test modules remain uncollectible. Branch `main` in sync, after a 75-commit
fast-forward performed during this session.

Notes on the two rows that are not simply green:

- `ggen-mcp`'s library and binary compiled for the first time this session (96 errors → 0, an
  Oxigraph 0.5.x migration). Its test targets still do not: **44 errors** on the lib test target,
  **219** with `--all-targets`. No test has been executed, so its test count is genuinely unknown.
- `ggen-spec-kit`'s 2 remaining uncollectible test modules and 16 failures are described under
  hazards below.

Clippy was clean where it was run (`ggen`'s `ggen-graph` and `praxis-core`, `ggen-legacy`'s root
crate). It was **not available** in `ggen-create` (minimal toolchain profile), and was not
reported for `ggen-mcp` or `ggen-spec-kit`.

## Outstanding hazards

Unresolved items that need a human decision. Nothing in this section was fixed this session.

### Needs a decision before anyone can proceed

1. **Unexplained `.claude/agents/*.md` deletions, three passes running.** `ggen-mcp` has 7
   deleted files in its working tree plus 112 more inside its dirty `ggen` submodule;
   `ggen-spec-kit` has 7. All were left uncommitted and unreverted. In `ggen-spec-kit` the
   deletions now **directly conflict with upstream work**: the 75 commits merged this session
   modified and expanded those same files (`11 files changed, 620 insertions, 82 deletions`,
   including 4 new agent files). Recovery in `ggen-spec-kit` is `git checkout HEAD --
   .claude/agents/`. No commit anywhere explains why they were removed.
2. **A private signing key is untracked in `ggen`'s working tree**:
   `examples/goat-capabilities-verify/.ggen/keys/signing.key`, alongside `verifying.key`. Flagged
   across three passes, still unowned. It must not be committed. Someone should confirm it is a
   throwaway demo key and delete it, or treat it as compromised.
3. **`ggen-mcp` has never run its test suite.** The largest single error class: integration tests
   reference a crate named `ggen_mcp` while `Cargo.toml` declares `spreadsheet-mcp`. That is a
   naming decision (rename the package, or add a `[lib] name`), not a mechanical fix. Other
   classes: stale struct shapes, `QuerySolution: From<Vec<…>>` in test constructors, `E0133`
   unsafe `env::set_var` under edition 2024, a missing `tests/common/` module.
4. **`ggen-spec-kit` was 75 commits behind `origin/main`** at the start of this session, blocked
   from fast-forwarding by a dirty tree. It was fast-forwarded to `d7556eb` and the working tree
   restored to its found state, but the pre-sync tree is still held in
   `stash@{0}: pre-ff-sync-1786919411`. That stash should be deleted once hazard 1 is ruled on.

### Cross-repo compatibility

5. **`ggen-mcp`'s generated code will re-break on the next `ggen sync`.** The ggen template still
   emits `#[tool(...)]` on free functions taking `&SpreadsheetServer`; rmcp 0.11's macro boxes a
   `'static` future, so that form cannot compile. The attributes were stripped from the *output*
   in `src/generated/mcp_tools.rs`. The real fix belongs in the `ggen` repository's template.
6. **`ggen-create`'s CI pins a stale ggen binary.** `.github/workflows/ci.yml` pins
   `GGEN_VERSION: "v26.8.6"`; a live check showed the latest release as v26.8.16 (2026-08-16). The
   parity crown is validating against an old engine. Bumping it needs the ggen owner — blind
   bumping could break the crown.
7. **`ggen-marketplace` pins `v26.8.11` and `ggen-spec-kit` pins v5.0.2.** These are three
   different engine versions across three consumers. The v5.0.2 pin could not be verified against
   crates.io this session (the API response did not parse) and was left alone.
8. **`ggen-legacy` depends on an unmerged branch.** `lsp-max` is pinned to a git rev on the
   unmerged branch `fix/wasm4pm-lsp-example-crates-io-dep` in the same GitHub org, with an
   explicit in-manifest note that it is not admitted as a stable dependency. Unblocking requires
   that branch merged upstream, or a released tag to re-pin against.
9. **`ggen-mcp`'s `chicago-tdd-tools` dependency points outside the repository**
   (`../chicago-tdd-tools`), bypassing the vendored submodule of the same name. Non-hermetic: CI
   or a fresh clone will not resolve it.
10. **`ggen`'s vendored praxis crates have no drift detection.** `ggen-engine`, `praxis-core`, and
    `praxis-graphlaw` are hand-copied from `~/praxis` with no sync mechanism or version marker.
    Divergence is silent.

### Untracked or unexplained trees

11. **`ggen`**: `packs/goat-capabilities-pack/` and `examples/goat-capabilities-verify/` — 21
    untracked files including `.pytest_cache/`, `__pycache__/`, `.ggen-v2/receipt-log.jsonl`, and
    the private key in hazard 2. Unexplained for three passes; neither committed nor deleted.
12. **`ggen-legacy`**: `tools/architecture-foundry/` — 511 MB of untracked build debris
    (`Cargo.lock` + `target/`, no source on this branch). Not gitignored, so it appears in every
    `git status` and is one careless `git add -A` away from being committed.
13. **`ggen-mcp`**: an untracked 13-line `Justfile` wrapping `cargo make`, plus a checked-in
    backup file `src/state_original.rs.bak`.
14. **`ggen-marketplace`**: live WIP in `packs/dflss-pack/` from a concurrent agent, uncommitted
    at the end of this session. Stage file-by-file in this repository — the exact pin
    `wasm4pm-compat = "=26.6.28"` has been broken before by a blind `git add -A`.

### Repository hygiene and gates

15. **`ggen` reports 42 open Dependabot vulnerabilities** on its default branch (5 critical, 22
    high, 15 moderate), surfaced by GitHub on push. Nobody is triaging them.
16. **`ggen` tracks a nondeterministic generated artifact** in git:
    `.cargo-cicd/ocel/chatman/admission_table.ocel.json` regenerates with fresh UUIDs and
    reordered events on every test run, dirtying the tree and inviting spurious conflicts.
17. **`ggen-spec-kit`'s CI lint gate cannot pass**: `ruff check src/ tests/` reports 2302 errors
    (397 auto-fixable). Its coverage gate is `--cov-fail-under=50`; a single-file run measured
    3.36%, so the real figure needs a full-suite measurement.
18. **`ggen-spec-kit` test decay**: `tests/unit/test_ops_jtbd.py` imports 6 symbols that do not
    exist in its module (which defines only `analyze_jobs` plus 4 private helpers) — a product
    decision, not a rename. `tests/property/test_hyperdimensional_properties.pbt.py` has never
    run: the `.pbt.py` suffix makes the module name unimportable. 22 `__pycache__/*.pyc` files
    remain tracked despite `.gitignore` and need `git rm --cached`.
19. **`ggen-marketplace`'s `ci-status` shard cross-check detects overlap, not omission.** Its step
    is named "covers every admitted pack exactly once", but the script only raises on duplicate
    pack names — it never asserts the shard union equals the admitted corpus. A pack missing from
    every shard would pass CI.
20. **`ggen-marketplace` cross-pack gate: 669 statements remain unparseable** — genuine blank-node
    and collection syntax outside its declared flat dialect. They are reported, never silently
    accepted. Closing this fully needs a real RDF parser dependency the repository deliberately
    avoids.
21. **Recurring bug class in `ggen`**: three passes each found code gated behind a feature never
    declared (`mfw::planner`, then two `signed` guards in `praxis-core` referencing a module that
    does not exist). A CI gate on `unexpected_cfgs` would catch the next one automatically.
22. **Fragmented build graphs.** `ggen-legacy` has no root workspace over `tools/*`, so a green
    root `cargo test` does not mean a green repository — `just ci-all` is required.
    `ggen-marketplace` has two pytest homes (`scripts/` and `tests/`) where basename collisions
    break root collection.
23. **Long-lived unmerged branches.** `ggen-create`'s `feat/rust-dspy-kernel-20260812` and
    `ggen`'s `agent/lifecycle-boundary-doc-comment` diverge from their default branches with each
    pass.

## Limits of this document

- It covers six repositories. `~/praxis`, `lsp-max`, `chicago-tdd-tools`, `star-toml`,
  `uvmgr`, and `hygen-create` appear here only as named dependencies; none was read first-hand.
- Every health figure came from one run on one machine. None was re-run for this document.
- Clippy, coverage, and CI status were not uniformly measured across all six repositories; where
  a figure is absent above, it was not collected, which is not evidence that it is clean.
- No claim is made that any hazard listed above is still open at the time you read this.

## See also

- [Source of truth](source-of-truth.md) — why marketplace pack bytes are canonical after admission
- [Why a separate marketplace](why-a-separate-marketplace.md) — the ownership boundary with ggen
- [Security and authority](security-and-authority.md)
- [Pack lifecycle](pack-lifecycle.md)

Last updated: 2026-08-15 (observation date). Point-in-time record, not a standing guarantee.
