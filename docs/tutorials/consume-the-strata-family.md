# Tutorial: Consume the Strata family

This tutorial walks the smallest end-to-end consumption of the Strata pack
family: observe the wire contract, compose a consumer, generate the projections,
and verify the result. It stops before actuation — the generated artifacts are
frame constants and refusal skeletons, not a running network.

All seven Strata packs are status **alpha**: the contracts are grounded in real
source (`~/strata`), but the surface may still move. Do not build production
dependencies on them yet.

## The family in one paragraph

The Strata family models a fail-closed protocol stack as RDF and projects the
mechanical parts from it:

- `strata-protocol-pack` — the wire kernel: CLAP/1.0 64-byte PDU header
  constants, wire classes (receipt digest, refusal receipt).
- `strata-cas-pack` — content-addressed storage vocabulary (Merkle commits,
  knowledge wormholes, snapshots).
- `strata-pn64-pack` — PN64 Petri-net masks: one transition per u64 word.
- `strata-signer-pack` — ML-DSA-65 (FIPS 204) detached-signature constants.
- `strata-stratus-pack` — witness valves gating state registers.
- `strata-temprun-pack` — fuel-leased actuation arena vocabulary.
- `strata-valve-pack` — the Elixir refusal taxonomy (constant-time, fail-closed).

Exact contracts live in
[../reference/strata-family-contracts.md](../reference/strata-family-contracts.md).

## Step 1: Observe

Read the wire truth before generating anything. The protocol pack's ontology is
the canonical statement of the frame:

```text
packs/strata-protocol-pack/ontology.ttl
```

Note three facts you will carry through the whole tutorial:

1. The header is a fixed 64 bytes, big-endian, magic `0x434C_4150` ("CLAP").
2. The parent receipt digest is 32 bytes at offset 24.
3. A refusal on the wire is an opaque fixed 32-byte `RefusalReceipt` — no
   structure, no cause channel.

## Step 2: Compose a consumer

Create a `ggen.toml` in your consumer project that consumes the protocol and
valve packs. The minimal consumer surface is two projections: the PDU constants
(Rust) and the refusal skeletons (Elixir). Keep the consumer a projection
target, never a second source of truth — if you find yourself editing a
generated file, the edit belongs in the pack's ontology or template.

## Step 3: Generate

From inside each pack directory, run:

```bash
cd packs/strata-protocol-pack && ggen sync run
cd packs/strata-valve-pack && ggen sync run
```

`ggen sync run` executes the pack's declared pipeline: load `ontology.ttl`,
run the SPARQL gates in `gates/` (a failing gate is a typed refusal, not a
warning), then project `queries/*.rq` results through `templates/*.tera` into
`generated/`.

## Step 4: Verify

Verification is mechanical, not visual:

- Every gate query must pass (refuse-and-repair, never bypass).
- The generated constants must agree with the ontology values — re-run sync
  and confirm the projection is byte-identical (idempotent).
- Cross-check the wire facts: header length 64, magic offset 0 length 4,
  refusal receipt length 32.

## Where this stops

This tutorial deliberately does not actuate. Sending real frames through a
running valve is a consequential actuation boundary and is out of scope here;
see [../how-to/generate-from-strata-ontologies.md](../how-to/generate-from-strata-ontologies.md)
for the regeneration workflow and
[../explanation/strata-family-design.md](../explanation/strata-family-design.md)
for why the family is shaped the way it is.
