# capability-ecology-pack (filesystem family)

Qualified capability contract for the **filesystem family** (lane 2 of the
v26.9.30 capability-ecology wave). Nine pinned semantic capabilities that a
capability-resolution engine (consumer: `ash_pplan` v26.9.30) resolves against
qualified realizations. Version 0.1.0.

- Namespace: `https://ggen.dev/ontology/filesystem-capability#` (pinned in
  `docs/jira/v26.9.30/RESOLUTIONS.md`)
- Composition: reuses `qce:` verbatim
  (`packs/qualified-capability-ecology-pack` — `fscap:Realization
  rdfs:subClassOf qce:CapabilityVersion`, lifecycle stays consumer-court work)
  plus public `prov:`, `earl:`, `dcterms:`, `skos:`. Family-local terms exist
  only for failed edges against the public set (below).

## CAPABILITY != IMPLEMENTATION

A capability is a semantic identity (`File.Read`), never a package, module or
version. A realization is provider metadata (hex coordinates, cited — never
claimed as local code inspection) plus the `fscap:qualificationCondition`s
under which it counts as the capability.

## Pinned capabilities (dcterms:identifier)

`File.Read` `File.Write` `File.Copy` `File.Move` `File.Delete` `File.Exists`
`Dir.List` `Dir.Mkdir` `Dir.Remove`

No family siblings were minted: the nine pinned IDs cover the resolution
surface; provider steps beyond them (`CpR`, `MkdirP`, `Stat`, `Glob`, …)
appear as additional realizations of pinned capabilities, not as new
capabilities.

## Realizations (provider metadata cited 2026-09-30 from hexdocs/hex listings)

| capability | realizations | provider coordinates |
|---|---|---|
| File.Read | `Reactor.File.Step.ReadFile` | hex `reactor_file` 0.18.5 (MIT, ash-project) |
| File.Write | `Reactor.File.Step.WriteFile` | hex `reactor_file` 0.18.5 |
| File.Copy | `Reactor.File.Step.Cp`, `Reactor.File.Step.CpR` | hex `reactor_file` 0.18.5 |
| File.Move | `:file.rename/2` | Erlang/OTP `:file` (stdlib) |
| File.Delete | `Reactor.File.Step.Rm` | hex `reactor_file` 0.18.5 |
| File.Exists | `:file.read_file_info/1` | Erlang/OTP `:file` (stdlib) |
| Dir.List | `Reactor.File.Step.Glob` | hex `reactor_file` 0.18.5 |
| Dir.Mkdir | `Reactor.File.Step.Mkdir`, `Reactor.File.Step.MkdirP` | hex `reactor_file` 0.18.5 |
| Dir.Remove | `Reactor.File.Step.Rmdir` | hex `reactor_file` 0.18.5 |

The DSL-entity inventory for `reactor_file` 0.18.5 (Chgrp, Chmod, Chown,
CloseFile, Cp, CpR, Glob, IoBinRead, IoBinStream, IoRead, IoStream, IoWrite,
Ln, LnS, Lstat, Mkdir, MkdirP, OpenFile, ReadFile, ReadLink, Rm, Rmdir, Stat,
Touch, WriteFile, WriteStat) was witnessed from
`https://reactor-file.hexdocs.pm/api-reference.html` on 2026-09-30. No local
`reactor_file` checkout exists; nothing here claims code-level inspection.

## Encoded invariants

- **Plan != Execution** — `fscap:Capability` declares semantics only;
  `gates/010` refuses capabilities no realization can execute.
- **Generated != Admitted** — `gates/020` refuses realizations that claim a
  capability with zero qualification conditions; qce lifecycle
  (candidate → qualified → frozen) is consumer-court work.
- **ProviderAvailable != Authorized** — `gates/040` refuses DO capabilities
  without `fscap:requiresAuthority true` + `fscap:authorityScope`; authority
  is bound at execution time by the consumer, never by this graph.
- **Typed failure honesty** — `gates/030` refuses capabilities whose outcome
  model lacks the universal `enoent`/`eacces` classes (silent failure
  absorption).
- **Projection != Source** — this `ontology.ttl` is the source; any manifest
  an engine renders from it is a projection and is never edited back.

