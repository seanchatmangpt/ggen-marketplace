# beam4pm-mcp-contracts-pack

## What this pack generates

This pack projects an admitted `mcp:MessageType` graph into typed Erlang
records, Elixir structs, a codec (`to_map`/`from_map`/`encode`/`decode`),
JSON Schema, and constructors with required-field validation for each of
the ten canonical MCP (Model Context Protocol) wire-message data shapes:

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
from admitted RDF individuals rather than hand-written.

**Shipped: the complete pack — vocabulary, gates, AND templates.** This pack
ships the `mcp:` vocabulary, its three admission gates, and 9 real Tera
templates — one Erlang types module + tests, one Erlang codec module +
tests, one Elixir types module + tests, one Elixir codec module + tests, and
one JSON Schema document — covering all 10 admitted message types. Only the
ten `mcp:MessageType`/`mcp:Field` *instance* individuals themselves are
consumer-supplied (in the consuming project's own `ontology.ttl`), the same
division every sibling `beam4pm-*-contracts-pack` uses. Manufactured codec
paths use the OTP 27+ built-in `json` module (Erlang) and Elixir 1.18+
built-in `JSON` module (Elixir), mirroring `beam4pm-ai-contracts-pack`'s own
codec convention.

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
of typed objects" member, and two real spec fields have a wire-format JSON
key that differs from this vocabulary's own snake_case naming convention.
Both classes are handled the same way `beam4pm-ai-contracts-pack` disclosed
`tool_intent`'s "no execution authority" simplification — stated plainly
here, not silently narrowed:

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
- **`rpc_error_response`'s `error` is ONE nested object**
  (`{"code": ..., "message": ..., "data": ...}`), per JSON-RPC 2.0 and the
  MCP schema's own `JSONRPCError` definition (verified directly against the
  real schema: `required: ["code", "message"]` on the nested object,
  `required: ["error", "id", "jsonrpc"]` on the envelope). This vocabulary
  models it the same "wrap the whole object as one map field" way as
  `content`/`contents` above: a single `error`:`map` field, not three
  flattened `error_code`/`error_message`/`error_data` fields. Flattening
  would be a real, wire-breaking divergence — no real MCP peer sends or
  understands top-level `error_code`/`error_message` keys — so this pack
  models `error` as one field, not three.
- **Five fields have a real MCP wire-format JSON key that differs from this
  vocabulary's own snake_case `mcp:fieldName`** (the Erlang atom / Elixir
  struct field identifier): `inputSchema`, `outputSchema`, `isError`,
  `structuredContent`, `mimeType`. The OPTIONAL `mcp:wireName` property
  (falls back to `mcp:fieldName` when absent) carries the real wire spelling
  for exactly those five fields — see "Vocabulary" below. Every generated
  codec and the JSON Schema template emit/read `COALESCE(wireName,
  fieldName)` as the actual JSON key, while `mcp:fieldName` alone remains
  the Erlang atom / Elixir struct identifier. Renaming these fields to their
  snake_case `fieldName` on the wire (the pre-fix behavior) would have been
  a real, undisclosed wire-breaking divergence.
- **`mcp_tool.description` is OPTIONAL**, matching the real MCP `Tool`
  schema's own `required` array (`["inputSchema", "name"]` — verified
  directly against the schema; `description` is not in it), not required as
  an earlier revision of this pack modeled it.
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
| `mcp:fieldName` | `Field` | `xsd:string` | The field's snake_case name (the Erlang atom / Elixir struct identifier — never changes on the wire). |
| `mcp:fieldType` | `Field` | `xsd:string` | Closed 8-value enum: `string`, `integer`, `float`, `boolean`, `datetime`, `atom`, `list_string`, `map`. |
| `mcp:fieldDoc` | `Field` | `xsd:string` | Human-readable field description. |
| `mcp:fieldRequired` | `Field` | `xsd:string` | Plain string literal `"true"` or `"false"` (templates tolerate a bareword `true`/`false` too, not just the quoted string). |
| `mcp:fieldOrder` | `Field` | `xsd:integer` | Bare-integer field position (never `^^xsd:integer`-suffixed in instance data). Must be unique among a message type's own fields — enforced by `gates/030_field_order_unique.rq`. |
| `mcp:wireName` | `Field` | `xsd:string` | OPTIONAL. The field's real MCP wire-format JSON key, when it differs from `mcp:fieldName` (e.g. camelCase `inputSchema` vs. this vocabulary's snake_case `field_name` `input_schema`). Every codec/JSON-Schema template selects `COALESCE(wireName, fieldName)` for the JSON key; `mcp:fieldName` alone remains the Erlang/Elixir identifier. Set explicitly only on the five fields with a real camelCase wire spelling. |

