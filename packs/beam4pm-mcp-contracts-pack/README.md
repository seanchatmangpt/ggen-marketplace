# beam4pm-mcp-contracts-pack

## What this pack generates

This pack projects an admitted `mcp:MessageType` graph into typed Erlang
records, Elixir structs, JSON Schema, and constructors with required-field
validation for each of the ten canonical MCP (Model Context Protocol)
wire-message data shapes:

- `rpc_request`
- `rpc_result_response`
- `rpc_error_response`
- `rpc_notification`
- `mcp_tool`
- `mcp_tool_call_request`
- `mcp_tool_call_result`
- `mcp_resource`
- `mcp_resource_read_request`
- `mcp_resource_read_result`

This follows the exact pattern already established by
`beam4pm-process-model-pack`'s `bpm:RecordType` and
`beam4pm-ai-contracts-pack`'s `aic:ContractType`: typed record/struct
definitions, validating constructors returning `{ok, _} | {error,
{missing_field, atom()}}`, and Chicago-style (no mocks) unit tests, generated
from admitted RDF individuals rather than hand-written. (The template
projections themselves — Erlang/Elixir types, codecs, JSON Schema, tests —
are a separate manufacturing stream against this same vocabulary; this pack
ships the vocabulary and its two admission gates.)

**Real spec, not invented.** Every message shape and field name in this pack
was transcribed verbatim from the real MCP specification, fetched and read
directly:

**<https://modelcontextprotocol.io/specification/2025-06-18/>**

**Manufactured, not hand-written.** Modeling these ten wire-message shapes as
ggen-admitted O* individuals and generating real Erlang/Elixir/JSON-Schema
projections compresses what would otherwise be a hand-written codec/type
authoring effort to minutes — the same "minutes not weeks" compression
already proven for `beam4pm-ai-contracts-pack` (data-shape slice) and
`beam4pm-post-llm-runtime-pack` (authority/BRCE slice) in the post-LLM
capability roadmap. MCP/A2A interoperability was the remaining named,
uncovered slice; this pack covers its wire-message data-shape half.

**Scope boundary (deliberate).** This pack models wire-message data shapes
only — field names, types, documentation, and required/optional status. It
carries **no** tool-execution, transport, session, or capability-negotiation
semantics of any kind.

## Disclosed simplifications

The vocabulary's closed 8-value `fieldType` enum (`string`, `integer`,
`float`, `boolean`, `datetime`, `atom`, `list_string`, `map`) has no "array
of typed objects" member. Two real spec shapes need one, and both are
handled the same way `beam4pm-ai-contracts-pack` disclosed `tool_intent`'s
"no execution authority" simplification — stated plainly here, not silently
narrowed:

- **JSON-RPC `id` is real-spec `string | number`.** This vocabulary models
  it as a single `"string"` field. A numeric id is expected to be
  stringified by the caller before constructing a message. This is a real,
  bounded compression: it costs the ability to preserve an id's original
  JSON numeric-vs-string type across a round trip, which no message shape in
  this pack otherwise depends on.
- **`tools/call` result `content`** (an array of typed content blocks, each
  discriminated by a `type` tag: `text` / `image` / `audio` /
  `resource_link` / `resource` / ...) **and `resources/read` result
  `contents`** (an array of `{uri, mimeType?, text?}` or `{uri, mimeType?,
  blob?}` items — a single `resources/read` call can return multiple content
  items) are each modeled as **one `"map"` field wrapping the real array
  under a single key** (e.g. `{"blocks": [...]}` for `mcp_tool_call_result`,
  `{"contents": [...]}` for `mcp_resource_read_result`). This is a real,
  bounded scope limit, not a defect: the wrapped array's own elements are
  not independently field-validated by this pack. A future revision could
  model content-block types as their own `mcp:MessageType` if a real
  consumer needs field-level validation on them.
- **`rpc_notification` has no `id` field at all**, by the real spec's own
  rule (a notification is exactly the message shape that omits `id`) — this
  is a modeling fact carried faithfully, not a simplification.

## Vocabulary

