"""
ggen_marketplace.cli
Modern Typer CLI for searching, inspecting, and managing ggen marketplace packs.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Optional IEEE OCEL v2 Trace Emission Collector
try:
    from pm4pytest.ocel import ProcessTraceCollector
except ImportError:
    ProcessTraceCollector = None

# Active global trace collector for session
_TRACE_COLLECTOR = None
_TRACE_PATH = None


def init_trace_collector(trace_path: Optional[str] = None) -> Optional[ProcessTraceCollector]:
    global _TRACE_COLLECTOR, _TRACE_PATH
    path_str = trace_path or os.environ.get("GGMKT_TRACE_LOG")
    if _TRACE_COLLECTOR is None and path_str and ProcessTraceCollector is not None:
        _TRACE_COLLECTOR = ProcessTraceCollector()
        _TRACE_PATH = Path(path_str)
        _TRACE_COLLECTOR.register_object("cli_session_1", "CliSession", {"app": "ggmkt"})
    elif path_str:
        _TRACE_PATH = Path(path_str)
    return _TRACE_COLLECTOR


def emit_cli_event(event_type: str, attributes: Optional[dict] = None, rel_objects: Optional[list] = None) -> None:
    if _TRACE_COLLECTOR is not None:
        rels = [{"objectId": "cli_session_1"}]
        if rel_objects:
            for obj in rel_objects:
                rels.append({"objectId": obj})
        eid = f"ev_{len(_TRACE_COLLECTOR.events) + 1:04d}"
        _TRACE_COLLECTOR.emit_event(
            event_id=eid,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            attributes=attributes or {},
            relationships=rels,
        )


def finalize_trace() -> None:
    global _TRACE_COLLECTOR, _TRACE_PATH
    if _TRACE_COLLECTOR is not None and _TRACE_PATH is not None:
        try:
            if _TRACE_PATH.suffix.lower() == ".sqlite":
                _TRACE_COLLECTOR.write_sqlite(_TRACE_PATH)
            else:
                import json
                _TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(_TRACE_PATH, "w", encoding="utf-8") as f:
                    json.dump(_TRACE_COLLECTOR.to_json_dict(), f, indent=2)
        except Exception as e:
            sys.stderr.write(f"Warning: Failed to flush trace log to {_TRACE_PATH}: {e}\n")


# Import core marketplace logic from scripts
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

try:
    import marketplace as mp
    import marketplace_tiers as mt
except ImportError:
    mp = None
    mt = None

app = typer.Typer(
    name="ggmkt",
    help="🌿 ggmkt — Official ggen Marketplace CLI (Search, Inspection & Gate Calculus).",
    add_completion=True,
)
console = Console()


@app.callback()
def main_callback(
    trace_log: Optional[str] = typer.Option(
        None, "--trace-log", envvar="GGMKT_TRACE_LOG", help="Path to write IEEE OCEL v2 trace log"
    ),
) -> None:
    """Initialize process execution tracing if requested."""
    init_trace_collector(trace_log)
    emit_cli_event("CLI_INVOKED", {"executable": "ggmkt"})


def _get_scoped_records(scope: str = "all") -> list[dict]:
    emit_cli_event("REGISTRY_LOADED", {"scope": scope})
    if mp is None:
        return []
    packs = mp.scoped_packs(scope)
    return [p.catalog_record() for p in packs]


@app.command("catalog")
def emit_catalog(
    scope: str = typer.Option("active", "--scope", "-s", help="Scope: 'active' or 'all'"),
) -> None:
    """Emit the deterministic marketplace catalog JSON to stdout."""
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "marketplace.py"), "catalog", "--scope", scope])
    raise typer.Exit(code=res.returncode)


@app.command("search")
def search_packs(
    terms: list[str] = typer.Argument(..., help="Search keywords (e.g. 'a2a', 'mcp', 'ash')"),
    scope: str = typer.Option("all", "--scope", "-s", help="Scope to search: 'active' or 'all'"),
    limit: int = typer.Option(25, "--limit", "-l", help="Maximum results to display"),
) -> None:
    """Search marketplace packs with keyword matching and colored tiers."""
    emit_cli_event("COMMAND_DISPATCHED", {"command": "search", "terms": terms})
    records = _get_scoped_records(scope)
    if not records or mt is None:
        rprint("[red]Error: Unable to load marketplace pack registry.[/red]")
        finalize_trace()
        raise typer.Exit(code=1)

    matched = list(mt.search(records, terms))
    if not matched:
        rprint(f"[yellow]No packs found matching terms:[/yellow] {' '.join(terms)}")
        finalize_trace()
        return

    table = Table(
        title=f"🔎 ggen Marketplace Pack Search: {' '.join(terms)} ({len(matched)} matches)",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Pack Name", style="bold cyan", no_wrap=True)
    table.add_column("Version", style="dim")
    table.add_column("Tier", justify="center")
    table.add_column("Profile", style="italic")
    table.add_column("Status", justify="center")
    table.add_column("Description")

    matched_pack_ids = []
    for rec in matched[:limit]:
        pname = rec["name"]
        matched_pack_ids.append(pname)
        tier = rec.get("tier", "unknown")
        if tier == "verified":
            tier_style = "[bold green]verified[/bold green]"
        elif tier == "thin":
            tier_style = "[bold yellow]thin[/bold yellow]"
        elif tier == "documented":
            tier_style = "[bold blue]documented[/bold blue]"
        else:
            tier_style = f"[white]{tier}[/white]"

        status = rec.get("status", "active")
        status_style = "[green]active[/green]" if status == "active" else f"[red]{status}[/red]"
        desc = (rec.get("description") or "").split("\n")[0][:60]

        table.add_row(
            pname,
            rec.get("version", "0.1.0"),
            tier_style,
            rec.get("profile", "unknown"),
            status_style,
            desc,
        )

    console.print(table)
    if len(matched) > limit:
        omitted = ", ".join(rec["name"] for rec in matched[limit:])
        rprint(f"[dim]... and {len(matched) - limit} more matches (use --limit to expand): {omitted}[/dim]")

    emit_cli_event(
        "OUTPUT_RENDERED",
        {"matched_count": len(matched), "limit": limit},
        rel_objects=matched_pack_ids[:5],
    )
    finalize_trace()


@app.command("info")
def pack_info(
    name: str = typer.Argument(..., help="Exact pack name (e.g. 'aaif-vanilla-pack')"),
) -> None:
    """Show detailed metadata, ontologies, templates, and gates for a pack."""
    emit_cli_event("COMMAND_DISPATCHED", {"command": "info", "pack_name": name})
    records = _get_scoped_records("all")
    match = [r for r in records if r["name"] == name]
    if not match:
        rprint(f"[bold red]Error:[/bold red] Pack '[cyan]{name}[/cyan]' not found.")
        finalize_trace()
        raise typer.Exit(code=1)

    rec = match[0]
    pack_dir = ROOT / "packs" / name

    content = f"""[bold]Version:[/bold] {rec.get('version')}
