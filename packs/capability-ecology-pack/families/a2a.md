# capability-ecology-pack (a2a family)

Qualified capability-contract pack for distributed agent-to-agent (SA2A)
invocation: the semantic capability layer `ash_pplan` (v26.9.30, parallel
wave) resolves against. Built in lane 6 of the v26.9.30 capability ecology
wave (`docs/jira/v26.9.30/_LANES.md`, `RESOLUTIONS.md`).

- Namespace: `aacap:` = `https://ggen.dev/ontology/a2a-capability#` (pinned)
- Pinned capability IDs (`dcterms:identifier` + `rdfs:label`): `A2A.Invoke`,
  `A2A.Discover`, `A2A.Await`. The workflow corpus joins these as
  `dcterms:identifier` literals; the join happens in the consumer resolver,
  never in-tree.
- Version 26.9.0. `[pack]` carries name/version/description only
  (FM-PACK-003). No `shapes.ttl` (FM-PACK-012). Gates are violation-row
  SELECTs, all with `ORDER BY` (E0013). SELECT/CONSTRUCT-only; grants no DO
  authority.

## Capability model

CAPABILITY != IMPLEMENTATION. `aacap:Capability` is semantic identity only;
`aacap:Realization` carries provider metadata (`aacap:providerRepo`,
`providerModule`, `providerSourceFile`, `providerSourceCommit`,
`versionPinPolicy`) plus a declared `aacap:QualificationCondition`
(`earl:outcome earl:passed` + statement + scope).

Each capability expresses: inputs, outputs, preconditions, postconditions,
typed outcomes (success + `peer_unreachable` / `timeout` / `refused_remote` /
`partial_completion` + the nondeterministic retry set), evidence
requirements, authority requirements, and execution properties
(durability / isolation / replay / concurrency) where witnessed.

Encoded invariants (each gate-backed):

| invariant | encoding |
|---|---|
| Plan != Execution | `aacap:grantsDoAuthority false` on every capability and realization |
| Policy != Authority | `aacap:admissionPolicy` never satisfies gate 030 |
| ProviderAvailable != Authorized | `aacap:providerReachable` never satisfies gate 030 |
| Projection != Source | `aacap:derivedFromSource` on index realizations; compiler "never creates business semantics" |
| Generated != Admitted | generated surfaces qualify only via a declared condition (gate 020) |

