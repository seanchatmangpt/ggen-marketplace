# WAVE-RECEIPT — G3, ggen maximization wave v26.9.18 (port-bridge pack)

Standing: **ALIVE** — observed renders + green runs, this session.
Ticket: `docs/jira/v26.9.18/g3-port-bridge-pack.md`

## Repo / base / tree

- Marketplace worktree `~/ggen-marketplace-wt/g3`, branch `pack/port-bridge`
  - base `800b8c6c5` (marketplace main)
  - `d0de05cf8` — cherry-picked the wave's vendored-pack ceiling raise
    (35→50 / 6→7) from
    `fix/hand-authored-qualification-ceiling-35-wave-26918` @ `f2ae5382e`
    (wt-integration vendored clone) so the proof consumer graph (36
    hand_authored_qualification admissions) passes gate 070. Not re-authored;
    the integration branch remains the origin of that fact.
  - `a9373be35` — **the pack increment**: beam4pm-process-model-pack
    v0.1.19 → **v0.1.20** (dated description 2026-09-18): bpm:PortBridge /
    bpm:BridgeOp / bpm:BridgeArg / bpm:BridgeEnv + closed vocabularies
    (BridgeFraming=lines_json; BridgeRestartPolicy=lazy|eager;
    BridgeArgType=string/integer/number/boolean/map/list_map/term;
    BridgeArgEncoding=passthrough/stringify/stringify_list), templates
    `beam4pm_port_bridge.ex.tmpl` + `beam4pm_port_bridge_test.exs.tmpl`,
    `gates/100_port_bridge_admitted.rq`, `qualification/echo_port_bridge.py`
    fixture + echo instance in `qualification/consumer.ttl`.
- Proof worktree `~/beam4pm-worktrees/wt-g3-proof` @ `27ff280` — proof
  deltas are UNCOMMITTED by design: `ggen.toml` pack paths re-pointed at the
  g3 worktree, consumer bpm:PortBridge echo facts appended to `ontology.ttl`,
  `ggen.lock` re-locked (pack hash churn during authoring), one stale rendered
  doc regenerated (`docs/reference/beam4pm_hand_authored_source.md`, stale by
  the ceiling raise itself — the only baseline would-change file).

## What was manufactured

- 524 delivered lines in the proof worktree — `lib/beam4pm_echo_bridge.ex`
  (387) + `test/beam4pm_echo_bridge_test.exs` (137) — 100% ggen-rendered,
  0 hand-written on 産面.
- Pack-side 法面 authorship (the investment surface): ~330 lines TTL
  vocabulary, ~560 + ~230 lines Tera templates, ~150 lines .rq gate, 77-line
  python fixture, ~100 lines Turtle qualification instance.
- Pack-side qualification observed: `qualification/consumer.ttl` renders the
  full family in a scratch project (`/tmp/g3-pack-qualify`), gates pass.

## Coverage vs P8's hand-written original (honest)

Original: `wt-integration/lib/beam4pm_autofde_bridge.ex`, 457 lines.

- **Covered: 375/457 ≈ 82%**, of which:
  - ~293 lines template near-verbatim (moduledoc contract, attrs,
    start_link/request/restart/os_pid, all GenServer callbacks, port
    plumbing: FIFO waiters, per-request timers, timeout poisoning,
    ArgumentError race, close/drain/dispatch, fail_all_waiters,
    stringify helpers — emitted only when encodings need them);
  - 36 lines (ping/cmca_allocate/calculate_salience wrappers) are FACTS,
    not template: rendered generically per bpm:BridgeOp/BridgeArg;
  - 46 lines (python_executable/lab_root/available?/missing_reason)
    rendered from root-resolution facts.
- **NOT covered: 82/457 ≈ 18%** — the one-shot CLI family
  (`oneshot_cmca_allocate`, `oneshot_cli`, `run_oneshot`, lines 124–172 +
  221–252): a different lifecycle (per-call `System.cmd`), owned by the
  CLI-bridge wrapper class (v26.9.18 class 1, G1). Recorded failed edge:
  folding it in would weld two lifecycles into one template.
- **The autofde op table stayed FACTS, not template** — exactly the point.
- Disclosed deltas inside the covered portion: `dispatch_reply` head
  rewritten (`{{:value, …}}` pattern → `{head, rest}` destructure) to avoid
  the Tera `{{` collision, semantics identical; state key `:lab_root` →
  `:root`; `request/3` leading-default API kept byte-for-byte (see
  falsifier 5); eager-restart branch exists in the template (P8 is lazy;
  echo instance is lazy).
