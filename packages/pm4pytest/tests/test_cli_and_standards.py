"""Chicago-School Test Court: pm4pytest CLI & Universal Testing Standards.

Verifies:
1. Universal TAP v13 emission (ok/not ok, YAML diagnostic blocks, 1..N plan)
2. CI/CD JUnit XML report emission (<testsuites>, <testcase>, <failure>)
3. Conformance check execution against real OCEL v2 logs with strict exit codes
4. Temporal SLA check execution and fail-closed breach handling
5. OCPQ graph querying via standalone CLI runner
"""

import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from pm4pytest.ocel import ProcessTraceCollector
from pm4pytest.reporters import JUnitXMLReporter, TAPReporter


@pytest.fixture
def sample_ocel_sqlite(tmp_path: Path) -> Path:
    """Produce a real IEEE OCEL v2 SQLite database using ProcessTraceCollector."""
    collector = ProcessTraceCollector()
    collector.register_object("order_101", "Order", {"amount": 2500})
    collector.register_object("agent_a2a", "Agent", {"role": "Settler"})

    collector.emit_event(
        event_id="ev_001",
        event_type="order_created",
        attributes={"channel": "gcp_marketplace"},
        relationships=[{"objectId": "order_101"}, {"objectId": "agent_a2a"}],
    )
    collector.emit_event(
        event_id="ev_002",
        event_type="payment_cleared",
        attributes={"currency": "USD"},
        relationships=[{"objectId": "order_101"}],
    )
    collector.emit_event(
        event_id="ev_003",
        event_type="entitlement_delivered",
        attributes={"status": "ACTIVE"},
        relationships=[{"objectId": "order_101"}, {"objectId": "agent_a2a"}],
    )

    db_path = tmp_path / "test_trace.sqlite"
    collector.write_sqlite(db_path)
    return db_path


class TestCLIAndStandardsCourt:
    """Chicago-School verification of pm4pytest CLI and standard test reporting."""

    def test_tap_reporter_v13_format(self):
        """Verify TAPReporter adheres strictly to TAP v13 specification."""
        reporter = TAPReporter()
        reporter.add_result(
            name="test_conformance_order",
            passed=True,
            diagnostics={"fitness": 1.0, "object": "order_101"},
            duration_sec=0.045,
        )
        reporter.add_result(
            name="test_sla_payment",
            passed=False,
            diagnostics={"breach_sec": 4.2, "limit_sec": 1.0},
            duration_sec=0.012,
        )

        tap_output = reporter.emit()
        lines = tap_output.strip().split("\n")

        assert lines[0] == "TAP version 13"
        assert lines[1] == "1..2"
        assert "ok 1 - test_conformance_order" in tap_output
        assert "not ok 2 - test_sla_payment" in tap_output
        assert "  ---" in tap_output
        assert "  fitness: 1.0" in tap_output
        assert "  breach_sec: 4.2" in tap_output
        assert "  ..." in tap_output

    def test_junit_xml_reporter_format(self, tmp_path: Path):
        """Verify JUnitXMLReporter adheres to standard CI/CD XML schema."""
        reporter = JUnitXMLReporter(suite_name="pm4pytest_integration")
        reporter.add_result(
            name="test_alignment",
            passed=True,
            duration_sec=0.05,
        )
        reporter.add_result(
            name="test_fsm_violation",
            passed=False,
            diagnostics={"message": "FSM transition error", "expected": "B", "got": "C"},
            duration_sec=0.02,
        )

        xml_output = reporter.emit()
        xml_file = tmp_path / "test_report.xml"
        xml_file.write_text(xml_output, encoding="utf-8")

        root = ET.fromstring(xml_output)
        assert root.tag == "testsuites"
        assert root.attrib["name"] == "pm4pytest_integration"
        assert root.attrib["tests"] == "2"
        assert root.attrib["failures"] == "1"

        testcases = root.findall(".//testcase")
        assert len(testcases) == 2
        fail_node = root.find(".//failure")
        assert fail_node is not None
        assert "FSM transition error" in fail_node.attrib["message"]

    def test_cli_check_conformance_tap_and_junit(self, sample_ocel_sqlite: Path, tmp_path: Path):
        """Execute pm4pytest check-conformance CLI subprocess with TAP output and JUnit XML."""
        junit_file = tmp_path / "conformance_junit.xml"
        cmd = [
            ".venv/bin/pm4pytest",
            "check-conformance",
            "--log",
            str(sample_ocel_sqlite),
            "--fsm",
            "order_created,payment_cleared,entitlement_delivered",
            "--min-fitness",
            "1.0",
            "--format",
            "tap",
            "--junitxml",
            str(junit_file),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 0, f"CLI stderr: {proc.stderr}"
        assert "TAP version 13" in proc.stdout
        assert "ok 1 - conformance_fsm_" in proc.stdout
        assert junit_file.exists()

        tree = ET.parse(junit_file)
        assert tree.getroot().attrib["failures"] == "0"

    def test_cli_check_conformance_fail_closed_exit_code_1(self, sample_ocel_sqlite: Path):
        """Anti-vacuity: verify CLI exits with status code 1 when FSM deviates."""
        cmd = [
            ".venv/bin/pm4pytest",
            "check-conformance",
            "--log",
            str(sample_ocel_sqlite),
            "--fsm",
            "order_created,unauthorized_step,entitlement_delivered",
            "--min-fitness",
            "1.0",
            "--format",
            "tap",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        assert proc.returncode == 1
        assert "not ok 1 - conformance_fsm_" in proc.stdout

    def test_cli_check_sla_and_query_ocpq(self, sample_ocel_sqlite: Path):
        """Execute SLA verification and OCPQ query via CLI."""
        # 1. SLA pass (generous limit)
        proc_sla = subprocess.run(
            [
                ".venv/bin/pm4pytest",
                "check-sla",
                "--log",
                str(sample_ocel_sqlite),
                "--sla",
                "order_created:payment_cleared:300.0",
                "--format",
                "tap",
            ],
            capture_output=True,
            text=True,
        )
        assert proc_sla.returncode == 0
        assert "ok 1 - temporal_sla_check" in proc_sla.stdout

        # 2. SLA breach fail-closed
        proc_sla_breach = subprocess.run(
            [
                ".venv/bin/pm4pytest",
                "check-sla",
                "--log",
                str(sample_ocel_sqlite),
                "--sla",
                "order_created:payment_cleared:0.0000001",
                "--format",
                "tap",
            ],
            capture_output=True,
            text=True,
        )
        assert proc_sla_breach.returncode == 1
        assert "not ok 1 - temporal_sla_check" in proc_sla_breach.stdout

        # 3. OCPQ query pass
        proc_ocpq = subprocess.run(
            [
                ".venv/bin/pm4pytest",
                "query",
                "--log",
                str(sample_ocel_sqlite),
                "--traverse",
                "Order,Agent",
                "--require-activity",
                "order_created",
                "--require-activity",
                "entitlement_delivered",
                "--format",
                "tap",
            ],
            capture_output=True,
            text=True,
        )
        assert proc_ocpq.returncode == 0
        assert "ok 1 - ocpq_invariants" in proc_ocpq.stdout
