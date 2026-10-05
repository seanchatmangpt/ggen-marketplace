"""pm4pytest.plugin

Native Pytest 11 plugin integrating Process Intelligence, Conformance, and OCPQ.
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import pm4py
import pytest

from pm4pytest.conformance import ConformanceResult, ConformanceSpec
from pm4pytest.ocel import ProcessTraceCollector
from pm4pytest.ocpq import OCPQ, OCPQResult
from pm4pytest.temporal import TemporalResult, TemporalSLA


class PM4PySession:
    """Instrumentation session bound to an executing pytest test case."""

    def __init__(self, test_name: str) -> None:
        self.test_name = test_name
        self.collector = ProcessTraceCollector()
        self.ocpq_spec: Optional[OCPQ] = None
        self.conformance_spec: Optional[ConformanceSpec] = None
        self.temporal_spec: Optional[TemporalSLA] = None
        self._temp_dir = tempfile.TemporaryDirectory()

    def register_object(self, obj_id: str, obj_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Register a domain object in the test's process log."""
        self.collector.register_object(obj_id, obj_type, attributes)

    def emit_event(
        self,
        event_id: str,
        event_type: str,
        timestamp: Optional[datetime] = None,
        attributes: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Emit a process event with optional multi-object relationships."""
        self.collector.emit_event(event_id, event_type, timestamp, attributes, relationships)

    def set_ocpq(self, ocpq: OCPQ) -> None:
        """Assign OCPQ query specification."""
        self.ocpq_spec = ocpq

    def set_conformance(self, spec: ConformanceSpec) -> None:
        """Assign Petri net or FSM conformance specification."""
        self.conformance_spec = spec

    def set_temporal_sla(self, sla: TemporalSLA) -> None:
        """Assign temporal SLA specification."""
        self.temporal_spec = sla

    def evaluate_all(self) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Evaluate all declared process intelligence gates."""
        all_violations: List[str] = []
        all_metrics: Dict[str, Any] = {}

        # 1. Evaluate Conformance (Petri net / FSM)
        if self.conformance_spec is not None:
            raw_events = [
                {"concept:name": ev.type, "time:timestamp": ev.time, **ev.attributes}
                for ev in self.collector.events
            ]
            c_res = self.conformance_spec.evaluate(raw_events)
            all_metrics["conformance"] = {"fitness": c_res.fitness, "diagnostics": c_res.diagnostics}
            if not c_res.success:
                all_violations.extend(c_res.violations)

        # 2. Evaluate Temporal SLA
        if self.temporal_spec is not None:
            raw_events = [
                {"concept:name": ev.type, "time:timestamp": ev.time}
                for ev in self.collector.events
            ]
            t_res = self.temporal_spec.evaluate(raw_events)
            all_metrics["temporal_sla"] = t_res.latencies
            if not t_res.success:
                all_violations.extend(t_res.violations)

        # 3. Evaluate OCPQ
        if self.ocpq_spec is not None:
            db_path = Path(self._temp_dir.name) / f"{self.test_name}.sqlite"
            self.collector.write_sqlite(db_path)
            ocel = pm4py.read_ocel2_sqlite(str(db_path))
            o_res = self.ocpq_spec.evaluate(ocel)
            all_metrics["ocpq"] = o_res.metrics
            if not o_res.success:
                all_violations.extend(o_res.violations)

        return (len(all_violations) == 0), all_violations, all_metrics

    def cleanup(self) -> None:
        try:
            self._temp_dir.cleanup()
        except Exception:
            pass


def pytest_configure(config: pytest.Config) -> None:
    """Register pm4pytest markers."""
    config.addinivalue_line("markers", "ocpq(query=None): Validate test outcome against declarative OCPQ query.")
    config.addinivalue_line("markers", "conformance(spec=None): Validate test outcome against Petri net / FSM conformance.")
    config.addinivalue_line("markers", "temporal_sla(sla=None): Validate inter-activity latencies against temporal SLA bounds.")
    config.addinivalue_line("markers", "expected_conformance_violation(keyword=None): Expect test to fail process intelligence gate (anti-vacuity).")
    config.addinivalue_line("markers", "expected_ocpq_violation(keyword=None): Expect test to fail OCPQ query (anti-vacuity).")


@pytest.fixture
def pm4py_session(request: pytest.FixtureRequest) -> Generator[PM4PySession, None, None]:
    """Provide active PM4Py process mining session to the test."""
    session = PM4PySession(test_name=request.node.name)
    request.node._pm4py_session = session

    # Check markers
    ocpq_marker = request.node.get_closest_marker("ocpq")
    if ocpq_marker:
        arg = ocpq_marker.args[0] if ocpq_marker.args else ocpq_marker.kwargs.get("query")
        if arg:
            session.set_ocpq(arg() if callable(arg) else arg)

    conf_marker = request.node.get_closest_marker("conformance")
    if conf_marker:
        arg = conf_marker.args[0] if conf_marker.args else conf_marker.kwargs.get("spec")
        if arg:
            session.set_conformance(arg() if callable(arg) else arg)

    temp_marker = request.node.get_closest_marker("temporal_sla")
    if temp_marker:
        arg = temp_marker.args[0] if temp_marker.args else temp_marker.kwargs.get("sla")
        if arg:
            session.set_temporal_sla(arg() if callable(arg) else arg)

    yield session


@pytest.fixture
def ocpq_session(pm4py_session: PM4PySession) -> PM4PySession:
    """Backward-compatible fixture alias for pm4py_session."""
    return pm4py_session


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, pytest.TestReport, None]:
    """Intercept test report creation to enforce process intelligence gates."""
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        session: Optional[PM4PySession] = getattr(item, "_pm4py_session", None)
        if session:
            success, violations, metrics = session.evaluate_all()
            expected_violation = (
                item.get_closest_marker("expected_conformance_violation")
                or item.get_closest_marker("expected_ocpq_violation")
            )

            if expected_violation:
                keyword = expected_violation.args[0] if expected_violation.args else None
                if success:
                    report.outcome = "failed"
                    report.longrepr = f"\n[ANTI-VACUITY FAILURE] Test '{item.name}' was expected to fail process conformance, but passed!"
                elif keyword and not any(keyword in v for v in violations):
                    report.outcome = "failed"
                    report.longrepr = f"\n[ANTI-VACUITY FAILURE] Expected violation containing '{keyword}', got {violations}"
                else:
                    report.outcome = "passed"
                    report.longrepr = None
            else:
                if not success:
                    report.outcome = "failed"
                    err_msg = (
                        f"\n[FAIL-CLOSED] PM4PYTEST PROCESS CONFORMANCE VIOLATION in test '{item.name}':\n"
                        + "\n".join(f"  • {v}" for v in violations)
                        + f"\nProcess Diagnostics: {metrics}"
                    )
                    report.longrepr = err_msg

            session.cleanup()
