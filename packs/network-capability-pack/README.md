# network-capability-pack

Qualified capability contract for the **network/HTTP family** (lane 2 of the
v26.9.30 capability-ecology wave). Five pinned semantic capabilities plus three
provider-closed siblings that a capability-resolution engine (consumer:
`ash_pplan` v26.9.30) resolves against qualified realizations. Version 0.1.0.

- Namespace: `https://ggen.dev/ontology/network-capability#` (pinned in
  `docs/jira/v26.9.30/RESOLUTIONS.md`)
- Composition: reuses `qce:` verbatim
  (`packs/qualified-capability-ecology-pack` — `ncap:Realization
  rdfs:subClassOf qce:CapabilityVersion`, lifecycle stays consumer-court work)
  plus public `prov:`, `earl:`, `dcterms:`, `skos:`. Family-local terms exist
  only for failed edges against the public set (below).

## CAPABILITY != IMPLEMENTATION

A capability is a semantic identity (`Http.Get`), never a package, module or
version. A realization is provider metadata (hex coordinates, cited — never
claimed as local code inspection) plus the `ncap:qualificationCondition`s
under which it counts as the capability.

## Pinned capabilities (dcterms:identifier)

Pinned: `Http.Request` `Http.Get` `Http.Post` `Remote.Invoke` `Endpoint.Resolve`

Minted family siblings (additive facts on witnessed provider closure,
recorded here per the lane contract): `Http.Put` `Http.Delete` `Http.Head` —
`reactor_req` 0.1.7 really ships the `Put`/`Delete`/`Head` DSL entities, so
the sibling capabilities cost no invention and complete the verb closure the
realizations already carry.

## Realizations (provider metadata cited 2026-09-30 from hexdocs/hex listings)

| capability | realizations | provider coordinates |
|---|---|---|
| Http.Request | `Reactor.Req.Dsl.Request` | hex `reactor_req` 0.1.7 (MIT, ash-project; wraps `req`) |
| Http.Get | `Reactor.Req.Dsl.Get` | hex `reactor_req` 0.1.7 |
| Http.Post | `Reactor.Req.Dsl.Post` | hex `reactor_req` 0.1.7 |
| Http.Put | `Reactor.Req.Dsl.Put` | hex `reactor_req` 0.1.7 |
| Http.Delete | `Reactor.Req.Dsl.Delete` | hex `reactor_req` 0.1.7 |
| Http.Head | `Reactor.Req.Dsl.Head` | hex `reactor_req` 0.1.7 |
| Remote.Invoke | `Reactor.Req.Dsl.Post` under Remote.Invoke qualification | hex `reactor_req` 0.1.7 |
| Endpoint.Resolve | `:inet.getaddr/2` | Erlang/OTP `:inet` (stdlib) |

The DSL-entity inventory for `reactor_req` 0.1.7 (Delete, Get, Head, Merge,
New, Options, Patch, Post, Put, Request, Run; step module `Reactor.Req.Step`)
was witnessed from `https://reactor-req.hexdocs.pm/api-reference.html` on
2026-09-30. No local `reactor_req` checkout exists; nothing here claims
code-level inspection.

## Typed network failures and retry stances

Every capability models `dns-failure`, `connect-timeout` (+ `read-timeout`,
`tls-error` where applicable); HTTP capabilities and Remote.Invoke also model
`http-4xx` (deterministic refusal) and `http-5xx` (nondeterministic). The
nondeterministic retry set is explicit per capability: `idempotent-retry`
(safe methods, PUT/DELETE), `no-retry` (POST, Remote.Invoke — a replay may
repeat a consequential effect), `manual` (method-agnostic Http.Request).

## Encoded invariants

- **Plan != Execution** — `ncap:Capability` declares semantics only;
  `gates/010` refuses capabilities no realization can execute.
- **Generated != Admitted** — `gates/020` refuses realizations that claim a
  capability with zero qualification conditions.
- **ProviderAvailable != Authorized** — `gates/040` refuses DO capabilities
  without `ncap:requiresAuthority true` + `ncap:authorityScope`; Remote.Invoke
  on a consequential endpoint needs a bound authority envelope, never mere
  endpoint reachability.
