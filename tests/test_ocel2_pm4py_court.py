"""Chicago-School Test Court for OCEL v2, PM4Py, and OCPQ Integration.

Verifies:
1. Native OCEL v2 log emission (JSON-OCEL and relational SQLite) across the 6 core object types.
2. PM4Py object-centric ingestion, DFG discovery, and summary metrics.
3. Declarative OCPQ query evaluation traversing GcpEntitlement -> A2AExecutionTask -> McpToolCall.
4. Fail-closed conformance tripwires with concrete anti-vacuity fail witnesses ($q_{process} = 1$).

ZERO MOCKS. Real SQLite databases, real PM4Py execution, real multi-object topologies.
"""

from __future__ import annotations

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pm4py
import pytest

from ggen_marketplace.mining.engine import ProcessMiningEngine
from ggen_marketplace.ocel2 import OCEL2Emitter


@pytest.fixture
def sample_ocel_emitter() -> OCEL2Emitter:
    """Build a compliant multi-object AAIF swarm and GCP Marketplace event log."""
    emitter = OCEL2Emitter()

    # 1. Register domain objects
    emitter.register_object("cust-acme-corp", "CustomerAccount", {"committedSpendUsd": 250000.0})
    emitter.register_object("ent-gcp-enterprise-01", "GcpEntitlement", {"planId": "enterprise-swarm-tier", "state": "ENTITLEMENT_ACTIVE"})
    emitter.register_object("swarm-lead-coord", "SwarmCoordinator", {"leadAgent": "MarketplaceCoordinator"})
    emitter.register_object("task-a2a-001", "A2AExecutionTask", {"fsmState": "COMPLETED"})
    emitter.register_object("tool-mcp-search", "McpToolCall", {"toolName": "search_packs", "transport": "streamable_http"})
    emitter.register_object("report-service-control-01", "ServiceControlReport", {"operationId": "op-101", "metricName": "pack_compilations"})

    t0 = datetime(2026, 10, 4, 17, 0, 0, tzinfo=timezone.utc)
    t1 = datetime(2026, 10, 4, 17, 1, 0, tzinfo=timezone.utc)
    t2 = datetime(2026, 10, 4, 17, 2, 0, tzinfo=timezone.utc)
    t3 = datetime(2026, 10, 4, 17, 3, 0, tzinfo=timezone.utc)
    t4 = datetime(2026, 10, 4, 17, 4, 0, tzinfo=timezone.utc)

    # 2. Emit causal events with multi-object relationships
    emitter.emit_event(
        "ev-01",
        "GCP_ENTITLEMENT_REQUESTED",
        t0,
        relationships=[
            {"objectId": "cust-acme-corp", "qualifier": "buyer"},
            {"objectId": "ent-gcp-enterprise-01", "qualifier": "procured"},
        ],
    )
    emitter.emit_event(
        "ev-02",
        "GCP_ENTITLEMENT_ACTIVATED",
        t1,
        relationships=[
            {"objectId": "ent-gcp-enterprise-01", "qualifier": "activated"},
            {"objectId": "swarm-lead-coord", "qualifier": "unlocked"},
        ],
    )
    emitter.emit_event(
        "ev-03",
        "AAIF_SWARM_BOOTSTRAPPED",
        t2,
        relationships=[
            {"objectId": "swarm-lead-coord", "qualifier": "supervisor"},
            {"objectId": "task-a2a-001", "qualifier": "dispatched"},
        ],
    )
    emitter.emit_event(
        "ev-04",
        "MCP_TOOL_INVOKED",
        t3,
        relationships=[
            {"objectId": "task-a2a-001", "qualifier": "caller"},
            {"objectId": "tool-mcp-search", "qualifier": "invoked"},
        ],
    )
    emitter.emit_event(
        "ev-05",
        "GCP_METERING_REPORTED",
        t4,
        attributes={"revenueRealizedUsd": 15.0},
        relationships=[
            {"objectId": "ent-gcp-enterprise-01", "qualifier": "billed"},
            {"objectId": "report-service-control-01", "qualifier": "emitted"},
        ],
    )

    return emitter


