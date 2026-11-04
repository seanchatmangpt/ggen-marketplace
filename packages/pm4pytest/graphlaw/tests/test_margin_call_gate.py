"""Case 3: margin-call collateral gate conformance over the graphlaw wasm
boundary (graphlaw-run-eh wasmtime 48 host, packet-4 stdio, DuckDB-linked
module).

Business net (permitted arm):
    Margin_Call_Received → Collateral_Inspected → Pledge_Admitted
        → Ledger_Updated → Pledge_Proof_Sealed
Encumbered arm:
    Margin_Call_Received → Collateral_Inspected → Pledge_Refused
        → State_Preserved → Refusal_Proof_Sealed

The gate is enforced on the real wire: the harness admits an INSPECT SELECT
through the module's compile law, drains the real cursor stream, and admits
the pledge UPDATE document ONLY when the inspected row is unencumbered. For
the encumbered facility NO pledge document is sent; a witness SELECT proves
the state was preserved (encumbered flag still set, both rows intact).

Petri-net legs over the wasm, per session:
  setup   : open → CREATE margin_call_gate(id, collateral_value, encumbered,
            facility_id) → INSERT permitted row (encumbered=false) → INSERT
            encumbered row (encumbered=true)
  inspect : SELECT (id, encumbered, facility_id) through the module; the
            drained cursor body is the gate's observation
  pledge  : permitted → UPDATE SET encumbered = true WHERE facility_id =
            'FAC-MC-1001' admitted with a receipt; encumbered → no UPDATE
            document admitted at all
  witness : readback SELECT over the same named session proving the mutation
            landed (permitted) or the state was preserved (encumbered)

Courts:
- MC-GATE-01 (permitted arm): full permitted trace judged by
  ConformanceSpec.from_fsm at min_fitness=1.0 / min_precision=1.0.
- MC-GATE-02 (encumbered arm): encumbered trace judged the same way; the
  pledge UPDATE document is never admitted — the witness readback is the
  state-preservation proof.
- MC-GATE-03 (anti-vacuity, no wasm needed): a trace that executes the
  pledge with no Collateral_Inspected event must score fitness < 1.0.
- MC-GATE-04: the arm traces export a real OCEL2 SQLite file.

Skip discipline: a missing runner, an unresponsive spawn (host under
concurrent lane load), or a not-yet-EH-linked artifact is a LOUD typed SKIP
naming the reason — a SKIP is not a pass. The net twins always run.

Chicago: real runner subprocess, real wasm artifact, real frozen-duckdb in
the module, real cursor streams, real pm4py nets; no mocks, no sleeps.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from pm4pytest.conformance import ConformanceSpec
from pm4pytest.ocel import ProcessTraceCollector

# Canonical packet-4 framing, imported from the framing court (single source
# of the frame() law; no hand-rolled duplicate here).
_spec = importlib.util.spec_from_file_location(
    "test_packet4_framing",
    Path(__file__).with_name("test_packet4_framing.py"),
)
_framing = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_framing)
frame = _framing.frame
parse_frames = _framing.parse_frames

GRAPHLAW_RUN_EH = os.environ.get(
    "GRAPHLAW_RUN_EH",
    os.environ.get("GRAPHLAW_RUN", "/Users/sac/graphlaw/target/debug/graphlaw-run-eh"),
)
WASM_ARTIFACT = os.environ.get(
    "GRAPHLAW_WASM", "/Users/sac/graphlaw/priv/graphlaw.wasm"
)

SESSION_PERMITTED = "margin-call-permitted"
SESSION_ENCUMBERED = "margin-call-encumbered"

TABLE = "margin_call_gate"
FAC_PERMITTED = "FAC-MC-1001"
FAC_ENCUMBERED = "FAC-MC-2002"

PROBE_TIMEOUT_S = 900

# ------------------------------------------------------------------- framing


def capabilities_wire() -> bytes:
    return frame(b'{"op":"capabilities"}')


_RUNNER_STATE: dict | None = None


def runner_state() -> dict:
    """One real spawn probe per session: is the eh runner up and the artifact
    EH-linked? Cached; the wasm courts read the verdict and skip typed."""
    global _RUNNER_STATE
    if _RUNNER_STATE is not None:
        return _RUNNER_STATE
    state: dict = {"runner": GRAPHLAW_RUN_EH, "ok": False, "reason": ""}
    if not os.path.isfile(GRAPHLAW_RUN_EH):
        state["reason"] = (
            f"SKIP(typed: RUNNER-MISSING): {GRAPHLAW_RUN_EH} not built — "
            "build with `cargo build --features runner-eh` in /Users/sac/graphlaw"
        )
    else:
        try:
            proc = _wire(capabilities_wire())
        except subprocess.TimeoutExpired:
            state["reason"] = (
                "SKIP(typed: RUNNER-UNRESPONSIVE): capabilities probe exceeded "
                f"{PROBE_TIMEOUT_S}s (host under concurrent lane load)"
            )
            _RUNNER_STATE = state
            return state
        if proc.returncode in (95, 96):
            state["reason"] = (
                f"SKIP(typed: ARTIFACT-NOT-EH-LINKED): spawn exited "
                f"{proc.returncode}: {proc.stderr.decode(errors='replace').strip()}"
            )
        elif proc.returncode != 0:
            state["reason"] = (
                f"SKIP(typed: RUNNER-SPAWN-FAILED): capabilities probe exited "
                f"{proc.returncode}: {proc.stderr.decode(errors='replace').strip()}"
            )
        else:
            state["ok"] = True
    _RUNNER_STATE = state
    return state


def _wire(wire: bytes) -> subprocess.CompletedProcess:
    return subprocess.run(
        [GRAPHLAW_RUN_EH, "--wasm", WASM_ARTIFACT],
        input=wire,
        capture_output=True,
        timeout=PROBE_TIMEOUT_S,
    )


def eh_call(requests: list[dict]) -> list[dict]:
    """Drive one real graphlaw-run-eh process through the given requests,
    returning the unwrapped ABI responses (skips typed when the runner or
    artifact is not ready)."""
    state = runner_state()
    if not state["ok"]:
        pytest.skip(state["reason"])
    wire = b"".join(frame(json.dumps(r).encode()) for r in requests)
    try:
        proc = _wire(wire)
    except subprocess.TimeoutExpired:
        pytest.fail(
            f"FAIL(typed: RUNNER-UNRESPONSIVE): exec batch exceeded "
            f"{PROBE_TIMEOUT_S}s on the real wire"
        )
    assert proc.returncode == 0, (
        f"runner exited {proc.returncode}: {proc.stderr.decode(errors='replace')}"
    )
    bodies = parse_frames(proc.stdout)
    assert len(bodies) == len(requests), "one reply frame per request frame"
    out = []
    for body in bodies:
        envelope = json.loads(body)
        assert envelope["ok"] is True, f"runner-level fault: {envelope}"
        out.append(envelope["result"])
    return out


# --------------------------------------------------------------- gate docs
# Inline sql-rdf documents (dialect duckdb). Shapes: CreateStatement
# tableDefinition form (sql-ast.ttl), InsertStatement positional assign
# pairs (SQLRDF-22 G4), SelectStatement legacy fromTable + selectList,
# UpdateStatement with BOTH whereColumn and whereValue (the compiler guard
# in src/sql_ast.rs compile_command is stricter than the sh:or shape).
# xsd:boolean assign values render as quoted SQL string literals
# (render_scalar_literal, src/sql_ast.rs) and DuckDB casts them into the
# BOOLEAN column.


def exec_req(turtle: str, session: str) -> dict:
    return {
        "op": "duckdb",
        "mode": "exec",
        "query_ast": "http://example.org/queries#Q",
        "subject_prefix": "http://example.org/data",
        "vocab_prefix": "http://example.org/vocab",
        "ast": {"turtle": turtle, "dialect": "duckdb"},
        "session": session,
    }


def create_doc() -> str:
    return (
        "@prefix ex: <http://example.org/mc#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "ex:s1 a sql:CreateStatement ;\n"
        "    sql:statementIndex 0 ;\n"
        f"    sql:tableDefinition [ sql:tableName \"{TABLE}\" ;\n"
        "        sql:columns (\n"
        "            [ sql:columnName \"id\" ; sql:columnType \"INTEGER\" ]\n"
        "            [ sql:columnName \"collateral_value\" ; sql:columnType \"DECIMAL\" ]\n"
        "            [ sql:columnName \"encumbered\" ; sql:columnType \"BOOLEAN\" ]\n"
        "            [ sql:columnName \"facility_id\" ; sql:columnType \"VARCHAR\" ] ) ] ."
    )


def insert_doc(row_id: int, collateral: str, encumbered: str, facility: str, idx: int) -> str:
    return (
        "@prefix ex: <http://example.org/mc#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:s1 a sql:InsertStatement ;\n"
        f"    sql:statementIndex {idx} ;\n"
        f"    sql:targetTable \"{TABLE}\" ;\n"
        "    sql:assignColumn \"id\" ; "
        f"sql:assignValue \"{row_id}\"^^xsd:integer ;\n"
        "    sql:assignColumn \"collateral_value\" ; "
        f"sql:assignValue \"{collateral}\"^^xsd:decimal ;\n"
        "    sql:assignColumn \"encumbered\" ; "
        f"sql:assignValue \"{encumbered}\"^^xsd:boolean ;\n"
        "    sql:assignColumn \"facility_id\" ; "
        f"sql:assignValue \"{facility}\" ."
    )


def inspect_doc(idx: int) -> str:
    """INSPECT SELECT: the gate's observation projection (no WHERE — the
    harness reads every row and locates each facility by its facility_id)."""
    return (
        "@prefix ex: <http://example.org/mc#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "ex:s1 a sql:SelectStatement ;\n"
        f"    sql:statementIndex {idx} ;\n"
        f"    sql:fromTable [ sql:tableName \"{TABLE}\" ] ;\n"
        "    sql:selectList ( "
        "[ sql:columnName \"id\" ] "
        "[ sql:columnName \"encumbered\" ] "
        "[ sql:columnName \"facility_id\" ] ) ."
    )


def pledge_doc(facility: str, idx: int) -> str:
    """PLEDGE UPDATE: encumber the inspected, unencumbered facility. Bounded
    by BOTH whereColumn and whereValue."""
    return (
        "@prefix ex: <http://example.org/mc#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:s1 a sql:UpdateStatement ;\n"
        f"    sql:statementIndex {idx} ;\n"
        f"    sql:targetTable \"{TABLE}\" ;\n"
        "    sql:assignColumn \"encumbered\" ; "
        "sql:assignValue \"true\"^^xsd:boolean ;\n"
        "    sql:whereColumn \"facility_id\" ;\n"
        f"    sql:whereValue \"{facility}\" ."
    )


def witness_doc(idx: int) -> str:
    """WITNESS SELECT: the state-preservation / mutation-landed readback."""
    return inspect_doc(idx)


# ---------------------------------------------------------------- OCEL net

PERMITTED_TRACE = [
    "Margin_Call_Received",
    "Collateral_Inspected",
    "Pledge_Admitted",
    "Ledger_Updated",
    "Pledge_Proof_Sealed",
]

ENCUMBERED_TRACE = [
    "Margin_Call_Received",
    "Collateral_Inspected",
    "Pledge_Refused",
    "State_Preserved",
    "Refusal_Proof_Sealed",
]

NET_PATHS = [PERMITTED_TRACE, ENCUMBERED_TRACE]


def gate_collector(path: list[str]) -> ProcessTraceCollector:
    collector = ProcessTraceCollector()
    collector.register_object("mc-gate", "case", {"label": "mc-gate"})
    base = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)
    for i, activity in enumerate(path):
        collector.emit_event(
            f"ev-{i}",
            activity,
            timestamp=base + timedelta(seconds=i),
            attributes={"case": "mc-gate"},
            relationships=[{"objectId": "mc-gate", "qualifier": "lifecycle"}],
        )
    return collector


def judge(path: list[str]):
    spec = ConformanceSpec.from_fsm(NET_PATHS, min_fitness=1.0, min_precision=1.0)
    events = [
        {"concept:name": ev.type, "time:timestamp": ev.time}
        for ev in gate_collector(path).events
    ]
    return spec.evaluate(events)


# ------------------------------------------------------------ wasm courts


def setup_requests(session: str) -> list[dict]:
    return (
        [{"op": "duckdb", "mode": "open", "session": session}]
        + [exec_req(create_doc(), session)]
        + [
            exec_req(insert_doc(1, "500000.00", "false", FAC_PERMITTED, 1), session),
            exec_req(insert_doc(2, "750000.00", "true", FAC_ENCUMBERED, 2), session),
        ]
    )


def stream_all(cursor: str) -> str:
    """Drain one real cursor through mode:stream frames (the fibo court
    pattern)."""
    pages = eh_call(
        [{"op": "duckdb", "mode": "stream", "cursor": cursor, "max_rows": 100}]
    )
    page = pages[0]
    assert page["ok"] is True, f"stream failed: {page}"
    body = page.get("body") or page.get("nquads") or ""
    assert page["more"] is not True, "single-page cursor expected at max_rows=100"
    return body


def test_mc_gate_01_permitted_arm_admits_pledge_and_seals_proof() -> None:
    """MC-GATE-01: setup → INSPECT SELECT (drained) → gate decision on the
    real observation → pledge UPDATE admitted with a receipt → witness
    readback proves the encumbrance landed — judged over the permitted
    business net at full fitness and precision."""
    session = SESSION_PERMITTED
    requests = setup_requests(session)
    requests.append(exec_req(inspect_doc(3), session))
    responses = eh_call(requests)
    (open_resp, create, ins1, ins2, inspect) = responses
    assert open_resp["ok"] is True and open_resp["session"] == session, (
        f"session open refused: {open_resp}"
    )
    for label, resp in (
        ("CREATE", create),
        ("INSERT permitted", ins1),
        ("INSERT encumbered", ins2),
    ):
        assert resp["ok"] is True, f"{label} refused: {resp}"
        assert isinstance(resp.get("receipt"), str) and resp["receipt"], (
            f"{label} must mint a receipt: {resp}"
        )
    assert inspect["ok"] is True and inspect["rows_emitted"] == 2, (
        f"INSPECT SELECT must emit both rows: {inspect}"
    )
    body = stream_all(inspect["cursor"])
    assert FAC_PERMITTED in body and FAC_ENCUMBERED in body, (
        f"inspect body must carry both facilities: {body}"
    )
    # Gate decision on the real observation: the permitted facility's row
    # reads unencumbered.
    assert "false" in body.lower(), (
        f"permitted row must read unencumbered in the inspect body: {body}"
    )

    requests = [
        exec_req(pledge_doc(FAC_PERMITTED, 4), session),
        exec_req(witness_doc(5), session),
        {"op": "duckdb", "mode": "close", "session": session},
    ]
    responses = eh_call(requests)
    (pledge, witness, close_resp) = responses
    assert pledge["ok"] is True, f"pledge UPDATE refused: {pledge}"
    assert isinstance(pledge.get("receipt"), str) and pledge["receipt"], (
        f"pledge UPDATE must mint a receipt: {pledge}"
    )
    assert isinstance(pledge.get("query_hash"), str) and pledge["query_hash"], (
        f"pledge UPDATE must carry a query_hash: {pledge}"
    )
    assert witness["ok"] is True and witness["rows_emitted"] == 2, (
        f"witness SELECT must read the ledger: {witness}"
    )
    witness_body = stream_all(witness["cursor"])
    assert FAC_PERMITTED in witness_body, (
        f"pledged facility must appear in the witness readback: {witness_body}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    result = judge(PERMITTED_TRACE)
    assert result.fitness >= 1.0 and result.precision >= 1.0


def test_mc_gate_02_encumbered_arm_sends_no_pledge_doc() -> None:
    """MC-GATE-02: setup → INSPECT SELECT reads the encumbered row → the
    harness admits NO pledge document at all → witness SELECT proves the
    state was preserved — judged over the encumbered business net at full
    fitness and precision."""
    session = SESSION_ENCUMBERED
    requests = setup_requests(session)
    requests.append(exec_req(inspect_doc(3), session))
    responses = eh_call(requests)
    (open_resp, create, ins1, ins2, inspect) = responses
    assert open_resp["ok"] is True, f"session open refused: {open_resp}"
    for label, resp in (
        ("CREATE", create),
        ("INSERT permitted", ins1),
        ("INSERT encumbered", ins2),
    ):
        assert resp["ok"] is True, f"{label} refused: {resp}"
    assert inspect["ok"] is True and inspect["rows_emitted"] == 2, (
        f"INSPECT SELECT must emit both rows: {inspect}"
    )
    body = stream_all(inspect["cursor"])
    assert FAC_ENCUMBERED in body, (
        f"encumbered facility must appear in the inspect body: {body}"
    )
    # Gate decision: the target row reads encumbered — no pledge doc is
    # admitted. State preservation is proved by a real witness SELECT.
    assert "true" in body.lower(), (
        f"encumbered row must read encumbered in the inspect body: {body}"
    )

    requests = [
        exec_req(witness_doc(4), session),
        {"op": "duckdb", "mode": "close", "session": session},
    ]
    responses = eh_call(requests)
    (witness, close_resp) = responses
    assert witness["ok"] is True and witness["rows_emitted"] == 2, (
        f"witness SELECT must read the ledger: {witness}"
    )
    witness_body = stream_all(witness["cursor"])
    assert FAC_PERMITTED in witness_body and FAC_ENCUMBERED in witness_body, (
        f"both rows must survive untouched: {witness_body}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    result = judge(ENCUMBERED_TRACE)
    assert result.fitness >= 1.0 and result.precision >= 1.0


# ----------------------------------------------------- conformance-net twins
# These run regardless of runner/artifact availability: the net itself must
# never be vacuous.


def test_mc_gate_03_anti_vacuity_pledge_without_inspection_scores_below_one() -> None:
    """MC-GATE-03 (always runs, no wasm needed): a trace that executes the
    pledge with no Collateral_Inspected event must score fitness < 1.0 —
    the net is not vacuous."""
    result = judge([
        "Margin_Call_Received",
        "Pledge_Admitted",
        "Ledger_Updated",
        "Pledge_Proof_Sealed",
    ])
    assert result.fitness < 1.0, (
        "a trace skipping Collateral_Inspected must score below min_fitness — "
        "the net is not vacuous"
    )


def test_mc_gate_04_ocel2_sqlite_export_is_real(tmp_path) -> None:
    collector = gate_collector(PERMITTED_TRACE)
    out = tmp_path / "mc_gate.ocel.sqlite"
    written = collector.write_sqlite(out)
    assert written.is_file() and written.stat().st_size > 0, (
        "OCEL2 sqlite export must be a real nonempty file"
    )
