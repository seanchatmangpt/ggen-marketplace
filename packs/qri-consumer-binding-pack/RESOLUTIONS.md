# RESOLUTIONS - qri-consumer-binding-pack term list

Published by lane P1-pack-semantics for P2, E1, F1, S1. Authoritative source: `ontology.ttl`,
`shapes/qcb.shacl.ttl`, `gates/`. Namespaces:

- `qcb:` `https://seanchatmangpt.github.io/packs/qri-consumer-binding-pack#`
- `qri:` `https://seanchatmangpt.github.io/packs/qri-qualification-profile-pack#`
- `spdx:` `http://spdx.org/rdf/terms#`, `dcat:` `http://www.w3.org/ns/dcat#`, `prov:` PROV-O

## Classes

| class | subClassOf | role |
|---|---|---|
| `qcb:ConsumerBinding` | prov:Entity | selection input |
| `qcb:RealizationProfile` | prov:Entity | host/realization profile; `qcb:profileId` in {`node-wasi`, `beam-wasmex`} |
| `qcb:ArtifactPin` | prov:Entity, dcat:Distribution | exact artifact identity |
| `qcb:GeneratedProjection` | prov:Entity | emitted file set |
| `qcb:ProjectionReceipt` | qri:ReplayReceipt | replay receipt |
| reused | | `qri:CapabilityContract`, `qri:Realization`, `qri:Operation`, `qri:RefusalCode`, `spdx:Checksum` |

## Properties

ConsumerBinding: `qcb:contract` (1, qri:CapabilityContract), `qcb:chosenRealization` (exactly 1),
`qcb:candidateRealization` (0..n), `qcb:realizationProfile` (1), `qcb:artifactPin` (1),
`qcb:requestedProjection` in {`host`, `op-names`, `tests`}, `qcb:logicalOperation` (qri:Operation,
names only via `qri:opName`), `qcb:authorityCeiling` (exactly one literal `"NONE"`).

Contract (bound): `qri:contractDigest` (64 lowercase hex, RDFC-1.0 sha256), `qri:contractVersion`,
`qcb:registrySha256` (64 lowercase hex).

ArtifactPin: `qcb:checksum` -> `spdx:Checksum` with `spdx:algorithm spdx:checksumAlgorithm_sha256`
and `spdx:checksumValue` (64 lowercase hex); `dcat:byteSize` (xsd:nonNegativeInteger, >= 1);
`dcat:mediaType`; `qcb:registrySha256`; `qcb:abiVersion`; `prov:wasDerivedFrom` (source ref,
out-of-tree, optional).

GeneratedProjection: `qcb:projectionOf` (subPropertyOf prov:wasDerivedFrom, ConsumerBinding),
`prov:wasGeneratedBy` (prov:Activity), `qcb:outputDigest`, `qcb:authorityCeiling "NONE"`.

ProjectionReceipt: `qcb:projection`, `qcb:packVersion`, `qcb:generatorVersion`, `qcb:packContentDigest`,
`qcb:bindingDigest`, `qcb:outputDigest`,
`qcb:authorityCeiling "NONE"`. All digests 64 lowercase hex. No standing property exists. The contract digest is NOT a receipt property: it is `qri:contractDigest` on the bound
contract (reused directly; the receipt JSON `contract_digest` is read through `qcb:projection` /
`qcb:projectionOf` / `qcb:contract`, and `consume.py` admits only when declared == RDFC-1.0 recomputed).

Refusal vocabulary: `qcb:refusalClass`, `qcb:brokenTerm`, `qcb:refusedByGate`, `qcb:standingLiteral`.

## Refusal codes (scheme `qcb:generation-refusals`, each `qri:RefusalCode`, `skos:notation` = code)

| code | class | broken_term | gate stem | standing literal |
|---|---|---|---|---|
| AMBIGUOUS_REALIZATION | refused_structure | admission_vacuous | 100_realization_unambiguous | REFUSED:AMBIGUOUS_REALIZATION |
| PIN_MISSING | refused_identity | R_missing_identity | 090_pin_present | REFUSED:PIN_MISSING |
| PIN_DIGEST_MALFORMED | refused_identity | R_missing_identity | 095_pin_digest_wellformed | REFUSED:PIN_DIGEST_MALFORMED |
| PIN_REGISTRY_MISMATCH | refused_identity | mu_on_O | 120_pin_registry_match | REFUSED:PIN_REGISTRY_MISMATCH |
| CEILING_NOT_NONE | refused_authority | R_missing_authority | 110_authority_ceiling_none | REFUSED:CEILING_NOT_NONE |
| CONTRACT_DIGEST_MISSING | refused_identity | R_missing_identity | 130_contract_digest_present | REFUSED:CONTRACT_DIGEST_MISSING |
| PROFILE_UNSUPPORTED | unsupported | mu_on_O | 140_profile_supported | UNSUPPORTED:PROFILE_UNSUPPORTED |
| PROJECTION_TYPE_UNSUPPORTED | unsupported | mu_on_O | 150_projection_type_supported | UNSUPPORTED:PROJECTION_TYPE_UNSUPPORTED |

