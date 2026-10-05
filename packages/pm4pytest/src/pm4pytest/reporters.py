"""Universal testing standard formatters: TAP v13 and JUnit XML.

This module provides standard test reporting for process intelligence,
Petri net conformance, temporal SLA validations, and OCPQ query assertions.
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class TestResult:
    """Represents an atomic test or assertion outcome."""

    test_id: int
    name: str
    passed: bool
    skip: bool = False
    skip_reason: Optional[str] = None
    directive: Optional[str] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    duration_sec: float = 0.0


class TAPReporter:
    """Test Anything Protocol (TAP) v13 emitter with YAML diagnostic blocks."""

    def __init__(self, plan_count: Optional[int] = None) -> None:
        self.results: List[TestResult] = []
        self.plan_count = plan_count

    def add_result(
        self,
        name: str,
        passed: bool,
        skip: bool = False,
        skip_reason: Optional[str] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        duration_sec: float = 0.0,
    ) -> TestResult:
        res = TestResult(
            test_id=len(self.results) + 1,
            name=name,
            passed=passed,
            skip=skip,
            skip_reason=skip_reason,
            diagnostics=diagnostics or {},
            duration_sec=duration_sec,
        )
        self.results.append(res)
        return res

    def emit(self) -> str:
        """Render results as TAP v13 string."""
        lines = ["TAP version 13"]
        total = len(self.results) if self.plan_count is None else self.plan_count
        lines.append(f"1..{total}")

        for res in self.results:
            status_str = "ok" if res.passed else "not ok"
            desc = f"{status_str} {res.test_id} - {res.name}"
            if res.skip:
                desc += f" # SKIP {res.skip_reason or ''}"
            lines.append(desc)

            if res.diagnostics:
                lines.append("  ---")
                for k, v in res.diagnostics.items():
                    if isinstance(v, (dict, list)):
                        import json
                        lines.append(f"  {k}: {json.dumps(v)}")
                    else:
                        lines.append(f"  {k}: {v}")
                lines.append("  ...")

        return "\n".join(lines) + "\n"


class JUnitXMLReporter:
    """JUnit XML format emitter compatible with standard CI/CD engines."""

    def __init__(self, suite_name: str = "pm4pytest") -> None:
        self.suite_name = suite_name
        self.results: List[TestResult] = []

    def add_result(
        self,
        name: str,
        passed: bool,
        skip: bool = False,
        skip_reason: Optional[str] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        duration_sec: float = 0.0,
    ) -> TestResult:
        res = TestResult(
            test_id=len(self.results) + 1,
            name=name,
            passed=passed,
            skip=skip,
            skip_reason=skip_reason,
            diagnostics=diagnostics or {},
            duration_sec=duration_sec,
        )
        self.results.append(res)
        return res

    def emit(self) -> str:
        """Render test results as JUnit XML string."""
        total = len(self.results)
        failures = sum(1 for r in self.results if not r.passed and not r.skip)
        skipped = sum(1 for r in self.results if r.skip)
        total_time = sum(r.duration_sec for r in self.results)
        from datetime import timezone
        timestamp = datetime.now(timezone.utc).isoformat()

        xml = [
            '<?xml version="1.0" encoding="utf-8"?>',
            f'<testsuites name="{html.escape(self.suite_name)}" tests="{total}" failures="{failures}" errors="0" skipped="{skipped}" time="{total_time:.4f}">',
            f'  <testsuite name="{html.escape(self.suite_name)}" tests="{total}" failures="{failures}" errors="0" skipped="{skipped}" time="{total_time:.4f}" timestamp="{timestamp}">',
        ]

        for r in self.results:
            name_esc = html.escape(r.name)
            xml.append(f'    <testcase name="{name_esc}" classname="pm4pytest" time="{r.duration_sec:.4f}">')
            if r.skip:
                reason = html.escape(r.skip_reason or "Skipped")
                xml.append(f'      <skipped message="{reason}"/>')
            elif not r.passed:
                msg = html.escape(str(r.diagnostics.get("message", "Test failed")))
                diag_str = html.escape(str(r.diagnostics))
                xml.append(f'      <failure message="{msg}">{diag_str}</failure>')
            xml.append("    </testcase>")

        xml.append("  </testsuite>")
        xml.append("</testsuites>")
        return "\n".join(xml) + "\n"
