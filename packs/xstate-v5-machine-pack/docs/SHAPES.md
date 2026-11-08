# Pack Shapes: XState v5 Compile Law Register

Standing: PARTIAL_ALIVE

Register of compile shapes, wiring laws, and defect classes extracted from
machine-rendering and wiring court waves (source:
`srve/docs/diagrams/state/xstate/SHAPES.md`, receipts cited inline by wave id).
Pack consumers must compile against an established shape or register a new row
here before landing. Standing inherited PARTIAL_ALIVE: shapes are court-witnessed
on the source corpus; cross-repo pilot confirmation is pending (see Pending
Pilots).

## Compile Shapes

Each shape: the law, its court witness, and whether Gate Checklist #20 (this
pack's per-machine court) can check it mechanically.

- **flat-guarded-states / no-parallel** — doc serial-tab semantics compile as
  flat state nodes + transition guards; `type: 'parallel'` is banned.
  Witness: first court wave, 4/4 PASS. Gate-checkable: yes (direct grep).
- **sibling-region pattern** — region-like subflows compile as sibling child
  states with explicit entry/exit edges, never parallel regions. Witness:
  wave 34. Gate-checkable: partially (structural scan; parallel grep is the
  hard arm).
- **guarded-branch arrays** — one shared trigger with multiple destinations
  compiles as multiple guard-ordered arms on a single event (first match
  wins). Witness: wave 31/35 (two edges between the same pair compiled as
  two guard-ordered arms). Gate-checkable: no (semantic; needs review).
- **two-actor split + shared event union** — split actor-scoped machines
  share one event union type; no cross-actor bare-string events. Witness:
  wave 39. Gate-checkable: partially (union-presence check covers the arm;
  cross-actor strings need review).
- **invoked channel / comment seam** — realtime/external streams are NOT
  compiled as transitions; use invoked actors or a disclosed comment seam
  for wiring-time hookup. Witness: wave 40. Gate-checkable: no (disclosure
  review).
