# cscb-x2-target-profiles-2026-11-07 (Lane X2 — spec-level target-profile fix from G11's finding)

Standing: PASS

- Lane: X2. Repo: /Users/sac/ggen-marketplace (no git commands; pack untracked, no commits per lane law).
- Finding fixed: the RFC invariants (p99 <= 100us, alloc == 0) govern the no_std Rust runner target; BEAM comparator subjects lawfully cannot meet them, so every BEAM-side run concluded INCONCLUSIVE by construction. The law works; the target distinction was unspecified.

## Defaults + rationale

- Closed target vocabulary `cscb:rust_no_std | cscb:beam_hot_path` (ontology.ttl `cscb:TargetProfile` class + individuals; `cscb:targetProfile` property, domain owl:unionOf(MetricAssertion, HardwareProfile)).
- `rust_no_std` keeps the RFC law: p99 <= 100.0us, alloc == 0. The 100us/0-alloc proof requires a measured Rust-runner receipt.
- `beam_hot_path` honest comparator defaults: **p99 <= 10_000us** and **alloc_per_op <= 512B**. Rationale: BEAM per-op binary encode + worker-side duration sampling allocate by construction (G11 measured 33.8ms tail / 106,880B per op), so the no_std law is unreachable on BEAM; 10ms is two orders under the measured tail baseline, 512B is ~2 orders under the measured alloc baseline (one small binary + result tuple per op). These bounds admit honest BEAM comparators; they do NOT certify the RFC no_std claim.
- Conservative fallback: missing `:target_profile` defaults to `:rust_no_std` (unspecified subjects stay under the strict RFC law); unknown targets refused (closed vocabulary).
- One-kernel bounds: `CscbMetricAdmission.target_bounds/1` is the only code home for the ceilings; `CscbVerdict` reads them through it.

## Diff (owned files)

