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

## Consumer Contract

npm deps (`[consumer_contract]` in pack.toml, derived mechanically from the bare
non-relative imports in `templates/*.tmpl`): runtime `ai @ai-sdk/gateway
@ai-sdk/react @neondatabase/serverless @noble/hashes @opentelemetry/api
@vercel/otel better-auth class-variance-authority clsx drizzle-orm lucide-react
next react sonner tailwind-merge ws zod`; dev tooling `typescript vitest
@playwright/test drizzle-kit`. The projected `package.json` pins exact versions
for this set plus `@types/*`; install from it after sync.

The projected code refuses at boundaries rather than guessing: `DATABASE_URL`
and `BETTER_AUTH_URL`/`BETTER_AUTH_SECRET` are consumer-supplied runtime facts
(DatabaseConfigurationRefusedError / auth-boundary error without them).
`@/lib/utils`, `@/lib/db`, `@/lib/auth`, `@/lib/ai/*`, `@/components/*` are
projected by this pack itself, not npm packages.

`nai:aiSdkVersion` must be a real published `ai@7.x` version (e.g. `7.0.163`);
the court witnessed `ai@7.1.2` (a plausible but unpublished version) fail npm
resolution with `notarget`. The projected `@ai-sdk/react` pin requires
`react@^19.2.1`; set `nai:reactVersion` accordingly.

## Verification Court

Scratch consumer `/tmp/g01-consumer` (ggen 26.11.3; consumer ontology with 1
Application, 2 Models, 1 Agent, 2 Tools — one read, one mutate requiring
approval; deps installed from the projected package.json). Full command + exit
log: `docs/jira/v26.11.5/receipts/G01.md`.

- `ggen sync run --skip-ea-admission` -> exit 0, full Next.js app projected
  (package.json, tsconfig.json, lib/, app/, components/, scripts/, tests/,
  drizzle/); second run reports `"written": []` (fixed point).
- strict `tsc --noEmit` (typescript 5.9) over the projected app -> exit 0.
- Anti-vacuity flip: remove a projected helper, re-run tsc -> expected TS2307;
  restore.
