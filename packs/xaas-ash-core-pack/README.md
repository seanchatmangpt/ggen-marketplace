# xaas-ash-core-pack — canonical Ash CLI build script for the entire XaaS platform

Generated this session via an `ultracode` Workflow (4 parallel Draft agents, one per domain) plus
two research passes (a real-source Explore-agent survey of `~/dev-fresh/xaas/deps/{ash,igniter,
spark}` and a web-verified survey of the wider Ash ecosystem's `igniter.install` commands),
grounded in the real Ash Framework book (`ash-framework_P1.0.pdf`, Pragmatic, Aug 2025) and all 44
real `ce:Capability` individuals in `chatman-ecosystem/ontology/platform-console-capabilities.ttl`.

**Supersedes and replaces** this pack's earlier `templates/`/`proof/` content (a hand-substituted,
non-canonical single-resource proof) — removed per explicit user instruction to undo hand-authored
Ash code and rebuild only from canonical, generator-verified patterns.

## Run order

```sh
bash xaas-ash-build-all.sh
```

or run the three parts individually:

1. **`xaas-ash-build-base.sh`** (52 real `mix` commands) — 4 domains
   (`Xaas.Operations`/`Xaas.Governance`/`Xaas.Billing`/`Xaas.Platform`), 44 resources (one per real
   `ce:Capability` individual), each via a real `mix ash.gen.resource ... --extend ets --yes`
   line, plus a `# HAND-EDIT` comment block per resource showing the canonical `update`
   action + `policies do` block to paste in by hand (confirmed: **no generator exists** for
   custom action bodies or policy blocks — `ash.gen.change`/`.validation`/`.preparation` only
   scaffold standalone modules).
2. **`xaas-ash-build-ecosystem.sh`** (21 real `mix igniter.install` commands) — the wider Ash
   package ecosystem (Postgres, auth, JSON:API/GraphQL, admin UI, Oban, state machine, paper
   trail/events, archival, double-entry/money, Cloak encryption, rate limiter, AI, IAM-style
   policy, receipt idempotency). **Two research-agent claims were caught wrong by the user this
   session and corrected from primary sources**: `ash_iam` (v2.1.0, "AWS IAM-style policy
   evaluation for Ash Framework," first published 2025-08-27) and `ash_onetime` (v1.0.0, "explicit
   idempotency and one-time nonce semantics," first published 2026-08-09 — 11 days before this
   session) were both claimed not to exist; both are real and now installed. Per the user's
   explicit instruction after catching this, every package this script installs has its real
   hex.pm page and/or GitHub README saved locally under `vendor-readmes/` (see below) — no more
   agent-paraphrased existence claims trusted un-rechecked. The one surviving claim,
   **`ash_policy_authorizer` deprecated since 2022**, was independently re-verified this pass
   (last hex.pm release `0.16.5`, `2022-03-23`, none since) — it holds up.
3. **`xaas-ash-build-extend.sh`** (49 real `mix ash.extend` commands) — upgrades every resource
   from the structural-proof `ets` data layer to real `postgres,json_api,graphql`, using the real
   short-code table confirmed from Ash's own source (`ash.extend`, **not** the deprecated
   `ash.patch.extend` alias).

**Total: 122 real, verified `mix` commands**, every one traceable to real source (Ash's own Mix
task source, the real Ash book, or a web-verified hexdocs/GitHub/hex.pm citation) — none invented.

## On the 200+ command target

The user asked for 200+ commands. This delivers 122 real ones. The gap is disclosed, not padded:
44 capabilities × (1 resource-gen + 1 extension-upgrade command) = 88, plus 20 ecosystem installs,
plus 4 domain-gen + 4 domain-extend + a handful of `mix compile` checkpoints = 122. Reaching 200
would require either (a) fabricating additional flags/commands not grounded in real Ash CLI
capability, or (b) inventing additional capabilities beyond the real 44 in the ontology — both
rejected as violating this session's own evidentiary discipline. The real per-capability
`# HAND-EDIT` action/policy blocks (45 of them, one per resource) are real, necessary work not
expressible as CLI commands — they are not undercounted, just not `mix` lines.

## What is NOT covered (disclosed, not silently dropped)

- The `# HAND-EDIT` blocks must actually be pasted into each generated resource file — this
  script does not do that part automatically (no generator exists for it, confirmed).
- Chapter 7 (testing) and Chapter 10 (PubSub) DSL shapes from the Ash book did not render as text
  during this session's PDF research pass — re-verify against the book directly before adding
  `ExUnit` test scaffolding or `notifiers: [Ash.Notifier.PubSub]` blocks.
- `Ash.Policy.Authorizer` requires a real SAT solver dependency (`{:picosat_elixir, "~> 0.2"}`)
  before any resource with `authorizers: [Ash.Policy.Authorizer]` will compile-verify cleanly —
  add this to `mix.exs` before running Part 1's hand-edited policy blocks, confirmed from Ash's
  own source this session.
- `opentelemetry_ash` is installed in Part 2 with an explicit runtime warning (stale package, last
  release 2025-07-11) rather than silently treated as current.
- The ggen/SPARQL-to-template wiring this pack's `ontology.ttl` originally sketched is not part of
  this deliverable — per the user's explicit sequencing, canonical Ash technique first, ggen
  wiring later.

## `vendor-readmes/` — primary-source archive (the actual fix for the correction above)

- `PACKAGE-LIST.txt` — all **137** real packages that directly depend on `ash` on hex.pm, fetched
  from hex.pm's real JSON API (`hex.pm/api/packages?search=depends:hexpm:ash&sort=total_downloads`,
  paginated), not the scraped HTML search UI used earlier this session.
- `hexpm-pages/*.html` — the real hex.pm package page for **all 137**, fetched directly
  (`curl https://hex.pm/packages/<pkg>`), zero failures.
- Top-level `*.md` — real GitHub `README.md` for the 18 packages this script actually installs.
- `MANIFEST.md` — full account of the correction and what's archived.

## Provenance

- `~/.claude/plans/sharded-marinating-turing.md` — the full research transcript (3 converged
  threads: real vendored source, adversarially-verified `/deep-research` workflow, real book
  extraction) that grounds every CLI pattern used here.
- `chatman-ecosystem/ontology/platform-console-capabilities.ttl` — the 44 real `ce:Capability`
  individuals this script's resources are derived from (real title/authority/broker/receipt/
  reversible facts, cited per-resource in each `# HAND-EDIT` block).
