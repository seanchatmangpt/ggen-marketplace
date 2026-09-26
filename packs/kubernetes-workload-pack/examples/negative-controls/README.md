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

## Verified refusals (gate 020, real, since v0.2.0)

| Directory | Violation | Refusal row |
|---|---|---|
| `privileged-container/` (was `privileged-container-KNOWN_GAP/`) | `privileged: true`, `allowPrivilegeEscalation: true`, no exception | `PRIVILEGE_UNWAIVED` |
| `privileged-incomplete-exception/` | `privileged: true` with an exception missing `k8s:approvedBy` | `EXCEPTION_INCOMPLETE` + `PRIVILEGE_UNWAIVED` |
| `obfuscated-privilege-key/` | `"privil\x65ged": true` (YAML escape decodes to the key) | `SECURITY_BLOCK_OBFUSCATION` |
| `scalar-newline-injection/` | clean blocks, but `k8s:containerName` carries a line break that would splice a `securityContext` key | `SCALAR_LINE_BREAK` |

The lawful counterpart is `../privileged-typed-exception/`: the same
`privileged: true`, admitted because that container binds a complete
`k8s:SecurityException` for `SEC-PRIV-001`.

Gate 020 verdicts were evaluated against every fixture on three SPARQL
engines -- Oxigraph (pyoxigraph), rdflib, and ggen_igniter's Rustler NIF
over the Rust oxigraph engine -- with identical results; the matrix and a
13-spelling privilege sweep are pinned in
`tests/test_kubernetes_privilege_gate.py`. **Not yet re-run through the
`ggen` binary itself** (its pinned release asset was unreachable from the
session that built this gate); `ggen sync run --dry-run` in each directory
is the remaining confirmation.

```
cd examples/negative-controls/missing-resources && ggen sync run --dry-run
cd ../missing-security-context && ggen sync run --dry-run
```

Both were re-verified in this session against the real `ggen` binary; the
refusal message cites the exact missing property and subject IRI (see
`gates/010_required.rq`'s `FM-PACK-013` output).

## Known gaps (not yet enforced -- candidate v0.3.0+ gates)

| Directory | Violation | Why gate 010 can't catch it today |
|---|---|---|
| `mutable-image-tag-KNOWN_GAP/` | `image: "example/app:latest"` | `k8s:image` is untyped `xsd:string`; no gate inspects its value. |

```
cd examples/negative-controls/mutable-image-tag-KNOWN_GAP && ggen sync run --dry-run
```

Re-verified when documented: real `ggen` **admits** it unchanged
(`k8s/mutable-image-demo.yaml` written under dry-run planning) --
confirming the gap is real, not merely theorized. (The privileged fixture
was admitted the same way under v0.1.0; gate 020 now refuses it, above.)

This directory is the honest record of Phase 5's instruction:
"Where an important control lacks a gate, that is a candidate pack defect
to fix." See `../control-mapping/control-map.md`'s `SEC-IMG-001` row, and `../../playground/scenarios/` for the same
fixtures in the mutate-one-property experimentation loop.
