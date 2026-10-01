# authority-capability-pack

Authority family of the v26.9.30 qualified capability ecology (lane 7). Namespace
`https://ggen.dev/ontology/authority-capability#`. Consumers (the capability-resolution engine
built in parallel, `ash_pplan`) resolve against the pinned `dcterms:identifier` literals below;
the dotted short name is also carried as `rdfs:label`.

This pack is a semantic contract surface. It grants no execution authority. Policy is not
authority; a request naming authority is not authority; nothing here actuates.

## Pinned capabilities

| pinned ID | individual | class | summary |
|---|---|---|---|
| `Authority.Verify` | `authcap:authority-verify` | `authcap:Capability` | verifies that a **signed** lease presentation satisfies a required ceiling; records lease identity for replay; grants nothing |
| `Authority.Grant` | `authcap:authority-grant` | `authcap:Capability, authcap:ConsequentialCapability` | minting a lease is itself a consequential act: the grantor must already hold a verified envelope of at least equal ceiling; refuses `REFUSED_NO_AUTHORITY` |
| `Actuation.Execute` | `authcap:actuation-execute` | `authcap:Capability, authcap:ConsequentialCapability` | consequential DO over one registered `{resource, action}` pair; **requires a bound typed envelope as precondition** (`ProviderAvailable != Authorized`); refuses `REFUSED_NO_AUTHORITY`; environment-dependent outcomes are first-class |

No sibling IDs were minted in this family: every inspected real module maps onto one of the
three pinned capabilities (the lease read-side is a qualification-conditioned second
realization of `Authority.Grant`, not a new capability).

## Realizations (all transcribed from direct reads, 2026-09-30)

| realization | capability | provider | binding | source file opened | pin policy |
|---|---|---|---|---|---|
| `ash-graphlaw-authority` | `Authority.Verify` | `ash_graphlaw` v26.9.30 | `AshGraphLaw.Authority` | `~/ash_graphlaw/lib/ash_graphlaw/authority.ex` | exact release tag; pinned engine GraphLaw v26.9.28 |
| `ash-graphlaw-authority-readside` | `Authority.Grant` | `ash_graphlaw` v26.9.30 | `AshGraphLaw.Authority (claim/1, identity/1)` | `~/ash_graphlaw/lib/ash_graphlaw/authority.ex` | exact release tag |
| `xaas-actuation-run` | `Actuation.Execute` | `xaas` 26.9.28 | `Xaas.Actuation.run/4` | `~/xaas/lib/xaas/actuation.ex` | VERSION 26.9.28 + receipt schema version |

Honest limits recorded as qualification conditions, not glossed over:

- `AshGraphLaw.Authority` is a **presentation** check: only a signed lease counts; a bare
  ceiling atom, `:lease`, `:unverified_lease` or `nil` all grant `:observe` — a caller cannot
  self-grant `:select`/`:construct` from context. The pinned GraphLaw v26.9.28 engine ignores
  lease keys entirely (`UNSUPPORTED(engine-capability)`): signature/signer/expiry are forwarded
  but not verified today; the ceiling pre-check is the only enforced lease check.
- `Authority.Grant` issuance is not implemented in any inspected module (`ash_graphlaw`,
  `ash_affidavit`, `xaas`); its realization qualifies only the lease read-side and records
  issuance as a brokered operator cut.
- `Xaas.Actuation.run/4` is the exclusive control-plane API for consequential Ash actions
  (admission -> intent/prepared receipt -> DO -> sealed receipt -> replay; external
  consequences via a three-commit protocol). Authority enters as an explicit lease over the
  work; admitting the intent is not itself the authority.
- Surface correction against the family brief: the stated graphlaw surface
  "Policy.Evaluate / Constraint.Decide" does not exist. The real GraphLaw capability registry
  (`~/ash_graphlaw/lib/ash_graphlaw/capability/registry.ex`, GraphLaw 26.9.29 ABI 1) has 14 ops
  — canonical capabilities convert hooks datalog parse entail law shex **policy** sparql n3
  sniff shacl — and op `policy` **admits a FOND policy as strong-cyclic**
  (`~/ash_graphlaw/lib/ash_graphlaw/capability/policy.ex`); it is policy admission, not
  authorization evaluation. The real authority surface is the signed-lease presentation check
  above.

