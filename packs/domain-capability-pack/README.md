# domain-capability-pack (v0.2.0)

Qualified capability-contract pack for the **DOMAIN family** (Ash domain actions),
consumable by a capability-resolution engine (consumer: `ash_pplan` v26.9.30). Extends the
v0.1.0 drift-guard transcription layer (SREGym 14-capability worked instance — unchanged)
with a contract layer: pinned semantic capability identities, qualified realizations,
authority requirements, and refusal gates.

## Namespace alignment (explicit, not silent)

`dcp:` moved verbatim from the legacy `http://seanchatmangpt.github.io/packs/domain-capability#`
to the wave-pinned `https://ggen.dev/ontology/domain-capability#` (RESOLUTIONS.md). Every
legacy term carries a `dcterms:isReplacedBy` record (`dcp:NamespaceAlignment2026-09-30`);
no term was deleted or redefined. Known consumers of the legacy IRIs
(`gym-upper-ontology-pack`, `standing-ladder-pack`) carry self-contained legacy-IRI copies
in their own qualification fixtures — unaffected.

## Pinned capability IDs (canonical, via `rdfs:label` + `dcterms:identifier`)

| ID | authority req | realizations (all modules actually read 2026-09-30, real sha256 digests in ontology.ttl) |
|---|---|---|
| `Domain.Action.Invoke` | construct | `Ash.Reactor.ActionStep` (ash 3.33.11); `AshPPlan.Providers.Steps.DomainAction` kind `:action` (ash_pplan @de92fceb) |
| `Domain.Query.Read` | observe | `Ash.Reactor.ReadStep`; `AshPPlan.Providers.Steps.DomainAction` kind `:read`; `Ash.CodeInterface` |
| `Domain.Change.Apply` | construct | `AshPPlan.Providers.Steps.DomainAction` kinds `:create/:update/:destroy`; `Ash.Reactor.CreateStep`/`UpdateStep`/`DestroyStep` |
| `Domain.Query.ReadOne` (sibling) | observe | `Ash.Reactor.ReadOneStep` |
| `Domain.Record.Create` (sibling) | construct | `Ash.Reactor.CreateStep`; `Ash.CodeInterface` |
| `Domain.Record.Update` (sibling) | construct | `Ash.Reactor.UpdateStep` |
| `Domain.Record.Destroy` (sibling) | construct | `Ash.Reactor.DestroyStep` |
| `Domain.Bulk.Apply` (sibling) | construct | `Ash.bulk_create/4`/`bulk_update/4`/`bulk_destroy/4`; `Ash.Reactor.BulkCreateStep`/`BulkUpdateStep`/`BulkDestroyStep` |

Provider aliases observed on the consumer side (`dcp:providerAlias`): `Domain.Action`,
`Domain.Read`, `Domain.Create`, `Domain.Update`, `Domain.Destroy` (ash_pplan's current
provider capability list, read 2026-09-30 — recorded so the consumer's alignment to the
pinned IDs is explicit).

## Gates (all refusal SELECTs; rows = REFUSE; every new gate has a firing negative fixture)

| gate | refuses | firing negative fixture |
|---|---|---|
| `gates/010_required.rq` (v0.1.0, conserved) | transcription facts missing required fields; out-of-enum `dcp:consequence` | (worked-instance guard; negative shape covered by fixtures for 040) |
| `gates/020_exact_count_per_source.rq` (v0.1.0, conserved) | real per-source capability count diverging from the declared manifest | (worked-instance guard) |
| `gates/030_allowlist_subset.rq` (v0.1.0, conserved) | allowlist admitting a non-real capability | (worked-instance guard) |
| `gates/040_required_contract_fields.rq` | contract-layer required fields missing; `authorityRequirement` outside `none/observe/construct` | `qualification/fixtures/negative-missing-required-contract-fields.ttl` |
| `gates/050_capability_requires_realization.rq` | capability with zero realizations | `qualification/fixtures/negative-capability-without-realization.ttl` |
| `gates/060_realization_requires_qualification.rq` | realization with zero qualification conditions | `qualification/fixtures/negative-realization-without-qualification.ttl` |
| `gates/070_availability_requires_authority.rq` | **ProviderAvailable ≠ Authorized**: `available true` with no `qce:authorityEnvelope`, or envelope ceiling below the capability's requirement | `qualification/fixtures/negative-available-without-authority.ttl` (both branches, 2 rows) |
| `gates/080_no_do_authority.rq` | **Policy ≠ Authority**: any `qce:grantsDoAuthority true`, any `authorityRequirement "do"` | `qualification/fixtures/negative-do-authority.ttl` (both branches, 2 rows) |
| `gates/090_runtime_only_frozen.rq` | **Plan ≠ Execution**: a runtime episode executing a non-frozen realization | `qualification/fixtures/negative-runtime-unfrozen.ttl` |

