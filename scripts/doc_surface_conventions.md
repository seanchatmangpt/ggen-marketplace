# doc_surface_conventions

# doc-hdit v1 Conventions

Feeds `doc-hdit:vectorize`. v1 is a **rigorous deterministic symbol scanner**,
not a semantic indexer: stdlib Python only (regex + `ast`), no tree-sitter and
no oxigraph. tree-sitter (real grammar-based parsing) + oxigraph (RDF store
for the claim triples) is the **v2 path**; the EAV claim shape below was
chosen so claims lift directly into RDF subjects/predicates/objects later.

## Determinism contract

- Same repo tree in -> byte-identical JSON out (all iteration is sorted;
  output `sort_keys=True`). No network, no clock, no randomness.
- Stdlib only. No third-party dependency to audit.

## Code mode

`gen_doc_surface.py code REPO > code-surface.json`

- **Language detection** by marker file; all present markers are scanned:
  `mix.exs` (Elixir), `Cargo.toml` (Rust, workspace-aware). Skip dirs:
  deps/_build/node_modules/target/.git/.venv/priv.
- **Elixir**: `lib`-rooted `*.ex` (excludes `mix.exs` as a module file);
  defmodule names via do/end depth tracking (comment lines are naively
  stripped before depth counting — disclosed limit: a `#` inside a string
  naively strips, depth still recovers at the next real `end`).
  Public `def name/arity` (defp excluded by design), first-line `@doc`,
  `@spec` line captured when adjacent to the def line, Ash `resource`
  blocks (`attributes`/`actions` via block capture → `ash_resource` items
  with attribute/action invariants). Version from mix.exs `@version "x"`
  or `version: "x"`.
- **Rust**: workspace crates (dirs with Cargo.toml + src/) or single crate;
  `pub fn (name+args)`, `pub struct/enum/trait`, version+package from
  Cargo.toml `[package]` (workspace.package fallback). Comment stripping
  may over-strip but only risks false negatives, not false positives on
  `pub` items (disclosed limit).
- **Node/bun**: package.json `bin` verbs + `scripts`.
- **Python**: classes and public defs via `ast` (deterministic by
  construction).

Output shape:

```json
{
  "repo": "...", "path": "...", "version": {...},
  "modules": [{"name": "...", "file": "relative.ex", "items": [
    {"kind": "function", "ident": "plan", "signature": "plan/4", "doc": "...", "spec": "..."}
  ]}]
}
```

Ash resource items carry `invariants` = `{attributes: [...], actions: [...]}`.

## Doc mode

`gen_doc_surface.py doc REPO --code-json code-surface.json > doc-claims.json`

- Scans markdown under `docs/` and `book/` (fall back to repo root);
  `--docs-dir` overrides. deps/_build/node_modules/target/.git/.venv/priv skipped.
- Headings track current section → `subject: file#Section`.
- Inline code spans → `{subject: file#Section, predicate: mentions, object: span}` when the span
  resolves against the code surface (exact, arity-suffixed, dotted-last-segment, or `--flag` passthrough).
- Fenced blocks whose text references a known module → `{predicate: references_block}`.
- Tables whose header row contains param+default columns → `{predicate: has_param, object: {param, default}}` pairs.

Output shape:

```json
{
  "repo": "...", "doc_roots": [".../docs"],
  "claims": [{"subject": "docs/x.md#Usage", "predicate": "mentions",
              "object": "plan/4", "kind": "inline_span"}]
}
```

## Self-test receipt (2026-10-08)

Ran against two live repos; outputs at /tmp/{repo}_code.json, /tmp/{repo}_doc.json.

| repo | code modules | code items | versions | doc claims |
|---|---|---|---|---|
| ex4pm | 596 | 1353 | mix.exs 26.10.8 | 1014 |
| ferroplan | 224 | 1732 | 12 crates 0.29.0 (ferroplan-mcp 1.88) | 919 |

Spot-verified in source (grep, all present):
`def canonicalize/1` (lib/ex4pm_core/capsule_graph/digest.ex),
`def canonical/1` (lib/ex4pm/gall.ex),
`pub fn simulate_ppddl` (crates/ferroplan/src/ppddl/solver/part05.rs),
`pub fn load` (crucible/crates/crucible-publish/src/compare.rs),
`pub enum RefusalCode` (crates/ferroplan-cli/src/harvest/model.rs).

## TypeScript/JavaScript (gen_doc_surface_ts.py)

`gen_doc_surface_ts.py code REPO` emits the same JSON schema via a
stdlib-only TS/JS scanner: `src/**/*.ts` exports (function/class/
const/interface/type/enum + default), class methods (brace-depth),
function signatures, and package.json `bin`/`scripts`. Same skip dirs
plus test/tests/fixtures/__tests__/dist/coverage and `*.test.ts`/
`*.spec.ts`/`*.d.ts`; shares the determinism contract and naive
comment-strip limits above.

## Known v1 limits (disclosed)

- No real parser: regex + do/end depth, not AST-accurate for Elixir/Rust.
  Strings containing `do`/`end` keywords can perturb depth; multi-line
  signatures only captured when fully on one line or via the multiline
  Rust fn regex (non-greedy within one signature).
- Public-only by design (def, pub); private helpers out of scope for v1.
- Doc-claim spans resolve only against the same repo's code surface.
- Excludes test/ — scan covers `*.ex`/`*.rs` anywhere outside skip dirs,
  including test files; filter by `file` field downstream if needed.
- Param tables with prose-containing rows extract verbatim (deterministic
  verbatim extraction, no cleanup).
- tree-sitter + oxigraph upgrade path: claims are already EAV-shaped; v2
  maps subject/predicate/object 1:1 onto an RDF graph in oxigraph.
