# jotp-benchmark-site-shadcn-pack

Semantic-profile pack admitting `/Users/sac/jotp/benchmark-site` (Next.js 16 /
React 19, package `jotp-benchmark-monitor`) into the marketplace. The pack
projects the confirmed-on-disk shadcn shape of that app: `components.json`
(style `base-nova`, base color `neutral`, ui alias `@/components/ui`), the
canonical `cn()` helper, and the cva-based primitives the subject's
`components/ui/` carries.

## What It Projects

- `components.json` — shadcn registry config (style `base-nova`, lucide icons,
  `@/` aliases)
- `jotp-benchmark-site-shadcn-pack/ggen-create.json` — generation metadata
- `jotp-benchmark-site-shadcn-pack/components/ui/badge.tsx` — cva badge
- `jotp-benchmark-site-shadcn-pack/components/ui/button.tsx` — cva button
  (`@radix-ui/react-slot` `asChild`)
- `jotp-benchmark-site-shadcn-pack/components/ui/card.tsx` — card primitives
- `jotp-benchmark-site-shadcn-pack/components/ui/benchmark-card.tsx` —
  metric card importing `@radix-ui/themes` + `@radix-ui/react-icons`
- `jotp-benchmark-site-shadcn-pack/lib/utils.ts` — `cn()` =
  `twMerge(clsx(...))`

All 7 templates render from the pack's ontology individual
(`gc_subject_jotp_benchmark_site_shadcn_pack`) via SPARQL entity selection.

## Consumer Contract

npm deps (derived mechanically from template imports):
`react class-variance-authority @radix-ui/react-slot @radix-ui/themes
@radix-ui/react-icons clsx tailwind-merge`, plus `typescript` for the court
and `@types/react` (radix lists it as a peer npm does not auto-install; JSX
strict type-check needs React types).

This pack MIXES two Radix families. `button`/`badge` are the per-primitive
`@radix-ui/react-*` style; `benchmark-card` imports the framework package
`@radix-ui/themes` (and `@radix-ui/react-icons`). A consumer mounting the
projected `benchmark-card` should provide a `<Theme>` provider (or the themes
css reset); the react-* primitives are provider-free.

`@/lib/utils` is a path alias — the consumer's `tsconfig.json` must map
`"@/*"` to the project root. The helper arrives via the projected
`lib/utils.ts`; deleting it is load-bearing: every component imports
`@/lib/utils`, so a consumer without it fails `tsc` with TS2307 on all 4
components (the court's anti-vacuity flip).

## Rendering

Bind the pack by path in a consumer `ggen.toml`:

```toml
[project]
name = "my-consumer"

[ontology]
source = "ontology.ttl"

[packs]
"jotp-benchmark-site-shadcn-pack" = { path =
"../ggen-marketplace/packs/jotp-benchmark-site-shadcn-pack" }

[templates]
dir = "local-templates"
```

Notes learned from real renders of sibling packs (P4/F1 precedent):

- `[ontology]` and `[templates]` are required fields (FM-CONFIG-002); paths
  must be relative (FM-CONFIG-003).
- `[templates].dir` must NOT point at the pack's templates dir when the pack
  is also bound via `[packs]` — templates render twice and FM-WRITE-008 fires
  on the duplicate output. Point it at an empty local dir.
- The EA admission gate requires `ea.graph.json` or `--skip-ea-admission`
  (FM-LAW-015); the scratch consumer used `--skip-ea-admission`.

Then `ggen sync run --skip-ea-admission` renders the 7 files.

## Verification Court

Scratch consumer at `/tmp/g04-consumer` (npm init; deps installed; consumer
`ggen.toml` binding the pack by path). Full command + exit log:
`docs/jira/v26.11.5/receipts/G04.md`.

- `ggen sync run --skip-ea-admission` → exit 0, 7 files rendered
- `tsc --noEmit --strict` → exit 0, zero unresolved imports
- anti-vacuity flip: `rm lib/utils.ts` → `tsc` exit 2, TS2307 on
  `@/lib/utils` across all components; restore → PASS re-proven