Remote authority is NEVER ambient: a realization with
`aacap:authorityLocation "remote"|"both"` must carry a `qce:AuthorityEnvelope`
(composed verbatim from `packs/qualified-capability-ecology-pack`) whose
`aacap:validAtEnd` is `"remote"` or `"both"` — valid at the REMOTE end.
The modeled envelope is minted by the remote end's broker and re-verified
live at execution time (real provider fact:
`AshA2A.Delivery.ObanAuthority.verify_live!/3`, RFC-SA2A-001 "none may
regain ambient DO").

`A2A.Await` models the suspension gap and composes `Workflow.Resume`
(dcap pinned dotted ID) via `aacap:resumeReference "Workflow.Resume"` —
dotted-ID literal only, no cross-pack import; the resolver performs the join.

## Realizations: real ash_a2a surface (operator mapping CORRECTED)

Provider tree: `~/ash_a2a` @ `fbea18c5d58c5b38776b70b477d9cd24c96963a8`
(read-only inspection, 2026-09-30). The operator's provisional mapping
named `Distributed.Invoke`, `AwaitResponse`, and `CapabilityDiscover` —
grep over `~/ash_a2a/lib` returns zero hits for all three; the real surface
is:

| capability | real realization (inspected files) |
|---|---|
| `A2A.Invoke` | `AshA2A.Reactor.ExecuteCommand` (`lib/ash_a2a/reactor/execute_command.ex`); `AshA2A.CommandBus.run/4` (`lib/ash_a2a/command_bus.ex`); `AshA2A.Dispatcher.dispatch/6` under `ConsequenceKernel.W4.DispatcherFence` (`lib/ash_a2a/dispatcher.ex`); authority carriage + live re-verification: `AshA2A.Delivery.ObanAuthority` (`lib/ash_a2a/delivery/oban_authority.ex`) |
| `A2A.Await` | `AshA2A.A2ATransport.TaskEvents` (`lib/ash_a2a/a2a_transport/task_events.ex`; runtime documented in `lib/ash_a2a/a2a_transport/transport.ex`); durable variant `AshA2A.TaskStore.Ekv` (`lib/ash_a2a/task_store/ekv.ex`) |
| `A2A.Discover` | `AshA2A.CapabilityIndex` facade (`lib/ash_a2a/capability_index.ex`); `AshA2A.CapabilityIndex.Compiler` (`lib/ash_a2a/capability_index/compiler.ex`); agent card built by `AshA2A.CapabilityIndex.AgentCardBuilder.build_agent_card/2` (named by the facade) |

The consequence calculus is transcribed 1:1 from the real
`AshA2A.Skill` `consequence` field (`lib/ash_a2a/skill.ex`):
`:observe | :change | :external_do`, with `:unknown` failing closed
(`:consequence_unclassified`) — modeled as closed `aacap:consequenceClass`
`"observation" | "change" | "external_do"`.

Standing: these are INSPECTION-scope qualifications
(`aacap:conditionScope` says so explicitly). `inspection != execution`:
no capability here claims ALIVE execution standing; resolution standing is
established by the consumer (ash_pplan) against observed executions.

## Gates (violation-row SELECTs — rows mean refusal)

| gate | refuses | firing fail witness (witnessed firing, exact stem) |
|---|---|---|
| `gates/aacap_010_capability_requires_realization.rq` | capability without any realization | `witnesses/fail/aacap_010_capability_requires_realization.ttl` (1 row) |
| `gates/aacap_020_realization_requires_qualification.rq` | realization without complete qualification condition (no `earl:passed` / statement / scope) | `witnesses/fail/aacap_020_realization_requires_qualification.ttl` (1 row) |
| `gates/aacap_030_remote_authority_modeled.rq` | remote realization with no envelope, or policy/reachability only, or envelope valid only locally | `witnesses/fail/aacap_030_remote_authority_modeled.ttl` (2 rows: policy-only + local-envelope-only) |
| `gates/aacap_040_discover_never_consequential.rq` | Discover re-typed consequential; observation capability claiming authority | `witnesses/fail/aacap_040_discover_never_consequential.ttl` (1 row) |
| `gates/aacap_050_invoke_requires_evidence.rq` | change/external_do capability without remote receipt/ack evidence requirement | `witnesses/fail/aacap_050_invoke_requires_evidence.ttl` (1 row) |

Every gate has a pass witness (`witnesses/pass/<same stem>.ttl`) proving the
satisfied shape stays silent, and every fail witness fires ONLY its target
gate (observed counts, 2026-09-30). The witness court contract is
`gate-court.toml` (`case_key = "exact-stem"`); runner:
`python3.11 qualification/verify.py`.

## Composition: what is reused vs minted (failed edges)

Composed BY REFERENCE (no duplication, no import):

- `qce:AuthorityEnvelope` + `qce:` properties
  (`packs/qualified-capability-ecology-pack`) — the remote authority
  envelope class, used verbatim.
- `earl:outcome earl:passed` (public EARL) — qualification condition
  outcomes.
- `prov:` / `dcterms:` / `skos:` / `xsd:` (public, first per RESOLUTIONS).
- `sa2a.semantic-evidence-envelope.v1` schema string
  (`packs/sa2a-semantic-evidence-pack`,
  `sa2a:DefaultEvidenceEnvelopeContract`, contractVersion v26.9.29) —
  referenced by `aacap:evidenceEnvelopeSchema`.
- dcap `Workflow.Resume` pinned dotted ID — via
  `aacap:resumeReference` literal.

Failed edges — why existing family vocabulary could NOT express the
capability-contract layer (each justifies the minted `aacap:` terms):

1. `ema:` (`elixir-mcp-a2a-pack`): `ema:Capability` is keyed to ONE
   generating app's `CapabilitySurface` (`capabilityOf`, `exposedVia`
   mcp/a2a/both). It cannot express a capability as cross-peer semantic
   identity with realization plurality, remote-end authority validity, or
   typed remote failure sets (no outcome model at all). Failed edge for
   `aacap:Capability` / `aacap:Realization` / `aacap:outcome`.
2. `s2b:` (`sa2a-bridge-pack`): `s2b:EdgeSpec` binds edge→portOp of ONE
   bridge contract (autofde-lab BEAM port, source SHA pinned in-file). It
   cannot express capability→realization qualification or peer refusal as a
   typed outcome. Failed edge for `aacap:qualificationCondition` /
   `aacap:Outcome`.
3. `sa2a:` (`sa2a-semantic-evidence-pack`): contract-level facts only (one
   `EvidenceEnvelopeContract` individual); there is no capability layer to
   attach per-capability evidence requirements to, and its classes are
   bare (`sa2a:ContractClass` without class definitions). Failed edge for
   `aacap:EvidenceRequirement` / `aacap:requiresEvidence` (the schema
   string is still referenced, not duplicated).
4. `qce:` (`qualified-capability-ecology-pack`): `qce:CapabilityVersion`
   models the version lifecycle of ONE capability identity
   (candidate→qualified→frozen→retired); the capability→realization axis
   across providers with per-realization qualification conditions is a
   different multiplicity. Failed edge for `aacap:Realization` +
   `aacap:QualificationCondition` (envelope class still reused verbatim).
5. `dcp:` (`domain-capability-pack`): `dcp:worldBinding`/`sourceFile` are
   `rdfs:domain dcp:Capability` — reusing them on realizations would
   violate the declared domains; also `dcp:consequence` is a world-local
   READ|DO pair, not the fail-closed observe/change/external_do calculus.
   Failed edge for `aacap:providerSourceFile` / `aacap:consequenceClass`.

## Verification (commands + exits, 2026-09-30)

```text
python3.11 packs/capability-ecology-pack/qualification/verify.py   # exit 0, ADMITTED
python3.11 scripts/marketplace.py check capability-ecology-pack (a2a family)    # exit 0 (turtle=ok qualify=ok, real ggen)
python3.11 -m pytest tests/test_a2a_capability_pack.py         # 4 passed, exit 0
```

Gate silence on the bare ontology (the graph real ggen qualifies) was
observed directly: all five gates return zero rows.
