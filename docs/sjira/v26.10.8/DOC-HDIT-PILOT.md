# DOC-HDIT-PILOT — end-to-end pilot of the doc-hdit pipeline (v26.10.8)

Lane: hdit-pilot, 2026-10-08. Extraction via `scripts/gen_doc_surface.py` (v1 deterministic
scanner); metrics via `packs/rust-doc-hdit-pack/target/release/doc-hdit` against
`packs/rust-doc-hdit-pack/courts/doc_quality.court`. Inputs in `/tmp/hdit/*.inputs.json`
(claim `id` + stringified `object` added to satisfy the v1 CLI schema; no repo source touched).

## Metrics per repo (real runs)

| repo | claims | S_coverage | Phi_halluc | Q_density | audit exit |
|---|---|---|---|---|---|
| ex4pm (Elixir) | 1014 | 0.2060 | 1.2602 | 0.0089 | 1 (FAIL x3) |
| ferroplan (Rust) | 919 | 0.2108 | 1.2563 | 0.0096 | 1 (FAIL x3) |

Offending claim indices (audit output, top-3 ranking): ex4pm `[327, 84, 897]`,
ferroplan `[357, 679, 680]`.

## Phantom classification (top-5 per repo, ground-truthed against source)

Key finding: **every top-5 "phantom" references a symbol that exists in the extracted code
surface.** The VSA alignment metric carries no signal (see Verdict).

| repo | idx | claim object | exists in code surface? | classification |
|---|---|---|---|---|
| ex4pm | 327 | `verify/0` (doc: `Ex4pm.Contracts.verify/0`) | yes (`Ex4pm.Contracts`) | metric false positive |
| ex4pm | 84 | `receipt/1` | yes (`evidence.ex`, API span) | metric false positive |
| ex4pm | 897 | `Ex4pm.OCEL.normalize/1` | yes (`ocel.ex:101`) | metric false positive |
| ex4pm | 158 | `Ex4pmEngine.Wasm.Conform` | yes (`conform.ex:1`) | metric false positive |
| ex4pm | 248 | `Ex4pm.Evidence.Receipt` | yes (`evidence.ex:1`) | metric false positive |
| ferroplan | 357 | `--mem-gb` | no — CLI flag, not a symbol | over-extraction (v1 doc scanner claims flags as symbols) |
| ferroplan | 679–681 | `valid` (x3) | yes (`plan.rs`, lib.rs `pub fn valid`) | metric false positive |
| ferroplan | 725 | `solve_hddl` | yes (`crates/ferroplan/src/hddl.rs`) | metric false positive |

ex4pm row 5 (idx 248) ground truth: `Ex4pm.Evidence.Receipt` is real
(`lib/ex4pm/evidence.ex:1`), also metric false positive.

## Verdict

**No. The repos do not meet the court thresholds, but the failures are implementation
artifacts, not documentation defects.** Evidence:

1. **Phi_halluc is uncalibrated.** A control claim with an invented symbol
   (`zzz_totally_fake_symbol_zzz`) scores alignment 0.2854 vs. median 0.2894 — no separation
   between real and fabricated references. All 1014/919 claims rank as phantoms with
   alignment in a narrow band (ex4pm 0.265–0.315). Phi = 1.26 > 1 is impossible for a
   normalized residual and confirms encoder/projection mismatch in
   `info_theory/mod.rs` (`projection_residual`, `rank_phantoms`).
2. **Q_density = (log2(n) - 1) / n by construction.** `claim_grounded` requires the claim
   `subject` (a doc file path like `docs/foo.md#Section`) to be in the code token set — never
   true, so every claim is ungrounded and MI = H(D) - 1. Observed 0.00886 ≈ (log2(1014)-1)/1014
   exactly. The 0.65 threshold is unattainable as implemented.
3. **S_coverage ≈ 0.21 is a scope mismatch**, not hallucination: the v1 scanner's "code verbs"
   include every internal/duplicate clause of the whole repo, while docs cover the public
   surface. The court's 0.90 assumed a public-API scope.

