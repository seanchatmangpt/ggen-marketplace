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
   (a gate that can never fail is vacuous).
6. **Falsifier failures branch, they do not stop**: a refused sync names the
   violated constraint; the repair lands in ontology/query/template, and the
   next sync re-admits.
7. **Operationalization** — the recurring operation (regenerate after ontology
   edit) is fixed as a documented procedure in
   [../how-to/generate-from-strata-ontologies.md](../how-to/generate-from-strata-ontologies.md);
   the exact contracts live in
   [../reference/strata-family-contracts.md](../reference/strata-family-contracts.md);
   the consumption walk lives in
   [../tutorials/consume-the-strata-family.md](../tutorials/consume-the-strata-family.md).
   The same reasoning is never re-purchased per pack.

## Why seven packs, not one

Each pack owns one semantic responsibility, matching the pack-classes
doctrine (see [../explanation/level5-diataxis.md](../explanation/level5-diataxis.md)
and [../reference/pack-classes.md](../reference/pack-classes.md)):

- protocol = the wire kernel (CapabilityPack-shaped: one capability, exact
  constants);
- cas / pn64 / signer = orthogonal capability packs over the same vocabulary;
- stratus / temprun = runtime-side state and fuel vocabularies;
- valve = a compatibility/evidence pack: it cross-checks the protocol wire
  classes and projects a different language (Elixir), proving the pipeline is
  language-neutral.

## What is deliberately not here

- No actuation: nothing in the family sends frames; actuation authority is a
  separate, separately admitted boundary.
- No Level-5 crown: all packs are alpha. Diátaxis closure (this page, the
  tutorial, the how-to, the reference) is the documentation dimension only.
