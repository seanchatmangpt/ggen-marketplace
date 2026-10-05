# pm4pytest

**pm4pytest** is an autonomous Process Intelligence, Conformance Checking, and Object-Centric Process Querying (OCPQ) engine powered by [PM4Py](https://pm4py.fit.fraunhofer.de/).

It provides:
1. **Native Pytest Plugin (`pytest-pm4pytest`)**: Execute Chicago-school tests whose success is determined solely against Petri net fitness, state alignment costs, temporal SLAs, and multi-object causal graphs.
2. **Standalone Binary / Universal CLI (`pm4pytest` / `pm4pytest-cli`)**: Universal test runner that can be called from **any programming language** (Rust kernels, Elixir OTP, Go, C++, Shell scripts, CI/CD runners) outputting standard formats:
   - **TAP v13 (Test Anything Protocol)** with structured YAML diagnostic blocks.
   - **JUnit XML** for direct ingestion by GitHub Actions, GitLab CI, and GCP Cloud Build.
   - **JSON** machine-parseable results.
   - **Strict Exit Codes**: `0` on conformance, `1` on violation, `2` on syntax/config error.

---

## Universal Testing Standards

Process intelligence is polyglot. Swarms emit IEEE OCEL v2 logs across heterogeneous substrates:
- `A2A` agents orchestrated in Elixir/Ash.
- Core mathematical kernels in Rust.
- Commercial gateway proxies in Envoy/Go.

By packaging `pm4pytest` as a standalone binary CLI supporting standard test protocols, external processes can verify traces without writing Python:

```bash
# Verify Petri Net conformance via TAP stream:
pm4pytest check-conformance \
  --log /var/log/traces/session.sqlite \
  --fsm "order_created,payment_cleared,entitlement_delivered" \
  --min-fitness 1.0 \
  --format tap

# Verify Temporal Latency SLA with JUnit XML report for CI/CD:
pm4pytest check-sla \
  --log /var/log/traces/session.sqlite \
  --sla "order_created:payment_cleared:30.0" \
  --junitxml /tmp/reports/sla_report.xml

# Execute OCPQ multi-object causal graph queries:
pm4pytest query \
  --log /var/log/traces/session.sqlite \
  --traverse "Order,Agent,ToolCall" \
  --require-activity "order_created" \
  --format tap
```

### Sample TAP v13 Output

```text
TAP version 13
1..1
ok 1 - conformance_fsm_order_created,payment_cleared,entitlement_delivered
  ---
  fitness: 1.0
  min_fitness: 1.0
  violations: []
  diagnostics: {"tbr_fitness": {"log_fitness": 1.0, "perc_fit_traces": 100.0}}
  ...
```

---

## Pytest Plugin Usage

In Python environments, tests can use pytest fixtures and markers:

```python
import pytest
from pm4pytest import ConformanceSpec, PM4PySession

@pytest.mark.conformance(
    spec=lambda: ConformanceSpec.from_fsm(
        valid_paths=[["SUBMITTED", "WORKING", "COMPLETED"]],
        min_fitness=1.0,
    )
)
def test_saga_conformance(pm4py_session: PM4PySession):
    pm4py_session.emit_event("e1", "SUBMITTED")
    pm4py_session.emit_event("e2", "WORKING")
    pm4py_session.emit_event("e3", "COMPLETED")
```