## Gates and their witnessed firing fixtures (anti-vacuity)

Every gate is a violation-row SELECT (`ORDER BY`-ed); rows mean refusal. Each
has a negative fixture that fires it — witnessed by
`python3 qualification/verify.py` and by
`tests/test_filesystem_capability_pack.py` (which additionally asserts the
exact single-gate fire property: each negative fixture trips its own gate and
no other).

| gate | invariant | firing fixture |
|---|---|---|
| `gates/fscap_010_capability_requires_realization.rq` | capability-without-realization | `qualification/fixtures/negative-fscap_010_capability_requires_realization.ttl` |
| `gates/fscap_020_realization_requires_qualification_conditions.rq` | realization-without-qualification-conditions | `qualification/fixtures/negative-fscap_020_realization_requires_qualification_conditions.ttl` |
| `gates/fscap_030_capability_requires_typed_failure_set.rq` | typed-failure-set-missing (enoent/eacces coverage) | `qualification/fixtures/negative-fscap_030_capability_requires_typed_failure_set.ttl` |
| `gates/fscap_040_consequential_requires_authority.rq` | authority-unbound-on-consequential | `qualification/fixtures/negative-fscap_040_consequential_requires_authority.ttl` |
| `gates/fscap_050_path_safety_precondition_required.rq` | family falsifier: path traversal precondition absent on File.*/Dir.* | `qualification/fixtures/negative-fscap_050_path_safety_precondition_required.ttl` |
| `gates/fscap_060_mutator_execution_properties_declared.rq` | mutator execution properties (File.Move reversible, File.Delete compensable; idempotency) | `qualification/fixtures/negative-fscap_060_mutator_execution_properties_declared.ttl` |

`witnesses/pass/<stem>.ttl` and `witnesses/fail/<stem>.ttl` are byte-identical
copies of `qualification/fixtures/fscap_positive.ttl` and the matching negative
fixture (exact-stem court: `gate-court.toml`; identity asserted by the test
file).

## Failed edges (recorded, never silently pruned)

1. **No move step in reactor_file v0.18.5** — the witnessed DSL inventory has
   no move entity (only `Ln`/`LnS` links and `Cp`). `File.Move` therefore
   realizes via OTP `:file.rename/2`. Rejected alternative: a `Ln`+`Rm`
   composite realization — non-atomic, two failure surfaces for one semantic
   step, so `exdev` could leave a half-applied move.
2. **No exists-check step in reactor_file v0.18.5** — `Stat`/`Lstat` model
   metadata, not boolean existence with absence/permission distinction.
   `File.Exists` realizes via `:file.read_file_info/1` errno mapping
   (qualification condition pins the mapping).
3. **No directory-listing step in reactor_file v0.18.5** — `Dir.List`
   realizes via `Reactor.File.Step.Glob`, the nearest real provider, with an
   added pattern-confinement qualification condition (Glob takes a pattern,
   not a plain directory path — the confinement closes the traversal edge the
   pattern input would otherwise open).
4. **No public vocabulary for path-safety preconditions or filesystem typed
   failures** — searched `prov:`, `earl:`, `dcterms:`, `skos:`: none carries
   FS path confinement or errno-class semantics, so `fscap:Precondition`,
   `fscap:Outcome`, `fscap:failureClass` and kin are family-local terms.
5. **No reuse of `dcp:consequence` verbatim** — the READ/DO value vocabulary
   is shared with `packs/domain-capability-pack`, but the property is
   family-local (`fscap:consequenceClass`): `dcp:consequence`'s
   `rdfs:domain` points at `dcp:Capability`, so verbatim reuse would couple
   this family's graph to another pack's domain class. Families join at the
   value level.
6. **`dcp:Capability` itself not reused as the class** — same domain coupling
   argument; `qce:` is the shared upper layer this pack composes instead.

## Evidence boundary

Marketplace admission and ggen qualification only. Zero execution authority:
a capability is not a permission, a realization is not a run, and a rendered
manifest is not standing. Consequential actuation stays behind BRCE in the
consuming system. `qualification/verify.py` is stdlib+rdflib only: no network,
no subprocess, no DO surface.
