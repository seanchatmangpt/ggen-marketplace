# v26.9.30 Capability Ecology Wave — Pinned Resolutions

Cross-lane seams resolved BEFORE dispatch. Lanes code against these, not against each other.

## Namespaces

| prefix | IRI | owner lane |
|---|---|---|
| `qce:` | `https://ggen.dev/ontology/qualified-capability-ecology#` | existing pack (read-only reuse) |
| `fscap:` | `https://ggen.dev/ontology/filesystem-capability#` | 2 |
| `ncap:` | `https://ggen.dev/ontology/network-capability#` | 2 |
| `dcp:` | `https://ggen.dev/ontology/domain-capability#` (align to existing `packs/domain-capability-pack/ontology.ttl`; lane 1 owns any extension) | 1 |
| `pcap:` | `https://ggen.dev/ontology/process-capability#` | 3 |
| `scap:` | `https://ggen.dev/ontology/scheduling-capability#` | 3 |
| `escap:` | `https://ggen.dev/ontology/event-state-capability#` | 4 |
| `ocap:` | `https://ggen.dev/ontology/observation-capability#` | 4 |
| `dcap:` | `https://ggen.dev/ontology/durability-capability#` | 5 |
| `aacap:` | `https://ggen.dev/ontology/a2a-capability#` | 6 |
| `authcap:` | `https://ggen.dev/ontology/authority-capability#` | 7 |
| `ecap:` | `https://ggen.dev/ontology/evidence-capability#` | 7 |
| `wfc:` | `https://ggen.dev/ontology/workflow-corpus#` | 8 (defines; 9/10 use) |

Public vocabularies before custom: `prov:`, `earl:`, `dcterms:`, `skos:`, `xsd:`.
Standing individuals: `https://w3id.org/chatman/aps#` (ALIVE / PARTIAL_ALIVE / UNKNOWN /
UNSUPPORTED / BLOCKED / REFUSED_*). Custom terms are legal only with a recorded failed edge
against the public set.

## Pinned capability IDs (dotted short names via `rdfs:label`; corpus references them as
`dcterms:identifier` literals — the join happens in the consumer resolver, not in-tree)

- fscap: `File.Read` `File.Write` `File.Copy` `File.Move` `File.Delete` `File.Exists`
  `Dir.List` `Dir.Mkdir` `Dir.Remove`
- ncap: `Http.Request` `Http.Get` `Http.Post` `Remote.Invoke` `Endpoint.Resolve`
- dcp: `Domain.Action.Invoke` `Domain.Query.Read` `Domain.Change.Apply`
- pcap: `Process.Spawn` `Process.Supervise` `Process.Signal` `Process.Link`
- escap: `Event.Emit` `Event.Subscribe` `State.Observe` `State.Query`
- scap: `Schedule.At` `Schedule.Cron` `Schedule.Delay`
- dcap: `Durability.Checkpoint` `Durability.Replay` `Durability.Resume`
  `Workflow.Halt` `Workflow.Resume`
- ocap: `Observation.Tap` `Observation.Sample` `Telemetry.Emit`
- aacap: `A2A.Invoke` `A2A.Discover` `A2A.Await`
- authcap: `Authority.Verify` `Authority.Grant` `Actuation.Execute`
- ecap: `Evidence.Establish` `Evidence.Bind` `Receipt.Sign` `Provenance.Record`

Lanes may mint family siblings freely inside their own namespace (recording them in README);
no lane mints IDs in another family's namespace.

## Realization metadata (provider facts — cite, never fabricate local inspection)

Real packages/repos that may appear as `qce:`-aligned realizations: `reactor_file`
(Reactor.File.*), `reactor_req` (Reactor.Req.*), `reactor_process` (Reactor.Process.*),
`ash` (Ash.Reactor steps), `ash_a2a`, `ash_affidavit`, `ash_graphlaw`, `ash_r2rml`,
`ash_ex4pm`, `xaas`. Local read-only checkouts exist at `~/ash_a2a`, `~/ash_affidavit`,
`~/ash_graphlaw`, `~/ash_r2rml`, `~/ash_ex4pm`, `~/xaas`, `~/ash_pplan` (READ-ONLY — Claude
owns its writes). `reactor_*` have no local checkout: cite hex coordinates as provider
metadata, never claim local inspection.

## `wfc:` corpus schema (lane 8 defines exactly this; lanes 9/10 emit conforming individuals)

```
wfc:WorkflowFixture a rdfs:Class, prov:Entity .       # one per fixture directory
wfc:ExpectedDecomposition a rdfs:Class, prov:Entity .
wfc:ExpectedOutcome a rdfs:Class, prov:Entity .
wfc:ProviderClosure a rdfs:Class, prov:Entity .
wfc:Falsifier a rdfs:Class, prov:Entity .
wfc:fixtureNumber   a rdf:Property ; rdfs:range xsd:integer .
wfc:goal            a rdf:Property ; rdfs:range xsd:string .
wfc:task            a rdf:Property .                  # -> task individual (prov:Activity typed)
wfc:capability      a rdf:Property ; rdfs:range xsd:string .   # pinned dotted ID literal
wfc:expectedDecomposition a rdf:Property .
wfc:expectedOutcome        a rdf:Property .
wfc:requiredEvidence       a rdf:Property ; rdfs:range xsd:string .
wfc:requiredAuthority      a rdf:Property ; rdfs:range xsd:string .
wfc:expectedProviderClosure a rdf:Property .          # -> wfc:ProviderClosure (realization names)
wfc:forbiddenRealization   a rdf:Property ; rdfs:range xsd:string .
wfc:falsifierStatement     a rdf:Property ; rdfs:range xsd:string .
```

Fixture directory contract: `packs/workflow-corpus-pack/fixtures/<NN>-<slug>/fixture.ttl`
(individuals only, no class definitions, no cross-pack imports) plus `expected.md` rendering
the human-readable expectation. Per-fixture refusal gates live at
`packs/workflow-corpus-pack/gates/f<NN>_<slug>.rq` owned by the same lane that owns the
fixture.

## Verification surface (lane-safe)

- Scaffold: `python3.11 scripts/new_pack.py <name> --profile semantic` (refuses existing dirs).
- Scoped real-ggen qualification: `python3.11 scripts/marketplace.py check <pack-name>`.
- Global (integration, coordinator-owned): `marketplace.py validate`, catalog determinism,
  `fingerprint`, `pytest tests/ scripts/`.
- Cross-lane noise rule: a failure pointing at a pack you do not own is not yours to fix.

## Real-ggen hard constraints (from commit e7ac25a75, ggen 26.9.28 refusals)

`[pack]` admits only name/version/description (FM-PACK-003) · no `shapes.ttl` (FM-PACK-012) ·
`gates/` are refusal SELECTs, data projections go in template frontmatter (FM-PACK-013) ·
multi-row SPARQL needs `ORDER BY` (E0013) · no non-schema `ggen.toml` (FM-CONFIG-102).
