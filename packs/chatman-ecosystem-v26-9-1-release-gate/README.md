# Chatman Ecosystem v26.9.1 Release Gate

This pack manufactures the bounded release-gate contract for Chatman Ecosystem v26.9.1.

It preserves the canonical control path:

`graph -> query -> ggen -> admission -> SELECT/CONSTRUCT -> GymAct BRCE DO -> independent observation -> receipt -> OCEL -> replay -> release standing`

## Non-authority boundary

This pack is CONSTRUCT-only. It does not grant execution authority. Generated artifacts, planner output, MCP requests, ontology derivations, hooks, and remote standing claims remain non-authoritative until independently admitted by the runtime consequence boundary.

## Required crown

The release is not ALIVE because this pack exists. The release crown requires exact-subject observed execution proving:

- direct actuation without admitted authority is refused;
- successful consequential DO crosses BRCE;
- postcondition truth is established by independent observation rather than actuator self-report;
- observation/postcondition disagreement is refused;
- receipts bind exact subject, authority, consequence, and verification evidence;
- tampered receipts are rejected;
- deterministic replay reproduces the admitted result;
- OCEL/process evidence corresponds to the verified consequence;
- the next planning episode is seeded from observed state, not a stale plan suffix.

## Inputs

Copy `release-manifest.example.toml` to `release-manifest.toml` and replace every placeholder SHA with an exact immutable subject. `standing-policy.toml` defines the minimum release-standing and refusal court.

## Release rule

Only the immutable post-merge/tag subject may receive ecosystem release standing. Draft PRs, workflow definitions, generated files, and successful inspection are evidence inputs, not execution receipts.
