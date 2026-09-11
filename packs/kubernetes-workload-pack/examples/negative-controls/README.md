# negative-controls

Deliberately invalid fact graphs, split honestly into two categories --
per the standing no-overclaiming discipline, a "negative control" that
isn't actually refused by anything is a gap, not a control, and is named
as such rather than staged to look enforced. Each subdirectory is a
self-contained `ggen.toml` + `facts.ttl` project (same pattern as
`../minimal-secure-workload/`), so every claim below is directly runnable.

## Verified refusals (gate 010, real)

| Directory | Missing fact | `ggen sync run --dry-run` result |
|---|---|---|
| `missing-resources/` | `k8s:resourceRequestsBlock` / `k8s:resourceLimitsBlock` | REFUSED |
| `missing-security-context/` | `k8s:podSecurityContextBlock` | REFUSED |

```
cd examples/negative-controls/missing-resources && ggen sync run --dry-run
cd ../missing-security-context && ggen sync run --dry-run
```

Both were re-verified in this session against the real `ggen` binary; the
refusal message cites the exact missing property and subject IRI (see
`gates/010_required.rq`'s `FM-PACK-013` output).

## Known gaps (not yet enforced -- candidate v0.2.0+ gates)

| Directory | Violation | Why gate 010 can't catch it today |
|---|---|---|
| `privileged-container-KNOWN_GAP/` | `privileged: true`, `allowPrivilegeEscalation: true` | `*SecurityContextBlock` is a raw YAML string (ontology.ttl's deliberate escape-hatch design); gate 010 checks property *presence*, never content. |
| `mutable-image-tag-KNOWN_GAP/` | `image: "example/app:latest"` | `k8s:image` is untyped `xsd:string`; no gate inspects its value. |

```
cd examples/negative-controls/privileged-container-KNOWN_GAP && ggen sync run --dry-run
cd ../mutable-image-tag-KNOWN_GAP && ggen sync run --dry-run
```

Both were re-verified in this session: real `ggen` **admits** them
unchanged today (`k8s/privileged-demo.yaml`, `k8s/mutable-image-demo.yaml`
written under dry-run planning) -- confirming the gap is real, not merely
theorized.

These two directories are the honest record of Phase 5's instruction:
"Where an important control lacks a gate, that is a candidate pack defect
to fix." See `../control-mapping/control-map.md`'s `SEC-PRIV-001` and
`SEC-IMG-001` rows, and `../../playground/scenarios/` for the same
fixtures in the mutate-one-property experimentation loop.
