# Pack Consumer Contract

Standing: PARTIAL_ALIVE — schema defined and proven on one pack
(shadcn-ui-primitives-pack v0.2.0, court receipt P4); three of the four
cmms-referenced packs were mid-flight authoring at write time (see
Disclosures).

## Scope

One consistent `[consumer_contract]` section for ggen-marketplace packs that
project frontend code into consumer repos. Reference implementation:
`packs/shadcn-ui-primitives-pack/pack.toml`. This document is the
convention layer only — it does not modify any pack.

## The schema

Every pack that projects files a consumer must compile declares:

```toml
[consumer_contract]
runtime = ["clsx", "tailwind-merge", "class-variance-authority",
           "@radix-ui/react-tabs"]
peer_context = "@/lib/utils via projected lib/utils.ts"
```

### Key names

- `runtime` — array of npm packages a consumer MUST have installed before
  projecting. Derived mechanically from the pack's templates: the exact set
  of non-relative, non-`react` bare imports in `templates/*.tmpl`. P2
  verified this derivation for shadcn-ui-primitives-pack (7/7 templates
  import `@/lib/utils`; only radix dep is `@radix-ui/react-tabs`).
- `peer_context` — one line naming the helper/module the consumer must have
  at a fixed path. House value: `"@/lib/utils via projected lib/utils.ts"`.
  Packs that project their own `lib/utils.ts` template still declare the
  peer path (the helper must resolve at `@/lib/utils` regardless of who
  projects it).
- `projected_helpers` — reserved key for the list of helper files the pack
  itself projects (e.g. `["lib/utils.ts"]`). Packs that project no helpers
  omit the key. F1/F2/F3 packs should adopt it when they land: jotp and
  nextjs-ai-sdk-ui each ship a `0007/0006-lib_utils_ts-*.tmpl`, ai-chatbot
  does not.

### Versioning law

Contract-bearing packs bump the PACK version on any contract change:
adding/removing a `runtime` entry, changing `peer_context`, or adding
`projected_helpers` is a version bump (semver-compatible minor for additive
changes, major when an existing consumer that passed under the old contract
would fail under the new one). Landed precedent: shadcn-ui-primitives-pack
0.1.0 → 0.2.0 was exactly this bump (P2 receipt).

### Court law

A contract is not proved by prose; each pack carries a scratch-consumer
court and an anti-vacuity flip, per the P4 recipe:

1. Fresh scratch consumer (disposable /tmp dir), pinned deps from
   `runtime`, pinned TypeScript (5.9.3 pinned — TS 7.0.2 `tsc` hangs in
   this environment; see P4 Deviations).
2. Real render: `ggen sync run --skip-ea-admission` exit 0, all templates
   rendered.
3. `tsc --noEmit --strict` exit 0, zero unresolved imports.
4. Anti-vacuity flip: remove the peer helper (`rm lib/utils.ts`), re-run
   tsc — must fail with `TS2307 Cannot find module '@/lib/utils'`. A court
   that cannot flip is FAIL. Restore via `ggen sync run` (an FM-PACK-008
   lock mismatch after a substrate move is remediated by `rm ggen.lock`
   and re-lock, per P4).

Consumer ggen.toml facts every court must respect: relative paths only
(FM-CONFIG-003), required `[ontology]` + `[templates]` sections
(FM-CONFIG-002), empty local templates dir to avoid double render
(FM-WRITE-008), `--skip-ea-admission` (FM-LAW-015).

## cn-package migration note

The shadcn changelog (September 2026 entry) now recommends the dedicated
`cn` class-merging package as a drop-in replacement for
`twMerge(clsx(...))` in per-project `lib/utils.ts`, with migration via
`pnpm dlx shadcn@latest migrate cn`. Research receipt:
`/Users/sac/cmms/docs/research/shadcn-best-practices-deep-research.md`
(claims verified against ui.shadcn.com/docs/changelog, fetched 2026-11-05).

