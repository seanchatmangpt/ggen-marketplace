# ai-chatbot-shadcn-pack

shadcn/ui new-york primitives admitted as real evidence from the local
`/Users/sac/ai-chatbot` Next.js 16 / React 19 project: Alert, Badge, Button,
Card, Dialog, Input. Each template is a `.tmpl` with a SPARQL entity select
and a `for_each` projection into the consumer's `components/ui/`.

## Consumer Contract (v0.2.0)

Declared in `pack.toml `[consumer_contract]``, derived mechanically from the
bare (non-relative, non-react) imports in `templates/*.tmpl`:

| dep | imported by |
|---|---|
| `@radix-ui/react-dialog` | dialog.tsx |
| `@radix-ui/react-slot` | badge.tsx, button.tsx |
| `class-variance-authority` | alert.tsx, badge.tsx, button.tsx |
| `lucide-react` | dialog.tsx (`XIcon`) |

Peer context: every primitive imports `{ cn }` from `@/lib/utils`. This pack
does **not** project `lib/utils.ts` — the consumer must provide it (a clsx +
tailwind-merge `cn`, or a re-export of the `cn` npm package). Tailwind CSS 4
with the shadcn theme variables (`bg-card`, `text-muted-foreground`, `ring`,
...) is assumed present; class strings are inert without it.

Failure modes if the contract is skipped: `TS2307 Cannot find module` for any
missing runtime dep or missing `@/lib/utils`; visual (non-tsc) breakage from
missing theme variables.

## Templates

| file | projects |
|---|---|
| `0000-...alert...` | `components/ui/alert.tsx` |
| `0001-...badge...` | `components/ui/badge.tsx` |
| `0002-...button...` | `components/ui/{{ row.lower }}.tsx` (subject `gc:lower = "button"`) |
| `0003-...card...` | `components/ui/card.tsx` |
| `0004-...dialog...` | `components/ui/dialog.tsx` |
| `0005-...input...` | `components/ui/input.tsx` |

## Verification Court

A scratch consumer with `typescript@5.9` + the declared runtime deps runs
`ggen sync` → `tsc --strict --noEmit` → exit 0. Anti-vacuity flip: breaking a
declared dep must flip the court to non-zero. Receipt:
`docs/jira/v26.11.5/receipts/G02.md`.
