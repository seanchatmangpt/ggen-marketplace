# xaas-ash-core-pack — Real Build Difficulties and Repairs

Target observed in the speedrun: `/Users/sac/dev-fresh/xaas`.
Ash subject: 3.32.0.

## Original observed run

| Part | Program used | Attempted | Succeeded | Failed |
|---|---|---:|---:|---:|
| 1 — base | `xaas-ash-build-base-GENERATED.sh` | 45 | 45 | 0 |
| 2 — ecosystem | `xaas-ash-build-ecosystem.sh` | 21 | 20 | 1 |
| 3 — extend | `xaas-ash-build-extend-GENERATED.sh` | 49 | 49 | 0 |
| 4 — changes | `xaas-ash-build-changes-GENERATED.sh` | 89 | 89 | 0 |
| 5 — finishing | `xaas-ash-build-finishing.sh` | 6 | 5 | 1 |
| **Total** | | **210** | **208** | **2** |

No command timed out. The final direct `mix compile` on that observed project exited 0.

That run is evidence for the **pre-repair** script subject only. It does not crown the repaired
211-command program.

## Failure 1 — `ash_onetime` installer routing

Observed command:

```sh
mix igniter.install ash_onetime --yes
```

Observed error:

```text
The following installers did not exist or could not be found.
If you chose not to install dependencies, this will be true for any uninstalled packages.
```

### Corrected diagnosis

The original speedrun write-up incorrectly concluded that `ash_onetime` was not a published package.
That claim is **retracted**.

Primary-source evidence already archived in this pack at `vendor-readmes/ash_onetime.md` states:

- package: `ash_onetime`;
- published version: v1.0.0;
- canonical installer task: `mix ash_onetime.install`;
- Ash compatibility floor: `>= 3.31.3 and < 4.0.0`.

Therefore the observed failure class is **installer discovery/invocation**, not package
nonexistence.

### Repair

The ecosystem program now performs the dependency and installer transitions explicitly:

```sh
mix igniter.add ash_onetime
mix ash_onetime.install
```

This follows Igniter's documented `igniter.add` semantics—add/fetch a dependency without requiring
`igniter.install` to discover and dispatch the package installer—and then calls the package's own
installer exactly as documented.

**Post-repair runtime standing:** `NOT YET EXECUTED` for this exact two-command sequence.

## Failure 2 — unsupported diagram flag

Observed command:

```sh
mix ash.generate_resource_diagrams --yes
```

Observed error identified the accepted options as `--format`, `--only`, and `--type`; `--yes` was
not accepted.

### Repair

The finishing program now uses:

```sh
mix ash.generate_resource_diagrams
```

with no invented global flag.

**Post-repair runtime standing:** `NOT YET EXECUTED` for this exact command in the repaired full
program.

## Orchestration defect found during repair

The original master runner called the hand-assembled base/extend/change scripts even though the
speedrun and architecture had already established the ggen-rendered variants as the preferred
subject. It also changed into the pack directory, making the target Ash project implicit.

The repaired runner now:

1. accepts an explicit target project path;
2. refuses if that path has no `mix.exs`;
3. keeps the target project as the working directory;
4. invokes:
   - `xaas-ash-build-base-GENERATED.sh`,
   - `xaas-ash-build-ecosystem.sh`,
   - `xaas-ash-build-extend-GENERATED.sh`,
   - `xaas-ash-build-changes-GENERATED.sh`,
   - `xaas-ash-build-finishing.sh`.

The repaired program contains **211** Mix commands: 45 + 22 + 49 + 89 + 6. The additional command
is the explicit `igniter.add ash_onetime` transition.

## Repository verifier repair

Adding `autofde-gymact-certification-pack` caused the deterministic gym court to refuse the new pack
set. `scripts/verify-gym-packs.py` now admits that exact pack identity/version/files and checks its
certification vocabulary, evidence-integrity refusal tokens, and qualification fixture. A mutation
falsifier was added for the evidence-integrity rule.

Exact-head Gym pack contract subsequently passed receipt manufacture, deterministic replay, all
mutation falsifiers, and marketplace closure.

The workflow itself is now bounded with `timeout-minutes: 5`, satisfying the repository's timeout
coverage invariant without weakening the verifier.

## Current standing

| Surface | Standing |
|---|---|
| Original 210-command speedrun | `PARTIAL_ALIVE` — 208/210 observed |
| Two exact source repairs | `CHANGED` |
| Repaired 211-command end-to-end run | `NOT YET EXECUTED` |
| Gym deterministic court at repaired exact head | `ALIVE` |
| Public-ontology-first XaaS semantic closure | `PARTIAL_ALIVE` — public profile exists; CQ coverage still open |

The next crown requires observed execution of the repaired 211-command subject against the exact
admitted Ash project/toolchain. Source edits, compilation of the older target, and green repository
Gym CI do not substitute for that subject-level execution.