[bold]Profile:[/bold] {rec.get('profile')}
[bold]Tier:[/bold] {rec.get('tier')}
[bold]Lifecycle State:[/bold] {rec.get('status')}
[bold]Description:[/bold] {rec.get('description', 'N/A')}

[bold cyan]Structure in packs/{name}:[/bold cyan]
 • Ontologies: {len(list(pack_dir.glob('**/*.ttl')))} files
 • Templates:  {len(list(pack_dir.glob('templates/**/*')))} files
 • Gates:      {len(list(pack_dir.glob('gates/**/*.rq')))} SPARQL queries
 • Path:       {pack_dir}
"""
    console.print(Panel(content, title=f"📦 Pack: [bold cyan]{name}[/bold cyan]", border_style="green"))
    emit_cli_event("OUTPUT_RENDERED", {"pack_name": name, "tier": rec.get("tier")}, rel_objects=[name])
    finalize_trace()


@app.command("list")
def list_packs(
    tier: Optional[str] = typer.Option(None, "--tier", "-t", help="Filter by tier (verified, thin, documented)"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="Filter by profile (semantic, projection, project)"),
    limit: int = typer.Option(30, "--limit", "-l", help="Number of packs to display"),
) -> None:
    """List marketplace packs with optional tier and profile filters."""
    emit_cli_event("COMMAND_DISPATCHED", {"command": "list", "tier": tier, "profile": profile})
    records = _get_scoped_records("all")
    if tier:
        records = [r for r in records if r.get("tier") == tier]
    if profile:
        records = [r for r in records if r.get("profile") == profile]

    table = Table(
        title=f"📚 ggen Marketplace Packs (Showing {min(len(records), limit)} of {len(records)})",
        header_style="bold magenta",
    )
    table.add_column("Pack Name", style="bold cyan")
    table.add_column("Tier", justify="center")
    table.add_column("Profile")
    table.add_column("Version", style="dim")

    for rec in records[:limit]:
        t = rec.get("tier", "unknown")
        t_style = "[green]verified[/green]" if t == "verified" else f"[yellow]{t}[/yellow]"
        table.add_row(rec["name"], t_style, rec.get("profile", ""), rec.get("version", "0.1.0"))

    console.print(table)
    emit_cli_event("OUTPUT_RENDERED", {"total_listed": min(len(records), limit)})
    finalize_trace()


@app.command("validate")
def validate_repo() -> None:
    """Validate all marketplace packs and native SPARQL gates."""
    rprint("[bold blue][*] Running marketplace validation calculus...[/bold blue]")
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "marketplace.py"), "validate"])
    raise typer.Exit(code=res.returncode)


@app.command("aaif-audit")
def aaif_audit(
    fail_under: float = typer.Option(95.0, "--fail-under", help="Minimum required coverage percentage"),
) -> None:
    """Run full-spectrum 6-project AAIF combinatorial coverage audit."""
    cmd = [sys.executable, str(ROOT / "scripts" / "track_aaif_coverage.py"), "--fail-under", str(fail_under)]
    res = subprocess.run(cmd)
    raise typer.Exit(code=res.returncode)


@app.command("k8s-sim")
def k8s_sim(
    action: str = typer.Option("test", "--action", help="Action: setup, test, cleanup, or all"),
) -> None:
    """Run Kind cluster GCP Marketplace SaaS monetization loop."""
    cmd = [sys.executable, str(ROOT / "scripts" / "simulate_gcp_marketplace_k8s.py"), "--action", action]
    res = subprocess.run(cmd)
    raise typer.Exit(code=res.returncode)


# Process Mining & OCPQ sub-app
mine_app = typer.Typer(
    name="mine",
    help="🔍 Process Mining, OCEL v2 Intelligence & OCPQ Query Engine (PM4Py).",
)
app.add_typer(mine_app, name="mine")


@mine_app.command("discover")
def mine_discover(
    log_path: Path = typer.Argument(..., help="Path to OCEL v2 log (.json or .sqlite)"),
) -> None:
    """Discover object-centric process models and directly-follows graphs."""
    from ggen_marketplace.mining.engine import ProcessMiningEngine

    engine = ProcessMiningEngine(log_path)
    summary = engine.get_summary()

    table = Table(title=f"📊 OCEL v2 Summary: {log_path.name}", header_style="bold cyan")
    table.add_column("Metric", style="bold")
    table.add_column("Value")
    table.add_row("Events Count", str(summary["events_count"]))
    table.add_row("Objects Count", str(summary["objects_count"]))
    table.add_row("Object Types", ", ".join(summary["object_types"]))
    table.add_row("Activities", ", ".join(summary["activities"]))
    console.print(table)

    dfg = engine.discover_dfg_per_type()
    rprint(f"[bold green][+] Discovered DFG across {len(dfg)} object types.[/bold green]")


@mine_app.command("query")
def mine_query(
    log_path: Path = typer.Argument(..., help="Path to OCEL v2 log (.json or .sqlite)"),
    entitlement_id: str = typer.Option("ent-001", "--entitlement", help="Entitlement ID to audit"),
) -> None:
    """Evaluate OCPQ multi-object entitlement-to-metering query."""
    from ggen_marketplace.mining.engine import ProcessMiningEngine

    engine = ProcessMiningEngine(log_path)
    res = engine.evaluate_entitlement_to_metering_ocpq(entitlement_id)
    if res["compliant"]:
        rprint(f"[bold green][✓] OCPQ CONFORMANCE PASS: Revenue ${res['revenue_realized_usd']:.2f} covers {res['tool_calls']} tools.[/bold green]")
    else:
        rprint(f"[bold red][✗] OCPQ VIOLATION: {res}[/bold red]")
        raise typer.Exit(code=1)


@mine_app.command("conform")
def mine_conform(
    log_path: Path = typer.Argument(..., help="Path to OCEL v2 log (.json or .sqlite)"),
) -> None:
    """Check swarm execution conformance against fail-closed tripwire gates."""
    from ggen_marketplace.mining.engine import ProcessMiningEngine

    engine = ProcessMiningEngine(log_path)
    conformant, violations = engine.check_swarm_conformance_tripwire()
    if conformant:
        rprint("[bold green][✓] Swarm execution is fully conformant ($q_{process} = 1). Zero violations.[/bold green]")
    else:
        rprint(f"[bold red][✗] CONFORMANCE TRIPWIRE TRIPPED: {len(violations)} violations found.[/bold red]")
        for v in violations:
            rprint(f"  - [red]{v}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
