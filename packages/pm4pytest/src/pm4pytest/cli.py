"""Standalone CLI for pm4pytest: IEEE OCEL v2 Conformance, OCPQ, and SLA verification.

Emits standard test formats (TAP v13, JUnit XML, JSON) with strict exit codes:
- 0: All assertions and conformance metrics satisfied
- 1: Conformance failure, SLA breach, or OCPQ violation
- 2: Configuration or syntax error
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import List, Optional

import pm4py
import typer
from rich.console import Console

from pm4pytest.conformance import ConformanceSpec
from pm4pytest.ocpq import OCPQ
from pm4pytest.reporters import JUnitXMLReporter, TAPReporter
from pm4pytest.temporal import TemporalSLA

app = typer.Typer(
    name="pm4pytest",
    help="Autonomous Process Intelligence & IEEE OCEL v2 Test Runner",
    add_completion=False,
)
console = Console(file=sys.stderr)


def _load_events_and_ocel(log_path: Path):
    """Load events list and pm4py OCEL object from SQLite or JSON."""
    if not log_path.exists():
        console.print(f"[red]Error: Log file not found: {log_path}[/red]")
        sys.exit(2)

    suffix = log_path.suffix.lower()
    try:
        if suffix in [".sqlite", ".db"]:
            ocel = pm4py.read_ocel2_sqlite(str(log_path))
        elif suffix == ".json":
            ocel = pm4py.read_ocel2_json(str(log_path))
        else:
            # Try sqlite first, fallback to json
            try:
                ocel = pm4py.read_ocel2_sqlite(str(log_path))
            except Exception:
                ocel = pm4py.read_ocel2_json(str(log_path))
    except Exception as e:
        console.print(f"[red]Failed to load OCEL log from {log_path}: {e}[/red]")
        sys.exit(2)

    # Extract events dict list for Conformance and Temporal evaluation
    events = []
    for _, row in ocel.events.iterrows():
        ev = {
            "case:concept:name": "cli_execution_trace",
            "concept:name": str(row.get("ocel:activity", "")),
            "time:timestamp": row.get("ocel:timestamp"),
        }
        events.append(ev)

    return events, ocel


@app.command(name="check-conformance")
def check_conformance(
    log_path: Path = typer.Option(..., "--log", "-l", help="Path to OCEL v2 SQLite or JSON-OCEL file"),
    fsm: str = typer.Option(..., "--fsm", "-f", help="Comma-separated FSM sequence: step1,step2,step3"),
    min_fitness: float = typer.Option(1.0, "--min-fitness", "-m", help="Minimum required alignment fitness [0.0 - 1.0]"),
    format_type: str = typer.Option("tap", "--format", help="Output format: tap, junit, or json"),
    junitxml: Optional[Path] = typer.Option(None, "--junitxml", help="Optional path to output JUnit XML report"),
) -> None:
    """Verify trace conformance against a Petri net / FSM transition pipeline."""
    start_time = time.time()
    tap_reporter = TAPReporter()
    junit_reporter = JUnitXMLReporter(suite_name="conformance")

    events, _ = _load_events_and_ocel(log_path)
    fsm_sequence = [s.strip() for s in fsm.split(",") if s.strip()]
    if not fsm_sequence:
        console.print("[red]Error: FSM sequence cannot be empty[/red]")
        sys.exit(2)

    spec = ConformanceSpec.from_fsm([fsm_sequence], min_fitness=min_fitness)
    res = spec.evaluate(events)
    duration = time.time() - start_time

    diag = {
        "fitness": res.fitness,
        "min_fitness": min_fitness,
        "violations": res.violations,
        "diagnostics": res.diagnostics,
    }
    test_name = f"conformance_fsm_{fsm}"
    tap_reporter.add_result(name=test_name, passed=res.success, diagnostics=diag, duration_sec=duration)
    junit_reporter.add_result(name=test_name, passed=res.success, diagnostics=diag, duration_sec=duration)

    if junitxml:
        junitxml.write_text(junit_reporter.emit(), encoding="utf-8")

    if format_type == "tap":
        sys.stdout.write(tap_reporter.emit())
    elif format_type == "junit":
        sys.stdout.write(junit_reporter.emit())
    elif format_type == "json":
        out = {
            "success": res.success,
            "fitness": res.fitness,
            "violations": res.violations,
        }
        sys.stdout.write(json.dumps(out, indent=2) + "\n")
    else:
        console.print(f"[red]Unknown format: {format_type}[/red]")
        sys.exit(2)

    sys.exit(0 if res.success else 1)


@app.command(name="check-sla")
def check_sla(
    log_path: Path = typer.Option(..., "--log", "-l", help="Path to OCEL v2 SQLite or JSON-OCEL file"),
    sla_rule: List[str] = typer.Option(..., "--sla", "-s", help="SLA rule: source_act:target_act:max_seconds"),
    format_type: str = typer.Option("tap", "--format", help="Output format: tap, junit, or json"),
    junitxml: Optional[Path] = typer.Option(None, "--junitxml", help="Optional path to output JUnit XML report"),
) -> None:
    """Verify temporal latency SLAs between sequential activities in OCEL traces."""
    start_time = time.time()
    tap_reporter = TAPReporter()
    junit_reporter = JUnitXMLReporter(suite_name="temporal_sla")

    events, _ = _load_events_and_ocel(log_path)
    sla = TemporalSLA()

    for rule in sla_rule:
        parts = rule.split(":")
        if len(parts) != 3:
            console.print(f"[red]Invalid SLA rule format: {rule}. Expected source:target:max_seconds[/red]")
            sys.exit(2)
        source_act, target_act, max_sec_str = parts[0].strip(), parts[1].strip(), parts[2].strip()
        try:
            max_seconds = float(max_sec_str)
        except ValueError:
            console.print(f"[red]Invalid max_seconds float in rule: {rule}[/red]")
            sys.exit(2)
        sla.require_max_latency(source_act, target_act, max_seconds)

    res = sla.evaluate(events)
    duration = time.time() - start_time

    diag = {
        "latencies": res.latencies,
        "violations": res.violations,
    }
    test_name = f"temporal_sla_check"
    tap_reporter.add_result(name=test_name, passed=res.success, diagnostics=diag, duration_sec=duration)
    junit_reporter.add_result(name=test_name, passed=res.success, diagnostics=diag, duration_sec=duration)

    if junitxml:
        junitxml.write_text(junit_reporter.emit(), encoding="utf-8")

    if format_type == "tap":
        sys.stdout.write(tap_reporter.emit())
    elif format_type == "junit":
        sys.stdout.write(junit_reporter.emit())
    elif format_type == "json":
        out = {
            "success": res.success,
            "latencies": res.latencies,
            "violations": res.violations,
        }
        sys.stdout.write(json.dumps(out, indent=2) + "\n")
    else:
        console.print(f"[red]Unknown format: {format_type}[/red]")
        sys.exit(2)

    sys.exit(0 if res.success else 1)


@app.command(name="query")
def query_ocpq(
    log_path: Path = typer.Option(..., "--log", "-l", help="Path to OCEL v2 SQLite or JSON-OCEL file"),
    traverse_path: Optional[str] = typer.Option(None, "--traverse", help="Comma-separated object types to traverse"),
    require_act: Optional[List[str]] = typer.Option(None, "--require-activity", help="Required activity names"),
    balanced_ratio: Optional[str] = typer.Option(None, "--balanced-ratio", help="source_act:target_act:ratio"),
    format_type: str = typer.Option("tap", "--format", help="Output format: tap, junit, or json"),
    junitxml: Optional[Path] = typer.Option(None, "--junitxml", help="Optional path to output JUnit XML report"),
) -> None:
    """Execute Object-Centric Process Query (OCPQ) assertions over multi-object event graphs."""
    start_time = time.time()
    tap_reporter = TAPReporter()
    junit_reporter = JUnitXMLReporter(suite_name="ocpq_query")

    _, ocel = _load_events_and_ocel(log_path)
    ocpq = OCPQ()

    if traverse_path:
        types = [t.strip() for t in traverse_path.split(",") if t.strip()]
        ocpq.traverse(*types)

    if require_act:
        for act in require_act:
            ocpq.require_activity(act.strip())

    if balanced_ratio:
        parts = balanced_ratio.split(":")
        if len(parts) == 3:
            s_act, t_act, r = parts[0].strip(), parts[1].strip(), float(parts[2].strip())
            ocpq.require_balanced_ratio(s_act, t_act, r)
        else:
            console.print(f"[red]Invalid balanced ratio format: {balanced_ratio}. Expected src:tgt:ratio[/red]")
            sys.exit(2)

    res = ocpq.evaluate(ocel)
    duration = time.time() - start_time

    diag = {
        "violations": res.violations,
        "metrics": res.metrics,
    }
    test_name = "ocpq_invariants"
    tap_reporter.add_result(name=test_name, passed=res.success, diagnostics=diag, duration_sec=duration)
    junit_reporter.add_result(name=test_name, passed=res.success, diagnostics=diag, duration_sec=duration)

    if junitxml:
        junitxml.write_text(junit_reporter.emit(), encoding="utf-8")

    if format_type == "tap":
        sys.stdout.write(tap_reporter.emit())
    elif format_type == "junit":
        sys.stdout.write(junit_reporter.emit())
    elif format_type == "json":
        out = {
            "success": res.success,
            "violations": res.violations,
            "metrics": res.metrics,
        }
        sys.stdout.write(json.dumps(out, indent=2) + "\n")
    else:
        console.print(f"[red]Unknown format: {format_type}[/red]")
        sys.exit(2)

    sys.exit(0 if res.success else 1)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
