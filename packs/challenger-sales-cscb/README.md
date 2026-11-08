# challenger-sales-cscb

RDF/SHACL-governed Challenger Sales capability (RFC-2026-0042). The pack turns
the Challenger Sale into an **admission-forcing DAG**: a benchmark arc whose
six stages must validate in order, so reaching The Solution (S6) is gated on
passing Rational Drowning (S3: >= 3 measured metric assertions that map to
loss) and Emotional Impact (S4: positive computed economic total).

## The measured-not-declared law

Every number a stage admits is a number the arc forced a producer to measure.
An assertion without `measured: true` and an attestation stamp is refused
(`{:refused, :unmeasured_claim}`); an unmeasured pack side can never refuse
the legacy stack (the verdict degrades to `:inconclusive`, never
`status_quo_refused` on pack-side gaps — the anti-self-serving law). All
published CSCB numbers must be MEASURED on target hardware with attest
stamps. The RFC's example comparison table is **illustrative only**; nothing
in this pack copies it.

## Honesty banner

* Attestation stamps bind a run to the machine **as the BEAM observes it**
  (`CscbHardware.profile/0` via `:erlang.system_info/1`). This is not a TPM,
  not enclave anchoring, and not tamper-resistant; a privileged process can
  lie to the BEAM's sources. Enclave anchoring is Phase 2/3.
* The status-quo-vs-pack comparison runs two REAL workloads; neither side's
  numbers are asserted. The BEAM pack subject's claim is
  **zero-GC-at-ops-scale** (per G15): `:erlang.trace/3` GC events over the
  measured op window show no collections at ops scale, courted as "GC delta
  below 1% of the status-quo delta" (BEAM has background GC; "zero
  allocation" is a Rust-runner-target claim, never a BEAM one).
* Where a stage's evidence is not yet measured, this README says pending —
  it never rounds UNVERIFIED up.

## Module map (all `lib/` modules on disk — 11/11)

| module | one line |
|---|---|
| `CscbArc` | Six-stage fixed-order FSM (`new/0`, `advance/2`,
  `arc_complete?/1`, `receipt_inputs/1`); refuses until each stage's
  payload validates. |
| `CscbMetricAdmission` | `admit/1` per-assertion admission — target-aware
  as of lane X2: each assertion scores against its declared `:target_profile`
  (`:rust_no_std`: p99 <= 100us, alloc == 0 — the RFC law; `:beam_hot_path`:
  p99 <= 10_000us, alloc <= 512B — honest BEAM comparator bounds). Missing
  target defaults to `:rust_no_std` (conservative); unknown targets refused.
  Refusals name the target whose invariant fired
  (`{:refused, {:beam_hot_path, :tail_latency_inflation}}`). Plus
  `admit_arc/1` min-count (>= 3 admitted metrics mapping to impacts). |
| `CscbHardware` | `profile/0` + `profile_digest/1`: BEAM-visible
  machine profile, SHA-256 over the canonical term. |
| `CscbAttest` | `nonce/0`, `stamp_run/2`, `verify_stamp/1`:
  run-to-machine stamps; typed refusals (profile/nonce mismatch,
  clock rollback, negative duration, missing header). |
| `CscbHarness` | `run_bench/2`: warm-up + dedicated worker
  process, GC/reduction deltas via process snapshots. |
| `CscbStatusQuo` | `subject/1`, `pack_subject/1`, `side_by_side/1`,
  `court/1`, `measure/1`: two real workloads, busy-wait spin latency
  (never `Process.sleep`), GC-ratio court. |
| `CscbTerminal` | RFC §4.1 artifact 2 split-screen table
  (`render/2`, `run/2`); every cell from passed result maps; absent
  metrics render `— (not measured)`. |
| `CscbVerdict` | `rule/1`: closed verdicts (`:status_quo_refused`,
  `:adopted`, `:inconclusive`) over invariant rows; refuses
  `{:refused, :unattested_input}` before verdict logic. |
