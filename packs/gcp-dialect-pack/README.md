# gcp-dialect-pack

Standing: UNVERIFIED

## GCP Dialect Pin Pack

Class: CapabilityPack. Version 0.1.0.

Ggen pack carrying the GCP dialect pin lattice: 17 pubsub.proto field-number
pins (17 WirePin individuals across PubsubMessage / PublishRequest /
PullRequest / PullResponse / ReceivedMessage / AcknowledgeRequest /
ModifyAckDeadlineRequest / Timestamp), the 5 GCS V4 signing laws (L1-L5) and
the 4 error-envelope/LRO laws (E1-E4) pinned by the TS sibling lane's probes.

Ported from smalt `lib/smalt/data_plane/pubsub_grpc/wire.ex` (lane K-GC
v26.11.6) and `verification/ts/gcp/*.probe.mjs`; every individual carries
`prov:wasDerivedFrom` its source entity.

## Not equivalent to gcp-terraform-pack

This pack is a Pub/Sub wire-law pack (protobuf field numbers, wire types, GCS V4
signing laws, JSON error-envelope laws) for an ingest dialect adapter. It is
NOT equivalent to, a subset of, or a replacement for `gcp-terraform-pack`,
which models GCP infrastructure resources and Terraform provider projection.
The two share only the word "GCP"; neither imports, supersedes, or merges with
the other, and similar names are not equivalence proof.

## Structure

- `ontology.ttl` - the canonical graph (`urn:arcus:` namespace, arcus-pack
  conventions: class/predicate definitions + individuals + prov source
  entities).
- `pack.toml` - pack identity and validation gate list
  (`gates/010_required.rq` ... `gates/040_error_law.rq`).
- `gates/` - four SPARQL gates (pin metadata presence, wire-type closure,
  signing-law closure, envelope-law closure).
- `qualification/consumer.ttl` - consumer binding (pin-data + law-E2), lane
  convention.
- `templates/gcp_wire_laws.go.tmpl` - Go projection of the WirePin lattice,
  signing laws, envelope laws, and enforced-but-unpinned dialect constants.

## Classes

| Class | Carries | Count |
|---|---|---|
| `arcus:WirePin` | `arcus:message` + `arcus:fieldName` + `arcus:fieldNumber` + `arcus:wireType` | 17 |
| `arcus:SigningLaw` | `arcus:lawId` + `arcus:lawStatement` | 5 |
| `arcus:EnvelopeLaw` | `arcus:lawId` + `arcus:lawStatement` | 4 |

## Law

Construction only: a pinned field admits exactly its pinned number and wire
type; an unpinned field is a typed refusal, never nil. Laws are registered
against their probe sources, never silently reconciled. The Go binding of the
pins is `internal/dialect/gcp/` (wire.go constants, signing.go L1-L5,
errors.go E1-E3, lro.go E4).

## Open edges

- The `arcus:DialectPin` rows at the end of `ontology.ttl` use `arcus:symbol`,
  `arcus:version`, and `arcus:src-gcp-dialect-go-consts`; none is defined in
  this pack (declared in the arcus repo's shared graph).
- Companion pack: `arcus-pack` carries the gcp-pubsub dialect and operations
  in the same `urn:arcus:` namespace; no `owl:imports` edge exists.

## See Also

- `packs/arcus-pack/pack.toml` and `packs/arcus-pack/ontology.ttl`
