# beam4pm-contracts-pack

Beam4PM data-contract vocabulary + renderers: model contract/message shapes as
admitted individuals; generate real, compiling Erlang and Elixir type and
struct definitions, codecs, JSON Schema, required-field-validating constructors,
and Chicago-style (no mocks) unit tests. **One pack, two disjoint family
modules.**

## Supersession (v0.2.0, 2026-10-01 consolidation wave)

Absorbed and RETIRED:

| retired pack | what moved where |
|---|---|
| `beam4pm-ai-contracts-pack` (v0.1.1) | ontology verbatim as `ontology/ai.ttl` (`aic:`); 9 `beam4pm_ai_contracts_*.tmpl` renderers verbatim; consumer fixture as `qualification/consumer/ai.ttl` |
| `beam4pm-mcp-contracts-pack` (v0.1.0) | ontology verbatim as `ontology/mcp.ttl` (`mcp:`); 9 `beam4pm_mcp_contracts_*.tmpl` renderers verbatim; consumer fixture as `qualification/consumer/mcp.ttl` |

Nothing semantic was rewritten in either vocabulary — namespaces, terms and
renderer bodies are byte-identical to their sources.

## Template dedup measurement (the consolidation's falsifier)

All 9 cross-family renderer pairs were similarity-measured on the exact
subjects (`difflib.SequenceMatcher` over full file text):

| pair | ratio | ruling |
|---|---|---|
| `_codec.erl.tmpl` | 0.953 | keep separate — surface-equal but load-bearing lines diverge: aic joins `aic:FieldType`/`isAtomCodec` for the codec decision; mcp uses `COALESCE(wireName, fieldName)` + hardcoded `field_type == "atom"` |
| `_codec.ex.tmpl` | 0.911 | keep separate |
| `_tests.erl.tmpl` | 0.809 | keep separate |
| `.erl.tmpl` | 0.797 | keep separate |
| `_test.exs.tmpl` | 0.801 | keep separate |
| `.ex.tmpl` | 0.789 | keep separate |
| `_codec_test.exs.tmpl` | 0.690 | keep separate |
| `_schema.json.tmpl` | 0.647 | keep separate |
| `_codec_tests.erl.tmpl` | 0.558 | keep separate |

Pairs merged: 0. Pairs kept as family variants inside the one pack: 9 (18
templates). The reduction is at the admission-unit level (2 packs → 1, one
version, one court), not at renderer-body level — no renderer semantics were
mutated to force a merge.

## Gates

Family-prefixed exact-stem ladder, all violation-row SELECTs with ORDER BY:

- `ai_010_required.rq` / `mcp_010_required.rq` — required-field completeness per class.
- `ai_020_field_type_enum.rq` / `mcp_020_field_type_enum.rq` — field-type closed-set check. **ai's anti-join form is THE single archetype**: both anti-join against `ontology/ai.ttl`'s `aic:FieldType` vocabulary. mcp's predecessor hardcoded `STR NOT IN ("string", ...)` — retired. A 9th field type now admits at exactly one site.
- `mcp_030_field_order_unique.rq` — no duplicate `fieldOrder` among sibling fields (mcp-only; its wire-format field order is contract-visible).

Witnesses (`witnesses/pass|fail/*.ttl`) are synthesized from both packs'
consumer fixtures; `qualification/verify.py` is the ONE uniform court
(pass silent, fail fires; exit 0 = ADMITTED).

## What stays out of scope

Data shapes only — no execution authority, admission, or actuation semantics;
those remain the exclusive responsibility of `beam4pm-post-llm-runtime-pack`'s
`rt:` vocabulary. The Erlang and Elixir target vocabularies stay disjoint
renderer families (`.erl.tmpl` / `.ex.tmpl` per module).