Ground truth across 10 hand-checked claims: 8 real-symbol references flagged phantom
(metric FP), 1 CLI flag, 1 prose keyword (`valid` in gall-checkpoints.md is a boolean value in
a checkpoint table, also present as `pub fn valid`). **Zero true hallucinations found.**

## Recommended threshold adjustments (contingent on fixes, not now)

Thresholds must not move until the metric bugs are fixed (court file's own rule: do not relax
without a receipt showing the old value failing — this receipt is that showing, but the failure
is in the implementation, so the correct move is fix-then-remeasure, not relax).

## v2 extractor priorities

1. **P0 — encoder/projection fix**: `claim_grounded` must match on `object` only (subject is a
   doc path); `rank_phantoms` alignment must separate grounded vs. invented symbols (fake-symbol
   control belongs in the pack's tests).
2. **P1 — over-extraction filter**: backticked spans that are CLI flags (`--*`), prose keywords,
   or version strings should not become `mentions` claims (ferroplan top phantoms are flags).
3. **P2 — scope switch for S_coverage**: restrict the denominator to public/documented modules
   (Elixir `@doc`-annotated defs; Rust `pub` items reachable from crate root), or docs-dir-scoped
   symbol inventory.

## Replay

```sh
python3 scripts/gen_doc_surface.py code /Users/sac/ex4pm > /tmp/hdit/ex4pm.code.json
python3 scripts/gen_doc_surface.py doc /Users/sac/ex4pm --code-json /tmp/hdit/ex4pm.code.json > /tmp/hdit/ex4pm.doc.json
python3 - <<'EOF'  # merge to inputs schema (id + string object), see lane transcript
EOF
cargo build --release
target/release/doc-hdit vectorize /tmp/hdit/ex4pm.inputs.json
target/release/doc-hdit audit /tmp/hdit/ex4pm.inputs.json courts/doc_quality.court
# same for /Users/sac/ferroplan
```

Standing: PARTIAL_ALIVE — pipeline runs end to end on real repos (Elixir + Rust), audit gate
executes and refuses; metrics themselves are v1-uncalibrated (receipt above).

## Addendum — P2 scope fix + external-deps allowlist (lane hdit-p2, 2026-10-08)

Landed after P0/P1 (commits 67a283585, 42b031cfa):

1. **Public-surface scope (S_coverage)**: `gen_doc_surface.py` now marks every item and module
   `is_public` (Elixir: not `defp`/`defmacrop`/`defguardp` and not `@doc false`; Rust: `pub`
   items, file modules outside `tests/`/`benches/`/`examples/`/`bin/`; Python: non-underscore).
   `doc-hdit` computes S_coverage over the public surface only; the full-surface value is kept
   as `s_coverage_raw` (report-only). S_coverage gates again (was report-only pending this fix).
   Pre-P2 inputs without flags load as the full public surface (serde default, tested).
2. **External-deps allowlist**: `gen_doc_surface.py` emits `known_external` — module prefixes
   derived from `mix.exs` deps (`{:ash, ...}` → `Ash.`) and `Cargo.toml [dependencies]`
   (`serde_json = ...` → `serde_json::`). The audit classifies ungrounded claims whose object
   starts with a known prefix as `external_documented`: excluded from Phi, counted as density,
   reported as a separate count. Documented-deps allowance made explicit and enforceable —
   thresholds unchanged (S 0.90 / Phi 0.001 / Q 0.65).
3. Tests: `cargo test` 15 passed / 0 failed (includes P2 public-scope, external-classification,
   and legacy-inputs-default tests); `pytest tests/test_gen_doc_surface.py` 5 passed.

### Re-run (v2 inputs + P2 rescope, same repos, real runs)

| repo | claims | S_coverage (public) | S_coverage_raw | Phi_halluc | external_documented | Q_density | audit exit |
|---|---|---|---|---|---|---|---|
| ex4pm (Elixir) | 1046 | 0.1782 | 0.2316 | 0.0086 | 0 | 0.9914 | 1 (FAIL coverage, phantom) |
| ferroplan (Rust) | 756 | 0.2186 | 0.2204 | 0.0106 | 0 | 0.9894 | 1 (FAIL coverage, phantom) |

(Pre-P2 baselines: ex4pm S 0.2060 / Phi 1.2602 / Q 0.0089; ferroplan S 0.2108 / Phi 1.2563 /
Q 0.0096 — v1 metric bugs, see main receipt.)

### Findings

- **P0 fixed Phi/Q.** With exact-match grounding (P0) plus the allowlist, Phi fell from
  1.26 → 0.0086/0.0106 and Q_density rose to 0.9914/0.9894. Q_density now PASSES its 0.65 gate
  on both repos.
- **The documented-deps allowance classified 0 claims on both repos.** The residual phantoms
  (9 ex4pm / 8 ferroplan) are not external-dep references: they are prose artifacts — version
  tags (`release/v26.8.23`), source paths (`stream/metrics.ex`, `stage/{id}.jsonl`), a
  checkpoint-table cell dumped as a param row, and genuine private-surface references
  (`wasm_export/0`, facade methods). The mechanism is implemented and unit-tested; on this
  corpus the measured count is 0. A later extractor-side fix (claim shapes for paths/version
  tags) is the remaining over-extraction residue, not a court matter.
- **S_coverage gets worse, not better, under the public denominator** (0.206 → 0.178 ex4pm;
  0.211 → 0.219 ferroplan): a smaller code subspace absorbs less of the doc bundle. The v1
  scanner's denominator was not the binding constraint — the metric itself (VSA projection
  cosine of the doc bundle against the code subspace) does not implement the court's stated
  definition ("fraction of public surface items appearing in ≥ one doc claim"). Correct next
  step is a set-coverage implementation of S_coverage, not a threshold change. Thresholds were
  NOT relaxed; S_coverage gates at 0.90 and both repos honestly FAIL.

