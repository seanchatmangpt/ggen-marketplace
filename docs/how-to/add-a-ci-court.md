# How to add or migrate a CI court

A court is a bounded, pure verification of one pack's claim. Add one when a pack needs a check the
generic admission does not perform. Do not add a workflow file for it.

## 1. Write the court body

Create `ci/courts/<name>.sh`. It runs from the repository root under `bash -euo pipefail`, may use
`python` with the packages in `ci/requirements.txt`, and must not touch the network, install
packages, or modify tracked or untracked files. Write scratch output under `"$RUNNER_TEMP"`.

## 2. Register it

Append to `ci/courts.json`:

```json
{ "name": "<name>", "paths": ["packs/<pack>/**"], "timeout_minutes": 10 }
```

`paths` decide which pull requests run it; nightly runs always do.

## 3. Run it locally

```bash
python3 -m venv /tmp/ci-venv && /tmp/ci-venv/bin/pip install -r ci/requirements.txt
PATH=/tmp/ci-venv/bin:$PATH python3 scripts/ci_plan.py run --all     # every court
PATH=/tmp/ci-venv/bin:$PATH python3 scripts/ci_plan.py run --base origin/main
```

## 4. When it is not a court

If the check needs a compiler toolchain, a differently pinned dependency, Docker, or the network, keep
a dedicated workflow for it (with `permissions`, `timeout-minutes` and SHA-pinned actions) and add a
`paths:` filter so it does not run on unrelated pull requests.

## See Also

- [CI architecture](../reference/ci-architecture.md)
- [Validate locally](validate-locally.md)
