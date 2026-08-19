# Security

Treat packs as executable or execution-adjacent manufacturing inputs. RDF, templates, rules, queries, gates, qualification fixtures, and project configuration can influence files, decisions, or intents produced by ggen consumers. Review pack source with the same care as build tooling.

Report vulnerabilities privately through GitHub's security-reporting surface when available rather than publishing exploit details in a public issue.

## Fail-closed marketplace admission

Marketplace acceptance refuses unsafe or malformed source conditions such as symlinks below `packs/`, malformed/duplicate identities, missing RDF authority, unsupported visible source forms, invalid SemVer identity, unsafe qualification paths, and incomplete required repository documentation.

Semantic packs are not made safer by inventing empty templates. Validation should reflect the capability actually claimed.

## Configuration and supply-chain identity

`marketplace.toml` centralizes the admitted manufacturer/toolchain/distribution identity needed for qualification. Raw values must be admitted before execution. Runtime versions, release commits, asset names/digests, timeout bounds, and worker counts should not be duplicated into scripts or prose where they can drift.

Published pack archives are digest-verifiable distribution artifacts. A valid digest proves identity/integrity for the archive, not correctness or runtime safety of its consequences.

## Read-only CI

Pull-request CI has read-only source authority and must never push generated corrections to the subject under test. Generated documentation/control surfaces may be manufactured in the CI workspace for verification/build, but canonical source is repaired through a purpose branch/PR, not by the court rewriting its own input.

## Pack and verifier boundary

A passing repository validator is structural/source evidence, not a sandbox guarantee and not proof that an arbitrary pack-owned verifier is safe to execute. Consumers remain responsible for inspecting selected pack source, using the admitted ggen/runtime identity, validating manufactured outputs, and running the native consumer boundary appropriate to the claim.

Qualification fixtures are synthetic admitted inputs. They must not be represented as external observations, credentials, customer acceptance, benchmark evidence, or production authority.

## SELECT / CONSTRUCT / DO

The critical authority fence is:

```text
SELECT → CONSTRUCT → DO
```

Marketplace/ggen source can select or construct powerful artifacts and intents without receiving ambient authority to actuate them. Generated Terraform, GitHub Actions, MCP/API payloads, deployment specs, security policies, or operational instructions remain construction artifacts until a separately admitted consumer/runtime authority path executes them.

Where BRCE is used by a consumer, consequential DO remains behind that separately admitted, receipted path. Marketplace admission cannot manufacture credentials or risk acceptance.

## Level-5 security requirement

The authority-fence dimension of [Level 5](docs/reference/level5-maturity-contract.md) requires explicit documentation and executable evidence for the claimed boundary. A Level-5 how-to that could reach consequential DO must name prerequisites, authority ceiling, refusal conditions, receipt, falsifiers, and rollback.

If required authority is unavailable, record `BLOCKED:<reason>`. Do not use mocks or generated intents to promote an unexecuted external boundary to ALIVE.

## Consolidation security

Pack-family consolidation must not widen authority by union. Factoring shared semantics into a kernel or umbrella is lawful only when generated target ownership, admission law, runtime boundaries, compatibility obligations, and authority ceilings remain explicit.

A consolidation that makes a new irreversible transition possible without a newly admitted authority contract is a security regression and should be refused.
