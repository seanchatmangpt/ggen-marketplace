# court-kit-pack

Anti-vacuity court kit for typed-refusal registers. One command, fail-closed:

```bash
ggen sync run && cargo test
```

This passes **only if every registered refusal code was observed firing**
through the consumer's real admission path. The pack's gate fails closed on
any register row without an `ck:observedTrigger` witness receipt, and the
generated twin-court KATs discharge each row against a real trigger through
the real admission path — no mocks, no sleeps, skips carry a typed reason.

## The four capitals

The pack packages four pieces of enforcement capital proven in graphlaw
(`/Users/sac/graphlaw`), pinned as of source version 26.10.22.

### 1. Refusal taxonomy + playbook grading

Transcribed from graphlaw's typed-refusal register and playbook:

- `docs/refusals.md` — the append-only register: every refusal is typed,
  leaves no child state, carries a stable `details.code` discriminator on the
  wire, and has a documented trigger + recovery. Codes append, never renumber.
- `docs/refusal-playbook.md` — grades every captured refusal message on
  WHAT / WHERE / WHAT-TO-DO (PASS / PASS-partial / FAIL) and files Display
  findings (F-1..F-9) for src lanes to improve. The pack packages the
  *grading method*, not graphlaw's specific findings.

### 2. SHACL admission shapes + the shacl_guard pattern

graphlaw admits SQL-in-RDF by SHACL shapes over the AST
(`ontologies/shapes/`, `ontologies/sql-ast.ttl`); refusals render as typed
`[REFUSAL-nn]` markers with shape-section citations (e.g. `section 4
StatementBaseShape`), never generic errors. The `shacl_guard` pattern
(`src/law.rs:909` — bound shape-nesting depth **before** the evaluator, so a
maliciously nested shapes document refuses typed instead of stack-overflowing
`src/shacl_guard.rs` depth court: `tests/shacl_depth_guard_court.rs`) is
packaged as the discipline: validate the validator's input bounds before
running admission itself.

### 3. BLAKE3-chained signed receipt protocol

Witness firings are receipted, not asserted:

- `src/attest.rs` — Ed25519 attestation: `payload_blake3` (BLAKE3 of the
  payload bytes), `key_id`, signature; `TrustedKeys` for verification
  (a priori pins, a new key is added by decision, not discovery).
- `src/receipt_chain.rs` — in-memory OCEL frames with chaining discipline;
  the durable inter-receipt chain is pending in graphlaw; the pack ports the
  discipline, disclosed as hand-written (see Honest limits).
- `receipts/` — durable per-file receipts, per-file blake3 digests
  (`receipts/CHAIN.blake3`), embedded real command output, exit codes,
  counts. A receipt with no embedded output is not a receipt.

### 4. DvP-style two-sided twin courts

The anti-vacuity core, from `tests/dvp_settlement_court.rs` DVP-03: a court
must attack its own pass condition. The DVP-03 shape runs both sides:

- **One-legged trace must be caught** — a trace recording only the asset leg
  must NOT pass the court's own two-sided check (`settlement_conformant`);
  the conformance layer catches it, not the execution layer (the engine has
  no zero-row-mutation refusal; a WHERE matching nothing commits `ok:true`
  — so the *court* owns the two-sided law).
- **Two-sided twin must pass** — the identical check must pass the committed
  DVP-01 settlement. A court that cannot flip is not a court; a skip is a
  loud `SKIP(typed)`, never a faked pass.

## Self-installing anti-vacuity mechanics

Three mechanisms install themselves around whatever register the consumer
renders through the pack.

### Shadow twins per happy-path test

Every positive control gets a shadow twin: the same input shape with the
offending element removed, well-formed per the register's recovery guidance.
The generated module renders both per code:

- positive: `kat_<token>_refusal_live` — the code MUST fire on its documented
  trigger, asserted on the observed refusal token;
- negative: the shadow twin must NOT fire the code, or the trigger input is
  not discriminating and the positive control was vacuous.

Chicago discipline is generated in, not left to convention: real inputs,
assert on the observed refusal token and verbatim engine message, no mocks,
no `std::thread::sleep`, `#[ignore]` requires a typed reason.

### Refusal-live KAT gate (fail-closed totality)

`gates/01_all_codes_live.rq` returns every `ck:RefusalCode` row lacking
`ck:observedTrigger`:

```
registered refusal code without a witnessed firing (no ck:observedTrigger) —
KAT cannot be discharged
violation: ...
```

Any returned row fails the sync gate: an unproven code may not ship in the
rendered enum or the KATs. "Code X registered but never observed" fails CI.
This inverts the usual test economics — coverage debt is visible as a red
gate, not a TODO.

### Mutation twins

