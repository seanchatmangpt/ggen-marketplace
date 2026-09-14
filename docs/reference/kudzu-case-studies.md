# Kudzu Case Studies

Status table of real candidate integrations between ggen-marketplace's
real-dependency + adapter convention (established by
`protocol-integration-pack`'s `enterprise_kudzu.ttl`) and five real,
on-disk repos. Sourced from direct repo inspection, not from documentation
claims made by those repos about themselves.

**Update (this run): real Workflow-driven pilots were executed against all
five repos.** Four are now `VERIFIED ALIVE` via real command output (real
`mix compile`/`mix test`, or real `cargo build` + real CLI invocation),
built in scratch apps outside `ggen-marketplace` (per the marketplace's
own pack-source-hierarchy law — generated consumer code does not live in
packs/) and never committed as live pack code. One (`open-ontologies`)
remains `BLOCKED`, for a re-derived, different real reason than before.
Per-pilot receipts (exact commands, real output summaries) are recorded
under `docs/reference/kudzu-case-study-pilot-receipts/`.

| Repo | Pilot status | Real API surface cited | Real evidence this run |
|---|---|---|---|
| beam4pm | VERIFIED ALIVE | `BeamPM.Discovery.traces_from_events/2` (ggen-generated Elixir mirror of `src/beam4pm_discovery.erl`) | `mix compile` (exit 0) + `mix test` (2 tests, 0 failures) against a real `{:beam4pm, path: "/Users/sac/beam4pm"}` dep in a scratch app; real `OcelEvent`/`LogTrace` structs, no mocks |
| ash_ex4pm | VERIFIED ALIVE | `AshEx4pm.Info.activities/1` | Real, in-repo evidence against `/Users/sac/ash_ex4pm` (no scratch app needed): `mix compile` + `mix test test/integration/beam4pm_via_ex4pm_test.exs` (5 tests, 0 failures, real Bandit HTTP server) + a real scratch-probe call returning a real, non-empty `AshEx4pm.Activity` list. A new gate (`030_dependency_resolved_ontology_contract.rq`, design captured in the pilot receipt) is still needed before this individual can drop its dependency-resolved-ontology caveat — deferred to a separate Integrate-phase change |
| deepwiki-rs | VERIFIED ALIVE (was BLOCKED) | `deepwiki-rs sync-knowledge` — real, purely local CLI subcommand (`src/integrations/knowledge_sync.rs`, no LLM API key needed) | `cargo build --release` succeeded; `deepwiki-rs --version`/`sync-knowledge` both real exit 0; a scratch Elixir adapter using the NEW `subprocess_adapter.ex.tmpl`/`subprocess_adapter_test.exs.tmpl` template family passed 2/2 real tests against the real binary. Prior BLOCKED reason (no subprocess-adapter template family existed) is now closed by `protocol-integration-pack`'s `gates/020_subprocess_adapter_contract.rq` |
| ash_a2a | VERIFIED ALIVE | `AshA2A.Dispatcher.dispatch/3`, proven callable today by `test/ash_a2a_test.exs` | Real scratch app with `{:ash_a2a, path: "/Users/sac/ash_a2a"}`: `mix compile` (exit 0, full real dependency chain including `ggen_igniter`'s Rustler NIF build) + `mix test` (1 doctest, 4 tests, 0 failures) against a real Ash fixture, asserting both a real success reply and a real unknown-skill error, no mocks |
| open-ontologies | BLOCKED (real reason re-derived) | `open-ontologies validate <file.ttl>` — real Cargo CLI subcommand | `cargo build --release` fails today with 70 pre-existing compilation errors in the repo's own source (`src/swarm.rs`'s `BreedOutput` struct missing fields referenced elsewhere in the crate) — a real, structural regression in that repo, not an environment/toolchain issue, and not something this pilot modified (repo is off-limits to edit) |

## What is and isn't built

- **Built**: `pack.toml` (identity, now versioned 0.2.0) and `ontology.ttl`
  (five `pr:PriorArtAdapter` individuals, reusing
  `protocol-integration-pack`'s exact predicate set — four now carrying
  `VERIFIED` rdfs:comments backed by real command output, one carrying a
  re-derived real `BLOCKED` reason) in this pack. Per-pilot JSON receipts
  under `docs/reference/kudzu-case-study-pilot-receipts/`.
- **Not built in this pack**: no generated adapter module or test lives
  inside `ggen-marketplace` itself — every real adapter/test file the
  pilots wrote was built and run in a scratch app outside this repo
  (`/tmp/kudzu-pilot-*`), per the marketplace's pack-source-hierarchy law.
  The new `030_dependency_resolved_ontology_contract.rq` gate that
  `ash_ex4pm`'s pattern motivates is designed (see its pilot receipt) but
  not yet added to `protocol-integration-pack` — a deferred,
  separate Integrate-phase change, not a same-day item.

## See also

- `packs/protocol-integration-pack/enterprise_kudzu.ttl` — the origin
  convention and the one real, fully-property'd `pr:PriorArtAdapter`
  example (`pr:AshA2ARuntimeAdapters`) this pack's individuals follow the
  shape of.
- `AGENTS.md` (marketplace root) — source hierarchy this pack conforms to.
