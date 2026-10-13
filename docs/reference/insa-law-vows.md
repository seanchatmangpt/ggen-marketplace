# Reference: insa-law-pack eight-vow typestate

Contract reference for [`packs/insa-law-pack/`](../../packs/insa-law-pack/):
the canonical RDF projection of insa-replaw's eight-vow sealed typestate law
(`eight_vow.rs` L172-321): `Source -> Pattern -> Field -> Motion -> Receiver
-> Fruit -> Receipt -> Rest`.

Class: **CapabilityPack**. Authority: SELECT/CONSTRUCT, no DO — generated
`vow_order.rs` is a classification projection; its existence is not runtime
correctness of insa-replaw, and no cross-repo boundary is exercised here.

## Typestate surface

The law is RDF in
[`packs/insa-law-pack/ontology.ttl`](../../packs/insa-law-pack/ontology.ttl)
(`urn:insa-law:` identity), projected by
[`queries/vow_order.rq`](../../packs/insa-law-pack/queries/vow_order.rq)
into `generated/vow_order.rs`. One individual per vow, ordered
Source..Rest; the typestate transition law itself lives in insa-replaw
and is mirrored here as declarative classification, not re-implemented.

## Fail-closed gates

Three SPARQL gates refuse manufacture on any returned row:

- [`gates/010_exactly_8_transitions.rq`](../../packs/insa-law-pack/gates/010_exactly_8_transitions.rq)
  — the chain has exactly 8 transitions, no more, no fewer.
- [`gates/020_linear_chain_closure.rq`](../../packs/insa-law-pack/gates/020_linear_chain_closure.rq)
  — linear chain closure Source..Rest with no gaps, duplicates, or skips.
- [`gates/030_refusal_exercise.rq`](../../packs/insa-law-pack/gates/030_refusal_exercise.rq)
  — every typed `BridgeError` variant is exercised by at least one transition.

## Capability command

```bash
cd packs/insa-law-pack && ggen sync run && python3 verify.py
```

## Standing

`PARTIAL_ALIVE`: the projection and its gates are witnessed on the pack's
own surface (`verify.py`); no consumer runtime boundary beyond that court is
exercised by this pack.