- **standalone-with-seam embedding** — a machine compiles standalone (own
  event union, no repo deps) with an explicit seam comment naming the
  wiring-time consumer. Witness: wave 35. Gate-checkable: yes (bundle +
  construct check #8 proves standalone-ness).
- **no-op submits -> submittedLocalOnly** — disclosed NOT-WIRED no-op submits
  compile as transitions to an explicit terminal state, never silently
  dropped. Witness: wave 34. Gate-checkable: partially (terminal-presence
  vs doc-row check #3 catches silent drops).
- **token-gated guarded entry** — token/auth presence compiles as an entry
  guard / immediate guarded check, not a polling transition. Witness:
  wave 36. Gate-checkable: no (semantic).
- **redirect-class EXCLUDED** — doc-only redirect edges that are not
  promoted carry `EXCLUDED` comments AND must be absent from the machine
  body. A witnessed violation claimed exclusion in comments while the edges
  existed in the body (wave 33-D2). Gate-checkable: yes (grep body for the
  excluded edge names).
- **URL-projection context law** — URL/route info enters via context, never
  as events or states. Witness: wave 47. Gate-checkable: no (semantic).
- **URL quickview** — deep-link entry-from-URL compiles as a guarded
  initial-entry branch resolving to the linked state. Witness: wave 52.
  Gate-checkable: no.
- **stepper inline regions** — stepper subflows compile as inline (flat,
  guarded) child states of the step composite, not parallel regions.
  Witness: wave 44/45. Gate-checkable: partially (parallel grep).
- **server-derived status divergence** — server status enums that diverge
  from doc vocabulary compile as a context-mapping (server -> machine vocab)
  disclosed in the header, never invented transitions. Witness: wave 49.
  Gate-checkable: no (pairs with the invented-transitions defect class).
- **dual-vocabulary separation** — doc vocabulary and machine event
  vocabulary stay distinct; row comments cite doc row ids, events use
  machine vocabulary. Witness: wave 46. Gate-checkable: no.
- **absent-substrate EXCLUDED/ABSENT** — substrate with no backing API yet
  is marked EXCLUDED/ABSENT in header + comment; no placeholder transitions
  are minted. Witness: wave 50. Gate-checkable: yes (check #3: absent row
  must be explicitly EXCLUDED).
- **leave-confirm dialog** — unsaved-changes confirmation compiles as a
  guarded transition to a confirm dialog state with explicit continue/cancel
  arms. Witness: wave 44. Gate-checkable: no.
- **WIP placeholder terminal** — unfinished flows end in a named WIP
  placeholder terminal state, disclosed in header; never an implicit dead
  end. Witness: wave 40/52. Gate-checkable: partially.
- **AST-expansion itemization** — doc summary rows expand into multiple AST
  transitions; each expansion carries the full ledger (row id per AST
  entry), so the header count reconciles against expanded entries, not the
  doc row count. Witness: wave 43. Gate-checkable: yes (check #2).
- **consume-once deep-link + rollback restore** — a deep-link entry consumes
  its URL payload once (guarded entry clears the param); editor state
  survives rollback via a context restore on cancel arms. Witness: wave 51.
  Gate-checkable: no.
- **server-set expiry as wiring comment** — server-set expiry/TTL timing is
  not a machine transition; disclosed as a wiring comment seam for the
  consumer, never compiled as a timed event. Witness: wave 48.
  Gate-checkable: no.
- **orthogonal-coextension** — when a composite's substates are genuinely
  concurrently live per the source doc + rendered screen, `type: 'parallel'`
  IS lawful — the flat law yields. Ruling recorded in the source receipt
  wave 88; flattened artifacts leave an ill-formed composite (missing
  `initial`). Compile lanes must not flatten genuine coextension.
  Gate-checkable: partially (the `initial` arm of check #8 catches the
  ill-formed result).

## Wiring Laws

Discovered by the wiring waves; each cites its witness. Wiring lanes must
satisfy these or register a new law before landing.

- **inline-in-setup** (w57) — externally-defined `assign()` consts fail
  xstate v5 `ActionFunction` variance; define assign actions inline in the
  machine setup, never hoisted to module-level consts.
- **absolute-target** (w74, w75, w78, w83) — bare relative targets resolve
  against the PARENT node; any cross-level target needs the
  `#machineId.state.path` form. Four lanes hit the same resolution surprise
  before registration.
- **missing-initial** (w74; w88 flattened-parallel variant) — a composite
  (nested node or flattened parallel region) without explicit `initial`
  throws at `createMachine` time. Every composite declares `initial`.
- **entry-invoke + payload-stash** (w71) — invokes fire on state ENTRY, not
  on the transition naming the target. Stash the invoke payload on the
  transition INTO the invoking state; clear it in `onDone`, never on entry
  (entry-clear wipes the payload before the invoke reads it — witnessed).
- **invoke-on-entry artifact** (w69) — because invokes are entry-bound, a
  nav-only path into the target still commits the mutation. When navigation
  and committing share a target, guard the mutation with a dedicated
  committing state and route nav to the plain state.
- **same-endpoint direct-call seam** (w71, w93) — framework-bound request
  hooks may be replaced by direct HTTP-client calls hitting byte-identical
  endpoints; lawful when disclosed per lane.
- **smoke-real-calls** — smoke suites fire real HTTP calls; jsdom
  `AggregateError` noise from refused sockets is expected and the run stays
  exit-0. Never mock the API layer to silence the noise — real-call firing
  is the point of the smoke court.
- **no-as-const-shared-configs** (w85b falsifier) — `as const`-asserted
  shared guard/action configs built OUTSIDE `createMachine` carry phantom
  brand props (`_out_TEvent`/`_out_TActor` resolved to base types) that are
  invariant-incompatible with the machine's narrowed union — the assertions
  CAUSE the TS2322 variance failures, not cure them. Lawful form: named
  actions declared in `setup({ actions })` referenced by string, plus plain
  inline action functions (bare functions lack assign's phantom brands).
- **static-invoke-src** (w77 falsifier; w70 corroboration) — xstate 5.33
  rejects function-form `invoke.src` at RUNTIME (`getInitialSnapshot is not
  a function`) even when it typechecks; use static string `src` registered
  in `setup()` with actor-internal stash guards. Bare async-fn fixtures
  throw the identical error — fixtures must be `fromPromise` too. The
  dynamic-src pattern from w57 is NOT portable to this version.
- **no-explicit-guard-annotations** (w84b fix) — do NOT annotate setup
  guard/action params as `{ context: XContext; event: XEvent }`: the
  explicit widening makes XState infer
  `ActionFunction<MachineContext, EventObject, ...>` and the whole actions
  map fails TS2322 against the machine's event union. Let `setup()` types
  infer (strip annotations, keep logic/casts). PARTIALLY OVERTURNS the
  annotation-based repair of w59/w59b.
- **tsc-parse-abort false pass** (w82b) — a syntax-broken SIBLING file can
  make tsc abort parsing and mask YOUR errors: a scoped grep can return zero
  on an un-aborted-file basis. Only a full un-aborted tsc run is a
  trustworthy gate.

## Defect Classes

- **count-ledger dishonesty** (w33-D2, w38-M1) — header `transitions: N`
  must equal the AST `target:`-prop count exactly; the ledger basis is the
  machine-compiled count, never a doc-edge count (one subject counted
  initial-entry markers the machine compiled as `initial:` props, not
  transitions).
- **comment-only-counted rows** (w38-C1) — a doc row present only as a
  comment in the machine (no transition) is missing and must not be counted
  in the header claim.
- **events off-union** (w33-D3, w38-C2) — every event used in a transition
  must be a member of the machine's own event union; a machine with no union
  makes the check vacuous-n/a, not passed.
- **stray `*/` inside comments** (w45F) — `*/` in header comment prose
  closes the block comment early; every line after parses as code. Reword
  prose; re-gate on the disk buffer, never a pre-damage buffer.
- **reserved tokens** (w6F note) — reserved TS/xstate tokens in identifiers
  or comments break parse; scan identifiers against reserved vocabulary.
- **invented server transitions** (wV04b) — do not mint transitions for
  server-side behavior the machine does not own; server-derived status maps
  via context per the server-derived-status shape above.
- **unparenthesized arrow-body object literal** (w51F) — an arrow returning
  an object literal without parens (`() => ({...})` written as
  `() => {...}`) parses as a block, silently yielding no transition targets;
  parenthesize and re-gate on disk.
- **malformed `type:` arm instead of `target:`** (w89-D9) — a transition arm
  written with `type:` where a `target:` was required compiles as an
  eventless/no-target transition, silently dropping the destination; audit
  every arm for a `target:` prop before gating.
- **vacuous-court-script** (w106) — a court check that cannot fail is worse
  than no check: one court's parallel detection never pushed to its stats
  field, reporting `[]` on every subject, so the "no parallel" gate
  fake-passed unconditionally. Zero-information checks carry no bits; a
  court that cannot flip is FAIL. Direct grep on the file replaces the
  script field (checklist #5).
- **missing-initial / relative-target at construction** (w149) — a
  count-only court passed 19/19 while 5 machines threw at real
  `createActor().start()`: composites lacking explicit `initial`, and
  sibling-scope targets written bare instead of `#machineId.state.path`
  form. Both throw only at real construction — invisible to count-based
  courts.

## Gate Checklist (per-machine court)

1. Parse diagnostics = 0 (typescript `createSourceFile` +
   `parseDiagnostics`, run on the DISK buffer).
2. AST `target:`-prop count == header `transitions:` == ledger total
   (exact; per-composite sub-claims also reconcile).
3. Every source doc row present as a transition or explicitly EXCLUDED
   (absent = defect).
4. Union membership: every transition event is in the machine's event
   union; a machine with no union is vacuous-n/a, not a pass.
5. No `type: 'parallel'` anywhere — via direct grep per file, NOT via any
   court-script stats field (vacuous-court-script class).
6. Stray `*/` scan over all comment blocks.
7. Reserved-token scan over identifiers.
8. Construction-proof: every artifact must construct for real — bundle +
   `createActor(machine).start()` against the real `xstate` dependency.
   Count-only courts are insufficient (w149: 19/19 count pass, 5
   construction throws).

## Pending Pilots

All source-corpus pilots landed; the pack-level cross-repo pilots are
pending. Standing stays PARTIAL_ALIVE until at least one non-source-repo
consumer machine passes this checklist end to end.

- Pack pilot slot 1: one machine per new consumer repo, full checklist.
- Pack pilot slot 2: a two-actor split consumer (shapes 4 + 6 combined).
- Pack pilot slot 3: a coextension consumer exercising the parallel
  exception + its `initial` repair arm.
