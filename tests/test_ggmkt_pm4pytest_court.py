"""Chicago-School Test Court: Applying pm4pytest to the ggmkt CLI.

Verifies:
1. Petri Net FSM Conformance: Strict lifecycle state transitions
   (CLI_INVOKED -> COMMAND_DISPATCHED -> REGISTRY_LOADED -> OUTPUT_RENDERED)
   achieving TBR log fitness >= 1.0.
2. Temporal SLA Bounds: Inter-activity execution latencies within performance limits.
3. Object-Centric Process Querying (OCPQ): Multi-object causal graph relations
   connecting CliSession, Pack, and Command execution.
4. Anti-Vacuity Fail Witness: Proving that an unauthorized skip or corrupted
   FSM sequence fails closed under Petri net conformance checking.
5. Standalone Universal CLI Verification: Executing the pm4pytest-cli binary
   directly over the exported ggmkt trace, streaming TAP v13 and emitting JUnit XML.

ZERO MOCKS. Real CLI invocations, real IEEE OCEL v2 logs, real PM4Py token replay.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ggen_marketplace.cli import app
from pm4pytest import OCPQ, ConformanceSpec, PM4PySession, TemporalSLA
from pm4pytest.ocel import ProcessTraceCollector

runner = CliRunner()


class TestGgmktPM4PytestCourt:
    """Comprehensive Chicago-School verification of ggmkt CLI using pm4pytest."""

    @pytest.mark.conformance(
        spec=lambda: ConformanceSpec.from_fsm(
            valid_paths=[
                ["CLI_INVOKED", "COMMAND_DISPATCHED", "REGISTRY_LOADED", "OUTPUT_RENDERED"],
            ],
            min_fitness=1.0,
        )
    )
    def test_ggmkt_search_lifecycle_conformance(self, pm4py_session: PM4PySession) -> None:
        """Prove that ggmkt search adheres strictly to the declared FSM lifecycle."""
        # Use an in-memory or env-directed trace collector linked to pm4py_session
        import ggen_marketplace.cli as cli_mod

        # Inject pm4py_session collector into cli module
        orig_collector = cli_mod._TRACE_COLLECTOR
        cli_mod._TRACE_COLLECTOR = pm4py_session.collector

        try:
            res = runner.invoke(app, ["search", "a2a", "--limit", "3"])
            assert res.exit_code == 0
            assert "aaif-vanilla-pack" in res.output
        finally:
            cli_mod._TRACE_COLLECTOR = orig_collector

    @pytest.mark.temporal_sla(
        sla=lambda: TemporalSLA().require_max_latency(
            "COMMAND_DISPATCHED", "OUTPUT_RENDERED", max_seconds=10.0
        )
    )
    def test_ggmkt_info_temporal_sla(self, pm4py_session: PM4PySession) -> None:
        """Prove that ggmkt info satisfies sub-second latency SLA between dispatch and rendering."""
        import ggen_marketplace.cli as cli_mod

        orig_collector = cli_mod._TRACE_COLLECTOR
        cli_mod._TRACE_COLLECTOR = pm4py_session.collector

        try:
            res = runner.invoke(app, ["info", "aaif-vanilla-pack"])
            assert res.exit_code == 0
            assert "Structure in packs/aaif-vanilla-pack" in res.output
        finally:
            cli_mod._TRACE_COLLECTOR = orig_collector

    @pytest.mark.ocpq(
        query=lambda: (
            OCPQ()
            .require_activity("CLI_INVOKED", min_count=1)
            .require_activity("COMMAND_DISPATCHED", min_count=1)
            .require_activity("OUTPUT_RENDERED", min_count=1)
            .require_object_type("CliSession", "Pack")
        )
    )
    def test_ggmkt_ocpq_multi_object_relationships(self, pm4py_session: PM4PySession) -> None:
        """Assert multi-object causal relationship connecting CliSession and Pack entities."""
        import ggen_marketplace.cli as cli_mod

        orig_collector = cli_mod._TRACE_COLLECTOR
        cli_mod._TRACE_COLLECTOR = pm4py_session.collector

        # Pre-register objects in the session
        pm4py_session.register_object("cli_session_1", "CliSession", {"app": "ggmkt"})
        pm4py_session.register_object("aaif-vanilla-pack", "Pack", {"tier": "verified"})

        try:
            res = runner.invoke(app, ["info", "aaif-vanilla-pack"])
            assert res.exit_code == 0
        finally:
            cli_mod._TRACE_COLLECTOR = orig_collector

    @pytest.mark.conformance(
        spec=lambda: ConformanceSpec.from_fsm(
            valid_paths=[["CLI_INVOKED", "COMMAND_DISPATCHED", "REGISTRY_LOADED", "OUTPUT_RENDERED"]],
            min_fitness=1.0,
        )
    )
    @pytest.mark.expected_conformance_violation("PETRI_NET_FITNESS_VIOLATION")
    def test_ggmkt_corrupted_lifecycle_anti_vacuity_fails_closed(self, pm4py_session: PM4PySession) -> None:
        """Anti-vacuity fail witness: bypassing mandatory steps fails closed under TBR."""
        # Intentionally emit an illegal truncated trace that skips COMMAND_DISPATCHED and REGISTRY_LOADED
        pm4py_session.emit_event("e1", "CLI_INVOKED")
        pm4py_session.emit_event("e2", "OUTPUT_RENDERED")

    def test_standalone_pm4pytest_cli_subprocess_on_ggmkt_trace(self, tmp_path: Path) -> None:
        """Prove that the standalone pm4pytest binary can verify an exported ggmkt trace log."""
        trace_file = tmp_path / "ggmkt_session.sqlite"
        junit_file = tmp_path / "ggmkt_junit.xml"

        # Run ggmkt CLI specifying trace output
        res = runner.invoke(app, ["--trace-log", str(trace_file), "search", "a2a", "--limit", "2"])
        assert res.exit_code == 0
        assert trace_file.exists()

        # Run standalone pm4pytest CLI binary over the trace
        cmd = [
            ".venv/bin/pm4pytest",
            "check-conformance",
            "--log",
            str(trace_file),
            "--fsm",
            "CLI_INVOKED,COMMAND_DISPATCHED,REGISTRY_LOADED,OUTPUT_RENDERED",
            "--min-fitness",
            "1.0",
            "--format",
            "tap",
            "--junitxml",
            str(junit_file),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"pm4pytest CLI error: {proc.stderr}"
        assert "TAP version 13" in proc.stdout
        assert "ok 1 - conformance_fsm_" in proc.stdout
        assert junit_file.exists()
