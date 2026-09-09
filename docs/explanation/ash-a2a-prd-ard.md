# ash_a2a — PRD / ARD

Status: DRAFT, UNSTARTED (`~/ash_a2a` does not exist as a repository yet). Every claim
below about upstream libraries is cited to a real file read during this session, not
inferred from names. Where a real gap or open question exists, it is named as such
rather than papered over.

## 0. What ash_a2a is

An Ash extension (`use Ash.Resource, extensions: [AshA2A]` / `use Ash.Domain,
extensions: [AshA2A]`) that exposes Ash resource/domain actions as [A2A protocol]
agent skills, without hand-writing a JSON-RPC server, a Task state machine, or an
Agent Card. Composition, grounded in real, already-inspected source:

```
ash_a2a = compose(
  ash_ai        [Ash ergonomics: dual Resource/Domain context normalization],
  ash_r2rml     [semantic-compiler doctrine: persisted canonical IR, fail-closed
                 verify, hybrid Info API, Reactor pipeline],
  a2a (0.2.0)   [A2A protocol runtime: already exists, see §2],
  ash-extension-core-pack v26.9.10  [the generator manufacturing all of the above]
)
```

---

## 1. PRD (Product Requirements Document)

### 1.1 Problem

Exposing an Ash action as an A2A-discoverable agent skill today means hand-writing:
a `use A2A.Agent` module with a `handle_message/2` clause per action, a `skills:`
list kept in sync by hand with the Ash resource's real actions, and manual
actor/tenant/context plumbing from the A2A message into the Ash call. This drifts:
nothing enforces that an advertised skill still maps to a real, still-existing Ash
action.

### 1.2 Goals

1. Declaring a skill on an Ash resource/domain is a DSL block (`a2a do skill
   :checkout, :checkout end`), not a hand-written GenServer callback.
2. The advertised `AgentCard` and the actually-dispatchable skill set can never
   diverge — both are projections of one persisted, verified compiled IR (see §3.2).
3. Actor/tenant/Ash-context propagate from the A2A message into the real Ash action
   automatically, using `{:ok, _} | {:error, _}` Ash APIs where practical (project
   convention), not bang-then-rescue as a default style.
4. Ship on top of the real `:a2a` 0.2.0 runtime (`~/xaas/deps/a2a`) — do **not**
   reimplement JSON-RPC, Task lifecycle, or HTTP transport.

### 1.3 Non-goals (v1)

- gRPC transport (the A2A `.proto` at `~/A2A/specification/a2a.proto` defines one;
  `:a2a` 0.2.0 does not ship one — see §2, open question, not solved here).
- Streaming (`{:stream, enumerable}` — `:a2a`'s `A2A.Agent` already supports this at
  the runtime layer; wiring an Ash `stream:`-capable read action into it is deferred).
- Push notifications / extended agent card (capabilities `:a2a`'s `AgentCard.capabilities`
  type already has slots for; not implemented in ash_a2a v1).

### 1.4 Users

- An Ash application author who wants existing resource actions callable by other
  A2A agents without writing protocol glue.
- A generator/pack author (`ash-extension-core-pack`) whose vocabulary this spec
  will exercise as an acceptance fixture, the same role `ash_r2rml`/`ash_ai` play
  today.

### 1.5 Functional requirements

| # | Requirement |
|---|---|
| FR1 | `a2a do skill :name, :action end` on a Resource; `skill :name, Resource, :action` on a Domain — same normalized IR either way (§3.1). |
| FR2 | Skill arguments map to the target action's accepted inputs; a `Skill.Argument` entity nested under `Skill` (not a separate top-level DSL construct — see §3.4). |
| FR3 | `AshA2A.Info.agent_card/1` returns a real `A2A.AgentCard.t()` built from the persisted, verified capability index — never from raw DSL entities directly. |
| FR4 | A message dispatched to a skill resolves actor/tenant/context, runs the real Ash action, and returns an `A2A.Agent` reply tuple (`{:reply, parts}` / `{:input_required, parts}` / `{:error, reason}`). |
| FR5 | An admitted spec with a skill naming a nonexistent action, or a duplicate skill name, fails verification (fail-closed, §3.3) — never silently ships a broken AgentCard. |
| FR6 | Installer adds `:a2a` and `AshA2A`/`AshA2A.Domain` (or however the target/domain split is finally named) to the target module via the existing pack installer pattern. |

### 1.6 Non-functional requirements

