# Why QRI is a thin waist over public vocabularies

No single public ontology covers the qualification of interchangeable runtime realizations, so
the pack reuses each one inside the boundary it already models and adds only what none expresses.

## What public vocabularies own

SOSA/SSN owns procedure, system, execution and platform. PROV-O owns activity, entity and
derivation. ODRL owns permission and prohibition. SPDX owns artifact identity. QUDT owns
quantities. SHACL owns admission. WIT owns the binary boundary of a generated projection.

## What QRI adds

Qualification, admission, invariant preservation, contextual substitution and receipted standing.
Qualification is contextual, so `qualifiesFor`, `preservesInvariant` and `interchangeableUnder`
hang from receipts and claims rather than from implementations. A claim qualified under one host
cannot silently be reused under another: gate `010_qualified_substitution` compares context.

## Why stable QRI terms shield SOSA 2023

The SOSA/SSN 2023 edition is still a Working Draft. Core QRI terms align to the 2017
Recommendation; the 2023 alignment is a separate file that is not imported, so a later
Recommendation changes the alignment without changing capability identity.

## Why evidence is not authority

A realization that satisfies a WIT function has established an observation. Gate
`030_authority_not_from_capability` refuses any realization or receipt that carries an ODRL
permission. A qualification receipt is evidence; it never authorizes the consequential action.

## Why a failed invariant means no claim

The qualification runner records `preservesInvariant` only for invariants it observed. A required
invariant it cannot establish makes the receipt Failed, and gate `060_invariant_complete` refuses a
Passed receipt that omits one. The shipped `gl` contract lists `noCredentialRead`, which the runner
cannot establish; the reference contract omits it so the reference court can truthfully pass.

## Prior art in this ecosystem

The same Rust to WASM to BEAM shape already runs in graphlaw (`gl_alloc`, `gl_free`, `gl_call`),
ash_graphlaw and ash_a2a (digest-pinned wasmex hosts), beam4pm and autofde. QRI generalizes the
ABI, digest admission and differential-parity discipline those hosts share.

## See Also

[QRI profile reference](../reference/qri-profile.md) ·
[Security and authority](security-and-authority.md)
