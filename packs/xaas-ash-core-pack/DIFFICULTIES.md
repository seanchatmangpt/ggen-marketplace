# xaas-ash-core-pack — Real Build Difficulties (Speedrun, Explore Pass)

Target project: `/Users/sac/dev-fresh/xaas`. Logs: `/tmp/xaas-speedrun/part{1..5}.log`,
`/tmp/xaas-speedrun/final_{compile,test}.log`. Ash 3.32.0.

## 1. Real run stats table

| Part | Script | Attempted | Succeeded | Failed | Skipped | Timed out |
|---|---|---|---|---|---|---|
| 1 — base | `xaas-ash-build-base-GENERATED.sh` | 45 | 45 | 0 | 0 | 0 |
| 2 — ecosystem | `xaas-ash-build-ecosystem.sh` | 21 | 20 | 1 | 0 | 0 |
| 3 — extend | `xaas-ash-build-extend-GENERATED.sh` | 49 | 49 | 0 | 0 | 0 |
| 4 — changes | `xaas-ash-build-changes-GENERATED.sh` | 89 | 89 | 0 | 0 | 0 |
| 5 — finishing | `xaas-ash-build-finishing.sh` | 6 | 5 | 1 | 0 | 0 |
| **Total** | | **210** | **208** | **2** | **0** | **0** |

Note on the "217" figure: the task brief's count comes from the non-GENERATED original
scripts, which include 4 `mix ash.gen.domain` lines (`Xaas.Operations`, `.Governance`,
`.Billing`, `.Platform`) that the GENERATED base script omits entirely. The GENERATED
variant used for this run (per instructions: prefer GENERATED) totals 210 real commands,
not 217. `mix ash.gen.resource --domain X` auto-creates the domain module when absent, so
the missing 4 domain-creation lines did not block any of the 44 resource-generation
commands — all 44 succeeded with the domain implicitly created on first reference.

## 2. Chronological difficulty log

### Failure 1 — Part 2, line 18

Command: `mix igniter.install ash_onetime --yes`
Script: `xaas-ash-build-ecosystem.sh`, line 18

```
The following installers did not exist or could not be found.
If you chose not to install dependencies, this will be true for any uninstalled packages.
```

Exit code: 1. What happened next: skipped, continued to the remaining 19 installers in
Part 2 plus the trailing `mix compile`, all of which succeeded.

### Failure 2 — Part 5, line 5

Command: `mix ash.generate_resource_diagrams --yes`
Script: `xaas-ash-build-finishing.sh`, line 5

```
** (Mix) Could not invoke task "ash.generate_resource_diagrams": 1 error found!
--yes : Unknown option

Supported options:
  --format STRING (alias: -f)
  --only STRING (alias: -o) (may be given more than once)
  --type STRING (alias: -t)
```

Exit code: 1. What happened next: skipped, continued to the final `mix compile` in Part 5,
which succeeded.

No other command in any of the 5 parts failed. No command hit the 3-minute timeout
(slowest observed: `ash_double_entry` install at 59s).

## 3. Root-cause clusters

**Cluster A — nonexistent package name (1 occurrence: Failure 1).**
`ash_onetime` is not a published Hex package. This is a bad literal string in
`xaas-ash-build-ecosystem.sh` line 18, not a version conflict, not a network issue, not an
environment issue. Evidence: igniter's own error text distinguishes "did not exist" from a
dependency-resolution failure, and every other `igniter.install` call in the same script
against real package names (ash_postgres, ash_authentication,
ash_authentication_phoenix, ash_json_api, ash_graphql, ash_admin, ash_oban,
ash_state_machine, ash_paper_trail, ash_events, ash_archival, ash_double_entry, ash_money,
ash_cloak, cloak, ash_rate_limiter, ash_iam, ash_ai, opentelemetry_ash) succeeded.

**Cluster B — flag doesn't exist on this task (1 occurrence: Failure 2).**
`--yes` is not a supported option for `mix ash.generate_resource_diagrams` in the
installed Ash/ash_admin version; the task's own `--help`-style error lists the real
supported flags (`--format`, `--only`, `--type`), none of which is `--yes`. This is a
script bug (wrong flag) against a real, existing task — not a missing dependency and not a
version-compatibility break in the sense of "this Ash version doesn't have this feature."

**Clusters not observed.** The task brief named three other candidate failure classes
("version conflict between installers", "resource name collision", "two installers
touching the same file") as things to watch for. None occurred in this run: all 19 real
ecosystem installs, all 48 per-resource `ash.extend ... postgres,json_api,graphql` calls,
all 4 domain-level `ash.extend ... json_api,graphql` calls, and all 88 `gen.change`/
`gen.validation` commands in Part 4 completed with 0 failures. No evidence of those classes
exists in this run's logs — not reported here as fixed or ruled out for other runs, only as
absent from what was actually observed.

## 4. What Exploit mode should fix first

Ordered by how many of the 210 commands actually run each fix would unblock — both fixes
unblock exactly 1 previously-failing command each, so ordering here is by which failure sits
earlier in the pipeline (Part 2 before Part 5) and blocks a smaller downstream surface if
left broken:

1. **Fix `xaas-ash-build-ecosystem.sh` line 18** — remove or replace the
   `mix igniter.install ash_onetime --yes` line (no real package by that name exists on
   Hex). Unblocks 1/210 commands directly; sits in Part 2, so leaving it broken means every
   future run of the ecosystem script keeps hard-failing on line 18 before reaching the 19
   real installers that follow it in file order (this run tolerated it only because the
   runner kept going after the failure — a strict runner would stop the whole part here).

2. **Fix `xaas-ash-build-finishing.sh` line 5** — drop `--yes` from
   `mix ash.generate_resource_diagrams` (task doesn't accept it; real supported flags are
   `--format`, `--only`, `--type`). Unblocks 1/210 commands. Lower priority than #1 only
   because it is the last part of the pipeline (Part 5) — a hard stop here does not block
   any other command from running, since it's followed only by the final `mix compile`
   which this run reached and passed regardless.

No other fix is justified by this run's evidence — every other command class (44 resource
generations, 19 real installers, 52 extend calls, 88 change/validation generators) came
through clean.

## 5. Final real state

Re-ran `mix compile` in `/Users/sac/dev-fresh/xaas` at the end of this run: clean, no
output, exit 0. The project is compiling clean right now, as of the end of this run —
confirmed by direct re-run, not carried forward from the earlier log.
