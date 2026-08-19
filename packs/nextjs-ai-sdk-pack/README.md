# nextjs-ai-sdk-pack

Projects an admitted Next.js AI application into canonical source paths. The consumer ontology owns model, agent, tool, approval, and version facts. SPARQL gates refuse incomplete cardinality, invalid references, duplicate identifiers, malformed constraints, and mutation without approval.

The pack does not own deployment credentials or external registry availability. Those are admitted at runtime and evidenced by the consumer verification workflow.

## Auth strategies

`nai:authStrategy` admits three values: `"none"`, `"better-auth"` (email/password via Better
Auth's own adapter), and `"keycloak"` (Better Auth's built-in `keycloak()` genericOAuth
provider, OIDC against an existing realm). Selecting `"keycloak"` additionally requires
`nai:keycloakIssuer` on the same `nai:Application` (gate `035_keycloak_requires_issuer.rq`
refuses otherwise) — the realm issuer URL is always a consumer-supplied fact, never a literal
baked into this pack's templates. Client ID/secret are supplied at runtime via
`KEYCLOAK_CLIENT_ID`/`KEYCLOAK_CLIENT_SECRET` env vars, matching Better Auth's own convention
for every other credential this pack projects (`BETTER_AUTH_SECRET`, `AI_GATEWAY_API_KEY`, …).