Resolutions of plan gaps (decisions, not observations): the plan gave no broken_term for
PIN_REGISTRY_MISMATCH, CONTRACT_DIGEST_MISSING, PROFILE_UNSUPPORTED, PROJECTION_TYPE_UNSUPPORTED;
assigned as above. UNSUPPORTED codes use the `UNSUPPORTED:` literal (UNSUPPORTED is not REFUSED).
Plan had no separate PIN_DIGEST_MALFORMED gate; split into 090 (pin or checksum absent) and 095
(digest/algorithm malformed) so each code has one gate and one exact-stem witness pair.

## Gates

Every gate: `SELECT ?subject ?code ... ORDER BY ?subject`; a row is a refusal; `?code` is the
refusal code. Court runner: `runners/semantic_runner.py`. qri gate 030 (odrl:permission /
qri:grantsAuthority) is NOT duplicated here; compose it from qri for permission escalation.

`090_pin_present`, `095_pin_digest_wellformed`, `100_realization_unambiguous`,
`110_authority_ceiling_none`, `120_pin_registry_match`, `130_contract_digest_present`,
`140_profile_supported`, `150_projection_type_supported`.

## Shapes (`shapes/qcb.shacl.ttl`)

`qcb:ConsumerBindingShape`, `qcb:BoundContractShape` (targetObjectsOf qcb:contract),
`qcb:RealizationProfileShape`, `qcb:ArtifactPinShape`, `qcb:ChecksumShape` (targetObjectsOf
qcb:checksum), `qcb:GeneratedProjectionShape`, `qcb:ProjectionReceiptShape`. Shape files import
nothing; `-e ontology.ttl` is optional (witnesses are explicitly typed).

## Notes for downstream lanes

- P2: scaffold left `ggen.toml`, `queries/10-subjects.rq`, `templates/subjects.txt.tera` untouched
  (they now match no individuals and emit an empty `generated/subjects.txt`); replace them. Add
  `ontology/alignments.ttl` and `shapes/qcb.shacl.ttl` to `[ontology] imports` in `ggen.toml` if
  queries need them. ggen.toml version is still `26.9.0`; pack.toml is `26.9.30`.
- Standing is derived, never stored. Refusal => zero files; the runner prints typed JSON
  `{code, class, broken_term, gate}` drawn from `qcb:generation-refusals`.
- Registry digest is a contract property (`qcb:registrySha256`) AND a pin property; gate 120 refuses
  when either is absent while the other is present, or when they differ.
- `witnesses/extra/*.ttl` (4 files, `<gate>.<variant>.ttl`) are judged by
  `python3.11 runners/semantic_runner.py --extras`; they are outside the exact-stem court.
- Witness literals: sample digests are synthetic except the pin byte size and wasm sha256 pattern
  taken from the plan (pin sha256 5e721cc2...a7761f7, 284650 bytes).

## Repair addendum (audit defects, 2026-09-30)

New gates: 092 `PIN_AMBIGUOUS` (exactly one pin), 105 `REALIZATION_CONTRACT_MISMATCH` (chosen realization
implements the bound contract and is a declared candidate when candidates exist), 160 `AUTHORITY_GRANTED`
(no `odrl:permission` / `qri:grantsAuthority` on any node of the binding graph; superset of qri gate 030).
Gate 110 now also requires `xsd:string` (no language tag, no other datatype). Runner-side typed codes in
the scheme: `CONTRACT_DIGEST_MISMATCH`, `SHAPE_NONCONFORMANT`. `qcb:ggenVersion` is renamed
`qcb:generatorVersion` (generator identity is opaque to the contract); the receipt JSON key is
`generator_version` (no generator product name in any record key).

## Alignment (audit repair G1)

Every `qcb:` class, property and scheme is subsumed by, or justified against, a public or qri term:
an entailing `rdfs:subClassOf` / `rdfs:subPropertyOf` in `ontology.ttl` (e.g. `qcb:profileId`
subPropertyOf `dct:identifier`), or a `skos:scopeNote` delta justification plus a non-entailing
`skos:relatedMatch` / `rdfs:seeAlso` to the nearest published term in `ontology/alignments.ttl`.
Court: `test_every_qcb_term_is_subsumed_or_justified_against_a_public_term`. `qcb:contractDigest` was a
duplicate of `qri:contractDigest` and is removed. SRFC-001 R1-R3 are the normative statement.
