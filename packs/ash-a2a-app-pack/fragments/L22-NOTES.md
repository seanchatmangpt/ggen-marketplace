# L22 notes: authority gate and lease duration

Standing: UNVERIFIED

## Files

- ontology.d/L22-authority.ttl (aap:authorityGate, aap:leaseDurationMs)
- templates/L22_authority.ex.tmpl -> lib/<app_path>/<resource_file>_l22.ex,
  module `<ResourceModule>.L22Authority` (Spark fragment, `extensions: [AshA2A]`)
- gates/L22_010_lease_duration_missing.rq, gates/L22_020_authority_gate_vocabulary.rq
- fixtures/L22-authority.ttl (legal), fixtures/L22-authority-refusing.ttl (refusing)

## DSL evidence (/Users/sac/ash_a2a/lib)

- ash_a2a/dsl.ex:228-251 authority section; gate :232-241; lease_duration_ms :242-249 (pos_integer)
- ash_a2a/dsl.ex:90-98 skill `lease_required?`
- ash_a2a/info.ex:196-198 lease_duration_ms/1; transformers/build_capability_index.ex:66,76
- ash_a2a/verify.ex:181-205 inert warnings: non-default lease_duration_ms and gate :open warn
  "declared but not enforced" (no lease issuer reads it). The emitted value is therefore
  declarative; the gate guarantees only that it is a valid positive integer.

## Seam (coordinator)

Add `L22Authority` to the resource `fragments: [...]` list for resources emitting the file
(the query only matches resources with authorityGate or leaseDurationMs). The `authority`
section is top-level in the AshA2A extension, not nested in `a2a`.

## Query variables

resources(module_name app_path resource_file gate lease_ms); gate L22_010 (resource skill);
gate L22_020 (resource gate skill).

## Known gaps

- L22_010 requires typed xsd:integer; plain-string "60000" is refused by design.
- Skills on `aap:skill` only; domain-level authority not modeled. Tera `default` on optional
  columns and `?d > 0` over typed literals are unverified against ggen's engine.
- Not duplicated: L07_030 (policy coverage of lease-required skills).
