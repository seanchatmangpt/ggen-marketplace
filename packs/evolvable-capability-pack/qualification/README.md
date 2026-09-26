# Evolvable capability qualification

This directory contains anti-vacuity fixtures for the pack's violation-row gates.

Expected observations:

- positive.ttl: all four gates return zero rows.
- neg-promotion-without-pair.ttl: gate 010 returns the promotion.
- neg-released-without-evidence.ttl: gate 020 returns the released capability.
- neg-candidate-in-closure.ttl: gate 030 returns the closure/member pair.

Gate 040 is also exercised by removing either the closure digest or a member
implementation digest from the positive fixture. These fixtures establish test
inputs only; they do not claim runtime authority or production standing.
