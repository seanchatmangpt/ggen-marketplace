"""Chicago-School Test Court for pytest-ocpq Process Intelligence Plugin.

Validates that tests validate success ONLY against declarative OCPQ queries:
1. Positive OCPQ query passes when multi-object process invariants hold.
2. Anti-vacuity fail witness: test body runs without exceptions, but fails closed
   because an OCPQ activity or balanced ratio was violated.
3. Multi-object traversal validation (GcpEntitlement -> A2AExecutionTask -> McpToolCall).
4. Balanced metering query enforcement (unmetered tool execution fails closed).

ZERO MOCKS. Real PM4Py execution and in-process SQLite OCEL v2 logs.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from ggen_marketplace.pytest_ocpq.dsl import OCPQQuery
from ggen_marketplace.pytest_ocpq.plugin import OCPQSession


class TestPytestOCPQPluginValidation:
    """Rigorous verification court for the pytest-ocpq plugin."""

    @pytest.mark.ocpq(
        query=lambda: (
            OCPQQuery()
            .require_activity("GCP_ENTITLEMENT_ACTIVATED", min_count=1)
            .require_activity("MCP_TOOL_INVOKED", min_count=1)
            .require_object_type("GcpEntitlement", "McpToolCall")
            .require_balanced_ratio("MCP_TOOL_INVOKED", "GCP_METERING_REPORTED", expected_ratio=1.0)
            .traverse("GcpEntitlement", "A2AExecutionTask", "McpToolCall")
        )
    )
    def test_ocpq_full_swarm_causal_chain_passes(self, ocpq_session: OCPQSession) -> None:
        """Prove that a fully compliant multi-object execution trace passes the OCPQ gate."""
        # 1. Register domain objects
        ocpq_session.register_object("ent-gcp-99", "GcpEntitlement", {"state": "ENTITLEMENT_ACTIVE"})
        ocpq_session.register_object("task-saga-101", "A2AExecutionTask", {"fsm": "WORKING"})
        ocpq_session.register_object("tool-search-01", "McpToolCall", {"tool": "search_packs"})
        ocpq_session.register_object("report-sc-01", "ServiceControlReport", {"amount": 4.50})

        t0 = datetime(2026, 10, 4, 17, 0, 0, tzinfo=timezone.utc)
        t1 = datetime(2026, 10, 4, 17, 1, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 10, 4, 17, 2, 0, tzinfo=timezone.utc)
        t3 = datetime(2026, 10, 4, 17, 3, 0, tzinfo=timezone.utc)

        # 2. Emit multi-object events
        ocpq_session.emit_event(
            "ev-1",
            "GCP_ENTITLEMENT_ACTIVATED",
            t0,
            relationships=[
                {"objectId": "ent-gcp-99", "qualifier": "activated"},
                {"objectId": "task-saga-101", "qualifier": "authorized"},
            ],
        )
        ocpq_session.emit_event(
            "ev-2",
            "MCP_TOOL_INVOKED",
            t1,
            relationships=[
                {"objectId": "task-saga-101", "qualifier": "caller"},
                {"objectId": "tool-search-01", "qualifier": "executed"},
            ],
        )
        ocpq_session.emit_event(
            "ev-3",
            "GCP_METERING_REPORTED",
            t2,
            relationships=[
                {"objectId": "ent-gcp-99", "qualifier": "billed"},
                {"objectId": "report-sc-01", "qualifier": "reported"},
            ],
        )

        # Note: No assert statement in test body! Success is validated ONLY against OCPQ query.

    @pytest.mark.ocpq(
        query=lambda: (
            OCPQQuery()
            .require_activity("MCP_TOOL_INVOKED", min_count=1)
            .require_activity("GCP_METERING_REPORTED", min_count=1)
            .require_balanced_ratio("MCP_TOOL_INVOKED", "GCP_METERING_REPORTED", expected_ratio=1.0)
        )
    )
    @pytest.mark.expected_ocpq_violation("ACTIVITY_COUNT_VIOLATION")
    def test_ocpq_in_session_anti_vacuity_fail_witness(self, ocpq_session: OCPQSession) -> None:
        """Anti-vacuity fail witness: Test runs cleanly, but evaluate_conformance() catches violations."""
        # Emit tool invocation WITHOUT metering event (Rogue unmetered execution)
        ocpq_session.register_object("tool-rogue-01", "McpToolCall")
        ocpq_session.emit_event(
            "ev-rogue",
            "MCP_TOOL_INVOKED",
            datetime.now(timezone.utc),
            relationships=[{"objectId": "tool-rogue-01"}],
        )

    @pytest.mark.ocpq(query=lambda: OCPQQuery().require_object_type("GcpEntitlement"))
    @pytest.mark.expected_ocpq_violation("OBJECT_TYPE_VIOLATION")
    def test_ocpq_missing_object_type_anti_vacuity(self, ocpq_session: OCPQSession) -> None:
        """Anti-vacuity fail witness: Query requires GcpEntitlement, but only tools were run."""
        ocpq_session.register_object("tool-only", "McpToolCall")
        ocpq_session.emit_event(
            "ev-tool",
            "MCP_TOOL_INVOKED",
            datetime.now(timezone.utc),
            relationships=[{"objectId": "tool-only"}],
        )
