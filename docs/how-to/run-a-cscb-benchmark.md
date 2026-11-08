# Run a CSCB Benchmark

Drive a Challenger Sales Combined Benchmark arc end to end: measure the
status quo against the pack workload, drive the six-stage arc, render a
verdict, and mint a signed receipt. Every invocation below is copied from a
script that ran green on this machine (2026-11-07, Elixir 1.19.5, OTP 28).
Path shorthand: `PACK = packs/challenger-sales-cscb`.

## 0. Compile the dependency set and preload the beams

The courts are standalone: each court script compiles the module subset it
needs into its own scratch ebin — run them WITHOUT preloading the full-set
beams (`-pa /tmp/cscb_ebin`), or the preloaded CscbAttest/CscbHardware shadow
the fixtures and the verdict court refuses fixture stamps
(`{:refused, :unattested_input}`). `CscbArc`/`CscbEconomics` need the
`decimal` beam on the path (witnessed: bare `elixirc` fails with
`Decimal.__struct__/1 is undefined`). Compile the full set for the step-by-step
walkthrough below:

```console
$ mkdir -p /tmp/cscb_ebin
$ cd PACK
$ elixirc lib/cscb_*.ex -o /tmp/cscb_ebin \
    -pa /Users/sac/ash_pplan/_build/dev/lib/decimal/ebin
$ elixir qualification/metric_admission_court.exs
21/21 passed
```

## 1. Measure the side-by-side comparison

`CscbStatusQuo.side_by_side/1` runs both REAL workloads in isolated worker
processes and courts the result:

```elixir
result = CscbStatusQuo.side_by_side(ops: 2_000, payload_bytes: 256, latency_us: 20)
#=> %{harness: :internal_fallback | :cscb_harness,
#     status_quo: %{ops: 2000, wall_us: 42841, reductions_delta: 1879251,
#                   gc_count: 26, gc_reclaimed_bytes: 6852888},
#     pack: %{...},
#     court: :pass | {:fail, {:pack_gc_above_threshold, gc_delta, threshold}}}
```

The numbers above are from this machine's run; yours will differ — that is
the point. `court/1` demands the pack path's GC delta below 1% of the status
quo delta. On this machine the court currently passes (`court: :pass`,
observed 2026-11-07, lane F13 run); treat a failing
court as a real measured finding, never as a number to publish.

## 2. Stamp the run to the machine

```elixir
nonce = CscbAttest.nonce()
run = %{start_time: :erlang.monotonic_time(),
        end_time: :erlang.monotonic_time() + 100,
        durations: [50, 60], nonce: nonce}
run = CscbAttest.stamp_run(run, nonce)
CscbAttest.verify_stamp(run)
#=> :ok   (typed refusals: {:error, :stamp_invalid, :profile_mismatch |
#          :nonce_mismatch | :clock_rollback | :negative_duration |
#          :missing_header})
```

## 3. Drive the six-stage arc

`CscbArc.advance/2` refuses until each stage validates — admission-forcing
as control flow. Payloads shown are the qualification fixture shapes
(`qualification/arc_fixtures.exs`):

```elixir
arc = CscbArc.new()

{:ok, arc} = CscbArc.advance(arc, %{volume: 5_000,
                                    sla_targets: ["p99 <= 100us"]})
# S1 Warmer

{:ok, arc} = CscbArc.advance(arc,
  %{identified_structural_causes: ["ets scan", "unbounded mailbox drain"]})
# S2 Reframe

metric = %{p99_max_micros: 95.0, max_allocation_bytes: 0, measured: true,
           stamp: "attest:v1:sha256:...", impacts: ["EI-1"],
           target_profile: :rust_no_std}
{:ok, arc} = CscbArc.advance(arc, %{metrics: [metric, metric, metric]})
# S3 Rational Drowning — < 3 admitted metrics mapping to loss is refused:
# {:error, {:stage_incomplete, :s3_rational_drowning, [{:metric_admission, :min_count_violated}]}
# target_profile is optional on metric payloads (defaults to :rust_no_std,
# the conservative RFC bounds); unknown targets are refused
# {:refused, {:unknown_target_profile, t}}.

{:ok, arc} = CscbArc.advance(arc,
  %{economic_impact: %{total_usd: 1_240_000, drivers: ["breach credits"]}})
# S4 Emotional Impact — zero/negative total is refused

{:ok, arc} = CscbArc.advance(arc,
  %{invariants: %{zero_alloc: true, bounded_state: true, attested_trace: true},
    evidence: %{zero_alloc: "benchee:alloc:0-bytes-hotpath",
                bounded_state: "state-size:cap-64-slots",
                attested_trace: "attest:v1:sha256:cscb-run-42"}})
# S5 Invariants — each boolean must carry an evidence ref

{:ok, arc} = CscbArc.advance(arc,
  %{pack_iri: "urn:ggen:pack:challenger-sales-cscb", install_verified: true})
# S6 Solution — after this, arc.stage == :complete

true = CscbArc.arc_complete?(arc)
{:ok, inputs} = CscbArc.receipt_inputs(arc)
```

