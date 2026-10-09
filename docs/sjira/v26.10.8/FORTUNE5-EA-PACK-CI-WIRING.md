# Fortune 5 EA pack test battery — CI wiring (R21)

The fortune5-enterprise-architecture-pack pytest battery (96 tests under
`packs/fortune5-enterprise-architecture-pack/tests/`, 96 passed / 0 failed
locally 2026-10-09) was previously runnable only on demand. It is now wired
into CI via `.github/workflows/fortune5-ea-pack-tests.yml`, which runs
`python3 -m pytest packs/fortune5-enterprise-architecture-pack/tests/ -q` on
push and pull_request to `hdit-v2-structs` and `main` (path-filtered to the
pack plus the workflow file; `workflow_dispatch` included). The workflow
follows the in-repo convention used by the card-ci lane (exact-head checkout
`actions/checkout@3d3c42e5` v7.0.1, `actions/setup-python@5fda3b95` v7.0.0
with Python 3.12, `permissions: contents: read`, concurrency group) as
established in chicago-work-equivalent.yml. Expected first run: on the push of
this commit to `hdit-v2-structs` (push event, paths match).

First witnessed run: BLOCKED (CI infrastructure, not test failures). Run
37949490109 (push, main, 2026-10-09T15:08:34Z, 13s, conclusion failure) and
37948179144 (push, hdit-v2-structs, 14:58:21Z, 13s, failure) both failed in
the "Run pack test battery" step with `/opt/hostedtoolcache/Python/3.12.15/x64/bin/python3: No module named pytest` — the workflow never installs
pytest before invoking it. Triage: workflow defect, fix is a
`python3 -m pip install pytest` step (or `pip install -e` of the pack's test
deps) before the pytest step. Not debugged further per lane scope.
