# Generation Determinism — ash-extension-pack Hardening (Lane BY)

Date: 2026-10-01 · Repo: ~/ggen-marketplace (branch `spark-closure-courts`) ·
Pack: `packs/ash-extension-pack`

## The defect class

A sibling consumer (ash_pplan) hit intermittent **byte-drift**: the SAME ontology
rendered twice produced different bytes (md5 flip-flop on
`capability_catalog.ex`). Root causes found in the pack's court templates:

1. **Unordered `for_each` driver queries.** Every court template declares
   `for_each: "spec"`, but nine templates' frontmatter `spec:` SPARQL had no
   `ORDER BY`. Row order was engine-implementation-defined, so which row feeds
   each render — and render set order — was nondeterministic.
2. **`GROUP_CONCAT` element order is unspecified in SPARQL.**
   `reactor_parity_court.exs.tmpl` and `reactor_pipeline.ex.tmpl` split
   `wait_for_names` (a GROUP_CONCAT string) and render `wait_for :a, :b` in
   concat order. Concat order is not guaranteed equal across runs/engines —
   the same class as ash_pplan's catalog drift.
3. **Tera renderer parse/render failures are deterministic once templates
   parse** — but four templates (`transformer_court`, `runtime_burn_in`,
   `evidence_export`, `closure_receipt`) FAILED outright under the production
   WASM tera renderer because of renderer-fragile syntax:
   - positional `replace` filter args (`replace(".Resource", "")`) — the WASM
     tera build rejects positional args; `replace(from=..., to=...)` works.
   - parenthesized dotted access `(sections | first).section_name` — rejected;
     must be `{% set s = sections | first %}{{ s.section_name }}`.
   - literal `{{` in embedded Elixir (`{{:., m, [...]}` AST match patterns;
     `&match?({{{ module_prefix }}...`) — Tera opens an interpolation at the
     first `{{`. Fix: `{% raw %}` wrapping (transformer_court) or rewrite the
     Elixir to avoid triple braces (`Enum.any?(mods, fn {m, _} -> m == ... end)`
     in runtime_burn_in).

## Hardened files (packs/ash-extension-pack)

Frontmatter `spec:` queries — added `ORDER BY ?package_name ?module_name`
(total order on DISTINCT rows):

- `templates/spark_parity_court.exs.tmpl`
- `templates/reactor_parity_court.exs.tmpl`
- `templates/info_parity_court.exs.tmpl`
- `templates/runtime_burn_in.exs.tmpl`
- `templates/evidence_export.exs.tmpl`
- `templates/closure_receipt.exs.tmpl`
- `templates/verifier_court.exs.tmpl` (GROUP BY + added ORDER BY)
- `templates/igniter_idempotence_court.exs.tmpl` (GROUP BY + added ORDER BY)

Body-level iteration fixes:

- `reactor_parity_court.exs.tmpl`: `wait_for` list now
  `split(pat=",") | sort` before the render loop.
- `reactor_pipeline.ex.tmpl`: same `split | sort` fix on `wait_for_names`
  (this template renders PRODUCTION code, not just courts — the highest-value
  single fix).
- `templates/transformer_court.exs.tmpl`:
  `(sections | first).section_name` → `{% set %}` + dotted access (2 sites);
  four `{{:., m, [...]}}` AST-match clause heads wrapped in `{% raw %}`.
- `runtime_burn_in.exs.tmpl`: two `&match?({{{ module_prefix }}...})` sites
  rewritten to `Enum.any?(mods, fn {m, _} -> m == {{ module_prefix }}.BurnIn.Specimen end)`.
- `closure_receipt` / `evidence_export` / `runtime_burn_in`: positional
  `replace(".Resource", "")` → `replace(from=".Resource", to="")`.

## Gates

All 13 `gates/*.rq` already carried `ORDER BY` on every SELECT (verified by
running every gate against the pack ontology via ggen_igniter's oxigraph
engine — all parse and run; gate 120's 8 rows are unique under
`ORDER BY ?s ?dead`). A `130_installer_dep_contract.rq` appeared mid-session
(another lane); it also runs ok with ORDER BY.