class TestOCEL2EmissionAndStorage:
    """Court 1: Validates IEEE OCEL v2 log emission to JSON-OCEL and SQLite."""

    def test_json_and_sqlite_emission_and_pm4py_ingestion(self, sample_ocel_emitter: OCEL2Emitter) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            json_file = tmp / "swarm_log.json"
            sqlite_file = tmp / "swarm_log.sqlite"

            sample_ocel_emitter.write_json(json_file)
            sample_ocel_emitter.write_sqlite(sqlite_file)

            assert json_file.exists() and json_file.stat().st_size > 0
            assert sqlite_file.exists() and sqlite_file.stat().st_size > 0

            # Ingest via PM4Py
            ocel_json = pm4py.read_ocel2_json(str(json_file))
            ocel_sqlite = pm4py.read_ocel2_sqlite(str(sqlite_file))

            assert len(ocel_json.events) == 5
            assert len(ocel_sqlite.events) == 5
            assert len(ocel_json.objects) == 6
            assert len(ocel_sqlite.objects) == 6

            object_types = pm4py.ocel_get_object_types(ocel_sqlite)
            assert "CustomerAccount" in object_types
            assert "GcpEntitlement" in object_types
            assert "A2AExecutionTask" in object_types
            assert "McpToolCall" in object_types


class TestPM4PyProcessDiscovery:
    """Court 2: Validates PM4Py directly-follows graph extraction and object-centric metrics."""

    def test_pm4py_directly_follows_graph_discovery(self, sample_ocel_emitter: OCEL2Emitter) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            sqlite_file = tmp / "swarm_discovery.sqlite"
            sample_ocel_emitter.write_sqlite(sqlite_file)

            engine = ProcessMiningEngine(sqlite_file)
            summary = engine.get_summary()

            assert summary["events_count"] == 5
            assert summary["objects_count"] == 6
            assert "MCP_TOOL_INVOKED" in summary["activities"]

            dfg = engine.discover_dfg_per_type()
            assert "GcpEntitlement" in dfg
            assert dfg["GcpEntitlement"]["dfg_edges"] >= 1


class TestOCPQQueryEvaluator:
    """Court 3: Validates OCPQ multi-object entitlement-to-metering queries."""

    def test_entitlement_to_metering_ocpq_conformance(self, sample_ocel_emitter: OCEL2Emitter) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            sqlite_file = tmp / "swarm_ocpq.sqlite"
            sample_ocel_emitter.write_sqlite(sqlite_file)

            engine = ProcessMiningEngine(sqlite_file)
            res = engine.evaluate_entitlement_to_metering_ocpq("ent-gcp-enterprise-01")

            assert res["compliant"] is True
            assert res["tool_calls"] == 1
            assert res["revenue_realized_usd"] == 15.0
            assert res["revenue_realized_usd"] >= res["expected_min_revenue_usd"]


class TestFailClosedTripwireProcessGate:
    """Court 4: Validates fail-closed process compliance with anti-vacuity fail witness."""

    def test_compliant_log_passes_tripwire(self, sample_ocel_emitter: OCEL2Emitter) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            sqlite_file = tmp / "compliant.sqlite"
            sample_ocel_emitter.write_sqlite(sqlite_file)

            engine = ProcessMiningEngine(sqlite_file)
            conformant, violations = engine.check_swarm_conformance_tripwire()
            assert conformant is True
            assert len(violations) == 0

    def test_anti_vacuity_fail_witness_on_unentitled_execution(self) -> None:
        """Prove that a rogue swarm executing tools without an active GCP entitlement fails closed."""
        rogue_emitter = OCEL2Emitter()
        # Register task and tool WITHOUT an entitlement
        rogue_emitter.register_object("task-rogue-001", "A2AExecutionTask")
        rogue_emitter.register_object("tool-rogue-001", "McpToolCall")

        rogue_emitter.emit_event(
            "ev-rogue-01",
            "MCP_TOOL_INVOKED",
            datetime.now(timezone.utc),
            relationships=[
                {"objectId": "task-rogue-001", "qualifier": "caller"},
                {"objectId": "tool-rogue-001", "qualifier": "invoked"},
            ],
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            rogue_file = tmp / "rogue.sqlite"
            rogue_emitter.write_sqlite(rogue_file)

            engine = ProcessMiningEngine(rogue_file)
            conformant, violations = engine.check_swarm_conformance_tripwire()
            assert conformant is False, "Anti-vacuity witness: Unentitled tool execution must fail closed."
            assert any("UNENTITLED_EXECUTION" in v for v in violations)
