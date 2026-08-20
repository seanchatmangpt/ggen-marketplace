# xaas-ash-core-pack — first proof, real scope

First proof of the `O_public → O* → ggen → Ash` architecture (chatman-ecosystem
`docs/jira/v26.8.20/07`), deliberately the smallest possible slice.

## What is real and verified this session

- **The source fact**: `pcc:ApprovalLegalHoldRelease`, a real `ce:Capability` individual in
  `chatman-ecosystem/ontology/platform-console-capabilities.ttl` (`ce:capabilityClass ce:Do`,
  `ce:brokerRequired true`, `ce:receiptRequired true`, `ce:reversible false`,
  `ce:requiredAuthority "approval-workflow.requireApproval(legal-hold.release)"`).
- **The bridge vocabulary**: `ontology.ttl`'s `xar:` render-hints, deliberately not asserting any
  `owl:equivalentClass` between `ce:Capability` and Ash/FnO concepts (per
  `xaas-public-ontology-profile/gates/020_no_unproven_equivalence.rq`).
- **The template**: `templates/resource.ex.tera` — a deliberately dumb rendering template (per
  "SPARQL understands, Tera renders").
- **The rendered proof**: `proof/legal_hold_release.ex` — the template's output with the real
  ontology values substituted, **verified this session as syntactically valid Elixir** via the
  real `elixir` binary (`Code.string_to_quoted!/1` succeeds).
- **The `Change → Intent` law, encoded**: the generated `update :release` action's `change`
  blocks only ever set local attributes — it does not call `platform-console`'s `legal-hold.ts`
  or any external system. `Ash.Policy` answers "may actor call this action," explicitly not
  claimed equivalent to BRCE execution authority (`ce:brokerRequired`/`ce:receiptRequired` are
  still a separate, unrendered check).

## What is NOT yet done (disclosed, not silently dropped)

- **The SPARQL-to-template wiring itself was not built or run this pass.** `proof/
  legal_hold_release.ex` was produced by manually substituting the ontology's real values into
  the template, not by a real `ggen sync run` executing a SPARQL query against `ontology.ttl`.
  That wiring is the actual next step, not this proof.
- **Not compiled against a real Ash dependency.** `elixir -e Code.string_to_quoted!` proves
  syntax validity only — it does not prove `use Ash.Resource` compiles, that the DSL blocks
  (`attributes`, `actions`, `policies`) are valid Ash syntax, or that the resource loads inside a
  real `Ash.Domain`. That requires a real Mix project with `{:ash, "~> 3.0"}` as a dependency,
  which does not exist yet anywhere in this proof.
- **`ce:reversible false` is rendered as a comment only.** What a `false` reversibility should
  mechanically change about the generated action (refuse a destroy action entirely? require an
  extra confirmation argument? something else) is a real open question, not resolved here.
- **No `Ash.Domain` module, no `AshPostgres`, no `AshAuthentication`, no `AshGraphql`/
  `AshJsonApi`** — single-resource proof only.

## Next real step

Stand up a real Mix project with `ash` as a dependency (not `~/dev/beamops`, not any existing
`~/dev/ash_*` project, per `chatman-ecosystem/docs/jira/v26.8.20/05`'s finding that none of those
have policy/tenancy code to build on), drop `proof/legal_hold_release.ex` in as
`lib/xaas/governance/legal_hold_release.ex`, and get `mix compile` real-green. Only then does
"first proof" mean anything beyond syntax.