This file (`ontology.ttl`) contains **zero individuals** — per this
marketplace's established pack contract, a pack's *instance data* is
supplied by the consuming project's own `ontology.ttl`. Consumer projects
(e.g. beam4pm) supply the admitted `mcp:MessageType` instance data built
from this vocabulary; this pack itself still ships real templates (see
above), only the ten concrete message-type/field individuals are
consumer-owned.

## The ten message shapes and their fields

`wire` is shown only for the five fields whose real MCP JSON key differs
from `fieldName` (via `mcp:wireName`); every other field's wire key equals
its `fieldName`.

| `messageName` | Fields (`fieldType`[, wire key]) | Required |
|---|---|---|
| `rpc_request` | jsonrpc:string, id:string, method:string, params:map | jsonrpc, id, method |
| `rpc_result_response` | jsonrpc:string, id:string, result:map | jsonrpc, id, result |
| `rpc_error_response` | jsonrpc:string, id:string, error:map | jsonrpc, id, error |
| `rpc_notification` | jsonrpc:string, method:string, params:map | jsonrpc, method (no `id` field at all) |
| `mcp_tool` | name:string, title:string, description:string, input_schema:map[`inputSchema`], output_schema:map[`outputSchema`] | name, input_schema |
| `mcp_tool_call_request` | name:string, arguments:map | name |
| `mcp_tool_call_result` | content:map, is_error:boolean[`isError`], structured_content:map[`structuredContent`] | content |
| `mcp_resource` | uri:string, name:string, title:string, description:string, mime_type:string[`mimeType`], size:integer | uri, name |
| `mcp_resource_read_request` | uri:string | uri |
| `mcp_resource_read_result` | contents:map | contents |