Generated courts must be able to flip. Inverting the trigger in the register
graph (or the consumer mutating their refusal arm) must flip the positive
control to failing, and removing the twin assertion must be caught by the
shadow twin going red. A gate that accepts a mutation without flipping is
itself vacuous — the failure mode the pack exists to kill. Run the pack's
courts against a deliberately inverted register as the non-vacuity self-check
before trusting a green run.

## Consumer walkthrough

Step by step, from clone to red-when-it-should-be-red:

1. **Vendor the pack.** Add `court-kit-pack` to your `ggen.toml` `[packs]`
   and run `ggen sync run`. This renders `generated/` from the templates,
   plus the gate into your gate set.

   ```bash
   ggen sync run
   ```

2. **Bring your own register.** Replace the 5 sample `ck:RefusalCode`
   individuals in `ontology.ttl` with your own codes. Required per row:
   `ck:token`, `ck:recovery`, `ck:trigger`, `ck:name`, `ck:sourceVersion`,
   `ck:observedTrigger` (a pointer to the receipt that witnessed the firing).
   Append-only: never renumber, never retract.

3. **Bind the harness seam.** Implement `CourtHarness::probe` over your REAL
   admission path (the compile/admit call that returns refusals) — not a
   stub of the refusal arm. Implement `ShadowTwin::shadow_twin` per code:
   the same input shape minus the offending element, well-formed per the
   row's `ck:recovery` guidance. The generated module compiles only after
   the seam is bound; until then the pack is graph-data-only.

4. **Trigger each code FOR REAL and receipt the firing.** Run the input
   named in each row's `ck:trigger`, capture the verbatim engine message and
   exit class, and record the pointer in that row's `ck:observedTrigger`.
   graphlaw's own probe is the model: `examples/refusal_probe.rs` drives
   every registered code through the real admission path and asserts
   exit-class MATCH per case (12/12 MATCH, exit 0, as of 2026-10-22 —
   re-read the count from the probe at use time, never recalled).

5. **Run the one command.**

   ```bash
   ggen sync run && cargo test
   ```

   Failure modes, all intentional: a row with no `ck:observedTrigger` → the
   gate returns it → sync fails; a twin that fires on well-formed input →
   the shadow-twin court fails → the trigger is not discriminating; a KAT
   that cannot be discharged through the real path → compile or assert
   failure. Green means every registered code was witnessed firing AND
   stayed silent on its twin.

Steps 1-5 are mechanical once the register graph carries real
`ck:observedTrigger` receipts; the pack's contract is the templates and
gate on disk, and this README documents the method they render.

## Honest limits

- **Method, not domain.** The pack ships admission/court machinery; the 5
  sample codes are illustrative data transcribed from graphlaw
  `docs/refusals.md`, pinned `ck:sourceVersion "26.10.22"`. Consumers bring
  their own codes; the register is consumer-extensible, append-only.
- **Hand-written chain port, disclosed.** The `receipt-chain` capability is
  a hand-written port of graphlaw's chain discipline
  (`src/receipt_chain.rs`), NOT generated from graphlaw source. No graphlaw
  source files are copied into this pack.
- **Textual scan, not semantic equivalence.** The shadow-twin court proves
  non-firing at the level of the consumer's harness input; it is a
  textual/structural vacuity scan, not a semantic proof that the twin covers
  the whole non-trigger space.
- **Codes pinned as-of 26.10.22.** The transcribed codes, triggers, and
  `observedTrigger` witness pointers are as of graphlaw v26.10.22. Upstream
  appends do not propagate automatically; re-transcribe on upgrade. Codes
  remain append-only, never renumbered, consumer-extensible.

## Differentiation

The marketplace already packages graphlaw-derived *vocabularies*:
`refusal-vocabulary-pack` (the code list itself),
`chicago-court-pack` (the real-collaborator testing vocabulary),
`receipt-provenance-pack` (receipt field vocabulary). Those packs answer
"what should I call things". **court-kit-pack packages the enforcement
*method*:** how to make a refusal register prove its own coverage — render
the register as data, render a refusal-live KAT per row, render a shadow
twin per happy-path test, gate on the totality of witnessed firings, and
mutation-test the courts themselves. Vocabularies describe; this pack makes
an unproven code a CI failure. It consumes the vocabulary packs' terms (its
`ontology.ttl` is compatible with `refusal-vocabulary-pack` terms) and is
the natural enforcement companion to them.

## See Also

- graphlaw: `docs/refusals.md`, `docs/refusal-playbook.md`,
  `tests/dvp_settlement_court.rs` (DVP-03), `src/attest.rs`,
  `src/receipt_chain.rs`, `src/shacl_guard.rs`,
  `tests/shacl_depth_guard_court.rs`
- `docs/reference/sql-rdf-rec.md` §5 refusal taxonomy (conformance text)
- Marketplace: `refusal-vocabulary-pack`, `chicago-court-pack`,
  `receipt-provenance-pack`
