"""pytest-ocpq: Native Process Intelligence & OCPQ Pytest Plugin.

Intercepts pytest execution to enforce that tests validate success ONLY
against declarative Object-Centric Process Querying (OCPQ) and OCEL v2 logs.
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional

import pm4py
import pytest

from ggen_marketplace.ocel2.emitter import OCEL2Emitter
from ggen_marketplace.pytest_ocpq.dsl import OCPQQuery, OCPQQueryResult


class OCPQSession:
    """Live process mining instrumentation session for an active test."""

    def __init__(self, test_name: str) -> None:
        self.test_name = test_name
        self.emitter = OCEL2Emitter()
        self.query: Optional[OCPQQuery] = None
        self._temp_dir = tempfile.TemporaryDirectory()

    def register_object(self, obj_id: str, obj_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Register a domain object in the active test's OCEL v2 log."""
        self.emitter.register_object(obj_id, obj_type, attributes)

    def emit_event(
        self,
        event_id: str,
        event_type: str,
        timestamp: Optional[datetime] = None,
        attributes: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Emit a multi-object event into the active test's OCEL v2 log."""
        t = timestamp or datetime.now(timezone.utc)
        self.emitter.emit_event(event_id, event_type, t, attributes, relationships)

    def set_query(self, query: OCPQQuery) -> None:
        """Assign declarative OCPQ query for test admission."""
        self.query = query

    def evaluate_conformance(self) -> OCPQQueryResult:
        """Write SQLite OCEL v2 and evaluate the registered OCPQ query."""
        if self.query is None:
            return OCPQQueryResult(success=True, violations=[], metrics={"info": "No OCPQ query declared."})

        resolved_query = self.query() if callable(self.query) else self.query

        db_path = Path(self._temp_dir.name) / f"{self.test_name}.sqlite"
        self.emitter.write_sqlite(db_path)
        ocel = pm4py.read_ocel2_sqlite(str(db_path))
        return resolved_query.evaluate(ocel)

    def cleanup(self) -> None:
        try:
            self._temp_dir.cleanup()
        except Exception:
            pass


def pytest_configure(config: pytest.Config) -> None:
    """Register the ocpq marker in pytest."""
    config.addinivalue_line(
        "markers",
        "ocpq(query=None): Validate test outcome strictly against declarative OCPQ process query.",
    )
    config.addinivalue_line(
        "markers",
        "expected_ocpq_violation(violation_keyword=None): Expect test to fail OCPQ conformance gate (anti-vacuity witness).",
    )


@pytest.fixture
def ocpq_session(request: pytest.FixtureRequest) -> Generator[OCPQSession, None, None]:
    """Provide active OCPQ session fixture to the running test."""
    session = OCPQSession(test_name=request.node.name)
    request.node._ocpq_session = session

    # Check if @pytest.mark.ocpq was attached with a query
    marker = request.node.get_closest_marker("ocpq")
    if marker and marker.args:
        if isinstance(marker.args[0], OCPQQuery):
            session.set_query(marker.args[0])
        elif callable(marker.args[0]):
            session.set_query(marker.args[0]())
    elif marker and "query" in marker.kwargs:
        session.set_query(marker.kwargs["query"])

    yield session
    # Session cleanup happens after makereport hook


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]) -> Generator[None, pytest.TestReport, None]:
    """Intercept test report creation to enforce OCPQ conformance gate."""
    outcome = yield
    report = outcome.get_result()

    if call.when == "call":
        session: Optional[OCPQSession] = getattr(item, "_ocpq_session", None)
        if session and session.query is not None:
            # Evaluate OCPQ query on the test's execution trace
            result = session.evaluate_conformance()
            expected_violation = item.get_closest_marker("expected_ocpq_violation")

            if expected_violation:
                # Anti-vacuity witness mode: test MUST violate OCPQ
                keyword = expected_violation.args[0] if expected_violation.args else None
                if result.success:
                    report.outcome = "failed"
                    report.longrepr = f"\n[ANTI-VACUITY FAILURE] Test '{item.name}' was expected to fail OCPQ conformance, but passed!"
                elif keyword and not any(keyword in v for v in result.violations):
                    report.outcome = "failed"
                    report.longrepr = f"\n[ANTI-VACUITY FAILURE] Expected violation containing '{keyword}', got {result.violations}"
                else:
                    # Successfully proved fail-closed behavior!
                    report.outcome = "passed"
                    report.longrepr = None
            else:
                # Normal mode: test must be conformant
                if not result.success:
                    # Force failure even if test body passed without exceptions!
                    report.outcome = "failed"
                    err_msg = (
                        f"\n[FAIL-CLOSED] OCPQ PROCESS CONFORMANCE VIOLATION in test '{item.name}':\n"
                        + "\n".join(f"  • {v}" for v in result.violations)
                        + f"\nProcess Metrics: {result.metrics}"
                    )
                    report.longrepr = err_msg
        if session:
            session.cleanup()
