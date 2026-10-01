# process-capability-pack

Qualified capability contracts for the **OTP/BEAM process family** (lane 3,
v26.9.30 capability ecology wave). The consumer of these contracts is a
capability-resolution engine (ash_pplan v26.9.30): plans name capabilities,
providers are resolved against realizations — never the reverse.

- Namespace: `https://ggen.dev/ontology/process-capability#` (`pcap:`)
- Version: 0.1.0 (SemVer, `pack.toml`)
- Profile: semantic; gates are violation-row SELECTs (rows mean refusal)

## Capabilities (pinned + minted)

| identity (`dcterms:identifier` = `rdfs:label`, the resolver join key) | family | consequence | source |
|---|---|---|---|
| `Process.Spawn` | process-lifecycle | DO | pinned (RESOLUTIONS.md) |
| `Process.Supervise` | process-supervision | DO | pinned |
| `Process.Signal` | process-signaling | DO | pinned |
| `Process.Link` | process-linking | DO | pinned |
| `Process.Monitor` | process-monitoring | READ | minted sibling (lane 3) |
| `Process.Unlink` | process-linking | DO | minted sibling (lane 3) |

Every capability carries: input/output contracts, precondition, postcondition,
typed outcomes (success + typed failures + nondeterministic set), evidence
requirement, authority requirement (for consequence-DO), and execution
properties (durability / isolation / concurrency / link-failure propagation).
`Process.Supervise` and its realizations carry `pcap:supervisionSemantics`
(restart intensity, isolation scope, propagation).

## Realizations (provider metadata: cited, never fabricated)

| realization | realizes | provider coordinates | basis |
|---|---|---|---|
| `pcap:real-reactor-process` | Spawn, Supervise | hex `reactor_process` 0.5.0, https://hex.pm/packages/reactor_process, https://github.com/ash-project/reactor_process | hex.pm page citation: "A Reactor extension which provides steps for working with supervisors." — **no local checkout exists; no local inspection claimed** |
| `pcap:real-otp-stdlib` | Spawn, Supervise, Signal, Link, Monitor, Unlink | Erlang/OTP stdlib (kernel/stdlib), https://github.com/erlang/otp | public OTP API surface; pin OTP 26+ |

Both carry `pcap:qualificationCondition`, `pcap:versionPinPolicy`,
`pcap:evidenceReference` (pending until a receipted run admits them) and
`qce:admitted false`. Realization availability is NOT authority.

## Gates and their witnessed refusals (anti-vacuity)

Every gate is a violation-row SELECT. Each has same-stem pass/fail witnesses
(`witnesses/pass`, `witnesses/fail`; structural court `gate-court.toml`) and a
named negative fixture that fires it and only it
(`qualification/verify.py`, exit non-zero on any mismatch):

| gate | refuses | firing negative fixture |
|---|---|---|
| `gates/010_capability_requires_realization.rq` | capability without any realization | `qualification/fixtures/negative-capability-without-realization.ttl` (unrealized `Process.Register`) |
| `gates/020_realization_requires_qualification.rq` | realization without a qualification condition | `qualification/fixtures/negative-realization-without-qualification.ttl` |
| `gates/030_supervision_semantics_required.rq` | supervision capability/realization without restart-intensity + isolation + propagation semantics | `qualification/fixtures/negative-supervision-semantics-missing.ttl` (unsemanticed `Process.RestartChild`) |
| `gates/040_consequential_requires_authority.rq` | consequence-DO capability without bound authority (ProviderAvailable != Authorized) | `qualification/fixtures/negative-authority-unbound.ttl` (unbound `Process.Send`) |
| `gates/050_capability_identity_impl_free.rq` | implementation token inside a capability identity (CAPABILITY != IMPLEMENTATION) | `qualification/fixtures/negative-provider-token-identity.ttl` (`Reactor.Spawn`) |
| `gates/060_admitted_requires_evidence.rq` | `qce:admitted true` without an evidence reference (Generated != Admitted) | `qualification/fixtures/negative-admitted-without-evidence.ttl` |

Positive fixture: `qualification/fixtures/positive.ttl` adds one fully-lawful
capability + realization binding (`Process.Demonitor`, real OTP primitive
`demonitor/1`) and must keep every gate at zero rows.

## Encoded invariants

`pcap:plan-not-execution`, `pcap:policy-not-authority`,
`pcap:provider-available-not-authorized`, `pcap:projection-not-source`,
`pcap:generated-not-admitted` (skos:Concepts in `ontology.ttl`); mechanically
enforced where checkable by gates 040, 050, 060.

## Search-ladder record: failed edges (nothing silently pruned)

1. `failed(edge_reuse_beam4pm_process_model)` —
   `packs/beam4pm-process-model-pack` is BEAM **record-type projection**
   vocabulary (`bpm:RecordType` / `bpm:Field` / `bpm:FieldType`) for
   process-mining records. It has no capability, realization, qualification,
   supervision-semantics or execution-property machinery; it cannot express an
   OTP supervision capability contract. Topology, not graph failure: this pack
   is the additive family; that pack is untouched.
2. `failed(edge_reuse_process_intelligence)` — `packs/process-intelligence-pack`
   (`pi:Event` / `pi:ProcessModel` / `pi:ConformanceCheck` / `pi:Drift`) and
   `packs/process-mining-proof-pack` model **observations of past executions**
   (OCEL/mining proofs), not executable capability contracts with
   preconditions and realizations.
3. `failed(edge_ash_reactor_process_steps)` — Ash.Reactor exposes Ash
   action/changeset/notification surfaces; it has no step expressing OTP
   process primitives (spawn/link/signal/supervise). The realization surface
   is therefore `reactor_process` + OTP stdlib, cited above.
4. `failed(edge_public_vocab_no_condition_slot)` — prov/earl/dcterms/skos have
   no declarative qualification-condition, supervision-semantics or provider-
   metadata slot (an `earl:Assertion` is an evidence *instance*, not a
   condition; dcterms has no provider-coordinate property). Hence the pcap:
   properties; each is domain-scoped and gated.
5. qce: is COMPOSED, not extended: capabilities are `rdfs:subClassOf
   qce:CapabilityVersion` and realizations reuse `qce:admitted` unchanged.
   dcp:'s closed consequence convention ("READ"|"DO") is reused as a
   convention.

## Evidence boundary

Marketplace admission and real-ggen qualification only. SELECT/CONSTRUCT
semantics; this pack grants **no DO authority**; BRCE remains the sole
consequential actuation boundary. Every `qce:admitted` in this graph is
`false` until a receipted run binds an earl: assertion on the exact subject.

## Verification

```bash
python3.11 scripts/marketplace.py check process-capability-pack   # real ggen, scoped
python3.11 packs/process-capability-pack/qualification/verify.py  # anti-vacuity court
python3.11 scripts/check_gate_witness_courts.py --packs packs     # structural court
python3.11 -m pytest tests/test_process_capability_pack.py        # execution falsifiers
```