- No mocking in tests (Chicago-style per this workspace's standing rule): the
  composition test must compile a real fixture resource, attach real `AshA2A`, and
  call the real `A2A.Agent`/`AgentCard` code — not stub A2A's runtime.
- `ggen sync run` must actually render valid Elixir (currently UNVERIFIED for this
  pack's templates in this environment — see `errc-tracker.md` Cycle 3 addendum for
  the `/workspace` path-resolution blocker; must be revisited before ash_a2a ships).

### 1.7 Success metric

A real fixture resource + domain, generated end-to-end from one `aex:AshExtensionSpec`
via `ash-extension-core-pack`, compiles, and `A2A.Client` (from the real `:a2a`
package) can discover its `AgentCard` and successfully call one skill in a test —
not a described capability, an executed one.

---

## 2. What already exists vs. what's new (the load-bearing finding)

Confirmed by direct read this session, not assumed:

- **`:a2a` 0.2.0** (`github.com/actioncard/a2a-elixir`, vendored in
  `~/xaas/deps/a2a`) already implements: `A2A.Agent` (a `use`-macro generating a
  full GenServer — task creation, state-machine transitions, history, `handle_message/2`/
  `handle_cancel/1` callbacks, `{:reply,_}`/`{:input_required,_}`/`{:stream,_}`/`{:error,_}`
  reply protocol), `A2A.Task`/`A2A.Task.Status` (state machine:
  `:submitted → :working → {:completed | :failed | :input_required | :canceled}`),
  `A2A.AgentCard` (wire-format struct: `skill`, `capabilities`, `provider`,
  `supported_interface` types), `A2A.Message`/`A2A.Part`/`A2A.Artifact`, JSON-RPC
  (`jsonrpc.ex`), Plug/Bandit HTTP transport (`plug.ex`), Req HTTP client
  (`client.ex`), OTP supervision + registry (`agent_supervisor.ex`, `registry.ex`),
  telemetry, Jason codec.
- **`~/A2A`** (the protocol spec repo) has zero Elixir code — protobuf spec +
  Erlang SDK + Python SDK docs only. Not a build target for ash_a2a.
- **ex4pm** does not currently depend on `:a2a` (`ex4pm/mix.lock` has no entry) —
  wiring `:a2a` in as a dependency is a real prerequisite step, not yet done.
- **Genuinely new** (nothing upstream provides this): the Spark DSL itself
  (`a2a do skill ... end`), the transformer that walks Ash resource/domain actions
  and builds `A2A.Agent`-shaped skill definitions + calls Ash with the resolved
  actor/tenant/context, and the verifier that fail-closes on a skill naming a
  nonexistent action.
- **Open, unresolved:** whether `:a2a` 0.2.0's wire behavior is actually conformant
  with `~/A2A/specification/a2a.proto` was not verified this session (no direct
  coupling found between the two repos) — flagged, not assumed either way. gRPC
  transport support was not found in `:a2a`'s file listing; the `.proto` defines a
  gRPC service. This is a real gap to resolve, not silently deferred without saying so.

---

## 3. ARD (Architecture Requirements/Decision Document)

Each decision cites the real pattern it's copied from, per this workspace's "echo,
don't synthesize" discipline (`ash-extension-core-pack/ontology.ttl`'s own stated
convention).

### 3.1 Dual Resource/Domain context, one normalized IR

**Decision:** use `ash-extension-core-pack` v26.9.10's `aex:contextNormalize` /
`contextTargetEntity` / `contextTargetField` (`contextTargetEntity = "skill"`,
`contextTargetField = "resource"`), which generates the real `AshAi.Transformers.
ResourceTools` pattern verbatim: `Module.get_attribute(module, :spark_is) ==
Ash.Resource` detection (`~/xaas/deps/ash_ai/lib/ash_ai/transformers/resource_tools.ex:125-127`),
implicit `resource:` fill-in on resource-local `skill :name, :action` (2-arg),
explicit-value rejection at the resource level, explicit-value requirement at the
domain level for `skill :name, Resource, :action` (3-arg) — exactly ash_ai's
`args: [:name, {:optional, :resource}, :action]` shape
(`~/xaas/deps/ash_ai/lib/ash_ai/dsl.ex:264`).

**Why not invent a new mechanism:** the pack's v26.9.9/10 cycle built this property
specifically because it's a real, already-shipped pattern — reuse it rather than
re-deriving.

### 3.2 Persisted canonical IR: `AgentCard ← CapabilityIndex → Dispatch`

**Decision:** one transformer builds and persists a single compiled struct
(`Transformer.persist(dsl, :ash_a2a_capability_index, index)`), the same shape
`AshR2RML.Resource.Persist` uses for `:ash_r2rml_public_mapping`
(`~/ash_r2rml/lib/ash_r2rml/resource.ex:241,243`). `AshA2A.Info.agent_card/1` reads
*only* this persisted index — never raw DSL entities directly — so the advertised
card and the dispatch table can't diverge (the invariant named in the triggering
plan, confirmed as the right shape by ash_r2rml's real precedent).

Use v26.9.10's `aex:normalizeModule`/`normalizeFunction` to pipe the compiled skill
list through a normalize pass before persisting (mirrors `AshR2RML.Mapping.normalize()`
at `resource.ex:241`), and `aex:provenanceSource` to tag `metadata: %{source:
:ash_first}`-equivalent provenance.

### 3.3 Fail-closed verifier, delegate-and-join

