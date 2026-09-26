# Interchangeable Parts Qualification

The pack is now a three-layer contract:

1. **UNRDF owns executable semantics.** `@unrdf/core` manufactures and
   evaluates PartRequirement/PartPassport. `@unrdf/receipts` owns
   substitution receipts and replay verification.
2. **This pack owns semantic admission and generation metadata.** SHACL/SPARQL
   refuse consequence drift, mutable replacement subjects, unqualified
   receipts and DO-authority laundering.
3. **ggen generates thin consumer adapters and their court.** The adapter
   delegates every decision to UNRDF and binds the expected canonical schema
   identities from `ipq:policyV1`.

```
ontology + policyV1
        |
        v
ggen query/template
        |
        +--> generated/unrdf-consumer-adapter.mjs
        |
        +--> generated/unrdf-consumer-adapter.test.mjs
                       |
                       v
                 @unrdf/core
                 @unrdf/receipts
```

This topology makes future consumers add generated adapters rather than copy
the substitution algorithm. Adapter results are SELECT/CONSTRUCT evidence and
always expose `authority: none`, `grantsDoAuthority: false`. A valid
substitution receipt proves qualification; it does not itself grant DO.