- **Typed failure honesty** — `gates/030` refuses capabilities whose outcome
  model lacks the universal `dns-failure`/`connect-timeout` classes (and, for
  HTTP/Remote.Invoke, `http-4xx`/`http-5xx`).
- **Projection != Source** — this `ontology.ttl` is the source; any manifest
  an engine renders from it is a projection and is never edited back.

## Gates and their witnessed firing fixtures (anti-vacuity)

Every gate is a violation-row SELECT (`ORDER BY`-ed); rows mean refusal. Each
has a negative fixture that fires it — witnessed by
`python3 qualification/verify.py` and by
`tests/test_network_capability_pack.py` (which additionally asserts the exact
single-gate fire property).

| gate | invariant | firing fixture |
|---|---|---|
| `gates/010_capability_requires_realization.rq` | capability-without-realization | `qualification/fixtures/negative-010_capability_requires_realization.ttl` |
| `gates/020_realization_requires_qualification_conditions.rq` | realization-without-qualification-conditions | `qualification/fixtures/negative-020_realization_requires_qualification_conditions.ttl` |
| `gates/030_capability_requires_typed_failure_set.rq` | typed-failure-set-missing (dns/connect-timeout + 4xx/5xx coverage) | `qualification/fixtures/negative-030_capability_requires_typed_failure_set.ttl` |
| `gates/040_consequential_requires_authority.rq` | authority-unbound-on-consequential | `qualification/fixtures/negative-040_consequential_requires_authority.ttl` |
| `gates/050_endpoint_resolution_precondition_required.rq` | family falsifier: outbound capability without endpoint resolution bound first | `qualification/fixtures/negative-050_endpoint_resolution_precondition_required.ttl` |
| `gates/060_retry_semantics_declared.rq` | nondeterministic retry stance undeclared or out of enum | `qualification/fixtures/negative-060_retry_semantics_declared.ttl` |

`witnesses/pass/<stem>.ttl` and `witnesses/fail/<stem>.ttl` are byte-identical
copies of `qualification/fixtures/positive.ttl` and the matching negative
fixture (exact-stem court: `gate-court.toml`; identity asserted by the test
file).

## Failed edges (recorded, never silently pruned)

1. **`reactor_http` does not exist** — hex package API returns 404 for
   `reactor_http` (checked 2026-09-30). The anticipated "reactor_http where
   real" realization surface is therefore empty; the HTTP family realizes via
   `reactor_req` (wrapping `req`), which is real and maintained.
2. **No endpoint-resolution step in reactor_req 0.1.7** — the witnessed DSL
   inventory has no resolve entity (resolution is implicit inside Req).
   `Endpoint.Resolve` therefore realizes via OTP `:inet.getaddr/2`, with a
   qualification condition forcing the resolved address into the receipt
   (endpoint pinning) and refusing silent resolver fallback.
3. **No public vocabulary for typed network failure or retry classes** —
   searched `prov:`, `earl:`, `dcterms:`, `skos:`: none carries DNS/timeout/
   HTTP-status failure semantics or retry-stance classification, so
   `ncap:Outcome`, `ncap:failureClass`, `ncap:determinism`, `ncap:retryClass`
   and kin are family-local terms.
4. **No reuse of `dcp:consequence`/`dcp:Capability` verbatim** — same domain
   coupling argument as the filesystem family (see its README, failed edges
   5–6); families join at the shared READ/DO value vocabulary and the `qce:`
   upper layer.
5. **Remote.Invoke has no dedicated provider step** — it realizes through
   `Reactor.Req.Dsl.Post` under stricter qualification conditions (authority
   envelope before actuation, BRCE receipt, no-retry). Modeling it as the same
   realization without extra conditions was rejected: it would let any POST
   step count as a consequential invocation.

## Evidence boundary

Marketplace admission and ggen qualification only. Zero execution authority:
a capability is not a permission, a reachable endpoint is not an authorization,
and a rendered manifest is not standing. Consequential actuation stays behind
BRCE in the consuming system. `qualification/verify.py` is stdlib+rdflib only:
no network, no subprocess, no DO surface.
