# beam4pm-ai-contracts-pack

## What this pack generates

This pack projects an admitted `aic:ContractType` graph into typed Erlang
records, Elixir structs, JSON Schema, and constructors with required-field
validation for each of the seven canonical AI-contract data shapes named in
the post-LLM capability architecture roadmap:

- `evidence_envelope`
- `research_task`
- `candidate_claim`
- `tool_intent`
- `admission_decision`
- `model_call_receipt`
- `evidence_hit`

This follows the exact pattern already established by
`beam4pm-process-model-pack`'s `bpm:RecordType`: typed record/struct
definitions, validating constructors returning `{ok, _} | {error,
{missing_field, atom()}}`, and Chicago-style (no mocks) unit tests, generated
from admitted RDF individuals rather than hand-written.

**Manufactured, not hand-written.** The post-LLM roadmap this pack draws from
proposed roughly 45-68 person-weeks of hand-built service code to define these
seven contract shapes plus the surrounding gateway/interoperability/evaluation
machinery. Modeling the data-shape slice as ggen-admitted O* individuals and
generating real Erlang/Elixir/JSON-Schema projections compresses that authoring
cost to minutes, the same way `beam4pm-process-model-pack` already did for
beam4pm's 31 process-mining record types.

**Scope boundary (deliberate).** This pack models data shapes only — field
names, types, documentation, and required/optional status. It carries **no**
execution-authority, admission, or actuation semantics of any kind. In
particular, `tool_intent` intentionally has no capability-grant or
authority field: it is inert data, admissible for planning and receipting
but conferring zero actuation authority on its own. Authority, admission,
replay, and refusal semantics are the exclusive, separately-owned
responsibility of `beam4pm-post-llm-runtime-pack`'s `rt:` vocabulary
(`RuntimeContract`, `ExactSubject`, `hasAuthorityPolicy`, `replayKey`,
`refusalCode`, `refusalReason`, `enablesCapability`) and its
`beam4pm_governor` templates. This pack neither touches nor extends that
pack or vocabulary.

Shipped: the vocabulary and its two admission gates, plus 9 real Tera
templates — one Erlang types module + tests, one Erlang codec module +
tests, one Elixir types module + tests, one Elixir codec module + tests, and
one JSON Schema document — covering all 7 admitted contract types. Manufactured
codec paths use the OTP 27+ built-in `json` module (Erlang) and Elixir 1.18+
built-in `JSON` module (Elixir), mirroring `beam4pm-process-model-pack`'s
established codec convention exactly.

## Vocabulary

Namespace: `https://ggen.dev/ontology/beam4pm-ai#` (prefix `aic:`). Mirrors
`beam4pm-process-model-pack`'s `bpm:RecordType`/`bpm:Field` pattern exactly,
under a sibling name for a sibling domain.

| Term | Domain | Range | Meaning |
|------|--------|-------|---------|
| `aic:ContractType` | — (class) | — | One admitted AI-contract data shape. |
| `aic:Field` | — (class) | — | One typed, ordered field of an `aic:ContractType`. |
| `aic:contractName` | `ContractType` | `xsd:string` | Canonical snake_case name (e.g. `evidence_envelope`). |
| `aic:contractDoc` | `ContractType` | `xsd:string` | Human-readable description of the contract type. |
| `aic:hasField` | `ContractType` | `aic:Field` | Links a contract type to one of its fields. |
| `aic:fieldName` | `Field` | `xsd:string` | The field's snake_case name. |
| `aic:fieldType` | `Field` | `xsd:string` | Closed 8-value enum (`string`, `integer`, `float`, `boolean`, `datetime`, `atom`, `list_string`, `map`), admitted by a matching `aic:FieldType_<name>` individual's `aic:fieldTypeName` -- see the shared field-type vocabulary in this same file. |
| `aic:fieldDoc` | `Field` | `xsd:string` | Human-readable field description. |
| `aic:fieldRequired` | `Field` | `xsd:string` | Plain string literal `"true"` or `"false"` (templates compare it as a string, not `xsd:boolean`). |
| `aic:fieldOrder` | `Field` | `xsd:integer` | Bare-integer field position (never `^^xsd:integer`-suffixed in instance data). |

This file (`ontology.ttl`) contains **zero domain instance data** (no
`aic:ContractType`/`aic:Field` individuals) — per this marketplace's
established pack contract, packs ship vocabulary (and templates) only.
Consumer projects (e.g. beam4pm) supply the admitted `aic:ContractType`
instance data in their own `ontology.ttl`. It does contain a small, fixed
set of `aic:FieldType` vocabulary individuals (see below) -- pack-owned
closed reference data, not consumer-supplied instance data.