| `CscbReceipt` | `mint/2`, `verify/1`, `render_markdown/1`:
  CRC32 + ECDSA P-256 signature, embedded public key; typed failures
  `{:error, :crc_mismatch}` / `{:error, :bad_signature}`. AR7/X3 closed:
  `render_markdown/1` escapes every interpolated value (`esc_md`) so a
  `|` in measured data cannot break the metric table, and the verdict slot
  validates against the closed set (`:status_quo_refused`, `:adopted`,
  `:inconclusive`) at mint — `:pass` or any out-of-vocabulary atom is
  refused `{:error, {:invalid_verdict, value}}`. |
| `CscbEconomics` | `loss/2` (metrics × pricing → annualized
  `EconomicImpact`): strict `Decimal` arithmetic, per-line provenance
  (formula + inputs); typed refusals `:negative_metric`,
  `:nil_metric`, `:invalid_pricing`. Delegated S4 math for `CscbArc`. |
| `CscbDemoSubjects` | RFC §5 Ingress-and-Settlement workload MFAs
  (status-quo alloc-heavy vs pack low-alloc style); measured numbers
  only, RFC table never copied. |

## Ontology and gates

`ontology.ttl` defines `cscb:BenchmarkArc`, `cscb:ArcStage`,
`cscb:RationalDrowningStage`, `cscb:MetricAssertion`, `cscb:EconomicImpact`,
`cscb:HardwareProfile`, `cscb:CSCBRun` with SHACL-parity rules mirrored in
`CscbMetricAdmission` (min-count >= 3, mapsToLoss). `ggen.toml` registers
SPARQL gates (`010_arc_integrity`, `020_rational_drowning`,
`030_anti_vacuity_mapsToLoss`, `040_label_safety`, `050_orphan_stage`) — all
five land under `gates/`. `queries/` holds `runner_profile.rq` (the Rust
emission query, arc-scoped, with the depth-2 Rust escaping) and
`arc_runs.rq`. The emission-security law (gates 040/050, charset
`^[A-Za-z0-9 _-]{1,64}$`, RCE closure) is in
[Security: emission hardening](#security-emission-hardening-ar6-p0p1-closure-2026-11-07)
below, with the full attack-replay matrix in
`receipts/cscb-emission-hardening-2026-11-07.md` (R15, Standing: PASS).

## Phase roadmap

| phase | scope | status |
|---|---|---|
| Phase 1 | Vocabulary: `ontology.ttl` (BenchmarkArc, six stages,
  MetricAssertion, EconomicImpact, HardwareProfile, closed verdicts) | **LANDED** |
| Phase 2 | BEAM harness: all eleven `lib/cscb_*.ex` modules landed,
  qualification courts green | **LANDED** (BEAM side) |
| Phase 2 | Rust runner: `templates/rust/` (Cargo.toml, cycle_counter,
  main, BINDING_CONTRACT.md) — emission templates only; no compiled
  runner on disk | **PENDING** |
| Phase 3 | SBB bundling | **PENDING** — nothing on disk |
| Phase 3 | Receipt signing | **LANDED** — `CscbReceipt.mint/2` +
  `verify/1` (ECDSA P-256, embedded key); PDF rendering deferred |

## Qualification

```
mkdir -p /tmp/cscb_ebin
elixirc lib/cscb_hardware.ex lib/cscb_attest.ex lib/cscb_metric_admission.ex -o /tmp/cscb_ebin
elixir -pa /tmp/cscb_ebin qualification/metric_admission_court.exs
# => 11/11 passed, exit 0
```

The court scripts compile their subject module in isolation; compile the
dependency set (`cscb_hardware`, `cscb_attest`) first and preload the beams
with `-pa`, or the court exits on a module-undefined diagnostic. End-to-end
pipeline receipt: `docs/how-to/run-a-cscb-benchmark.md`.

## Known open items (observed 2026-11-07, refreshed by lane F13 same day)

* `CscbStatusQuo.side_by_side/1` discloses `harness: :internal_fallback` on
  this machine; the GC-ratio court measured `:pass` on the lane F13 run
  (2026-11-07) — the earlier
  `{:fail, {:pack_gc_above_threshold, ...}}` witness did not reproduce.
  The 1% GC-ratio court remains the law; a failing court is a real measured
  finding, never a number to publish.
* `CscbTerminal` references `CscbVerdict.render/1` (not defined) and
  `CscbReceipt` references `CscbAttest.profile_digest/0` (not defined —
  the digest lives on `CscbHardware`); both degrade via optional-dep guards
  with compile warnings, no crash.

## Target profiles (lane X2, 2026-11-07)

The RFC invariants (p99 <= 100us, alloc == 0) govern the **no_std Rust runner
target** (`cscb:rust_no_std`). BEAM comparator subjects are scored against
their own honest bounds (`cscb:beam_hot_path`: p99 <= 10_000us,
alloc_per_op <= 512B — BEAM per-op binary encode + worker-side sampling
allocate by construction; the G11 measured baseline was 33.8ms tail /
106,880B per op). Closed vocabulary: `rust_no_std | beam_hot_path`.

- `CscbMetricAdmission.admit/1` and `CscbVerdict.rule/1` score each side
  against its DECLARED target; refusals name the target whose invariant
  fired. A measured side MUST declare its target (typed-comparison gate).
- Bounds live in one kernel: `CscbMetricAdmission.target_bounds/1` (mirrors
  the shapes.ttl ceilings 100.0/10_000.0us, 0/512B).
- **BEAM runs are honest comparators.** The 100us/0-alloc proof requires a
  measured receipt from the Rust runner; a BEAM number under the comparator
  ceiling is never adopted as that proof, and bounds are not loosened to
  force ADOPTED (the G11 BEAM witness — 33.8ms tail / 106,880B — still
  concludes INCONCLUSIVE against even the beam bounds).
- **BEAM verdicts are INCONCLUSIVE by design**: the RFC's 100µs tail
  invariant governs the `rust_no_std` target, so a BEAM comparator subject
  lawfully cannot satisfy it and the verdict degrades to `:inconclusive`
  rather than ADOPTED. This is the target distinction working, not a
  benchmark failure.

## Security: emission hardening (AR6 P0/P1 closure, 2026-11-07)

Stage labels flow from the ontology into emitted Rust string literals
(`emitted_rust/src/main.rs`). An unfiltered label is a code-injection channel:
a `"` or `\` in a label breaks out of the Rust literal and compiles attacker
bytes. Three independent layers, one charset law
(`^[A-Za-z0-9 _-]{1,64}$`):

1. **Gate 040 (sync-refusing)** — `gates/040_label_safety.rq` runs pre-write
   in `ggen sync` (`[validation].gates`, FM-LAW-018): any ArcStage
   `rdfs:label` outside the lawful charset refuses the sync, exit != 0, with
   emitted files untouched.
2. **Gate 050 (sync-refusing)** — `gates/050_orphan_stage.rq`: any typed
   ArcStage never bound to a BenchmarkArc (rogue stage) refuses the sync.
   `queries/runner_profile.rq` is additionally scoped to arc membership, so
   unbound stages can never enter emission.
3. **Query-layer Rust escaping (depth-2)** — `runner_profile.rq` emits
   `stage_name_rust` (backslash, double-quote, and control characters
   SPARQL-escaped), and `main.rs.tmpl` interpolates only the escaped form.
   Witnessed: with gates 040/050 bypassed, an injected RCE label emits as an
   inert string literal and the emitted crate still compiles
   (`cargo check` exit 0). The SHACL label shape (shapes.ttl `rdfs:label`
   pattern + maxLength 64) documents the same law for the pyshacl path in
   verify.py; ggen sync consumes SPARQL gates only, so the gate form is the
   enforcement layer.

Full attack-replay matrix and command receipts:
`receipts/cscb-emission-hardening-2026-11-07.md` (Standing: PASS — hostile
label, rogue stage, and 10MB label each refuse exit 1 with emitted sha256
unchanged; depth-2 witness emits inert).