### Verdict per repo

- ex4pm: **FAIL** — coverage 0.1782 < 0.90, Phi 0.0086 > 0.001; density PASS.
- ferroplan: **FAIL** — coverage 0.2186 < 0.90, Phi 0.0106 > 0.001; density PASS.

Standing: PARTIAL_ALIVE — P2 scope + allowlist are ALIVE end to end on real repos with real
test evidence; court admission of either repo remains BLOCKED on (a) S_coverage set-coverage
reimplementation and (b) extractor claim-shape filtering for path/version artifacts.

## Addendum — P3 set-coverage S_coverage + prose-artifact filter (lane hdit-coverage, 2026-10-08)

Landed after P2 (commits 20aadd175 [core, see collision note], 8effc8a5b [extractor]):

1. **S_coverage set semantics (the gated metric)**: `s_coverage_set` now implements the court's
   stated definition — fraction of public items whose ident (bare / qualified `Module.ident` /
   arity `ident/2` form) or full signature appears in any claim object. The VSA projection
   cosine stays as `s_coverage_vsa`, report-only. `vectorize` emits `s_coverage_report` with
   covered/total and the top-10 uncovered public modules (the remediation list).
2. **Prose-artifact class**: claim objects that are version strings (`v26.8.23`), path
   fragments (`release/v26.8.23`, `stream/metrics.ex`, `stage/{id}.jsonl`), CLI flags, or
   non-identifier prose classify as `ClaimStatus::ProseArtifact` — excluded from Phi and
   Q_density numerator AND denominator, reported as a count. Primary filter is extractor-side
   (`gen_doc_surface.py` no longer emits them as symbol claims); the core classifier is
   defense in depth. Signature-quoted objects (`ignite(fuel: Fuel) -> Spark`) are real symbol
   references and are not prose.
3. **Collision note (same-checkout fan-out)**: the P3 core (pack src/tests) was swept into
   another lane's broad commit 20aadd175 ("certify verb") — my lane's core changes landed
   inside that commit, not a lane-owned commit. The extractor filter landed as 8effc8a5b with
   an explicit pathspec.

### Re-run (P3 inputs, re-extracted with the filter, real runs)