## Gates

Two fail-closed SPARQL admission gates run automatically against the
post-materialization union graph on every `ggen sync run` once this pack is
declared in a consumer's `ggen.toml` `[packs]` table — no explicit
`[law].gates` wiring is needed; ggen-engine discovers and evaluates any
pack's `gates/*.rq` files itself (`crates/ggen-engine/src/sync.rs`):

- **`gates/010_required.rq`** — every admitted `aic:ContractType` must carry
  `contractName`/`contractDoc`/`hasField`; every `aic:Field` must carry
  `fieldName`/`fieldType`/`fieldDoc`/`fieldRequired`/`fieldOrder`. Any missing
  property on any admitted subject is a refusal row.
- **`gates/020_field_type_enum.rq`** — every `aic:Field`'s `fieldType` must name
  an admitted `aic:FieldType` individual (anti-join against this file's shared
  vocabulary, not a hardcoded string enum). Any other value is a refusal row.

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
beam4pm-ai-contracts = { path = "vendor/ggen-marketplace/packs/beam4pm-ai-contracts-pack" }
# ... plus any other packs your project already declares, e.g.:
# beam4pm-process-model = { path = "vendor/ggen-marketplace/packs/beam4pm-process-model-pack" }

[templates]
dir = "templates"
```

Then declare `aic:ContractType`/`aic:Field` individuals for the seven
canonical contract shapes (or any consumer-specific extension) in your own
`ontology.ttl`, following the field tables in this roadmap slice's design
notes, and run `ggen sync run`.

## Verification (real, not asserted)

Verified with a real scratch consumer (`ggen 26.8.18`) whose `ontology.ttl`
was beam4pm's actual, unmodified `ontology.ttl` plus a hand-written 2-field
`aic:ContractType` smoke-test fragment (`smoke_test`, fields `id`:string and
`count`:integer), with only this pack declared under `[packs]`.

1. **Baseline (valid data) — PASS.** `ggen sync run` exited 0, wrote
   `docs/AI_CONTRACTS_SCHEMA_ADMITTED.md`, and the sync receipt's `closure`
   explicitly lists both `gates/010_required.rq` and
   `gates/020_field_type_enum.rq` by content hash — proving both gate files
   are syntactically valid SPARQL that ggen actually parsed and executed
   against the real union graph, not merely present on disk.

2. **Falsifier 1 (gate 010) — REFUSED.** Removed `aic:fieldDoc` from the
   `count` field. Real command output:

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-ai-contracts` gate `010_required.rq` refused
   the sync against the union graph: every admitted aic:ContractType and
   aic:Field must contain the fields required by its class; any row is a
   refusal.: SELECT returned 1 row(s); first row: { ?missing =
   https://ggen.dev/ontology/beam4pm-ai#fieldDoc, ?subject =
   https://ggen.dev/ontology/beam4pm-ai#smoke_test_count_f }.
   ```

   Exit code 1.

3. **Falsifier 2 (gate 020) — REFUSED.** Reverted falsifier 1, then set
   `aic:fieldType "banana"` on the same field. Real command output (re-verified
   2026-09-04 against the post-v0.1.1 vocabulary-anti-join gate -- the message
   text changed from the pre-v0.1.1 hardcoded 8-value-enum wording since the
   underlying mechanism changed; the refusal itself did not):

   ```
   ERROR: CLI execution failed: Command execution failed: validation error:
   [FM-PACK-013] pack `beam4pm-ai-contracts` gate `020_field_type_enum.rq`
   refused the sync against the union graph: every aic:Field's aic:fieldType
   must name an admitted aic:FieldType: SELECT
   returned 1 row(s); first row: { ?subject =
   https://ggen.dev/ontology/beam4pm-ai#smoke_test_count_f, ?value = banana }.
   ```

   Exit code 1.

4. **Re-baseline — PASS.** Reverted falsifier 2 back to valid data; `ggen
   sync run` exited 0 again with the identical `graph_hash_hex` as step 1
   (`975ca37283fcb3ab22eb895ad98702bdad8827199a6d88c21306f847d16b1de4`),
   confirming both gates are deterministic and the pack is not left in a
   broken state by the falsifier runs.

## See also

- `beam4pm-process-model-pack` — the sibling pack this one's vocabulary/gate
  pattern is mirrored from (`bpm:RecordType`/`bpm:Field`).
- `beam4pm-post-llm-runtime-pack` — the separately-owned `rt:` vocabulary for
  execution authority, admission, and receipts; this pack's `tool_intent`
  shape deliberately carries no field from that domain.
