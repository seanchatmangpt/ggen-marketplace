# xaas-ash-core-pack — Ash construction research + executable generator proof

This pack is the Ash-side construction proof for XaaS. It captures the canonical Ash/Igniter
techniques researched from Ash 3.32.0, the wider Ash ecosystem archive, and a real 210-command
speedrun against `/Users/sac/dev-fresh/xaas`.

The architectural boundary is:

```text
public semantic authorities -> admitted/profiled O* -> ggen -> Ash construction program
                           -> Ash/Igniter -> Ash source/runtime
```

Ash/Igniter owns Ash source mutation. ggen renders constructor intent; it does not hand-render
`.ex` files when an Ash/Igniter constructor exists.

> **Important semantic boundary:** this pack's current `xar:` render-hint graph is a transitional
> construction proof derived from 44 platform-console capability instances. It is **not** the
> canonical XaaS domain ontology. `packs/xaas-public-ontology-profile/` is the public-ontology-first
> semantic profile; native/private render hints must not be promoted into public domain semantics.

## Canonical runner

Run the master program against an existing Ash project:

```sh
bash xaas-ash-build-all.sh /path/to/ash-project
```

The runner refuses when the target does not contain `mix.exs` and preserves the target project as
its working directory. It invokes the ggen-rendered variants for every row-driven stage.

| Part | Canonical program | Mix commands | Status from original speedrun |
|---|---|---:|---|
| 1 | `xaas-ash-build-base-GENERATED.sh` | 45 | 45/45 passed |
| 2 | `xaas-ash-build-ecosystem.sh` | 22 | original 20/21 passed; failing `ash_onetime` invocation corrected |
| 3 | `xaas-ash-build-extend-GENERATED.sh` | 49 | 49/49 passed |
| 4 | `xaas-ash-build-changes-GENERATED.sh` | 89 | 89/89 passed |
| 5 | `xaas-ash-build-finishing.sh` | 6 | original 5/6 passed; diagram flag corrected |
| **Total** | | **211** | original run: 208/210; two observed defects repaired in source |

The total changed from 210 to 211 because `ash_onetime` is now installed in two explicit canonical
steps: add/fetch the dependency, then invoke the package's own installer task.

## What ggen currently renders

`ggen.toml` has three real `ggen sync` rules:

1. `ontology.ttl` + `queries/render-targets.rq` -> `xaas-ash-build-base-GENERATED.sh`
2. the same admitted row set -> `xaas-ash-build-extend-GENERATED.sh`
3. the same admitted row set -> `xaas-ash-build-changes-GENERATED.sh`

The generated scripts were previously proven set-equivalent to their hand-assembled predecessors.
The master runner now executes the generated forms, not the hand-assembled copies.

The ecosystem installation and finishing stages remain fixed cross-cutting command programs because
they are project-wide operations, not one operation per capability row.

## Corrected speedrun findings

The real speedrun is recorded in `DIFFICULTIES.md`. Two commands failed:

### 1. `ash_onetime`

The original diagnosis in `DIFFICULTIES.md` incorrectly called `ash_onetime` nonexistent. The
primary-source archive in this same pack disproves that: `vendor-readmes/ash_onetime.md` documents
published `ash_onetime` v1.0.0 and its canonical installer:

```sh
mix ash_onetime.install
```

The observed failure was therefore an **installer-discovery/invocation failure**, not package
nonexistence. The corrected program is:

```sh
mix igniter.add ash_onetime
mix ash_onetime.install
```

This first makes the dependency/task available and then invokes the package's own documented
Igniter-powered installer.

### 2. Resource diagrams

The installed `ash.generate_resource_diagrams` task rejected `--yes`; its observed supported options
were `--format`, `--only`, and `--type`. The finishing program now invokes:

```sh
mix ash.generate_resource_diagrams
```

with no fabricated global flag.

## Ash ecosystem surfaces admitted by the build research

The build includes or evaluates the following capability families using real packages rather than
inventing XaaS-specific replacements where an Ash implementation already exists:

- persistence: AshPostgres;
- identity: AshAuthentication + AshAuthenticationPhoenix;
- API projection: AshJsonApi + AshGraphql;
- operator UI: AshAdmin;
- durable jobs: AshOban;
- lifecycle: AshStateMachine;
- audit/replay: AshPaperTrail + AshEvents;
- archival: AshArchival;
- economics: AshMoney + AshDoubleEntry;
- encryption: AshCloak + Cloak;
- throttling: AshRateLimiter;
- policy evaluation: AshIAM plus core `Ash.Policy.Authorizer`;
- keyed-effect admission: AshOnetime;
- agent/tool projection: AshAI;
- observability: OpenTelemetryAsh, retained with an explicit compatibility warning.

`vendor-readmes/` preserves the primary-source package corpus used for this research, including the
full Hex dependency census captured during the session.

## Known boundary still to close

The old 44-capability `xar:` rendering graph is a **construction experiment**, not the final semantic
source. The next semantic closure is intentionally upstream of Ash:

```text
packs/xaas-public-ontology-profile/
  -> exact public ontology locks
  -> competency-question coverage
  -> SHACL application profile over public classes/properties
  -> generic SPARQL construction view
  -> ggen-rendered Ash commands
```

No `xar:` class/property is allowed to become a business/domain concept merely because it is
convenient for generation. Public terms are preferred; an XaaS-native term must be earned by a
competency question that remains unsatisfied after public ontology composition is exhausted.

## Acceptance

Current source-level acceptance for this pack is:

1. master runner executes the ggen-rendered base/extend/change programs;
2. the target project is explicit and must contain `mix.exs`;
3. the two exact failures from the real speedrun are repaired without weakening checks;
4. `scripts/verify-gym-packs.py` admits the new AutoFDE GymAct certification pack while preserving
   deterministic receipt, replay, and mutation-falsifier semantics;
5. repository exact-head CI/Vacuity/Gym checks remain the publication gates.

A fresh 211-command execution against the exact repaired scripts is still required before claiming
`ALIVE` for the full Ash construction program. The previous observed run is evidence for 208/210
commands on the pre-repair subject, not a substitute for a post-repair rerun.
