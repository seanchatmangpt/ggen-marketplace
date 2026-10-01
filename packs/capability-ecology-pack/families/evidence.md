# capability-ecology-pack (evidence family)

Evidence/provenance family of the v26.9.30 qualified capability ecology (lane 7). Namespace
`https://ggen.dev/ontology/evidence-capability#`. Consumers (the capability-resolution engine
built in parallel, `ash_pplan`) resolve against the pinned `dcterms:identifier` literals below;
the dotted short name is also carried as `rdfs:label`.

This pack is a semantic contract surface. It grants no execution authority. Evidence is
observation, not actuation; a receipt is data about a consequence, never a license.

## Pinned capabilities

| pinned ID | individual | summary |
|---|---|---|
| `Evidence.Establish` | `ecap:evidence-establish` | verify a receipt / certify external evidence over an exact input; typed refusals; never actuation |
| `Evidence.Bind` | `ecap:evidence-bind` | bind an observation to the exact subject by SHA-256 digest over a canonical encoding; carries standing + lease identity |
| `Receipt.Sign` | `ecap:receipt-sign` | assemble a content-addressed, chain-hashed receipt + verify a signing input (see naming correction below) |
| `Provenance.Record` | `ecap:provenance-record` | lossless typed provenance of one law step (parent/child state ids, lease id, plan digest, raw kept) + payload commitment |

Minted family sibling (recorded per RESOLUTIONS.md): `Standing.Derive`
(`ecap:standing-derive`) — derive a standing value from one admission outcome over the closed
`UNKNOWN | PARTIAL_ALIVE | ALIVE | BLOCKED | BUILD_BROKEN | UNSUPPORTED` vocabulary, never
`ALIVE` from admission alone. No other sibling was minted: every inspected real module maps
onto a pinned capability.

## Realizations (all transcribed from direct reads, 2026-09-30)

| realization | capability | provider | binding | source file(s) opened | pin policy |
|---|---|---|---|---|---|
| `ash-affidavit-verify-op` | `Evidence.Establish` | `ash_affidavit` v26.9.30 | `AshAffidavit.Change.Receipt (op: :verify)` / `AshAffidavit.call/2 op "verify"` | `~/ash_affidavit/lib/ash_affidavit/change/receipt.ex`, `~/ash_affidavit/priv/affidavit/capability-registry.json` | release tag + registry digest |
| `ash-affidavit-certify-authzen` | `Evidence.Establish` | `ash_affidavit` v26.9.30 | `AshAffidavit.call/2 op "certify_authzen_evidence"` | `~/ash_affidavit/lib/ash_affidavit.ex`, capability-registry.json | release tag + registry digest |
| `ash-graphlaw-evidence` | `Evidence.Bind` | `ash_graphlaw` v26.9.30 | `AshGraphLaw.Evidence (digest/1)` | `~/ash_graphlaw/lib/ash_graphlaw/evidence.ex` | exact release tag |
| `ash-affidavit-assemble-op` | `Receipt.Sign` | `ash_affidavit` v26.9.30 | `AshAffidavit.Change.Receipt (op: :assemble)` | change/receipt.ex, capability-registry.json, `~/ash_affidavit/lib/ash_affidavit/type/chain_hash.ex` | release tag + registry digest |
| `ash-affidavit-signature-input` | `Receipt.Sign` | `ash_affidavit` v26.9.30 | `AshAffidavit.call/2 op "verify_signature_input"` | lib/ash_affidavit.ex, capability-registry.json | release tag + registry digest |
| `ash-graphlaw-receipt` | `Provenance.Record` | `ash_graphlaw` v26.9.30 | `AshGraphLaw.Receipt (from_map/1)` | `~/ash_graphlaw/lib/ash_graphlaw/receipt.ex` | exact release tag |
| `ash-affidavit-commit-op` | `Provenance.Record` | `ash_affidavit` v26.9.30 | `AshAffidavit.Change.Receipt (op: :commit)` | change/receipt.ex, capability-registry.json | release tag + registry digest |
| `ash-graphlaw-standing` | `Standing.Derive` | `ash_graphlaw` v26.9.30 | `AshGraphLaw.Standing (of/1)` | `~/ash_graphlaw/lib/ash_graphlaw/standing.ex` | exact release tag |

Honest limits recorded as qualification conditions, not glossed over:

- **The engine signs nothing.** The affidavit engine assembles (`assemble` -> receipt +
  content_address + BLAKE3 `chain_hash`, 64 lowercase hex per `AshAffidavit.Type.ChainHash`)
  and checks (`verify`, `verify_signature_input`) receipts. `Receipt.Sign` therefore qualifies
  as assemble + content-address binding with signing-input verification; signature production
  belongs to an external signer.
- `{:ok, _}` from `AshAffidavit.call/2` is "the engine's computation over exactly the request
  given, not an authorization, a receipt of any DO, or a standing" (moduledoc). Refusals are
  typed with a closed code set (`AshAffidavit.Refusal`).
- `AshGraphLaw` modules are data, not authority: `AshGraphLaw.Evidence` binds observations to
  exact input digests (SHA-256 over canonical encodings, keys sorted, digest excluded from its
  own content); `AshGraphLaw.Receipt` keeps the untouched engine map in `:raw`;
  `AshGraphLaw.Standing.of/1` maps `{:ok, admitted}` to `PARTIAL_ALIVE` and never `ALIVE` from
  admission alone.
