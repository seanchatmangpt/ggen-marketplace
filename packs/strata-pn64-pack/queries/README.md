# strata-pn64-pack — query surface and lowering

How the ontology rows in `../ontology.ttl` lower to the Rust PRE/POST
tables in `../templates/pn64_masks.rs.tera`, and what each query in this
directory extracts.

## Pipeline

```
ontology.ttl  --(queries/*.rq)-->  SPARQL result rows  --(templates/pn64_masks.rs.tera)-->  generated/pn64_masks.rs
```

`ggen.toml` binds one rule (`pn64-masks`) = `queries/transitions.rq` +
`templates/pn64_masks.rs.tera` -> `generated/pn64_masks.rs`. Run with
`ggen sync run` from the pack root. The generated file is a projection;
never patch it by hand — change `ontology.ttl` and regenerate.

## Row -> Rust lowering

`transitions.rq` yields one row per `pn:Transition` individual with a RONR
opcode (1-25; DAO transitions, opcodes 112-151, are excluded by the query's
opcode bound) with
bindings `?opcode ?pre ?post ?label` (ordered by opcode). The template
iterates `results` and lowers each row as:

| ontology binding | Rust artifact | encoding |
|---|---|---|
| `?pre` (xsd:integer place mask, e.g. `129`) | `PRE_MASKS[opcode - 1]` | `u16` literal (decimal, e.g. `129`) — bits [15:0] of the u64 word's `W-` field |
| `?post` | `POST_MASKS[opcode - 1]` | `u16` literal — bits [47:32] field `W+` |
| `?opcode` | array index (`opcode - 1`) and trailing comment | decimal `1`-`25` |
| `?label` | trailing line comment | prose only |

The template additionally emits the ABI constants and semantics that the
mask tables presuppose (they come from the ontology's vocabulary rows,
not from the query result): `MASK16 = 0xFFFF`, `enabled(m, pre) =
(m & pre) == pre`, `fire(m, pre, post) = ((m ^ pre) | post) & 0xFFFF`,
`TERMINALS` (exact-membership exemptions for the deliberately terminal
markings `0x0101` = adopted, `0x0401` = postponed indef), and
`TRANSITIONS` as `(pre, post)` pairs for the structural-invariant courts.
Row order in `transitions.rq` (`ORDER BY ?opcode`) is what makes the
array-index lowering sound; the template's empty-results branch renders
a `// REFUSED: empty ontology projection` comment instead of a table.

## Queries

- `transitions.rq` — one row per canonical transition; drives the
  `pn64-masks` generation rule.
- `places.rq` — all `pn:Place` individuals + `pn:bitOffset`, LSB-first.
  Lowers the marking-bit vocabulary (RONR noun space) that the mask
  literals are unions of.
- `dao_verbs.rq` — `DaoVerb` individuals + `pn:value`, ordered by value.
  Human/wire verb names for the seven verbs (values 1, 2, 3, 11, 116,
  144, 148).
- `deadlock_candidates.rq` — structural siphon PRE-FILTER as a query.
  Exact semantics, the arithmetic (hex-string) bit test, and its known
  imprecision are documented in the query header. Expected hits on the
  canonical six: opcodes `0x05` and `0x06` (the deliberately terminal
  states); hits are exempted from the deadlock gate via `TERMINALS`, not
  silent. Mask/opcode well-formedness is enforced upstream by
  `../gates/020_transition_pre_nonzero.rq` (fail-closed non-integer
  datatype arms over the xsd:integer literals, rebased 2026-10-13);
  this query's bit arithmetic assumes genuine integer literals and
  under-fires silently without it (rdflib treats filter type errors
  as false).

## Validation status

Queries are executed against `ontology.ttl` with rdflib 7.6.0
(`rdflib` SPARQL 1.1); see the wave receipt for actual output. ggen 26.10.11
exposes no standalone query runner — query execution reaches ggen only
through `ggen sync run`'s extract stage, which also renders templates
into `generated/` and is therefore run by the coordinator, not this lane.
