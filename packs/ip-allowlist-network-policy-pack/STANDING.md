# ip-allowlist-network-policy-pack Standing

Standing: VERIFIED

Coordinator follow-up 2026-11-19 (ggen 26.11.5, rdflib 7.1.4). GAP7 CIDR
regex fixed: removed invalid `\/` XSD escapes and the extra `)` that put
SPARQL `REGEX` alternation outside the outer group (rdflib
`unbalanced parenthesis`).

## Commands + exits

| Command | cwd / capsule | EXIT |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes/ianp.shacl.ttl` | pack | **0** (`shapes_conform: true`, 208 quads) |
| rdflib clean court: `gates/020_cidr_shape.rq` on `ontology.ttl` | pack | **0** (0 rows) |
| rdflib flip: `ianp:CidrAdminDocs` cidr → `not-a-cidr` ∪ ontology → gate 020 | scratch mut | **0** (1 row `CIDR_LITERAL_INVALID`) |
| `ggen sync run --skip-ea-admission` (scratch consumer + fixture) | prior court | **0** (unchanged; shapes/gate-only delta) |

## Fix (SESSION)

`shapes/ianp.shacl.ttl` `ianp:cidr` `sh:pattern` and `gates/020_cidr_shape.rq`
`REGEX` now use `/` unescaped and keep IPv4|IPv6 alternation inside one
outer group:

`^((octet\.){3}octet/pref4|((hextet:){2,7}hextet/pref6))$`

## Prior residue (not regressing)

GitHub org-level `github_ip_allow_list_entry` remains BLOCKED / disclosed
via gate 050. Sync projection paths and other gates (010/030/040/050)
were already clean in the PARTIAL court.
