# enterprise-sso-sp-pack Standing

Standing: VERIFIED

- Authored 2026-11-19 (ggen-author / GAP5): closed scaffold stub into real
  SHACL (`shapes.ttl`), vocabulary TTL (`ontology.ttl` v0.2.0: PKCE +
  ClaimMapping), six fail-closed gates with exact-stem witnesses, and four
  frontmatter `.tera` projections. Scaffold individuals in
  `qualification/scaffold.ttl`.
- Fence: zero IdP / token-mint / DO authority. `essp:clientSecretRef` and
  `essp:signingCertRef` are references only — no secrets authored.
- Max PARTIAL_ALIVE / ALIVE for a real tenant still requires a consumer pin
  of non-scaffold bindings (as-authored sync projects empty binding rows
  because `ontology.ttl` carries vocabulary only).

## Coordinator courts (2026-11-19, ggen 26.11.5)

Prior validate lane [Validate SSO pack gates](4dd14af4-222d-4774-9ecd-01acfc3aea61)
plus GAP5 follow-up (frontmatter FM-CONFIG-101 fix + scaffold SHACL).

| Command | EXIT | Notes |
|---|---|---|
| `ggen graph validate --files ontology.ttl --shapes shapes.ttl` | **0** | 137 quads, `shapes_conform: true` |
| scoped `python3.11 scripts/check_gate_witness_courts.py --packs <scratch-only-this-pack>` | **0** | 6 exact-stem cases, court standing ALIVE (prior validate) |
| rdflib SPARQL pass/fail anti-vacuity (6 gates × pass/fail) | **0** | all 12 PASS (prior validate) |
| `ggen sync run --skip-ea-admission` (as-authored, after frontmatter fix) | **0** | wrote then replay-skipped 4 under `generated/sso/` |
| `ggen graph validate --files qualification/scaffold.ttl --shapes shapes.ttl` | **0** | after anyURI + protocolToken scaffold fix |
| `ggen graph validate --files ontology.ttl,qualification/scaffold.ttl --shapes shapes.ttl` | **0** | union also clean |

### Frontmatter fix (SESSION)

As-authored sync was EXIT=1 `[FM-CONFIG-101]`. Dropped from `ggen.toml` for
frontmatter sync: `[project].version`, `[validation]`, `ontology.base_iri`.
Gates remain under `gates/` + `gate-court.toml` (not re-homed into sync
manifest). Version stays in `pack.toml` only.

### Scaffold SHACL (SESSION, closed)

Prior: 7 violations (string vs `xsd:anyURI` on ACS/metadata/discovery/
redirect; per-file `sh:class` on `usesProtocol` without local protocol
individuals). Fixed cheaply in `qualification/scaffold.ttl` (typed URIs +
local `protocolSaml2`/`protocolOidc` with `protocolToken`). Now EXIT=0.

## Lane 07 re-court (2026-11-19, v26.11.19)

Binary `ggen 26.11.5`. validate EXIT=0; scaffold validate EXIT=0; rdflib 6 gates clean + fail-witness FLIP; pack sync EXIT=0.
Standing: **VERIFIED**.
