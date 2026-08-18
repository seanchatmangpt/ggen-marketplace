# supabase-pack

Projects the standard Supabase client/config wiring for any Node.js project (Next.js, Nuxt,
Expo/React Native, or a plain Node backend) from admitted RDF facts about a Supabase project,
its client runtimes, its tables, and its auth providers.

## Grounding

This pack's shape is grounded in real usage mined from local projects using
`@supabase/supabase-js` 2.38-2.108, not invented from generic docs. Two findings shaped the
defaults:

- **Client pattern.** The dominant real pattern is a single-instance `createClient()` call in
  a small singleton module. `@supabase/ssr` appeared only as a transitive lockfile entry in a
  few projects and never as real imported source; `@supabase/auth-helpers-nextjs` had zero
  real usage. The pack therefore defaults `sb:Client.package` to `"@supabase/supabase-js"` and
  generates a plain singleton client. The `@supabase/ssr` cookie-based dual client/server split
  (Next.js App Router SSR auth) is available opt-in per `sb:Client` by setting
  `sb:package = "@supabase/ssr"` alongside `sb:runtime = "browser"` or `"server"` — it is not
  baked in as the default because it was not the observed default.
- **Env var names.** Node/backend projects overwhelmingly use bare `SUPABASE_URL` /
  `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY`. Expo/React Native projects use the
  `EXPO_PUBLIC_` prefix (required by Expo's public-env convention). A smaller share of Next.js
  projects use `NEXT_PUBLIC_`. The pack projects the prefix from an explicit
  `sb:Project.envPrefix` fact rather than assuming one framework's convention.
- **RLS discipline.** Every real migration sampled follows
  `ALTER TABLE ... ENABLE ROW LEVEL SECURITY` immediately with one or more `CREATE POLICY`
  statements keyed on `auth.uid()` or `auth.role() = 'service_role'`. Gate
  `030_rls_requires_policy.rq` refuses any `sb:Table` with `hasRLS = true` and no declared
  `sb:Policy`.

## Framework-agnostic by design

This pack is framework-agnostic: the base output (`lib/supabase/client.ts` with a plain
`createSupabaseClient` call, `.env.example`, `supabase/config.toml`, RLS migration) works for
any Node.js project. The only Next.js-App-Router-specific output — the `@supabase/ssr`
cookie-based client/server split, and the `next/headers` import in `lib/supabase/server.ts` —
is opt-in via `sb:Client.package = "@supabase/ssr"` on a per-client basis, never baked into the
default templates.

## Ontology

- **`sb:Project`** — `projectRef` (20-char lowercase alphanumeric), `projectId` (CLI
  `project_id`), `region`, `envPrefix` (`""`, `"EXPO_PUBLIC_"`, or `"NEXT_PUBLIC_"`),
  `apiPort`/`dbPort` (local CLI ports).
- **`sb:Client`** — `runtime` (`"browser"` | `"server"` | `"edge"`), `package`
  (`"@supabase/supabase-js"` | `"@supabase/ssr"`), `usesServiceRole` (bool).
- **`sb:Table`** — `tableName`, `hasRLS` (bool), `schema` (defaults to `public`), `hasPolicy`
  → `sb:Policy`.
- **`sb:Policy`** — `policyName`, `policyCommand` (`SELECT`/`INSERT`/`UPDATE`/`DELETE`/`ALL`),
  `policyUsing`, `policyWithCheck`.
- **`sb:AuthProvider`** — `providerKind` (`"email"` | `"oauth-google"` | `"oauth-github"` |
  `"oauth-apple"` | ...), `providerEnabled` (bool).

## Templates

- `templates/010_client_ts.tmpl` → `lib/supabase/client.ts`
- `templates/020_server_ts.tmpl` → `lib/supabase/server.ts` (service-role-aware; only emitted
  when a `sb:Client` with `runtime = "server"` is admitted)
- `templates/030_env_example.tmpl` → `.env.example` (real env var names per `envPrefix`)
- `templates/040_config_toml.tmpl` → `supabase/config.toml`
- `templates/050_migration_sql.tmpl` → `supabase/migrations/00000000000000_supabase_pack_rls.sql`

## Gates

- `010_required.rq` — required-field cardinality per class.
- `020_client_runtime_enum.rq` — `sb:Client.runtime`/`package` must be in the admitted enum.
- `030_rls_requires_policy.rq` — `hasRLS = true` requires at least one `sb:Policy`.
- `040_project_ref_shape.rq` — `sb:Project.projectRef` must match a real Supabase ref shape.

Verification practice: run `ggen sync run --dry-run` twice; the second run must report zero
pending writes.

## Self-hosted Supabase (out of scope, noted for future extension)

A self-hosted Supabase stack (Postgres + GoTrue + PostgREST + Realtime + Storage + Studio via
`docker-compose`) is a standard Docker Compose project, so it runs on any generic Docker host
(including colima) the same way any other Compose stack does. This pack generates only the
client-side integration code for consuming a Supabase project, hosted or self-hosted — it does
not generate the `docker-compose.yml` for the stack itself. A `sb:SelfHostedStack` template
generating that Compose file would be a reasonable future extension of this pack, but is not
built in this pass.
