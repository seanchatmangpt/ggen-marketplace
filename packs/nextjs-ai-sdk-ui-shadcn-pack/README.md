# nextjs-ai-sdk-ui-shadcn-pack

Semantic profile + projection pack for the real Next.js 16 / React 19 AI SDK v7
chat project (`/Users/sac/ggen/examples/nextjs-ai-sdk`): shadcn-configured,
`components/ui/button.tsx` built with `class-variance-authority`, and the
canonical shadcn `cn()` helper in `lib/utils.ts` (clsx + tailwind-merge).
No Radix packages exist in the source project — Button is shadcn-shaped, not
Radix-backed. deck.gl is confirmed absent (recorded as a negative finding).

## What it projects

- `components/ui/button.tsx` — cva-based Button primitive
- `components/ai-elements/confirmation.tsx`, `message.tsx`,
  `prompt-input.tsx`, `tool.tsx`, `conversation.tsx` — bespoke AI SDK chat UI
  components consuming `cn()` and the Button primitive
- `lib/utils.ts` — `cn()` helper (clsx + tailwind-merge body). This body is
  kept semantically stable; byte-identity with
  `jotp-benchmark-site-shadcn-pack`'s helper does not hold today
  (FM-PACK-008 dual-pack hazard) and is the single-sourcing wave's decision.

## Consumer contract

Derived mechanically from `templates/*.tmpl` bare imports.

- `runtime`: `ai`, `class-variance-authority`, `clsx`, `lucide-react`,
  `react`, `tailwind-merge`
- `dev_tools`: `typescript` (strict tsc is the qualification gate)
- `peer_context`: the consumer's tsconfig must map `@/*` to the project root
  so `@/lib/utils` resolves to the projected `lib/utils.ts`
- `projected_helpers`: `lib/utils.ts`

Compose the pack in a consumer `ggen.toml` via `[packs]` with an absolute
`path`; `ggen sync run --skip-ea-admission` projects the files above.

## Qualification court

A scratch consumer installs the runtime deps + `typescript`, runs
`ggen sync run --skip-ea-admission`, then `tsc --strict` (must exit 0 with all
imports resolving). Anti-vacuity flip: remove `lib/utils.ts` and re-run tsc —
`TS2307 Cannot find module '@/lib/utils'` must appear; the helper is then
restored by re-running sync and tsc exits 0 again. A court that cannot flip
is vacuous.