`rpc_error_response`'s `error` field wraps the real spec's nested
`{code, message, data?}` object as one opaque map (see "Disclosed
simplifications"). `mcp_tool.description` is optional, matching the real
MCP `Tool` schema's own `required: ["inputSchema", "name"]`.

## Gates

Three fail-closed SPARQL admission gates run automatically against the
post-materialization union graph on every `ggen sync run` once this pack is
declared in a consumer's `ggen.toml` `[packs]` table — no explicit
`[law].gates` wiring is needed; ggen-engine discovers and evaluates any
pack's `gates/*.rq` files itself (`crates/ggen-engine/src/sync.rs`):

- **`gates/010_required.rq`** — every admitted `mcp:MessageType` must carry
  `messageName`/`messageDoc`/`hasField`; every `mcp:Field` must carry
  `fieldName`/`fieldType`/`fieldDoc`/`fieldRequired`/`fieldOrder`. Any
  missing property on any admitted subject is a refusal row. (`mcp:wireName`
  is intentionally NOT in this list — it is OPTIONAL by design.)
- **`gates/020_field_type_enum.rq`** — every `mcp:Field`'s `fieldType` must
  be one of the closed 8-value enum. Any other value is a refusal row.
- **`gates/030_field_order_unique.rq`** — no two `mcp:Field` siblings of the
  same `mcp:MessageType` may share an identical `mcp:fieldOrder` value (a
  real `GROUP BY`/`HAVING COUNT>1` tie-break check). Any duplicate is a
  refusal row.

A violation of any gate refuses the sync outright with a typed
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
This pack's own 9 templates run automatically once it is declared under
`[packs]` — a consumer needs no template of its own for this pack's output
(an empty `[templates].dir` is enough), exactly as verified below.

## Verification (real, not asserted)

Verified with a real scratch consumer (`ggen 26.8.18`, matching this
ecosystem's pinned version) whose `ontology.ttl` is a hand-written, complete
set of all ten `mcp:MessageType`/`mcp:Field` individuals (post-fix field
shapes: `rpc_error_response` with one wrapped `error` field, `mcp_tool` with
`description` optional, and `mcp:wireName` set on the five affected fields),
with only this pack declared under `[packs]` and the consumer's own
`[templates].dir` left genuinely empty — every generated file below comes
from this pack's own real, shipped templates directly. No synthetic stub
template was needed (an earlier revision's `[FM-PACK-005]`-workaround
narrative no longer applies now that the pack ships templates).

1. **Baseline (valid data) — PASS.** `ggen sync run` exited 0, generated all
   9 files (`src/beam4pm_mcp_contracts.erl`, `src/..._codec.erl`,
   `test/..._tests.erl`, `test/..._codec_tests.erl`,
   `lib/beam4pm_mcp_contracts.ex`, `lib/..._codec.ex`, `test/..._test.exs`,
   `test/..._codec_test.exs`, `schema/beam4pm_mcp_contracts.schema.json`),
   and the sync receipt's `closure` explicitly lists all three gate files by
   content hash — proving all three gates are syntactically valid SPARQL
   that ggen actually parsed and executed against the real union graph, not
   merely present on disk. `graph_hash_hex`:
   `d072718c4cfaea94857239f9e9130c416820aa074f3024726992c31d6904609f`.

2. **`erlc -Werror` (via `rebar3 eunit`, which compiles with
   `warnings_as_errors`) — CLEAN, all pass.**

   ```
   ===> Compiling mcp_contracts_verify
   ===> Performing EUnit tests...
   .....................................................
   Finished in 0.183 seconds
   53 tests, 0 failures
   ```

3. **`mix compile --warnings-as-errors` — CLEAN.**

   ```
   Compiling 2 files (.erl)
   Compiling 2 files (.ex)
   Generated mcp_contracts_verify app
   ```

4. **`mix test` — all pass.**

   ```
   Running ExUnit with seed: 285280, max_cases: 32
   .............................................................
   Finished in 0.1 seconds (0.1s async, 0.00s sync)
   61 tests, 0 failures
   ```

5. **JSON Schema — validates.** `python3` with
   `jsonschema.Draft7Validator.check_schema` against all 10 generated
   definitions:

   ```
   OK: mcp_resource
   OK: mcp_resource_read_request
   OK: mcp_resource_read_result
   OK: mcp_tool
   OK: mcp_tool_call_request
   OK: mcp_tool_call_result
   OK: rpc_error_response
   OK: rpc_notification
   OK: rpc_request
   OK: rpc_result_response
   ALL 10 definitions are valid Draft7 schemas
   ```

   A real sample payload per message type (the same ten payloads from step 6
   below) was additionally validated with `Draft7Validator(defn).iter_errors`
   against its own generated definition — all 10 `PASS`, zero errors,
   confirming `mcp_tool`'s real payload (no `description`, camelCase
   `inputSchema`) and `rpc_error_response`'s real payload (nested `error`
   object) both satisfy the schema this pack itself generated for them.