- `packs/challenger-sales-cscb/ontology.ttl` — TargetProfile class + individuals, `cscb:targetProfile` property (union domain), per-target rationale comments, hw-001 + ma-001..003 annotated beam_hot_path.
- `packs/challenger-sales-cscb/shapes.ttl` — MetricAssertionShape now target-neutral structural + closed-set targetProfile (sh:in); per-target invariant classes via sh:SPARQLTarget: RustNoStdInvariantsShape (p99 <= 100.0, alloc hasValue 0), BeamHotPathInvariantsShape (p99 <= 10_000.0, alloc <= 512). HardwareProfileShape added. pyshacl (advanced=true) conforms.
- `packs/challenger-sales-cscb/lib/cscb_metric_admission.ex` — admit/1 target-aware; refusals name the target whose invariant fired (`{:refused, {target, invariant}}`, `{:refused, {:unknown_target_profile, t}}`); public `target_bounds/1`.
- `packs/challenger-sales-cscb/lib/cscb_verdict.ex` — per-side target scoring (tail/alloc scored against each side's DECLARED target bounds; invariant rows carry per-side target + bound + margin); typed-comparison gate (a measured side MUST declare its target, else `{:refused, :unattested_input}`); invariant ids generalized to `:tail_p99 | :alloc_per_op | :no_sla_breach_cost`; verdict vocabulary unchanged.
- `packs/challenger-sales-cscb/qualification/metric_admission_fixtures.exs` + `metric_admission_court.exs` — target-aware corpus: legacy rust corpus (conservative default), explicit rust corpus (a rust claim cannot ride beam bounds), beam corpus (at-bounds admits, 1us/1B-over refuses), G11-witness refusal, unknown-target refusal, beam arc-level min-count cases. 21/21, exit 0.
- `packs/challenger-sales-cscb/qualification/verdict_fixtures.exs` + `verdict_court.exs` — sides declare targets; BEAM-meets-beam mixed-target case (status_quo_refused, typed); G11 witness case (33_801.9us / 106_880B vs beam bounds -> INCONCLUSIVE, not loosened); measured-no-target and unknown-target refusals; per-side bounds/margins asserted. 36/36, exit 0.
- `packs/challenger-sales-cscb/README.md` — CscbMetricAdmission row updated + new "Target profiles (lane X2)" section: BEAM runs are honest comparators; the 100us/0-alloc proof requires the Rust runner.
- `receipts/cscb-e2e-run-2026-11-07.md` — X2 addendum appended (not rewritten).
- **Disclosed minimal unblock (SLA), not owned**: `qualification/cscb_full_run.exs` — the verdict input's measured sides lacked `:target_profile`; my typed-comparison gate would have crashed the run. Declared both sides `beam_hot_path` (honest — BEAM-measured demo subjects). Run still concludes MEASURED :inconclusive. Disclose in coordinator ledger; owner lane supersedes at drain if it edits this file.

## Concurrent-lane events (disclosed)

- `lib/cscb_verdict.ex` was overwritten mid-lane with pre-X2 content (incl. the `Float.is_finite/1` clause, which crashes on this Elixir 1.19 build — the function does not exist; BEAM floats cannot represent NaN/Inf). The X2 content was re-applied; the economics finite-guard was re-landed BEAM-safe by the concurrent lane (`total == total` NaN guard + `Float.max_finite()` bound) — kept, lawful.
- ontology.ttl/shapes.ttl: my multiline plain-string `rdfs:comment "..."` literals were Turtle-illegal; a concurrent lane converted them to `"""..."""` before the parse gate. Kept; both files parse clean and SHACL conforms.

## Court matrix (all real exits, this session)

| gate | command | exit | result |
|---|---|---|---|
| pack Chicago verifier | `python3 verify.py` | 0 | gates clean, SHACL conforms (per-target shapes), anti-vacuity flips, label-injection court flips, emitted Rust labels clean |
| admission court | `elixir qualification/metric_admission_court.exs` | 0 | 21/21 passed |
| verdict court | `elixir qualification/verdict_court.exs` | 0 | 36/36 passed |
| full run | `elixir qualification/cscb_full_run.exs` | 0 | `== G11 FULL RUN OK ==`, verdict MEASURED :inconclusive |
| arc court | `elixir qualification/arc_court.exs` | 0 | 19/19 passed |
| receipt court | `elixir qualification/receipt_court.exs` | 0 | 17/17 passed |
| economics court | `elixir qualification/cscb_economics_court.exs` | 0 | 12 pass / 0 fail |
| ar1 court | `elixir qualification/ar1_adversarial_court.exs` | 0 | 8 defended / 0 exploited |
| terminal court | `elixir qualification/cscb_terminal_court.exs` | 0 | 18/18 passed |

Gate logs preserved: /tmp/x2_verify.log, /tmp/x2_adm.log, /tmp/x2_vd.log, /tmp/x2_fr.log, /tmp/x2_arc_court.log, /tmp/x2_receipt_court.log, /tmp/x2_cscb_economics_court.log, /tmp/x2_ar1_adversarial_court.log, /tmp/x2_cscb_terminal_court.log.

## Falsifier status

- Non-vacuity witnesses (in court corpora): beam 10_001us refuses tail; beam 513B refuses alloc; G11 witness refused/INCONCLUSIVE; measured-no-target refused; unknown-target refused.
- NOT yet run: a shim-court mutation proving a court case flips when a beam bound is dropped. Registered as the open falsifier for the next audit lane; not claimed here.

## Standing

PASS on owned surface. One not-owned file touched (cscb_full_run.exs, disclosed SLA unblock). Bounds were NOT loosened to force ADOPTED: the G11 BEAM witness (33.8ms tail / 106,880B per op) still fails even the honest beam bounds and concludes INCONCLUSIVE. The honest conclusion stands: BEAM runs are honest comparators; the 100us/0-alloc proof requires the Rust runner.
