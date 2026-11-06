# shadcn-ui-primitives-pack

Renders the shadcn/ui primitive components that were confirmed absent from every
other pack in this marketplace: Card family, Badge, Label, Skeleton, Separator,
Tabs family, Table family, the Field form family, plus the `cn` helper
(`lib/utils.ts`) every one of them imports.

## The Form Story: the Field Family (v0.3.0)

v0.3.0 adds `components/ui/field.tsx`: `Field`, `FieldSet`, `FieldGroup`,
`FieldLegend`, `FieldLabel`, `FieldDescription`, `FieldError`, `FieldContent` —
the library-agnostic form primitives that replaced the legacy
Form/FormField/FormControl/FormLabel/FormMessage react-hook-form wrapper in
current shadcn docs. The research receipt
(`/Users/sac/cmms/docs/research/shadcn-registry-and-forms-deep-research.md`,
103-agent verified, fetched 2026-11-05) records the deprecation finding: the old
Form primitives are absent from current shadcn docs entirely (ui.shadcn.com
discussion #9505, ~Aug 2025), and the react-hook-form guide builds forms with
the Field family + RHF `<Controller />` + `data-invalid`/`aria-invalid`
attributes — `FieldError` replaces `FormMessage`. The primitives are
RSC-compatible server components (no `"use client"`, no react-hook-form import
inside the primitive); form wiring lives in the consumer. A worked
Controller + zodResolver example projects to
`docs/examples/use-form-hook.tsx` (template `use-form-hook.ts.tmpl`) — it is a
consumer-side example, imported by nothing under `components/ui/`.

## What It Projects

- `components/ui/badge.tsx`, `card.tsx`, `field.tsx`, `label.tsx`,
`skeleton.tsx`, `separator.tsx`, `tabs.tsx`, `table.tsx` (8 components, cva/cn
conventions matching `button.tsx` in nextjs-ai-sdk-pack)
- `docs/examples/use-form-hook.tsx` (optional form-family example)
- `lib/utils.ts` — v0.3.0 body: `export { cn } from "cn"`

## Consumer Contract

npm deps: `cn class-variance-authority @radix-ui/react-tabs`, plus `react
react-dom @types/react @types/react-dom`. The form example additionally needs
the optional family `react-hook-form @hookform/resolvers zod` (see
`optional_runtime` in `pack.toml`).

`@/lib/utils` is a path alias — the consumer's `tsconfig.json` must map
`"@/*"` to the project root (baseUrl + paths).

**cn migration**: per the September 2026 shadcn changelog, the `cn` utility is
now an npm package; `lib/utils.ts` re-exports it instead of the deprecated
`twMerge(clsx(...))` body. Consumers pinning pack versions < 0.3.0 keep the
clsx + tailwind-merge body and must keep `clsx` + `tailwind-merge` installed;
v0.3.0+ consumers install `cn` and may drop both. The `cn` helper arrives via
the projected `lib/utils.ts` (template `060_lib_utils_ts.tmpl`). Deleting it is
load-bearing: every projected component imports `@/lib/utils`, so a consumer
without it fails `tsc` with TS2307 on all 8 components.

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

v0.2.0 court (P4): scratch consumer `/tmp/p4-consumer`; full command + exit log
in `docs/jira/v26.11.5/receipts/P4.md` — `tsc --noEmit --strict` exit 0;
flip (delete `lib/utils.ts`) → TS2307 ×7. v0.2.0 projected the
clsx+tailwind-merge helper body.

v0.3.0 court (F6): scratch consumer `/tmp/f6-shadcn-court.0OPV`; commands +
exits in `docs/jira/v26.11.5/receipts/F6.md` — `tsc --noEmit --strict` over
`components/` + `lib/` + `docs/` (incl. the RHF example, deps installed) →
exit 0; flip (delete `lib/utils.ts`) → TS2307. Ontology gates
(`gates/010_cn_requires_helper_projection.rq`,
`gates/020_requires_dep_declared.rq`) run 0 rows on the pack graph and return
non-zero rows on their anti-vacuity flips (removed HelperProjection / removed
DeclaredDep). The helper is load-bearing; a court that cannot flip would have
been vacuous.

## See Also

- packs/nextjs-ai-sdk-pack (button.tsx conventions this pack matches)