- `certify_authzen_evidence` returns `policy_allows` as an observed fact about the presented
  decision — Policy != Authority holds at the evidence layer too.

## The five-field receipt law (gate 050)

A receipt is a receipt only when it carries ALL FIVE fields — the field vocabulary is REUSED
from `packs/qualified-capability-ecology-pack`, never redefined:

| field | property(ies) |
|---|---|
| identity | `qce:subjectCommit` (exact subject SHA) |
| authority | `qce:authorityDigest` or `qce:authorityEnvelope` |
| consequence | `qce:consequenceDigest` |
| replay | `qce:replayReceipt` or `qce:replayDigest` |
| standing | `ecap:standing` -> public APS individual (`https://w3id.org/chatman/aps#`) |

Missing ANY field: not a receipt; an `ecap:ReceiptClaim` asserting it is refused.

## Gates (violation-row SELECTs: rows mean refusal) and their firing fixtures

| gate | refuses | negative fixture that fires it (witnessed) |
|---|---|---|
| `gates/ecap_010_pinned_capability_identity.rq` | a subject claiming a pinned ID without the capability type; duplicate capability identifiers (ambiguous resolver join) | `qualification/fixtures/ecap_negative-pinned-impostor.ttl` |
| `gates/ecap_020_capability_contract_complete.rq` | a capability missing identifier / family / inputs / outputs / outcomes / ceiling, or a ceiling outside `observe < select < construct` | `qualification/fixtures/ecap_negative-incomplete-capability.ttl` |
| `gates/ecap_030_capability_without_realization.rq` | an admitted capability no realization backs | `qualification/fixtures/ecap_negative-capability-without-realization.ttl` |
| `gates/ecap_040_realization_without_qualification.rq` | a realization missing identifier / provider / binding / source file / pin policy / qualification conditions / ceiling, or orphaned from any capability | `qualification/fixtures/ecap_negative-realization-without-qualification.ttl` |
| `gates/ecap_050_receipt_missing_field.rq` | a receipt claim whose asserted artifact misses any of the five fields, or asserts nothing | `qualification/fixtures/ecap_negative-receipt-missing-field.ttl` |
| `gates/ecap_060_evidence_unbound_to_subject.rq` | an evidence claim with no `ecap:subjectDigest`, or a digest that is not 64 lowercase hex (provenance is SHA-bound) | `qualification/fixtures/ecap_negative-evidence-unbound.ttl` |

Anti-vacuity is mechanically witnessed: `python3.11 qualification/verify.py` refuses unless
`ecap_positive.ttl` (plus `ontology.ttl`) is gate-clean AND every negative fixture fires its named
gate. `witnesses/pass/` and `witnesses/fail/` mirror the same six cases under the
`gate-court.toml` exact-stem contract.

## Composition (REUSE -> COMPOSE -> EXTEND; nothing duplicated)

- Receipt classes and digest properties are **reused** from
  `packs/qualified-capability-ecology-pack` (`qce:QualificationReceipt`, `qce:ReplayReceipt`,
  `qce:subjectCommit`, `qce:authorityDigest`, `qce:consequenceDigest`, `qce:replayReceipt`,
  `qce:replayDigest`). No local receipt class exists.
- Standing uses the **public** APS individuals (`https://w3id.org/chatman/aps#`); the closed
  mapping itself is realized by `AshGraphLaw.Standing`.
- Authority requirements compose `packs/capability-ecology-pack` by pinned literal
  (`ecap:authorityRequirement "Authority.Verify"`); the join happens in the consumer resolver.

## Failed edges (recorded, not silently pruned)

- **evidence-standing-pack / evidence-capital-* family (6 packs) / affidavit-pack /
  affidavit-trust-plane-pack / certification-assist-evidence-control-pack /
  evidence-lineage-independence-pack** (all read-only this wave): they model standing control
  planes, evidence capital and lineage independence. None expresses the resolver-facing
  capability-contract layer: pinned `Family.Name` dotted identity joined by
  `dcterms:identifier` literal, realization metadata (provider/binding/pin-policy) and
  qualification conditions over inspected sources. Recorded as the failed edge justifying this
  pack rather than an extension of those.
- **earl:** was considered for evidence claims and rejected: `earl:Assertion` asserts test
  results about an `earl:TestSubject` via an `earl:Assertor`; an evidence claim here binds an
  observation to an exact subject digest and needs no assertor role. `prov:Entity` typing +
  `ecap:subjectDigest` is the minimal honest shape.
- **ash_pplan family parsing (cross-wave seam note, not fixable in this lane):** the pinned IDs
  `Receipt.Sign`, `Provenance.Record` (and sibling `Standing.Derive`) parse to families
  `receipt` / `provenance` / `standing`, which are absent from
  `~/ash_pplan/lib/ash_pplan/capability.ex @families` as inspected (it knows
  `authority` and `evidence`). `authority`/`evidence` IDs parse cleanly. Coordinator/Claude
  must extend the family list or remap; recorded here so the seam is not rediscovered.
- **"Receipt.Sign" literalism**: kept as the pinned ID (the seam is pinned), with the engine's
  real assemble/verify semantics recorded in the capability precondition and realization
  qualification conditions rather than silently renamed.

## Evidence boundary

Marketplace admission and ggen qualification only (SELECT/CONSTRUCT). No execution authority,
no DO surface. Evidence and receipts are observations; standing is derived, never stored.
