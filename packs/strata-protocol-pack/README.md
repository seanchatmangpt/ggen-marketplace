# strata-protocol-pack

Class: KernelPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

CLAP/1.0 PDU frame constants, receipt and refusal wire classes for the Strata sovereign execution runtime, projected from RDF to a Rust constant module.

## Capability surface

```bash
$ ggen pack capabilities strata-protocol-pack
```

## Verification

```bash
python3 verify.py                 # 3 gates zero-rows + pinned valve-copy sha256 court
rustc --test -O generated/pdu_constants.rs -o /tmp/pdu_t && /tmp/pdu_t
rustc --test -O generated/wire_constants.rs -o /tmp/wire_t && /tmp/wire_t
```

S2 hardening (L77, 2026-10-13): 3 gates (header abutment chain with
fail-closed constant-presence enumeration, refusal receipt length triangle,
refusal taxonomy closure) + 7 Rust courts (frame-constant abutment tiling of
[0,64), sabotage twins for gap/overlap/mutation, exhaustive 2-class wire
enum, refusal-taxonomy 4-atom closure cross-checked against the sha256-pinned
strata-valve-pack refusals.ex copy in `pinned/`). Regeneration is
byte-identical across repeated `ggen sync run`; a mutated constant refuses at
the actuator (FM-LAW-018) and, with the gate bypassed, trips the abutment test.

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. Generated wire constants are semantic projections, not a validated protocol implementation on any runtime.
