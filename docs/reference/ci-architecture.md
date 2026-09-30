# CI architecture

Exact contract of `.github/workflows/ci.yml` and the court index it executes. Values that are
operationally owned (ggen release, workers, timeouts) live in `marketplace.toml` and are read only
after admission; this page does not copy them.

## Lanes

| Job | Runs when | Consumes | Produces |
|---|---|---|---|
| `plan` | always | exact head + bounded base history | `qualify` output from `scripts/ci_plan.py plan` |
| `verify` | always | exact head | admission receipt, validate, hygiene, catalog/archive determinism, path-selected courts |
| `qualify` (shards 0–3) | `plan.qualify == true` | exact head, admitted config | per-shard qualification receipt |
| `tests` | always (advisory) | exact head, admitted config | full pytest result |
| `ci-status` | always | `plan`, `verify`, `qualify` results | the single aggregate check |

`verify`, `qualify` and `tests` do not consume each other's artifacts, so they run concurrently
after checkout. `ci-status` is the only required-check candidate; it refuses a skipped `qualify` lane
unless `plan` said the lane was not needed.

## Triggers and supersession

`pull_request` to `main`, `push` to `main`, nightly `schedule`, `workflow_dispatch`. A new PR commit
cancels the superseded run; pushes to `main` run to completion so they seed caches. Nightly and
manual runs execute **every** court and lane (`--all`).

## Court index

`ci/courts.json` is an ordered list of `{name, paths, timeout_minutes}`; `ci/courts/<name>.sh` is the
court body. `paths` use GitHub `paths:` glob semantics (`**` crosses `/`, `*` and `?` do not). A court
runs when a changed path matches, when CI infrastructure changed (`ci/`, `.github/actions/`,
`.github/workflows/ci.yml`, `scripts/ci_plan.py`), or on a full run. Courts run in parallel with a
private `RUNNER_TEMP`/`TMPDIR` each and must be pure verification: no network, no package
installation, no writes to the subject. A dirty tree after the run is `REFUSED:COURT_MUTATED_SUBJECT`.

## Plan inputs

`scripts/ci_plan.py plan --base <sha> [--head <sha>] [--all]` emits `{full, changed_files, courts,
qualify}`. The diff anchor is the merge base when reachable, else the two-dot diff (which can only
over-select). An unknown base (new branch, schedule, dispatch) means a full run. The `qualify` lane is
selected when a changed path is under `packs/`, `scripts/`, `tools/`, `ci/`, `.github/`, or is
`marketplace.toml`, `rust-toolchain.toml`, `ggen.toml`, `ggen.lock`.

## Caches (optimization only)

| Cache | Key schema | Writer | Miss behaviour |
|---|---|---|---|
| admission binary (`~/.cache/marketplace-config-bin`) | OS, arch, hash of `tools/marketplace-config/**` and `rust-toolchain.toml` | `push` to `main` only | install the pinned toolchain, build from source, run |

Pull requests restore default-branch state read-only. `scripts/admit-config.sh` honours
`GGEN_MARKETPLACE_CONFIG_BIN` when it names an executable and otherwise builds from source; both paths
produce byte-identical receipts.

## Dependencies

`ci/requirements.txt` is the single pinned Python dependency set for `verify` and `tests`. A court
that needs a different version, a toolchain, or the network is not a court; keep it as its own
workflow.

## See Also

- [Workflow map](workflow-map.md)
- [How to add or migrate a CI court](../how-to/add-a-ci-court.md)
- [Why CI is path-classified and consolidated](../explanation/why-ci-is-path-classified.md)
