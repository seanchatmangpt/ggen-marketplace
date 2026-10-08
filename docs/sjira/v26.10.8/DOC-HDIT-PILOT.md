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