No gate changes were required. The pack's `verify/render_check.exs` (run via
ash_pplan's ggen_igniter dep, `MIX_BUILD_ROOT=_build-by`) passed: 13/13 gates
run ok, 9/10 legacy templates render (reactor_pipeline's pre-existing
0-driver-rows error is now non-empty with the determinism probe fixture).

## 5x-identical proof

Harness: `tmp/by-determinism-proof.exs` in ash_pplan. Same ontology
(pack ontology.ttl + a minimal `det_probe` ReactorStep fixture,
`tmp/det-probe.ttl`, merged into `tmp/det-probe-merged.ttl`) rendered 5 times
through the real production path (frontmatter sparql →
GgenIgniter.Query.Oxigraph → build_bindings → TeraWasm). All 5 md5s identical
per template:

```
IDENTICAL  spark_parity_court.exs.tmpl      5x md5: 88c706e5005359593247dd479e12d123
IDENTICAL  reactor_parity_court.exs.tmpl    5x md5: 39fa7aac7e2c3a4193cd074dcaf670bb
IDENTICAL  info_parity_court.exs.tmpl       5x md5: 98de5f7671b8cbcc3cab7285ae75baac
IDENTICAL  verifier_court.exs.tmpl  5x md5: 38f78ee4a25e16658ab7eb40d6c870e3
IDENTICAL  transformer_court.exs.tmpl       5x md5: 88ccd98e5a2fb081e50fdce79ccbb403
IDENTICAL  igniter_idempotence_court.exs.tmpl 5x md5: 9afac215b23f61b5e33f94c14b7b1dcb
IDENTICAL  composition_court.exs.tmpl       5x md5: d59137e73dcc9e226dcbbba5e4eb33a0
IDENTICAL  runtime_burn_in.exs.tmpl         5x md5: 5172c1d7c4f8646ea696571fffd33ee5
IDENTICAL  evidence_export.exs.tmpl         5x md5: cb42647d0625f42efddf665d0ae64a89
IDENTICAL  closure_receipt.exs.tmpl         5x md5: f38f8e31c0a55d983f56c7aa0b82f1b7
IDENTICAL  reactor_pipeline.ex.tmpl         5x md5: 8511fbfbb7c1b91863c1dd183aa75273
```

Per-run outputs land in `~/ash_pplan/tmp/generation-determinism/` (5 files per
template, plus a merged ontology and the probe fixture).

## Recommendation for ggen_igniter (gate-level ORDER BY enforcement)

1. **Enforce ORDER BY at the gate level**: reject any `SELECT`/`SELECT DISTINCT`
   (frontmatter `sparql:` queries included) without a top-level `ORDER BY` —
   the same rule Rust ggen strict_mode already enforces (E0013). ggen_igniter's
   `mix ggen_igniter.sync` should refuse to render from an unordered query, the
   way it refuses `--out` outside the authorized root. Frontmatter queries are
   production render inputs, not just gates — they need the same discipline.
2. **Ban GROUP_CONCAT without a deterministic sub-order**: either reject it, or
   require templates to `| sort` the split list before iterating (what
   reactor_parity_court and reactor_pipeline now do).
3. **Renderer-fragile syntax blocklist**: reject positional filter args
   (`replace("a", "b")`), parenthesized dotted access
   (`(x | first).y`), and literal `{{` inside template bodies (require
   `{% raw %}` or an Elixir rewrite). Each of the three killed one or more
   court templates under WASM tera before this pass.
4. **Repeatability gate**: `mix ggen_igniter.sync --check` should render
   twice and fail on byte mismatch — turning this defect class into an
   admission-time failure instead of a downstream md5 flip-flop.

## Replay

```
cd /Users/sac/ash_pplan
MIX_BUILD_ROOT=_build-by mix run tmp/by-determinism-proof.exs        # 10 court templates, 5x md5
MIX_BUILD_ROOT=_build-by mix run tmp/reactor-pipeline-proof.exs      # reactor_pipeline, 5x md5
MIX_BUILD_ROOT=_build-by mix run tmp/gate-check.exs                  # 13/13 gates run ok
MIX_BUILD_ROOT=_build-by mix run <pack>/verify/render_check.exs      # full render_check
```

No git operations were run (per lane contract); coordinator owns commits.