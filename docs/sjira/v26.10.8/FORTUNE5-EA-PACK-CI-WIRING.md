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

## GREEN witness (R86, 2026-10-09)

The R85 BLOCKED triage was correct but incomplete: the runner lacked not only
pytest but three further dependency layers, each surfaced by a witnessed run:

1. Run 37972331878 (fix commit 2efd2d36f, `pip install pytest`): failed at
   plugin load — root `pyproject.toml` `[tool.pytest.ini_options]` addopts
   loads `ggen_marketplace.pytest_ocpq.plugin`, which imports `pm4py`
   (`No module named 'pm4py'`).
2. Run 37972493524 (fix commit ec1bb443b, `+ pm4py`): failed at collection —
   pack test modules import `rdflib` and `pyshacl` directly
   (`No module named 'rdflib'`, 6 collection errors).
3. Run 37972661395 (fix commit 9f1781ec9, `+ rdflib pyshacl`): 93 passed,
   3 failed — `test_provider_templates.py` imports `hcl2` inside test bodies
   (`No module named 'hcl2'`; PyPI name `python-hcl2`).
4. Run 37972875539 (fix commit 43615a4c6, `+ python-hcl2`): **GREEN**.

Final witnessed state: run **37972875539**, push on `hdit-v2-structs` at
commit `43615a4c6c9655bbc4e417144a9a2b6ce541ebd8`, conclusion **success**
(2026-10-09T18:23:39Z), log line `96 passed, 58 warnings in 6.88s`.
The workflow's "Install test dependencies" step now installs the full
third-party import surface of the pack battery (AST-verified: pytest, pm4py,
rdflib, pyshacl, python-hcl2). All are declared or used dependencies of the
repo; no test, threshold, or pathspec was relaxed.