Namespace: `https://ggen.dev/ontology/beam4pm-mcp#` (prefix `mcp:`). Mirrors
`beam4pm-ai-contracts-pack`'s `aic:ContractType`/`aic:Field` pattern (itself
mirroring `beam4pm-process-model-pack`'s `bpm:RecordType`/`bpm:Field`)
exactly, under a sibling name for a sibling domain.

| Term | Domain | Range | Meaning |
|------|--------|-------|---------|
| `mcp:MessageType` | — (class) | — | One admitted MCP wire-message data shape. |
| `mcp:Field` | — (class) | — | One typed, ordered field of an `mcp:MessageType`. |
| `mcp:messageName` | `MessageType` | `xsd:string` | Canonical snake_case name (e.g. `rpc_request`). |
| `mcp:messageDoc` | `MessageType` | `xsd:string` | Human-readable description of the message type. |
| `mcp:hasField` | `MessageType` | `mcp:Field` | Links a message type to one of its fields. |
| `mcp:fieldName` | `Field` | `xsd:string` | The field's snake_case name. |
| `mcp:fieldType` | `Field` | `xsd:string` | Closed 8-value enum: `string`, `integer`, `float`, `boolean`, `datetime`, `atom`, `list_string`, `map`. |
| `mcp:fieldDoc` | `Field` | `xsd:string` | Human-readable field description. |
| `mcp:fieldRequired` | `Field` | `xsd:string` | Plain string literal `"true"` or `"false"` (templates compare it as a string, not `xsd:boolean`). |
| `mcp:fieldOrder` | `Field` | `xsd:integer` | Bare-integer field position (never `^^xsd:integer`-suffixed in instance data). |

This file (`ontology.ttl`) contains **zero individuals** — per this
marketplace's established pack contract, packs ship vocabulary (and
templates) only. Consumer projects (e.g. beam4pm) supply the admitted
`mcp:MessageType` instance data in their own `ontology.ttl`.

## The ten message shapes and their fields

| `messageName` | Fields (`fieldType`) | Required |
|---|---|---|
| `rpc_request` | jsonrpc:string, id:string, method:string, params:map | jsonrpc, id, method |
| `rpc_result_response` | jsonrpc:string, id:string, result:map | jsonrpc, id, result |
| `rpc_error_response` | jsonrpc:string, id:string, error_code:integer, error_message:string, error_data:map | jsonrpc, id, error_code, error_message |
| `rpc_notification` | jsonrpc:string, method:string, params:map | jsonrpc, method (no `id` field at all) |
| `mcp_tool` | name:string, title:string, description:string, input_schema:map, output_schema:map | name, description, input_schema |
| `mcp_tool_call_request` | name:string, arguments:map | name |
| `mcp_tool_call_result` | content:map, is_error:boolean, structured_content:map | content |
| `mcp_resource` | uri:string, name:string, title:string, description:string, mime_type:string, size:integer | uri, name |
| `mcp_resource_read_request` | uri:string | uri |
| `mcp_resource_read_result` | contents:map | contents |

## Gates

Two fail-closed SPARQL admission gates run automatically against the
post-materialization union graph on every `ggen sync run` once this pack is
declared in a consumer's `ggen.toml` `[packs]` table — no explicit
`[law].gates` wiring is needed; ggen-engine discovers and evaluates any
pack's `gates/*.rq` files itself (`crates/ggen-engine/src/sync.rs`):

- **`gates/010_required.rq`** — every admitted `mcp:MessageType` must carry
  `messageName`/`messageDoc`/`hasField`; every `mcp:Field` must carry
  `fieldName`/`fieldType`/`fieldDoc`/`fieldRequired`/`fieldOrder`. Any
  missing property on any admitted subject is a refusal row.
- **`gates/020_field_type_enum.rq`** — every `mcp:Field`'s `fieldType` must
  be one of the closed 8-value enum. Any other value is a refusal row.

A violation of either gate refuses the sync outright with a typed
`[FM-PACK-013]` error naming the offending gate, subject, and missing/invalid
value — verified live (see below), not merely asserted.

## Composing this pack into a consumer

