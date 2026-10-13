# Explanation: Strata family design

Why the Strata family is shaped the way it is. The family applies a fixed
constitutional order to one protocol stack; each pack is one clause of that
constitution made executable as RDF + gates + templates.

## The constitutional order

The family instantiates a seven-clause order: Preserve → Fence → Calculus →
Exclusions → Falsifiers → Extensions → Operationalization.

1. **Preserve** — the wire truth (the real CLAP/1.0 frame, the real valve
   atoms) is preserved as RDF before anything is manufactured from it. The
   ontology comments cite the ground-truth source files. Generated artifacts
   are consequences, never a second source of truth.
2. **Fence** — authority boundaries are explicit: `gates/*.rq` are the admission
   step; pack manifests declare which gates must pass before any projection.
   The signer pack's gate refuses any key spec that is not the ML-DSA-65 triple
   (3309/1952) — a malformed key is a typed refusal at sync time, not a silent
   projection.
3. **Calculus** — selection is SPARQL (`queries/*.rq`) over the ontology, and
   projection is deterministic templates. The family has no hand-written
   constant tables: the header layout, mask tables, and refusal modules are all
   projections of `ontology.ttl`.
SPARQL select → template project → generated consequence, with gates between
   truth and consequence.
4. **Exclusions** — what the family does NOT do is stated: generated files are
   never hand-edited; the wire refusal receipt is opaque (no cause channel, no
   error entropy on the wire); refusal classes exist only valve-locally for
   policy and telemetry.
5. **Falsifiers** — every claim in the family is falsifiable by execution:
   re-run `ggen sync run` and the output must be byte-identical (idempotence
   falsifies non-determinism); gates refuse when a constraint is violated
   (a gate that can never fail is vacuous — hence the per-law sabotage twins
   described below).
6. **Falsifier failures branch, they do not stop** — a refused sync names the
   violated constraint; the repair lands in ontology/query/template, and the
   next sync re-admits.
6b. **Extensions: reuse→compose→extend before invent** — the family adds packs
   only where no existing pack owns the semantics (protocol kernel first;
   capability packs compose it; nothing re-implements a sibling's vocabulary).
7. **Operationalization** — the recurring operation (regenerate after ontology
   edit) is fixed as a documented procedure in
   [../how-to/generate-from-strata-ontologies.md](../how-to/generate-from-strata-ontologies.md);
   the exact contracts live in
   [../reference/strata-family-contracts.md](../reference/strata-family-contracts.md);
   the consumption walk lives in
   [../tutorials/consume-the-strata-family.md](../tutorials/consume-the-strata-family.md).
   The same reasoning is never re-purchased per pack.

## Why sixteen packs, not one

Each pack owns one semantic responsibility, matching the pack-classes
doctrine (see [../explanation/level5-diataxis.md](../explanation/level5-diataxis.md)
and [../reference/pack-classes.md](../reference/pack-classes.md)):

- protocol = `KernelPack`: it owns the canonical wire vocabulary other packs
  reference by IRI (it projects more than one artifact — PDU constants and wire
  classes — not a single capability);
- hash / cas / pn64 / signer / ledger / chain / store / net / consensus /
  governance / audit / stratus / temprun = `CapabilityPack`s, each one
  orthogonal capability over the same vocabulary — the family now spans the
  full stack from hashing (`hash`) through transactions (`tx`), signing
  (`signer`), ledger state (`ledger`), block assembly (`chain`), persistence
  (`store`), the mempool/transport surface (`net`), agreement (`consensus`),
  policy (`governance`), and cross-pack attack replay (`audit`);
- valve = `CapabilityPack` (the Elixir refusal taxonomy): it cross-checks the
  protocol wire classes and projects a different language (Elixir), proving
  the pipeline is language-neutral.

## Why the defense layers exist

The family's courts are layered so that no single court is trusted on its own
word. Each layer answers a different failure mode:

- **Sabotage twins (13 of 16 packs)** — a court that can never fail is vacuous,
  so each law ships with a twin implementation that deliberately violates it.
  The twins prove the courts CAN fail: if the sabotaged variant ever passes,
  the court is not testing the law. This converts "the court ran" into "the
  court distinguishes lawful from unlawful."
- **Lean witnesses** — the courts prove a generated implementation satisfies
  its law; the Lean witnesses prove the LAW ITSELF is the right law. For
  example, the ledger conservation law carries a Lean counterexample
  (`mfact procint/ProcInt/Petri/LedgerConservation.lean`) showing exactly why
  the naive token-sum (and the duplicate-input shadow-overwrite) mints value
  from nothing — the witnesses pin the attack class, and the generated courts
  replay it per run (e.g. the audit corpus court runs conservation over 1000
  funded transitions per run against 6 targets).
- **Shared KAT heads** — known-answer-test fixtures pinned in one place and
  consumed across packs (e.g. the BLAKE3 KAT vectors and
  `blake3_kat_pinned_frame_digest` in the tx pack, echoed by the chain pack's
  `verify.py`). Cross-repo agreement on the same fixture bytes proves the packs
  are composing one truth, not each re-deriving its own.
- **Compile-fail courts** — some laws are about what must NOT compile
  (private-state invariants). The ledger pack's `courts-compile/tests/`
  (`gate_state_private_field.rs`, `private_root_recompute.rs`) assert that
  violating code fails to build at all, not merely that a runtime check fires.
- **Boundary replay** — every refusal is replayable at the pack boundary: a
  refused input's exact bytes are pinned, and re-running the court must refuse
  it again with the state bit-identical. This is the family's
  "historical success at another SHA is not current evidence" rule made
  executable.
- **The composition law (`MEMPOOL_LEDGER_ADMISSION`, strata-net-pack)** —
  courts per pack prove each pack is lawful alone; the composition law proves
  valve-style composition: the mempool surface admits a transition only through
  the ledger's admission law, so the seam between packs is itself a gated
  consequence of the ontology, not a hand-shaken agreement.

## What is deliberately not here

- No actuation: nothing in the family sends frames; actuation authority is a
  separate, separately admitted boundary.
- No Level-5 crown: two packs declare status alpha (protocol, valve), the
  other fourteen are packaged at 0.1.0 without a maturity status. Diátaxis
  closure (this page, the
  tutorial, the how-to, the reference) is the documentation dimension only.
