# gymact-capability-schema-pack

Closes gymact's payload-schema gap. First-class pack, prefix `gcs:
<http://seanchatmangpt.github.io/packs/gymact-capability-schema#>`.

## The gap this closes

gymact's admitted public profile
(`~/gymact/src/gymact/ontology/profile.shacl.ttl`, `<urn:gymact:shape:capability>`)
already represents a capability as a real `sosa:Procedure` with a
`dct:title`/`dct:type` SHACL shape — but that shape describes the capability's
**identity**, not its **payload**. Nothing in gymact's admitted graph today says
what keys a `Consequence.DO` capability's `actuate(capability, payload: dict[str,
Any])` call actually accepts. That information exists only as free text folded
into `Capability.title` (`~/gymact/src/gymact/providers.py`), e.g.:

```python
Capability(
    iri="urn:gymact:memory:capability:increment",
    title=(
        "Increment a numeric value in the bounded memory world. "
        'Payload: {"key": <str>, "amount": <number, default 1>}.'
    ),
    consequence=Consequence.DO,
    binding="increment",
)
```

Readable by a human, not machine-checkable, and not renderable into a typed
model — gymact's own `dspy_agent` live-LM test found this the hard way: an
untitled-schema tool call guessed `{"counter": 1}` instead of the real
`{"key": "counter", "value": 1}` shape (see the comment at
`MEMORY_CAPABILITIES` in `providers.py`).

## How it closes it

**Schema-only, project-agnostic** (same contract as `packs/github-actions-pack`
v0.2.0 and `packs/dspy-pack`). `ontology.ttl` ships **zero**
`gcs:CapabilityPayloadShape` individuals. A consumer (gymact) declares one
`gcs:CapabilityPayloadShape` per `Consequence.DO` capability that wants a typed
payload, in its own instance-data `.ttl`, using real SHACL
`sh:NodeShape`/`sh:PropertyShape` facts against this pack's vocabulary.

Per gymact's own semantic-authority rule (`ProfileAuthority._custom_tbox_terms`
in `~/gymact/src/gymact/semantic.py` — gymact refuses any `urn:gymact:`-prefixed
custom TBox term in a validated graph), this ontology reuses standard vocabulary
rather than inventing a competing TBox:

- A payload shape **is**, structurally, exactly what SHACL's
  `sh:NodeShape`/`sh:PropertyShape` already are — a set of typed,
  cardinality-constrained property constraints. `sh:property`, `sh:path`,
  `sh:datatype`, `sh:minCount`, `sh:maxCount`, `sh:name`, `sh:description`,
  `sh:defaultValue`, and `sh:closed` are reused verbatim, not reinvented under a
  `gcs:` name.
- The capability being constrained is gymact's own `sosa:Procedure`
  (`dct:title`/`dct:type <urn:gymact:consequence:do>`), the exact class
  `<urn:gymact:shape:capability>` already targets.
- `gcs:CapabilityPayloadShape` is declared `rdfs:subClassOf sh:NodeShape,
  prov:Entity` — `prov:Entity` reused from gymact's own
  `<urn:gymact:profile:v26.8.7> a prof:Profile, prov:Entity` pattern in
  `profile.ttl`, since a payload shape is itself a versionable schema artifact.
- `qudt:hasUnit` is documented as an available, real (not invented) optional
  annotation on a numeric `sh:PropertyShape` for a payload field that carries a
  physical quantity — not exercised by this pack's own worked example, since
  gymact's real `MemoryProvider` payloads (`key`/`value`/`amount`) are unitless.

Only **two** new terms are minted, because no standard predicate expresses
either relation:

- `gcs:CapabilityPayloadShape` — the *role* a `sh:NodeShape` plays ("this is a
  capability's payload schema"), distinct from an arbitrary SHACL shape.
- `gcs:payloadShapeOf` — the *link* from that shape to the `sosa:Procedure`
  whose runtime payload it describes. SHACL's four target-declaration
  predicates (`sh:targetClass`/`sh:targetNode`/`sh:targetSubjectsOf`/
  `sh:targetObjectsOf`) all mean "this shape validates properties reached FROM
  this node/class" — the wrong relation here, since a payload shape validates a
  runtime dict passed *alongside* an `actuate()` call, not the `sosa:Procedure`
  resource's own RDF properties.

`templates/capability_payloads.py.tmpl` projects those facts into one
`gymact_capability_payloads.py` module of Pydantic v2 `BaseModel` classes (one
per `gcs:CapabilityPayloadShape`), matching gymact's own stated canonical typed-
model library. `sh:datatype` (an `xsd:` IRI) is mapped to a Python type inside
the template (`xsd:string`→`str`, `xsd:integer`→`int`, `xsd:double`/
`xsd:decimal`/`xsd:float`→`float`, `xsd:boolean`→`bool`, `xsd:dateTime`→
`datetime`, else `Any`) — never a template-hardcoded field type. `sh:minCount
>= 1` renders a required field; otherwise the field is `T | None` with a
default from `sh:defaultValue` (quoted for `xsd:string`/`xsd:anyURI`, bare
otherwise) or `None`.

## Refusals (gate)

`gates/010_required.rq` refuses (namespace-scoped, composes with other packs'
graphs without cross-firing):

1. A `sosa:Procedure` classified `dct:type <urn:gymact:consequence:do>` that is
   not the `gcs:payloadShapeOf` target of any `gcs:CapabilityPayloadShape` — the
   actual gap this pack closes: a DO capability with no declared payload shape
   means its payload is documented only as free text.
2. A `gcs:CapabilityPayloadShape` with zero `sh:property` (an empty, useless
   shape — the template can only ever emit `pass` for it).
3. A `gcs:CapabilityPayloadShape` with no `gcs:payloadShapeOf` (a shape naming
   no capability renders as orphaned dead code no capability ever references).

A `Consequence.READ` capability is **not** required to declare a payload shape
— gymact's own `Environment.observe()`/`checkpoint()` protocol methods for
READ-classified capabilities take no payload argument, so requiring one would
be a false positive. Verified empirically (not assumed): a real
`urn:gymact:memory:capability:observe` individual classified
`consequence:read` with no payload shape synced cleanly, 0 gate rows.

## How a consumer (gymact) wires this in

1. Author your own instance-data `.ttl` declaring `gcs:CapabilityPayloadShape`
   individuals against this pack's `gcs:` vocabulary — one per `Consequence.DO`
   capability you want a typed payload for. Worked example, mirroring gymact's
   real `MemoryProvider.increment` capability
   (`urn:gymact:memory:capability:increment`, payload `{"key": <str>, "amount":
   <number, default 1>}`):

   ```turtle
   @prefix gcs:  <http://seanchatmangpt.github.io/packs/gymact-capability-schema#> .
   @prefix sh:   <http://www.w3.org/ns/shacl#> .
   @prefix sosa: <http://www.w3.org/ns/sosa/> .
   @prefix dct:  <http://purl.org/dc/terms/> .
   @prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

   <urn:gymact:memory:capability:increment>
       a         sosa:Procedure ;
       dct:title "Increment a numeric value in the bounded memory world." ;
       dct:type  <urn:gymact:consequence:do> .

   <urn:gymact:memory:payload-shape:increment>
       a                  gcs:CapabilityPayloadShape ;
       gcs:payloadShapeOf <urn:gymact:memory:capability:increment> ;
       sh:name            "IncrementPayload" ;
       sh:property [
           sh:path        <urn:gymact:memory:payload:key> ;
           sh:name        "key" ;
           sh:datatype    xsd:string ;
           sh:minCount    1 ;
           sh:maxCount    1 ;
           sh:description "Memory-world key to increment."
       ] ;
       sh:property [
           sh:path         <urn:gymact:memory:payload:amount> ;
           sh:name         "amount" ;
           sh:datatype     xsd:double ;
           sh:minCount     0 ;
           sh:maxCount     1 ;
           sh:defaultValue 1 ;
           sh:description  "Amount to add; defaults to 1 when omitted."
       ] .
   ```

2. Add this pack to your own `ggen.toml` `[packs]` table, next to
   `gymact-registry-pack`:

   ```toml
   [packs]
   gymact-registry-pack = { path = "gymact-registry-pack" }
   gymact-capability-schema-pack = { path = "gymact-capability-schema-pack" }
   ```

   (gymact vendors marketplace packs as real relative symlinks into its own
   `ggen/` directory, matching the convention its existing `ggen.toml` already
   uses for `gymact-registry-pack`/`cloud-topology-validation-pack`/etc.)

3. Run `ggen sync run`. This renders `gymact_capability_payloads.py`, one
   Pydantic model per declared `gcs:CapabilityPayloadShape`. Diff the result,
   import it, and instantiate it against a real payload before trusting it —
   see "Verification" below for the exact checks this pack's own isolated
   consumer test ran.

## Not yet built (disclosed scope limit, not hidden)

Every generated field is single-valued regardless of `sh:maxCount > 1` —
list-valued payload fields are not yet projected. `sh:defaultValue` is quoted
for `xsd:string`/`xsd:anyURI` and emitted as a bare literal otherwise (correct
for numeric defaults; not specially cased for `xsd:boolean`, which would need
`True`/`False` capitalization the template does not yet apply). Neither gap is
exercised by gymact's real current capabilities (`MemoryProvider`'s `key`/
`value`/`amount` fields are all single-valued, non-boolean) — named here so a
future consumer with a boolean or repeated payload field knows to extend the
template's `py_type`/`py_default` macros rather than assume coverage.

## Verification

Real, isolated consumer test (outside this repo), `ggen 26.8.8`:

- A `facts.ttl` declaring the real `MemoryProvider.increment` capability plus
  its `gcs:CapabilityPayloadShape` (the worked example above) synced cleanly
  and rendered `gymact_capability_payloads.py` containing a real
  `IncrementPayload(BaseModel)` with `key: str` (required) and `amount: float |
  None = 1` (optional, real default). Confirmed with `ast.parse`,
  `python3 -m py_compile`, and a real `pydantic` 2.12.5 import: instantiation
  with/without `amount`, correct default value, `ValidationError` on a missing
  `key`, and `ValidationError` on an unknown field (`extra="forbid"`).
- A second consumer with a real `Consequence.DO` capability
  (`urn:gymact:memory:capability:delete`) and **no** payload shape was refused
  by `gates/010_required.rq` at `ggen sync run` time
  (`[FM-PACK-013] ... gate '010_required.rq' refused ... first row: { ?missing
  = gcs:payloadShapeOf, ?s = urn:gymact:memory:capability:delete }`).
- A third consumer with a real `Consequence.READ` capability
  (`urn:gymact:memory:capability:observe`) and no payload shape synced cleanly
  — confirms the gate does not false-positive on READ capabilities.
- Idempotency: re-running `ggen sync run` against the first (valid) consumer
  with no ontology change produced `"written": []` / `"skipped": [...]`, not a
  second write.

## Layout

- `pack.toml` — pack identity
- `ontology.ttl` — vocabulary only (`gcs:CapabilityPayloadShape`,
  `gcs:payloadShapeOf`), zero individuals
- `gates/010_required.rq` — the refusal gate above
- `templates/capability_payloads.py.tmpl` — Pydantic v2 module projection

## See Also

- `~/gymact/ggen/gymact-registry-pack/` — the only other existing precedent for
  a ggen pack touching gymact's Python surface; per gymact's own house law
  (`~/gymact/CLAUDE.md`), ggen projects admitted RDF facts into thin,
  declarative wiring here too — never gymact's business/verification logic.
- `packs/github-actions-pack/` — the schema-only rebuild shape and the
  `to:`/`sparql:` frontmatter convention this pack follows.
- `packs/star-toml-pack/` — the single-file, multi-row-aggregation template
  shape (`star_toml_config.rs.tmpl`) `capability_payloads.py.tmpl` mirrors.
