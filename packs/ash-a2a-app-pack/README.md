# ash-a2a-app-pack

Standing: UNVERIFIED

Turtle in, Ash + AshA2A application out. You write `aap:` triples; ggen projects the
domain, resources, agent, `mix.exs`, config and an agent-card test.

## Quickstart

```toml
# ggen.toml
[project]
name = "helpdesk"

[ontology]
source = "ontology/app.ttl"

[packs]
ash-a2a-app = { path = "/path/to/ggen-marketplace/packs/ash-a2a-app-pack" }
```

```sh
# ontology/app.ttl declares aap:Project, aap:Domain, aap:Resource, aap:Agent
rm -f ggen.lock                          # required after any pack edit
ggen sync run --skip-ea-admission        # drop the flag once L19 ea.graph.json admits
mix deps.get && mix compile
mix test                                 # generated agent-card test
```

A complete consumer lives in `examples/helpdesk/`.

Minimal shape (legacy core):

```turtle
ex:Desk a aap:Domain ; aap:moduleName "Helpdesk.Desk" ; aap:appPath "helpdesk" ;
  aap:domainFile "desk" .
ex:Ticket a aap:Resource ; aap:moduleName "Helpdesk.Desk.Ticket" ; aap:inDomain ex:Desk ;
  aap:resourceFile "ticket" ; aap:attribute ex:Ticket_id ; aap:action ex:Ticket_read .
```

## Vocabulary map

| Lane | Terms (aap:) | Generated module / file |
|---|---|---|
| core | Project, Domain, Resource, Attribute, Action, Skill, Agent | domain, resource, agent, mix.exs, config |
| L01 | AttributeSpec, attrSpec, EnumType, EnumValue | `<Res>.L01Attributes`, enum module |
| L02 | Relationship, RelManage, relationship, manage | `<Res>.Relationships` |
| L03 | Calculation, CalculationArgument | `<Res>` l03 fragment, calc module |
| L04 | Aggregate, AggregateJoinFilter | l04 fragment |
| L05 | Identity, Validation | `<Res>.L05` |
| L06 | L06Action, L06Argument, L06Step, L06Hook, L06Run | l06 fragment, hook, run |
| L07 | Policy, PolicyGroup, PolicyCheck, FieldPolicy | l07 fragment |
| L08 | Multitenancy, Mount, TenantTaskStore | l08 fragment, domain mounts, task store |
| L09 | Repo, CustomIndex, Reference, CheckConstraint, Statement | repo, l09 fragment, config |
| L10 | CodeInterface, CalculationInterface, Mount | l10 interface, domain config |
| L11 | PubSub, Publication, PubSubServer, Notifier, A2ABridge, Delegate | l11 fragment, notifier |
| L12 | CustomType, TypeField, UnionMember, TypedAttribute | types/, l12 fragment |
| L13 | StateMachine, State, Transition | l13 fragment |
| L14 | ObanTrigger, ObanSchedule, ObanChunks, ObanQueue, ObanConfig | l14 fragment, worker, config |
| L15 | Reactor, ReactorInput, ReactorStep, ReactorAction | reactors/, fragment |
| L16 | PPlanWorkflow, PPlanTask, PPlanProvider, PPlanControlPlane | pplan/ modules |
| L17 | SkillSpec, HookRef, DispatchHook, SecurityScheme, Endpoint | a2a fragments, endpoint, config |
| L18 | SparkExtension, SparkSection, SparkEntity, SparkField | extension, info, verify, docs |
| L19 | eaDeclare | `ea.graph.json` |
| L20 | CourtCase, PolicyCase, TransitionCase, ReactorCase, PlanCase, ShimCourt | `test/courts/`, `scripts/shim_court/` |

## Gates catalog

`gates/*.rq` are SELECT refusals: any returned row blocks the sync.

- Shared: `010` resource has a primary key, `020` skill targets a declared action,
  `030` consequence in observe|change|external_do|unknown.
- Per lane `Lnn_*.rq`: vocabulary, name collision, dangling references, wellformedness
  (for example L01 attribute kinds, L02 dangling destination, L13 unreachable states,
  L20 duplicate moduleName and generated-path collision).

## Limitations

- Every lane standing is UNVERIFIED: authored without a shell. Nothing here has been
  rendered or compiled by the authoring lanes.
- The shared `resource.ex.tmpl` emits no `fragments:` option. L01-L18 fragment modules
  are generated but a resource does not include them until the coordinator wires
  `fragments: [...]` (see `fragments/Lnn-NOTES.md`). Only the legacy terms are
  live in the resource body today.
- Several gates read only the legacy `aap:action` / `aap:attribute` edges and so
  reject resources that declare those facts through lane edges
  (list: `fragments/ERRC-E2-gates.md`).
- `ea.graph.json` admission (FM-LAW-015) is unproven; use `--skip-ea-admission`.
- `ggen.lock` content-hashes the whole pack; delete it after pack edits.
- Free-text values (description, message) are interpolated unescaped: no double quotes.
- No courts exist for L03/L04/L08 vocabulary yet.

## See Also

`examples/helpdesk/README.md` · `LANES.md` · `fragments/ERRC-C3-pack.md`