Forward path for all four packs' `lib/utils.ts`: keep the peer path
`@/lib/utils` stable and treat the helper's implementation as swappable —
the current `twMerge(clsx(inputs))` body is the deprecated form; consumers
and packs migrate to `import { cn } from "cn"` (packs re-project or stop
projecting the helper accordingly). This is the lawful target for F1/F2/F3
packs' helper templates; it is NOT yet landed in any of the four packs.

## Loader-admission caveat

P2's disclosure stands: `[consumer_contract]` is a newly minted section key
with no loader precedent (only pack-to-pack `[dependencies]` precedent
exists). Whether the ggen loader admits the key is UNVERIFIED — marketplace
structural validation was not run against the real loader. Until verified,
the key is prose-grade metadata: packs must not gate on it, and the court
(P4 recipe) is the only admission mechanism. First loader run against a
`[consumer_contract]`-bearing pack.toml should be recorded as a receipt
amendment here.

## Cross-check of the four cmms-referenced packs (as of this writing)

Reference pack (landed, committed 1b3d6fa7d):

- shadcn-ui-primitives-pack v0.2.0 — contract landed (runtime + peer_context),
  cn-helper gate `gates/010_cn_requires_helper_projection.rq` fail-closed,
  scratch-consumer court P4 PASS with real flip (TS2307 ×7).

Mid-flight (authored concurrently by F1/F2/F3; state below is committed
state, not lane output):

- ai-chatbot-shadcn-pack v0.1.0 — 6 templates, all import
  `@/lib/utils`; NO clsx/tailwind-merge import in any template → it does
  NOT project a helper and, on committed state, has no
  `[consumer_contract]`. Converging target: declare
  `runtime = ["class-variance-authority", "@radix-ui/react-slot",
  "@radix-ui/react-dialog", "lucide-react"]` + peer_context
  `@/lib/utils` (no `projected_helpers`).
  - Inconsistency already visible: its button/card/badge/alert templates
    are the same hashes as jotp's (`2795b661f0`, `c0ebd3fbaf`,
    `30348591d6`) — shared templates across packs, so a contract change to
    one is a contract change to the other; contracts must be kept in lockstep
    or the templates deduplicated into one pack.
- jotp-benchmark-site-shadcn-pack v0.1.0 — projects its own
  `0006-lib_utils_ts-98e56006aa.tmpl` (twMerge(clsx(...)) body), plus a
  `@radix-ui/themes` + `@radix-ui/react-icons` benchmark-card template.
  Converging target: `runtime` includes clsx/tailwind-merge/cva +
  `@radix-ui/react-slot` + `@radix-ui/themes` + `@radix-ui/react-icons`;
  `projected_helpers = ["lib/utils.ts"]`.
  - Inconsistency: mixing `@radix-ui/themes` components with shadcn/cn
    primitives in one pack breaks the single peer_context line — the
    benchmark card needs no `cn` at all. Either split the radix-themes
    component into its own contract or name the union in `runtime` and
    scope `peer_context` to the cn-importing templates only.
- nextjs-ai-sdk-ui-shadcn-pack v0.1.0 — projects its own
  `0007-lib_utils_ts-98e56006aa identical-hash` helper template, plus
  ai-elements components importing `ai` and `lucide-react`. Converging
  target: `runtime = ["clsx", "tailwind-merge",
  "class-variance-authority", "ai", "lucide-react"]` +
  `projected_helpers = ["lib/utils.ts"]`.
  - Inconsistency: its helper template is the same hash as jotp's — two
    packs project the identical lib/utils.ts; if F1 and F3 disagree on the
    helper (e.g. one migrates to the `cn` package and the other does not),
    a consumer projecting both packs gets a content-hash conflict
    (FM-PACK-008 class). The helper must be single-source.

## See Also

- `packs/shadcn-ui-primitives-pack/pack.toml` — reference schema
- `docs/jira/v26.11.5/receipts/P2.md`, `P4.md` — schema + court receipts
- `/Users/sac/cmms/docs/research/shadcn-best-practices-deep-research.md` —
  cn-package research receipt
