# shadcn-ui-primitives-pack

Renders the shadcn/ui primitive components that were confirmed absent from every
other pack in this marketplace: Card family, Badge, Label, Skeleton, Separator,
Tabs family, Table family — plus the `cn` helper (`lib/utils.ts`) every one of
them imports.

## What It Projects

- `components/ui/badge.tsx`, `card.tsx`, `label.tsx`, `skeleton.tsx`,
`separator.tsx`, `tabs.tsx`, `table.tsx` (7 components, cva/cn conventions
matching `button.tsx` in nextjs-ai-sdk-pack)
- `lib/utils.ts` (`cn()` = `twMerge(clsx(...))`)

## Consumer Contract

npm deps: `typescript clsx tailwind-merge class-variance-authority
@radix-ui/react-tabs`, plus `react react-dom @types/react @types/react-dom`
(radix lists `@types/react` as a peer that npm does not auto-install; JSX strict
type-check needs React types).

`@/lib/utils` is a path alias — the consumer's `tsconfig.json` must map
`"@/*"` to the project root (baseUrl + paths).

The `cn` helper arrives via the projected `lib/utils.ts` (template
`060_lib_utils_ts.tmpl`). Deleting it is load-bearing: every projected component
imports `@/lib/utils`, so a consumer without it fails `tsc` with TS2307 on all
7 components.

## Rendering

Bind the pack by path in a consumer `ggen.toml`:

```toml
[project]
name = "my-consumer"

[ontology]
source = "ontology.ttl"

[packs]
"shadcn-ui-primitives-pack" = { path =
"../ggen-marketplace/packs/shadcn-ui-primitives-pack" }

[templates]
dir = "local-templates"
```

Notes learned from a real render:

- `[ontology]` and `[templates]` are required fields (FM-CONFIG-002).
- Paths in `[ontology]`/`[templates]` must be relative (FM-CONFIG-003);
absolute paths are refused. Symlink the pack's `ontology.ttl`/`templates/`
into the consumer, or copy them, and point `[packs]` at the pack dir.
- `[templates].dir` must NOT point at the pack's templates dir when the pack is
also bound via `[packs]` — templates render twice and FM-WRITE-008 fires on the
duplicate `components/ui/badge.tsx` output. Point it at an empty local dir.
- The EA admission gate requires `ea.graph.json` or
`--skip-ea-admission` (FM-LAW-015); the scratch consumer used
`--skip-ea-admission`.

Then `ggen sync run --skip-ea-admission` renders all 8 files.

## Verification Court

Scratch consumer at `/tmp/p4-consumer` (npm init; deps installed; consumer
`ggen.toml` binding the pack by path). Full command + exit log:
`docs/jira/v26.11.5/receipts/P4.md`.

- ggen 26.11.3 `sync run --skip-ea-admission` → exit 0, 8 files written.
- `tsc --noEmit --strict` over `components/**/*.tsx` + `lib/utils.ts` →
exit 0, zero unresolved imports.
- Anti-vacuity flip: delete `lib/utils.ts`, re-run `tsc` → exit 2, TS2307
`Cannot find module '@/lib/utils'` on all 7 components. The helper is
load-bearing; a court that cannot flip would have been vacuous.

## See Also

- packs/nextjs-ai-sdk-pack (button.tsx conventions this pack matches)
