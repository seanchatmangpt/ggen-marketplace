# enterprise-sso-sp-pack

SAML 2.0 / OIDC **relying-party** ontology, SHACL shapes, refusal gates, and
templates for **Semantic Jira product SSO** (customer IdP → SJ product as SP/RP).

Covers metadata, ACS, PKCE (RFC 7636), and group claims → product roles.

## Boundary

| This pack | Not this pack |
|---|---|
| SJ product **Service Provider** / **Relying Party** | Smalt **IdP** faces (`smalt:face-saml-idp`, queued `smalt:face-oidc-idp`) |
| External customer IdPs (`essp:ExternalIdentityProvider`) | Token mint / STS / IdP metadata publication |
| Federation inventory + SP metadata + OIDC RP + claim map | Runtime SSO handlers / DO authority |

Smalt identity-plane IdP lives in `smalt-substrate-pack`. Wiring a Smalt IdP
face into `essp:trustsIdp` is refused by `gates/040_no_smalt_idp_face.rq`
and the matching SHACL SPARQL constraint.

## Identity

- Namespace: `https://seanchatmangpt.github.io/packs/enterprise-sso-sp#` (`essp:`)
- Capability URNs: `urn:ggen:pack:enterprise-sso-sp-pack`, `urn:ggen:capability:saml-sp`, `urn:ggen:capability:oidc-rp`, `urn:ggen:capability:sso-claim-map`
- Core classes: `essp:ProductServiceProvider`, `essp:ExternalIdentityProvider`, `essp:FederationBinding`, `essp:ClaimMapping`, `essp:ClaimRule`
- Closed role: `essp:roleSp` only
- SHACL: `shapes.ttl` (imported by `ggen.toml`)

## Gates (fail-closed)

| Gate | Refuses |
|---|---|
| `gates/010_sp_role_closed.rq` | `ProductServiceProvider` without `essp:spRole essp:roleSp` |
| `gates/020_saml_sp_required.rq` | saml2 binding missing entityId/ACS, IdP metadata, or nameIdFormat |
| `gates/030_oidc_rp_required.rq` | oidc binding missing discovery, clientId, redirectUri, or secret ref |
| `gates/040_no_smalt_idp_face.rq` | federation that trusts a Smalt IdP face / `urn:smalt:identity:*` |
| `gates/050_oidc_pkce_required.rq` | oidc binding without `essp:pkceRequired true` |
| `gates/060_claim_mapping_required.rq` | binding without a complete `ClaimMapping` / `ClaimRule` |

Witness pairs under `witnesses/pass|fail/` share exact stems with each gate
(`gate-court.toml`, exact-stem court).

## Templates

Frontmatter `.tera` (Rule A — no `[[generation.rules]]`):

| Template | Output |
|---|---|
| `templates/federation_inventory.md.tera` | `generated/sso/federation_inventory.md` |
| `templates/saml_sp_metadata.xml.tera` | `generated/sso/saml_sp_metadata.xml` |
| `templates/oidc_rp_config.toml.tera` | `generated/sso/oidc_rp_config.toml` |
| `templates/claim_role_map.toml.tera` | `generated/sso/claim_role_map.toml` |

Projections emit admitted graph facts only. They do not mint tokens, store
plaintext secrets, or claim IdP behavior.

## Consumer shape

1. Declare one `essp:ProductServiceProvider` with `essp:spRole essp:roleSp`.
2. Declare customer `essp:ExternalIdentityProvider` individuals (not Smalt faces).
3. Declare `essp:ClaimMapping` + `essp:ClaimRule` rows (group/attribute → product role).
4. Add per-tenant `essp:FederationBinding` rows with `essp:protocolSaml2` and/or `essp:protocolOidc`, required protocol fields, `essp:claimMapping`, and (for oidc) `essp:pkceRequired true`.
5. Optional local rehearsal: import `qualification/scaffold.ttl`.
6. Coordinator runs gate-court + `ggen sync run` (author lane does not sync).

## Standing

See `STANDING.md`. Authored closed (SHACL/TTL/templates); born **UNVERIFIED**
until coordinator court + sync receipt. ALIVE needs real tenant bindings
(not scaffold).