**Decision:** use v26.9.10's `aex:validateDelegateModule`/`validateDelegateFunction`
pointing at `AshA2A.CapabilityIndex.validate/1`, generating ash_r2rml's exact
2-branch shape (`~/ash_r2rml/lib/ash_r2rml/resource.ex:492-511`): nil-persisted-key
check stays inline in the generated `Verify` module; the real business check (does
every skill's action actually exist? are skill names unique?) lives in a
hand-written `validate/1` on a separate module, refusals joined as
`Enum.map_join(refusals, "; ", &"#{&1.code}: #{&1.detail}")`.

`DSL valid ⇏ Capability valid`. Only `Compile(DSL) = IR ∧ Validate(IR) = PASS`
admits the capability — the invariant from the triggering plan, now mapped onto a
concrete, already-built pack mechanism instead of hand-rolled Verify logic.

### 3.4 Nested DSL entity: `Skill.Argument`

**Decision:** use v26.9.10's `aex:NestedEntity`/`nestedOf`/`nestedFieldName`,
mirroring ash_ai's `@tool_argument` nested under `@tool` via `entities: [arguments:
[@tool_argument]]` (`~/xaas/deps/ash_ai/lib/ash_ai/dsl.ex:228-268`, target
`AshAi.Tool.Argument`). `Skill.Argument` gets its own entity struct (`name`, `type`,
`description`, `default`, `allow_nil?` — same field shape as `AshAi.Tool.Argument`,
`~/xaas/deps/ash_ai/lib/ash_ai.ex:46-58`) rather than a bag of anonymous config, per
the triggering plan's own instinct ("not a bag of anonymous configuration").

### 3.5 Execution context: actor/tenant/context threading

**Decision:** follow `AshAi.Tool.Execution`'s real `build_opts/2` shape
(`~/xaas/deps/ash_ai/lib/ash_ai/tool/execution.ex:100-107`) — a plain opts keyword
list `[domain:, actor: context[:actor], tenant: context[:tenant], context:
context[:context] || %{}]` fed into `Ash.Changeset.for_create/3` /
`Ash.Query.for_read/3` / `Ash.ActionInput.for_action/3`. **Deviation from ash_ai,
matching this project's own convention (not ash_ai's):** ash_ai's actual execution
path is bang-call-then-rescue throughout (`Ash.create!`, `Ash.bulk_update!`,
`Ash.run_action!`, wrapped in one outer `try/rescue/catch`,
`~/xaas/deps/ash_ai/lib/ash_ai/tool/execution.ex:83-96`) — confirmed by direct read,
not assumed. ash_a2a should prefer non-bang `{:ok,_}|{:error,_}` Ash calls where the
action type allows it, per this workspace's stated A2A conventions, rather than
copying ash_ai's bang-then-rescue style verbatim. This is a **named deviation from
the golden specimen**, not an unexamined copy.

An `AshA2A.ExecutionContext` struct should carry `actor`/`tenant`/`context`/`domain`
explicitly from A2A message metadata into the resolver — never pass raw A2A
metadata straight into an Ash call (trust-boundary requirement from the triggering
plan, concretely: a `ContextResolver` module, not inline pattern-matching at the
call site).

### 3.6 Installer

**Decision:** use the pack's existing `--target`-conditional real
`Igniter.Project.Module` patch (already ahead of `ash_r2rml`'s own installer, which
performs no AST-based detection at all — confirmed by direct read of
`~/ash_r2rml/lib/mix/tasks/ash_r2rml.install.ex`, zero `Spark.Igniter` references).
No new installer mechanism needed for v1.

### 3.7 Reactor (deferred to v1.1, not v1)

A2A's `{:stream, enumerable}` reply mode and multi-turn `:input_required` tasks are
naturally state-machine-shaped; a future Reactor-backed skill (long-running,
resumable) would use `aex:workflowReactor`, but whether that property already
supports per-Reactor middleware injection is **UNVERIFIED** (flagged in
`errc-tracker.md` Cycle 4) — resolve before building, not assumed to already work.

### 3.8 Open questions / explicit blockers before implementation starts

1. `:a2a` 0.2.0 → `~/A2A` proto conformance: unverified.
2. gRPC transport: not found in `:a2a`; needed only if a consumer requires it — named,
   not solved.
3. `ex4pm` does not yet depend on `:a2a` — add the dependency before any real fixture
   can compile against it, if ash_a2a is meant to live inside/alongside ex4pm.
4. `ggen sync run` verification of `ash-extension-core-pack` templates is currently
   blocked by an environment path-resolution issue in the installed `ggen` binary
   (see `errc-tracker.md` Cycle 3 addendum) — must be resolved or worked around before
   ash_a2a's generated code can be confirmed to actually compile, not just look right.
5. `~/ash_a2a` does not exist — this document is pre-repo-creation requirements, not
   a review of existing code. No golden-specimen parity check (the kind that caught
   real bugs in `ash-extension-core-pack`'s own history — entity ordering,
   taskModuleName derivation) is possible until the repo exists.