```toml
# ggen.toml (frontmatter schema — the same shape beam4pm's own ggen.toml uses)
[project]
name = "your-project"

[ontology]
source = "ontology.ttl"

[packs]
beam4pm-mcp-contracts = { path = "vendor/ggen-marketplace/packs/beam4pm-mcp-contracts-pack" }
# ... plus any other packs your project already declares, e.g.:
# beam4pm-ai-contracts = { path = "vendor/ggen-marketplace/packs/beam4pm-ai-contracts-pack" }
# beam4pm-process-model = { path = "vendor/ggen-marketplace/packs/beam4pm-process-model-pack" }

[templates]
dir = "templates"
```

Then declare `mcp:MessageType`/`mcp:Field` individuals for the ten canonical
MCP message shapes (or any consumer-specific extension) in your own
`ontology.ttl`, following the field table above, and run `ggen sync run`.

## Verification (real, not asserted)

Verified with a real scratch consumer (`ggen 26.8.18`) whose `ontology.ttl`
was beam4pm's actual, unmodified `ontology.ttl` plus a hand-written
`rpc_notification` smoke-test fragment (3 fields: `jsonrpc`:string,
`method`:string, `params`:map), with only this pack declared under
`[packs]`. Because a real `ggen sync run` refuses outright with `[FM-PACK-005]`
against a pack shipping zero templates, the scratch consumer's own copy of
this pack (not this pack's shipped copy) carried one trivial static
`templates/marker.txt.tmpl` for verification purposes only, so the run could
reach gate evaluation — the same convention `ggen`'s own test suite uses
(`crates/ggen-engine/tests/framework_packs_e2e.rs`) to test a pack's gates in
isolation from its template-count requirement.

1. **Baseline (valid data) — PASS.** `ggen sync run` exited 0 and the sync
   receipt's `closure` explicitly lists both `gates/010_required.rq` and
   `gates/020_field_type_enum.rq` by content hash — proving both gate files
   are syntactically valid SPARQL that ggen actually parsed and executed
   against the real union graph, not merely present on disk.
   `graph_hash_hex`: `13ec9c74268b895170b550c845e8b599286e5555180cb4422c1d5331f295bfd4`.

2. **Falsifier 1 (gate 010) — REFUSED.** Removed `mcp:fieldDoc` from the
   `rpc_notification`'s `params` field. Real command output:

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-mcp-contracts` gate `010_required.rq` refused
   the sync against the union graph: every admitted mcp:MessageType and
   mcp:Field must contain the fields required by its class; any row is a
   refusal.: SELECT returned 1 row(s); first row: { ?missing =
   https://ggen.dev/ontology/beam4pm-mcp#fieldDoc, ?subject =
   https://ggen.dev/projects/beam4pm#rpc_notification_params_f }.
   ```

   Exit code 1.

3. **Falsifier 2 (gate 020) — REFUSED.** Reverted falsifier 1, then set
   `mcp:fieldType "banana"` on the same field. Real command output:

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-mcp-contracts` gate `020_field_type_enum.rq`
   refused the sync against the union graph: every mcp:Field's mcp:fieldType
   must be one of the 8 admitted enum values; any row is a refusal.: SELECT
   returned 1 row(s); first row: { ?subject =
   https://ggen.dev/projects/beam4pm#rpc_notification_params_f, ?value =
   banana }.
   ```

   Exit code 1.

4. **Re-baseline — PASS.** Reverted falsifier 2 back to valid data; `ggen
   sync run` exited 0 again with the identical `graph_hash_hex` as step 1
   (`13ec9c74268b895170b550c845e8b599286e5555180cb4422c1d5331f295bfd4`),
   confirming both gates are deterministic and the pack is not left in a
   broken state by the falsifier runs.

## See also

- `beam4pm-ai-contracts-pack` — the sibling pack this one's vocabulary/gate
  pattern is mirrored from (`aic:ContractType`/`aic:Field`), itself mirroring
  `beam4pm-process-model-pack`'s `bpm:RecordType`/`bpm:Field`.
- `beam4pm-post-llm-runtime-pack` — the separately-owned `rt:` vocabulary for
  execution authority, admission, and receipts; this pack's message shapes
  deliberately carry no field from that domain.
- <https://modelcontextprotocol.io/specification/2025-06-18/> — the real MCP
  specification this pack's vocabulary was verified against.