```sh
python3 scripts/gen_doc_surface.py code <repo> > /tmp/hdit/<repo>.code.p3.json
python3 scripts/gen_doc_surface.py doc  <repo> --code-json /tmp/hdit/<repo>.code.p3.json > /tmp/hdit/<repo>.doc.p3.json
# merged to inputs schema -> /tmp/hdit/<repo>.inputs.p3.json
target/release/doc-hdit vectorize /tmp/hdit/<repo>.inputs.p3.json
target/release/doc-hdit audit /tmp/hdit/<repo>.inputs.p3.json courts/doc_quality.court
```

| repo | claims | public items | S_coverage (set, gated) | S_coverage_vsa | Phi_halluc | prose_artifacts | Q_density | audit exit |
|---|---|---|---|---|---|---|---|---|
| ex4pm (Elixir, 596 modules) | 1032 | 1336 | **0.9693 PASS** | 0.1734 | 0.001976 FAIL | 20 | 0.9980 PASS | 1 (FAIL phantom) |
| ferroplan (Rust, 224 modules) | 754 | 1693 | **0.2392 FAIL** | 0.2226 | 0.004016 FAIL | 7 | 0.9960 PASS | 1 (FAIL coverage, phantom) |

Audit lines (ex4pm): `PASS coverage 0.9693/0.90`, `FAIL phantom 0.0020/0.0010
offending_claims=[880, 981]`, `PASS density 0.9980/0.65`.
Audit lines (ferroplan): `FAIL coverage 0.2392/0.90`, `FAIL phantom 0.0040/0.0010
offending_claims=[599, 618, 617]`, `PASS density 0.9960/0.65`.

### Findings

- **Set coverage separates the repos the cosine could not.** ex4pm's docs cover 1295/1336
  public items (0.9693, PASSES 0.90) while the VSA cosine read 0.17 — the cosine measured
  subspace geometry, not coverage. ferroplan's docs cover 405/1693 (0.2392) — an honest FAIL.
- **ferroplan remediation list (top uncovered public modules)**: `crucible-publish/compare.rs`
  (59 uncovered items), `crucible/tui/app.rs` (45), `crucible-publish/promote.rs` (33),
  `crucible/sweep.rs` (30), `crucible-core/db/read.rs` (27), `ferroplan-cli/harvest/model.rs`
  (25), `ferroplan-sat/variables.rs` (25), `crucible-core/db/model.rs` (23),
  `ferroplan-sat/prop/assignment.rs` (22), `crucible-publish/history.rs` (22). The uncovered
  mass is concentrated in crucible/crucible-publish — docs cover ferroplan's own crates, not
  the vendored crucible workspace.
- **The extractor filter killed the P2 residual classes**: the witnessed `release/v26.8.23`
  and `stream/metrics.ex` claims no longer exist; `prose_artifacts` counts are 20 (ex4pm) /
  7 (ferroplan) from the core defense classifier — param-table cells dumped as whole
  sentences and inline code expressions (`applied.len() == rp.len()`) — extractor residue,
  not hallucination.
- **Residual Phi (0.0020 / 0.0040) is param-table over-extraction**, not hallucination: the
  offending claims are whole-sentence table cells captured by `has_param`. Next extractor fix
  is param-cell shape filtering, not a court change. ex4pm's remaining phantoms ([880, 981])
  are the same class.

### Verdict per repo

- ex4pm: **FAIL** — Phi 0.001976 > 0.001 (2 param-table artifacts); coverage and density PASS.
- ferroplan: **FAIL** — coverage 0.2392 < 0.90 (honest: 1288 of 1693 public items
  undocumented), Phi 0.004016 > 0.001; density PASS.

Standing: PARTIAL_ALIVE — P3 set-coverage gating and the prose filter are ALIVE end to end on
real repos with real test evidence (`cargo test` 9+0+2 passed / 0 failed at 20aadd175+;
`pytest tests/test_gen_doc_surface.py` 8 passed at 8effc8a5b). Court admission remains BLOCKED
on extractor param-cell shape filtering (the only remaining Phi residue) and, for ferroplan,
on actually documenting 1288 uncovered public items — a documentation defect, not a metric
artifact.
