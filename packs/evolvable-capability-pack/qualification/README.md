# Evolvable capability qualification

This directory contains the anti-vacuity court for the pack's violation-row gates.

## Gate witness matrix

`verify.py` runs every `gates/<stem>.rq` with rdflib over the pack ontology plus
`witnesses/pass/<stem>.ttl` (must return zero rows) and `witnesses/fail/<stem>.ttl`
(must return at least one row). Gates 010-040 are the lifecycle laws; gates 050-080
close adversarial holes found against them:

- 050 digest format: every ecap digest is a `sha256:<64 lowercase hex>` literal. A
  quote-bearing digest previously escaped the JSON projection and injected an
  `"authority": "DO"` key.
- 060 paired evidence well-formed: the pair is typed, names a released champion and
  the promoted candidate (never itself), and carries a cohort digest.
- 070 single lifecycle state: exactly one declared state; `Released` plus `Retired`
  previously satisfied the released-only closure gate.
- 080 single frozen identity: two digests for one subject are refused as ambiguous.

## Fixture matrix

`verify.py` also executes every file in `fixtures/` plus `consumer.ttl` and requires
the refusing gate set to equal `FIXTURE_EXPECTATIONS` exactly:

- positive.ttl and consumer.ttl: no gate refuses.
- neg-promotion-without-pair.ttl: only gate 010 refuses.
- neg-released-without-evidence.ttl: only gate 020 refuses.
- neg-candidate-in-closure.ttl: only gate 030 refuses.

An undeclared fixture or an unparseable input is refused with a typed reason.
`consumer.ttl` is also the ggen qualification consumer graph (`scripts/qualify_packs.py`),
so marketplace qualification renders a real closure, and it types `gp:Core1` so the
pack header's profile reference is qualified for the cross-pack reference lint.

## Benchmark

`bench.py` times all gates over a synthetic N-generation evolution history and
refuses if the largest size exceeds `MAX_SECONDS_PER_GENERATION` or scales
super-linearly. `bench-receipt.json` is the recorded run; `tests/test_evolvable_capability_pack.py`
re-runs the bound, the adversarial mutations, and the real ggen runtime cases.

These fixtures establish test inputs only; they do not claim runtime authority or
production standing.