6. **Wire-format round trip — the decisive proof.** A real script
   constructed one full JSON payload per message type using the REAL
   camelCase wire keys (e.g. `inputSchema`, `isError`, `mimeType`, a nested
   `error` object) and fed each into the generated Erlang and Elixir
   `decode`/`from_map` functions, then `encode`d the result back to JSON and
   compared it to the original by parsed-map equality (key order is not
   significant in JSON). All 10 message types round-tripped identically in
   **both** languages, including `mcp_tool_call_result`'s `isError: false`
   surviving the round trip (proving the `false`-vs-absent/`undefined`
   disambiguation actually works) and `mcp_tool`'s payload correctly having
   no `description` key at all (proving the optional-field fix). Real
   output (Erlang; Elixir's output is byte-for-byte the same shape):

   ```
   PASS rpc_request                    decode/encode round-trip semantically identical
        in:  {"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"x"}}
        out: {"id":"1","jsonrpc":"2.0","method":"tools/call","params":{"name":"x"}}
   PASS rpc_error_response             decode/encode round-trip semantically identical
        in:  {"jsonrpc":"2.0","id":"1","error":{"code":-32601,"message":"Method not found"}}
        out: {"error":{"code":-32601,"message":"Method not found"},"id":"1","jsonrpc":"2.0"}
   PASS mcp_tool                       decode/encode round-trip semantically identical
        in:  {"name":"get_weather","inputSchema":{"type":"object"}}
        out: {"inputSchema":{"type":"object"},"name":"get_weather"}
   PASS mcp_tool_call_result           decode/encode round-trip semantically identical
        in:  {"content":{"blocks":[{"type":"text","text":"sunny"}]},"isError":false}
        out: {"content":{"blocks":[{"text":"sunny","type":"text"}]},"isError":false}
   PASS mcp_resource                   decode/encode round-trip semantically identical
        in:  {"uri":"file:///a.txt","name":"a.txt","mimeType":"text/plain"}
        out: {"mimeType":"text/plain","name":"a.txt","uri":"file:///a.txt"}
   [... all 10 message types PASS in both Erlang and Elixir ...]

   ALL 10 ERLANG WIRE ROUND-TRIPS PASSED
   ALL 10 ELIXIR WIRE ROUND-TRIPS PASSED
   ```

7. **Falsifier 1 (gate 010) — REFUSED.** Removed `mcp:fieldDoc` from the
   `rpc_notification`'s `params` field. Real command output:

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-mcp-contracts` gate `010_required.rq` refused
   the sync against the union graph: every admitted mcp:MessageType and
   mcp:Field must contain the fields required by its class; any row is a
   refusal.: SELECT returned 1 row(s); first row: { ?missing =
   https://ggen.dev/ontology/beam4pm-mcp#fieldDoc, ?subject =
   https://ggen.dev/projects/mcp-verify#rpc_notification_params_f }.
   ```

   Exit code 1.

8. **Falsifier 2 (gate 020) — REFUSED.** Reverted falsifier 1, then set
   `mcp:fieldType "banana"` on the same field. Real command output:

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-mcp-contracts` gate `020_field_type_enum.rq`
   refused the sync against the union graph: every mcp:Field's mcp:fieldType
   must be one of the 8 admitted enum values; any row is a refusal.: SELECT
   returned 1 row(s); first row: { ?subject =
   https://ggen.dev/projects/mcp-verify#rpc_notification_params_f, ?value =
   banana }.
   ```

   Exit code 1.

9. **Falsifier 3 (gate 030, new) — REFUSED.** Reverted falsifier 2, then set
   `rpc_notification`'s `params` field to the same `mcp:fieldOrder` (`2`) as
   its sibling `method` field. Real command output:

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-mcp-contracts` gate `030_field_order_unique.rq`
   refused the sync against the union graph: no two mcp:Field siblings of the
   same mcp:MessageType may share an identical mcp:fieldOrder value; any
   duplicate is a refusal.: SELECT returned 1 row(s); first row: { ?count = 2,
   ?field_order = 2, ?message_type =
   https://ggen.dev/projects/mcp-verify#rpc_notification }.
   ```

   Exit code 1.

10. **Re-baseline — PASS.** Reverted falsifier 3 back to valid data; `ggen
    sync run` exited 0 again with the identical `graph_hash_hex` as step 1
    (`d072718c4cfaea94857239f9e9130c416820aa074f3024726992c31d6904609f`),
    confirming all three gates are deterministic and the pack is not left in
    a broken state by the falsifier runs. `rebar3 eunit` (53 tests) and
    `mix test` (61 tests) were re-run against this re-baselined output and
    both still passed with 0 failures.

## See also

- `beam4pm-ai-contracts-pack` — the sibling pack this one's vocabulary/gate
  pattern is mirrored from (`aic:ContractType`/`aic:Field`), itself mirroring
  `beam4pm-process-model-pack`'s `bpm:RecordType`/`bpm:Field`.
- `beam4pm-post-llm-runtime-pack` — the separately-owned `rt:` vocabulary for
  execution authority, admission, and receipts; this pack's message shapes
  deliberately carry no field from that domain.
- <https://modelcontextprotocol.io/specification/2025-06-18/> — the real MCP
  specification this pack's vocabulary was verified against.