## 4. Render the verdict

```elixir
side = fn r ->
  [p99_max_micros: r.wall_us / 2000.0, max_allocation_bytes: 0,
   sla_breach_cost_usd: 0, measured: true,
   stamp: "attest:v1:sha256:..."]
end

{:verdict, rationale} =
  CscbVerdict.rule(%{status_quo: side.(result.status_quo),
                     pack: side.(result.pack),
                     economics: %{total_breach_cost_usd: 1_240_000}})
rationale.verdict
#=> :status_quo_refused | :adopted | :inconclusive
```

An unmeasured side yields `:inconclusive` with `rationale.missing` naming
each `{side, invariant}` gap; a missing or failing stamp refuses outright
(`{:refused, :unattested_input}`).

## 5. Mint and verify the signed receipt

```elixir
{:ok, receipt} = CscbReceipt.mint(%{metrics: %{p99: 95.0}, verdict: rationale.verdict}, run)
CscbReceipt.verify(receipt)
#=> :ok   ({:error, :crc_mismatch} or {:error, :bad_signature} on tamper)
md = CscbReceipt.render_markdown(receipt)
```

`mint/2` returns `{:ok, receipt}`; `mint!/2` raises on the same refusals
(including `{:error, {:invalid_verdict, value}}` — the verdict slot validates
against the closed set `:status_quo_refused | :adopted | :inconclusive` at
mint, and `render_markdown/1` escapes every interpolated value so a `|` in
measured data cannot break the metric table).

## 6. Render the terminal table

```elixir
CscbTerminal.render(%{status_quo: result.status_quo_map, pack: result.pack_map})
|> IO.write()
```

Cells absent from a result map render `— (not measured)`. Live re-rendering:
`CscbTerminal.run(feed_fun, device: :stdio, poll_ms: 250, batches: 4)` or a
`:pg` topic `{:cscb, :results}`.

## 7. Run the qualification courts

| court | invocation | status this machine (2026-11-07) |
|---|---|---|
| metric admission | `elixir qualification/metric_admission_court.exs` | **PASS 21/21** |
| receipt | `elixir qualification/receipt_court.exs` | **PASS 17/17** |
| arc | `elixir qualification/arc_court.exs` | **PASS 19/19** |
| verdict | `elixir qualification/verdict_court.exs` | **PASS 36/36** |

All four courts are standalone — each compiles the module subset it needs
into its own scratch ebin (e.g. `/tmp/cscb_r12_ebin`), so no preload and no
decimal `-pa` are required. The end-to-end pipeline script also runs green
standalone: `elixir qualification/cscb_full_run.exs` (exit 0, verdict
`MEASURED :inconclusive`).

## Honesty banner

All published CSCB numbers must be MEASURED on target hardware with attest
stamps (`CscbAttest.stamp_run/2` + `verify_stamp/1`). The RFC's example
comparison table is illustrative; do not copy its numbers into receipts,
terminals, or docs. A court that fails is a finding, not a footnote: publish
`{:fail, reason}` or fix the workload — never round a failing court to a
passing claim.

## See Also

* `packs/challenger-sales-cscb/README.md` — concept, module map, phase roadmap
* `qualification/*.exs` — fixture corpora and court scripts