- P8's own test file (191 lines): the rendered suite covers every
  op-agnostic law (probe round-trip, unknown-op envelope survival, kill -9
  recovery with os_pid flip, restart/1) and ADDS timeout-poisoning +
  per-op argSample happy paths (P8's test had no timeout test); P8's
  cmca parity / latency benchmarks are one-shot-CLI-family comparisons,
  not generalized.

## Commands + exits (proof session)

- baseline falsifier: `ggen sync run --dry-run` → only the ceiling-stale doc
  would change; all other outputs byte-identical (exit 0)
- `ggen sync run --format plain` → `lib/beam4pm_echo_bridge.ex: written`,
  `test/beam4pm_echo_bridge_test.exs: written` (exit 0; gates 010–100 PASS)
- `mix compile` → app compiled; only pre-existing warning
  (`AshAutofde.CascadeAllocator` in untouched `lib/beam4pm_dfcm.ex`)
- `mix test test/beam4pm_echo_bridge_test.exs` → **8 tests, 0 failures**,
  observed 4x (incl. re-runs after re-render)
- gate falsifiers (see below): sync REFUSED with named rows (nonzero)
- fixture stderr note: during the timeout test the interpreter logs one
  BrokenPipeError — the interpreter-side symptom of the port-drop law the
  test asserts; client assertions unaffected.

## Falsifiers attempted

1. **kill -9 mid-session** (in rendered suite): GenServer survives, next
   request lazily boots a fresh interpreter, os_pid flips — observed green
   (`port exited (status 137); lazy restart` in the log).
2. **timeout poisoning**: sleep sample request vs 100 ms budget →
   `{:error, :request_timeout}`, port dropped, full recovery — observed.
3. **gate: op without reply shape** → sync refused,
   `bridge_op_without_reply_shape` on `echo_op_bad` — observed by name.
4. **gate: consumer-minted framing individual** (`carrier_pigeon`): first
   probe was malformed (bridge did not reference it) — corrected probe plus
   reasoning about the class-membership anti-join exposed that it could not
   refuse a consumer-minted individual; gate 100 strengthened with
   name-membership arms (`framing_name_not_rendered` et al.) and the refusal
   then observed BY NAME. The pre-strengthening weakness is inferred, not
   observed.
5. **rendered-suite falsifier that caught a real API trap**: first
   `mix test` run FAILED (1 failure, FunctionClauseError, args
   `(%{"op" => "sleep", ...}, 100, 5000)` preserved above): the original's
   `request(server \\ …, req, timeout \\ …)` leading default makes the
   2-arity clause bind `(server, req)`. P8 never called it 2-arity, so the
   trap was latent. Permanent guards: rendered test pins the explicit
   3-arity raw call; ontology comment discloses the divergence analysis.
6. **fixture path resolution**: first run 8 skips (moduletag) — relative
   `../` resolved into `/Users/sac/beam4pm-worktrees`; fixed to `../../`,
   observed running (skip → 8 green).

## 比

- Proof worktree delivered lines: 524 rendered / 524 total = 100%
  manufactured; hand-written on 産面 = 0 (consumer Turtle facts are
  manufacturing input; ggen.toml/lock edits are proof wiring).
- Pack v0.1.20 = ~1,209 inserted lines of 法面 (vocabulary + templates +
  gate + fixture), the surface that retires every future member of the
  port-bridge class.

## What the operator did NOT have to write

The client (387 lines), its Chicago qualification (137 lines), the gate
refusal matrix, and the fixture envelope law — all rendered/shipped from
pack facts; the operator's only lawful inputs were ontology facts and the
pack-side authoring now admitted upstream.

## Remaining

- beam4pm's `BeamPM.AutofdeBridge` itself remains admitted hand debt until
  the consumer declares `bpm:PortBridge` autofde facts (root resolution +
  3 ops + 120s solve timeout) and deletes the hand file — consumer-side
  conversion owned by the v26.9.18 integration, sunset plan unchanged
  (`admit the op surface as facts and render`).
- One-shot CLI family (82 lines) → bpm:CliBridge pack (G1).
- No Erlang/Gleam siblings: the original is Elixir-only; none manufactured.
- Un-pushed; branch `pack/port-bridge` local only, per wave law.
