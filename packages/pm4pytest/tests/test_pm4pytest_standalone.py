"""Standalone Chicago-School Test Court for pm4pytest Package.

Verifies:
1. Petri net token-based replay fitness and alignment conformance gates.
2. Anti-vacuity fail witness on invalid state machine transitions.
3. Multi-object OCPQ graph traversals (GcpEntitlement -> A2AExecutionTask -> McpToolCall).
4. Temporal SLA latency bounds and anti-vacuity SLA breach fail witness.

ZERO MOCKS. Real PM4Py Inductive Miner discovery, real Token-Based Replay, real SQLite OCEL v2.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from pm4pytest import OCPQ, ConformanceSpec, PM4PySession, TemporalSLA


class TestPM4PytestStandaloneCourt:
    """Comprehensive Chicago-school test court for pm4pytest."""

    @pytest.mark.conformance(
        spec=lambda: ConformanceSpec.from_fsm(
            valid_paths=[
                ["SUBMITTED", "WORKING", "COMPLETED"],
                ["SUBMITTED", "WORKING", "INPUT_REQUIRED", "WORKING", "COMPLETED"],
            ],
            min_fitness=1.0,
        )
    )
    def test_petri_net_alignment_conformance_passes(self, pm4py_session: PM4PySession) -> None:
        """Prove that a valid swarm saga satisfies Petri net alignment conformance."""
        t0 = datetime.now(timezone.utc)
        pm4py_session.emit_event("e1", "SUBMITTED", t0)
        pm4py_session.emit_event("e2", "WORKING", t0 + timedelta(seconds=1))
        pm4py_session.emit_event("e3", "COMPLETED", t0 + timedelta(seconds=2))
        # Success validated solely by Petri net fitness = 1.0!

    @pytest.mark.conformance(
        spec=lambda: ConformanceSpec.from_fsm(
            valid_paths=[["SUBMITTED", "WORKING", "COMPLETED"]],
            min_fitness=0.99,
        )
    )
    @pytest.mark.expected_conformance_violation("PETRI_NET_FITNESS_VIOLATION")
    def test_invalid_transition_fails_conformance(self, pm4py_session: PM4PySession) -> None:
        """Anti-vacuity witness: An illegal bypass (SUBMITTED -> COMPLETED without WORKING) fails closed."""
        t0 = datetime.now(timezone.utc)
        pm4py_session.emit_event("e1", "SUBMITTED", t0)
        # Missing mandatory WORKING state!
        pm4py_session.emit_event("e2", "COMPLETED", t0 + timedelta(seconds=1))

    @pytest.mark.ocpq(
        query=lambda: (
            OCPQ()
            .require_activity("GCP_ENTITLEMENT_ACTIVATED", min_count=1)
            .require_activity("MCP_TOOL_INVOKED", min_count=1)
            .require_balanced_ratio("MCP_TOOL_INVOKED", "GCP_METERING_REPORTED", expected_ratio=1.0)
            .traverse("GcpEntitlement", "A2AExecutionTask", "McpToolCall")
        )
    )
    def test_ocpq_multi_object_traversal_passes(self, pm4py_session: PM4PySession) -> None:
        """Prove that multi-object causal traversal passes OCPQ validation."""
        pm4py_session.register_object("ent-01", "GcpEntitlement")
        pm4py_session.register_object("task-01", "A2AExecutionTask")
        pm4py_session.register_object("tool-01", "McpToolCall")

        t0 = datetime(2026, 10, 4, 18, 0, 0, tzinfo=timezone.utc)
        t1 = datetime(2026, 10, 4, 18, 1, 0, tzinfo=timezone.utc)
        t2 = datetime(2026, 10, 4, 18, 2, 0, tzinfo=timezone.utc)

        pm4py_session.emit_event(
            "e1",
            "GCP_ENTITLEMENT_ACTIVATED",
            t0,
            relationships=[{"objectId": "ent-01"}, {"objectId": "task-01"}],
        )
        pm4py_session.emit_event(
            "e2",
            "MCP_TOOL_INVOKED",
            t1,
            relationships=[{"objectId": "task-01"}, {"objectId": "tool-01"}],
        )
        pm4py_session.emit_event(
            "e3",
            "GCP_METERING_REPORTED",
            t2,
            relationships=[{"objectId": "ent-01"}],
        )

    @pytest.mark.temporal_sla(
        sla=lambda: TemporalSLA().require_max_latency("SUBMITTED", "WORKING", max_seconds=2.0)
    )
    def test_temporal_sla_within_bounds_passes(self, pm4py_session: PM4PySession) -> None:
        """Prove that activity execution within SLA bounds passes."""
        t0 = datetime.now(timezone.utc)
        pm4py_session.emit_event("e1", "SUBMITTED", t0)
        pm4py_session.emit_event("e2", "WORKING", t0 + timedelta(seconds=1.2))

    @pytest.mark.temporal_sla(
        sla=lambda: TemporalSLA().require_max_latency("SUBMITTED", "WORKING", max_seconds=1.0)
    )
    @pytest.mark.expected_conformance_violation("TEMPORAL_SLA_BREACH")
    def test_temporal_sla_breach_fails_closed(self, pm4py_session: PM4PySession) -> None:
        """Anti-vacuity witness: Latency exceeding SLA bound (3.5s > 1.0s) fails closed."""
        t0 = datetime.now(timezone.utc)
        pm4py_session.emit_event("e1", "SUBMITTED", t0)
        pm4py_session.emit_event("e2", "WORKING", t0 + timedelta(seconds=3.5))