**Projection ≠ Source / Generated ≠ Admitted**: this ontology is the admitted
source-of-record; `templates/` are consequences (data projections via frontmatter, per
FM-PACK-013) and are never re-admitted as source.

## Anti-vacuity court

```
python3.11 packs/domain-capability-pack/qualification/verify.py
# ADMITTED:dcp semantic court (9 gates clean on positive; 6 negative fixtures witnessed firing)
```

Pinned by `tests/test_domain_capability_pack.py` (positive-clean + per-gate witnessed
firing + pinned-ID presence + alignment-record completeness).

## Failed edges (custom terms legal only against these)

- `dcp:realizes` — qce: binds receipts→versions (`qce:qualifies`) and substitutions, but has
  no stable-identity→realization edge. Public set (prov/dcterms/skos/earl) has none either.
- `dcp:authorityRequirement` — ODRL expresses permission policies, not the resolver's closed
  rank (`none < observe < construct`, `do` refused; `resolver.ex @authority_rank`).
- `dcp:precondition`/`dcp:postcondition` — SHACL `sh:condition` validates node shapes, not
  capability preconditions.
- `dcp:outcome` — `earl:TestResult` asserts test outcomes, not a capability's outcome set
  (success + typed failures + nondeterministic set).
- `dcp:acceptsInput`/`dcp:producesOutput` — no public IO-signature vocabulary.
- `dcp:executionProperty`/`dcp:evidenceKind` — the resolver's own property/evidence atoms
  (`:transactional`, `:policy_checked`, `:ash_result`); earl states assertions, not kinds a
  provider emits.
- `dcp:available`, `dcp:providerId`, `dcp:providerPackage`, `dcp:providerModule`,
  `dcp:providerVersion`, `dcp:providerAlias`, `dcp:versionPinPolicy`,
  `dcp:qualificationCondition` — provider metadata per RESOLUTIONS.md; DOAP describes
  projects, not realization bindings with pin policies.
- `dcp:DomainCapability` — qce:CapabilityVersion is lifecycle-relative, not a stable family
  identity; deliberately a SIBLING of `dcp:Capability` (transcription class), not a subclass,
  so gate 010's transcription required-fields never demand fabricated provenance on semantic
  identities.

## Verification surface

```
python3.11 scripts/marketplace.py check domain-capability-pack   # real ggen, scoped
python3.11 -m pytest tests/test_domain_capability_pack.py -q
```

## UNSUPPORTED (named, not papered over)

- Execution evidence for realizations: this pack admits capability CONTRACTS and their
  qualification conditions; it does not witness executions. `ALIVE` for any realization
  requires observed execution against the exact admitted subject — the consumer's runtime
  (qce:RuntimeEpisode + closure receipts). Intended owner: ash_pplan v26.9.30.
- `reactor_file`/`reactor_req` style hex-only provider packages for the DOMAIN family: none
  admitted here (no local checkout inspected); the ash/ash_pplan realizations above are the
  complete admitted set. Intended owner: this pack, in a later version, with real inspection.
- Rendering the SREGym allowlist for autofde-lab (v0.1.0 named follow-up) still lives in a
  different repo (autofde-lab); templates here project, they do not write consumer repos.
