# repository-reconstitution-pack v26.9.28

This pack turns an admitted repository contract into a deterministic
reconstitution manifest.

```text
repository observation
→ bounded observable contract
→ rr:ReconstitutionSpec
→ exact capability-owner graph
→ ggen projection
→ independent verification
→ receipt/replay
```

It deliberately manufactures **authority and intent**, not arbitrary
handwritten replacement code. Runtime/source generation is delegated to the
specific packs and canonical owners selected by the manifest.

## Hard boundaries

- observation is not admission;
- generated output is not semantic authority;
- SELECT is not CONSTRUCT and CONSTRUCT is not DO;
- exactly one declared owner may carry consequential-DO authority;
- trust/integrity is not authorization;
- Release Admission and Sunset Admission are separate;
- unknown outcomes cannot be promoted to success;
- candidate/unmerged owners cannot widen released standing.

## Files

- `ontology.ttl` — reusable vocabulary plus reference ggen-legacy v26.9.28 spec.
- `templates/reconstitution-manifest.json.tmpl` — deterministic projection.
- `gates/spec.rq` — single admitted reconstitution subject.
- `gates/owners.rq` — ordered exact capability-owner rows.
- `qualification/invalid-two-do-owners.ttl` — negative-control fixture.

The reference projection is intentionally smaller than a complete repository.
It is the portable semantic control surface from which specialized packs may
manufacture implementation.
