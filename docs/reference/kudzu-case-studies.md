# Kudzu Case Studies

Status table of real candidate integrations between ggen-marketplace's
real-dependency + adapter convention (established by
`protocol-integration-pack`'s `enterprise_kudzu.ttl`) and five real,
on-disk repos. Sourced from direct repo inspection, not from documentation
claims made by those repos about themselves.

**This pack does not yet contain working adapter code.** Every row below is
a proposal recorded as a `pr:PriorArtAdapter` individual in `ontology.ttl` —
none has been run through a Workflow-driven pilot, generated, compiled, or
tested yet. This mirrors how `enterprise_kudzu.ttl`'s Ash-sibling pilots
started as identified candidates before real pilots made them ALIVE; do not
read any row here as an ALIVE claim.

| Repo | Feasibility | Real API surface cited | Next real step |
|---|---|---|---|
| beam4pm | ALIVE_LOCAL | `BeamPM.Discovery.traces_from_events/2` (ggen-generated Elixir mirror of `src/beam4pm_discovery.erl`); real local path, no external accounts | Add `{:beam4pm, path: "/Users/sac/beam4pm"}` as a test-only dep in a new adapter project; generate `lib/beam4pm_protocol_adapter.ex` via `mix_dep_install.ex.tmpl`/`adapter.ex.tmpl`; write a Chicago-style test against a real event_log fixture |
| ash_ex4pm | ALIVE_LOCAL | `AshEx4pm.Info.activities/1`, `AshEx4pm.AutomatedPlanning` (existing generated stub, currently empty/`forward_declared`) | Design and add a gate variant tolerant of dependency-resolved ontology (`Application.app_dir(:ex4pm, "priv/ontology/ex4pm.ttl")`) before generating; this is new pack capability, not yet built |
| deepwiki-rs | BLOCKED | `src/main.rs` — Cargo binary only, no `lib.rs`, no exported Rust library API | Do not attempt an in-process adapter. If pursued at all, design a new subprocess-adapter template family (`System.cmd/3`-based) first — out of scope for this pack today |
| ash_a2a | ALIVE_LOCAL | `AshA2A.Dispatcher.dispatch/3`, proven callable today by `test/ash_a2a_test.exs` | Generate a NEW adapter binding a Capability to Protocol=A2A via `dispatch/3`; explicitly do NOT reuse `ash_a2a`'s own `priv/ggen/ash_a2a/ontology.ttl` (self-disclaimed as unexecuted, and its ggen_igniter sync is separately BLOCKED — receipt shows `standing: "refused"`, CompileError) |
| open-ontologies | ALIVE_LOCAL | `open-ontologies validate <file.ttl>` — real Cargo CLI subcommand (`src/main.rs`, clap) | Same missing capability as deepwiki-rs: a subprocess-adapter template family (`System.cmd/3` wrapping the compiled binary) does not exist in `protocol-integration-pack` yet; `cargo build` itself was not verified in the survey that produced this record |

## What is and isn't built

- **Built**: `pack.toml` (identity only) and `ontology.ttl` (five
  `pr:PriorArtAdapter` candidate individuals, reusing
  `protocol-integration-pack`'s exact predicate set) in this pack.
- **Not built**: any generated adapter module, any generated test, any
  gate, any template. Four of five candidates (`beam4pm`, `ash_ex4pm`,
  `ash_a2a`, `open-ontologies`) are `ALIVE_LOCAL` — reachable without new
  accounts or paid services — but none has actually been generated or
  compiled through this pack. `deepwiki-rs` is `BLOCKED` on a structural
  mismatch (no in-process Rust API), not a missing credential.
- Two candidates (`ash_ex4pm`, and to a lesser extent `open-ontologies`/
  `deepwiki-rs`) additionally require a new pack capability
  (dependency-resolved ontology gate, and a subprocess-adapter template
  family, respectively) that does not exist anywhere in
  `ggen-marketplace` yet — these are scope-expansion items, not
  same-day generation targets.

## See also

- `packs/protocol-integration-pack/enterprise_kudzu.ttl` — the origin
  convention and the one real, fully-property'd `pr:PriorArtAdapter`
  example (`pr:AshA2ARuntimeAdapters`) this pack's individuals follow the
  shape of.
- `AGENTS.md` (marketplace root) — source hierarchy this pack conforms to.