## Gates (violation-row SELECTs: rows mean refusal) and their firing fixtures

| gate | refuses | negative fixture that fires it (witnessed) |
|---|---|---|
| `gates/010_pinned_capability_identity.rq` | a subject claiming a pinned ID without the capability type; a pinned consequential ID without the consequential type; duplicate capability identifiers (ambiguous resolver join) | `qualification/fixtures/negative-pinned-impostor.ttl` |
| `gates/020_capability_contract_complete.rq` | a capability missing identifier / family / inputs / outputs / outcomes / ceiling, or a ceiling outside `observe < select < construct` | `qualification/fixtures/negative-incomplete-capability.ttl` |
| `gates/030_capability_without_realization.rq` | an admitted capability no realization backs | `qualification/fixtures/negative-capability-without-realization.ttl` |
| `gates/040_realization_without_qualification.rq` | a realization missing identifier / provider / binding / source file / pin policy / qualification conditions / ceiling, or orphaned from any capability | `qualification/fixtures/negative-realization-without-qualification.ttl` |
| `gates/050_actuation_without_envelope.rq` | a consequential capability with no envelope precondition, or an envelope link to an untyped node (ambient authority claim) | `qualification/fixtures/negative-actuation-without-envelope.ttl` |
| `gates/060_grant_without_authority.rq` | a consequential capability with no `authcap:authorizingCapability`, or whose outcome set lacks a first-class `REFUSED_NO_AUTHORITY` refusal | `qualification/fixtures/negative-grant-without-authority.ttl` |
| `gates/070_no_authority_increase.rq` | a realization claiming a higher ceiling than its capability (`ProviderAvailable != Authorized` at the boundary) | `qualification/fixtures/negative-authority-increase.ttl` |

Anti-vacuity is mechanically witnessed: `python3.11 qualification/verify.py` refuses unless
`positive.ttl` (plus `ontology.ttl`) is gate-clean AND every negative fixture fires its named
gate. `witnesses/pass/` and `witnesses/fail/` mirror the same seven cases under the
`gate-court.toml` exact-stem contract.

## Composition (REUSE -> COMPOSE -> EXTEND; nothing duplicated)

- `qce:AuthorityEnvelope` and `qce:authorityEnvelope` are **reused** from
  `packs/qualified-capability-ecology-pack` — no local envelope class is minted. The family's
  own version of the qce authority law (`qce` gate 070, delegation-depth non-increase on
  substitution) is specialized here as realization-vs-capability ceiling non-increase.
- Evidence requirements compose `packs/evidence-capability-pack` by pinned literal
  (`authcap:evidenceRequirement "Evidence.Establish"` etc.); the join happens in the consumer
  resolver, not in-tree.
- Standing vocabulary is not redefined; consumers use the public APS individuals
  (`https://w3id.org/chatman/aps#`).

## Failed edges (recorded, not silently pruned)

- **evidence-standing-pack / evidence-lineage-independence-pack / evidence-capital-* (6 packs) /
  affidavit-pack / affidavit-trust-plane-pack / certification-assist-evidence-control-pack**
  (all read-only this wave): their vocabularies model standing control, lineage independence and
  evidence capital — none expresses the capability-contract layer needed by a resolver: pinned
  `Family.Name` dotted identity joined by `dcterms:identifier` literal, realization metadata
  (provider/binding/pin-policy) and qualification conditions. Composing them would have meant
  forcing capability identity into standing vocabularies; recorded here as the failed edge that
  justifies this pack instead of an extension of those.
- **earl:** was considered for outcome/verdict modeling and rejected: `earl:Assertion` models
  test assertions about a `TestSubject`, not authority contracts with typed refusal outcomes;
  forcing it would have renamed, not reused. `authcap:Outcome` + `authcap:refusalCode` is the
  minimal honest shape.
- **`Policy.Evaluate` / `Constraint.Decide` as graphlaw capabilities**: failed against the real
  registry (see above). The pinned `Authority.Verify` models what the source actually does.

## Evidence boundary

Marketplace admission and ggen qualification only (SELECT/CONSTRUCT). No execution authority,
no DO surface, no ambient actuation. `REFUSED_NO_AUTHORITY` remains the family's typed refusal.
