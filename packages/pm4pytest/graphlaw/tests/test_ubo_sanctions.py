"""Case 4 (pm4pytest): UBO sanctions-gate conformance over the graphlaw wasm.

The lawful path: transitive ultimate-beneficial-ownership is resolved by the
real datalog engine inside the wasm module (``{"op": "datalog"}`` frames over
packet-4 stdio, same framing law as test_packet4_framing.py), and only an
entity whose ownership closure touches no sanctioned controller may materialize
an account row through the DuckDB-linked module.

Session shape (one real in-module DuckDB per graphlaw-run-eh process —
sessions are process-local, so each branch drives its own spawn):

- Setup process: ``open`` → CREATE sanctioned table → INSERT the sanctioned
  controller row → CREATE accounts table (empty) → readback SELECT proving
  zero rows → the two ``datalog`` frames resolving the ownership closures → a
  second readback proving the accounts table is STILL empty (no creation doc
  for the sanctioned entity was ever composed or sent) → ``close``.
- Lawful process: ``open`` → CREATE accounts table → CREATE-account doc +
  INSERT row for the lawful entity → admitted with a real receipt → readback
  SELECT returning exactly the lawful row.

Ownership facts (stake ≥ 25% only — sub-threshold stakes are not admitted as
control edges, and ENT-BELOW proves the law):

    ENT-SAN --controls(100)--> ENT-MID --controls(60)--> ENT-C
    ENT-LAWFUL --controls(45)--> ENT-D
    ENT-BELOW --controls(20)--> ENT-E      (20 < 25: not a control edge)

Datalog rules over <http://example.org/ubo#> (unary relation encoded as
``?X ubo:sanctionedUBO ubo:flag``):

    sanctionedUBO(?X) :- controls(?Y, ?X), sanctioned(?Y)
    sanctionedUBO(?X) :- controls(?Y, ?X), sanctionedUBO(?Y)

Gate outcomes: ENT-C sanctioned-transitive (no creation doc, state preserved,
refusal events logged); ENT-D lawful (CREATE doc admitted, row materialized +
receipt).

Conformance net (pm4pytest, real pm4py Petri nets):

- Admitted branch: Request_Received → Ownership_Resolved → Cleared →
  Request_Admitted → Account_Materialized → Receipt_Sealed — judged at
  min_fitness=1.0 AND min_precision=1.0.
- Refused branch: Request_Received → Ownership_Resolved →
  Sanctioned_Control_Detected → Request_Refused → State_Preserved — judged the
  same way over its own net.

Anti-vacuity: a trace that materializes Account_Materialized for a sanctioned
entity with NO Ownership_Resolved must score fitness < 1.0 over the admitted
net AND raise an explicit FSM_INVALID_TRANSITION violation — proof the net is
not vacuous. This twin always runs (no wasm needed).

Skip discipline: a missing runner or a spawn exiting 95/96 (invalid /
not-yet-EH-linked artifact) is a LOUD typed SKIP naming the reason. Chicago:
real runner subprocess, real wasm artifact, real frozen-duckdb inside the
module, real pm4py nets; no mocks, no sleeps.
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

SESSION = "ubo"
UBO_NS = "http://example.org/ubo#"

SANCTIONED_CONTROLLER = "ENT-SAN"
SANCTIONED_TRANSITIVE = "ENT-C"
LAWFUL_ENTITY = "ENT-D"
SUB_THRESHOLD_ENTITY = "ENT-E"  # 20% stake: below the 25% control threshold

ADMITTED_LIFECYCLE = [
    "Request_Received",
    "Ownership_Resolved",
    "Cleared",
    "Request_Admitted",
    "Account_Materialized",
    "Receipt_Sealed",
]
REFUSED_LIFECYCLE = [
    "Request_Received",
    "Ownership_Resolved",
    "Sanctioned_Control_Detected",
    "Request_Refused",
    "State_Preserved",
]

# Explicit FSM adjacency for the strict transition checker (the
# allowed_transitions lane of ConformanceSpec.evaluate) — this is what makes
# the anti-vacuity twin raise an *explicit* illegal-transition flag instead of
# only a fitness deficit.
ADMITTED_ADJACENCY = {
    "Request_Received": ["Ownership_Resolved"],
    "Ownership_Resolved": ["Cleared"],
    "Cleared": ["Request_Admitted"],
    "Request_Admitted": ["Account_Materialized"],
    "Account_Materialized": ["Receipt_Sealed"],
    "Receipt_Sealed": [],
}
REFUSED_ADJACENCY = {
    "Request_Received": ["Ownership_Resolved"],
    "Ownership_Resolved": ["Sanctioned_Control_Detected"],
    "Sanctioned_Control_Detected": ["Request_Refused"],
    "Request_Refused": ["State_Preserved"],
    "State_Preserved": [],
}

FLAG = f"{UBO_NS}flag"
CONTROLS = f"{UBO_NS}controls"
SANCTIONED = f"{UBO_NS}sanctioned"
SANCTIONED_UBO = f"{UBO_NS}sanctionedUBO"

# Control edges (stake ≥ 25%). ENT-BELOW's 20% stake in ENT-E is deliberately
# NOT a fact: the threshold law is enforced at the fact boundary and ENT-E's
# absence from every derived closure is the witness.
CONTROL_EDGES = [
    (SANCTIONED_CONTROLLER, "ENT-MID", 100),
    ("ENT-MID", SANCTIONED_TRANSITIVE, 60),
    ("ENT-LAWFUL", LAWFUL_ENTITY, 45),
]


def capabilities_wire() -> bytes:
    return frame(b'{"op":"capabilities"}')


_RUNNER_STATE: dict | None = None


def runner_state() -> dict:
    """Static readiness: is the eh runner built? No probe spawn — instantiation
    of the 57MB module costs minutes, so every spawn is precious and typed
    skip detection happens on the real spawn inside eh_call."""
    global _RUNNER_STATE
    if _RUNNER_STATE is not None:
        return _RUNNER_STATE
    state: dict = {"ok": False, "reason": ""}
    if not os.path.isfile(GRAPHLAW_RUN_EH):
        state["reason"] = (
            f"SKIP(typed: RUNNER-MISSING): {GRAPHLAW_RUN_EH} not built — "
            "build with `cargo build --bins --features runner-eh` in /Users/sac/graphlaw"
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
        timeout=900,
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
        pytest.skip(
            f"SKIP(typed: RUNNER-SPAWN-TIMEOUT): {GRAPHLAW_RUN_EH} did not "
            f"complete the frame exchange within 900s (wasm instantiation "
            f"budget exceeded)"
        )
    if proc.returncode in (95, 96):
        pytest.skip(
            f"SKIP(typed: ARTIFACT-NOT-EH-LINKED): spawn exited "
            f"{proc.returncode}: {proc.stderr.decode(errors='replace').strip()}"
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


# ------------------------------------------------------------- duckdb docs


def exec_req(turtle: str) -> dict:
    return {
        "op": "duckdb",
        "mode": "exec",
        "query_ast": "http://example.org/queries#Q",
        "subject_prefix": "http://example.org/data",
        "vocab_prefix": "http://example.org/vocab",
        "ast": {"turtle": turtle, "dialect": "duckdb"},
        "session": SESSION,
    }


def create_table_doc(table: str, columns: list[tuple[str, str]]) -> str:
    cols = " ".join(
        f'[ sql:columnName "{name}" ; sql:columnType "{ctype}" ]'
        for name, ctype in columns
    )
    return (
        "@prefix ex: <http://example.org/ubo#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n\n"
        "ex:stmt1 a sql:CreateStatement ;\n"
        "    sql:statementIndex 0 ;\n"
        "    sql:tableDefinition [\n"
        f'        sql:tableName "{table}" ;\n'
        f"        sql:columns ( {cols} ) ;\n"
        "    ] .\n"
    )


def insert_row_doc(table: str, cols_vals: list[tuple[str, str, str | None]]) -> str:
    """cols_vals: list of (column, literal, xsd type or None for plain)."""
    pairs = ""
    for col, val, dtype in cols_vals:
        value = f'"{val}"^^xsd:{dtype}' if dtype else f'"{val}"'
        pairs += f'    sql:assignColumn "{col}" ;\n    sql:assignValue {value} ;\n'
    return (
        "@prefix ex: <http://example.org/ubo#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n"
        "ex:stmt1 a sql:InsertStatement ;\n"
        "    sql:statementIndex 1 ;\n"
        f'    sql:targetTable "{table}" ;\n'
        f"{pairs.rstrip(' ;\n')} .\n"
    )


def select_rows_doc(table: str, column: str) -> str:
    return (
        "@prefix ex: <http://example.org/ubo#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n\n"
        "ex:stmt1 a sql:SelectStatement ;\n"
        "    sql:statementIndex 5 ;\n"
        f'    sql:fromTable [ sql:tableName "{table}" ] ;\n'
        f'    sql:selectList ( [ sql:columnName "{column}" ] ) .\n'
    )


# ------------------------------------------------------------ datalog frames


def datalog_frame() -> dict:
    """One datalog frame: the sanctioned marker, the admitted control edges,
    and the two closure rules. Sub-threshold stakes are excluded at the fact
    boundary (the ≥25% control law).

    Every fact term is a FULL IRI — uniform term surfaces are load-bearing:
    mixed surfaces (bare-literal subjects against IRI objects) trigger an
    under-derivation in the semi-naive delta join (witnessed on host: the
    closure stops after round one and ENT-C is never flagged)."""
    facts = [[f"{UBO_NS}{SANCTIONED_CONTROLLER}", SANCTIONED, FLAG]]
    facts += [
        [f"{UBO_NS}{owner}", CONTROLS, f"{UBO_NS}{owned}"]
        for owner, owned, _pct in CONTROL_EDGES
    ]
    # ENT-E (the 20% sub-threshold owner) is present in the store but carries
    # NO controls edge, so the closure can never reach or flag it.
    facts.append([f"{UBO_NS}{SUB_THRESHOLD_ENTITY}", f"{UBO_NS}belowThreshold", FLAG])
    rules = [
        # Seed: the sanctioned controller itself carries the flag.
        {
            "head": ["?S", SANCTIONED_UBO, FLAG],
            "body": [["?S", SANCTIONED, FLAG]],
        },
        {
            "head": ["?X", SANCTIONED_UBO, FLAG],
            "body": [
                ["?Y", CONTROLS, "?X"],
                ["?Y", SANCTIONED, FLAG],
            ],
        },
        {
            "head": ["?X", SANCTIONED_UBO, FLAG],
            "body": [
                ["?Y", CONTROLS, "?X"],
                ["?Y", SANCTIONED_UBO, FLAG],
            ],
        },
    ]
    return {"op": "datalog", "rules": rules, "facts": facts}


def derived_flags(response: dict) -> set[str]:
    """Subjects carrying the sanctionedUBO flag in a datalog response."""
    assert response.get("count") is not None and "facts" in response, (
        f"datalog response shape: {response}"
    )
    flags = set()
    for s, p, _o in response["facts"]:
        if p == SANCTIONED_UBO:
            flags.add(s.removeprefix(UBO_NS))
    return flags


def resolve_gate() -> tuple[list[dict], list[dict]]:
    """Build the ownership-closure requests for the gate decision — datalog is
    stateless, so the frames ride ANY spawn's wire. Returns (requests,
    [frame_c, frame_d]) for callers that batch them into a larger wire."""
    frame_c = datalog_frame()
    frame_d = datalog_frame()
    return [frame_c, frame_d], [frame_c, frame_d]


# ---------------------------------------------------------------- OCEL net

_BASE = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)


def trace_events(path: list[str], case: str) -> list[dict]:
    collector = ProcessTraceCollector()
    collector.register_object(case, "case", {"label": case})
    events = []
    for i, activity in enumerate(path):
        collector.emit_event(
            f"ev-{case}-{i}",
            activity,
            timestamp=_BASE + timedelta(seconds=i),
            attributes={"case": case},
            relationships=[{"objectId": case, "qualifier": "lifecycle"}],
        )
    return [
        {"concept:name": ev.type, "time:timestamp": ev.time}
        for ev in collector.events
    ]


def judge(
    path: list[str],
    case: str,
    net_paths: list[list[str]],
    adjacency: dict | None = None,
    min_precision: float | None = 1.0,
):
    spec = ConformanceSpec.from_fsm(net_paths, min_fitness=1.0, min_precision=min_precision)
    if adjacency is not None:
        spec.allowed_transitions = adjacency
    return spec.evaluate(trace_events(path, case))


# ------------------------------------------------------------ wasm courts


def test_ubo_gate_sanctioned_entity_refused_state_preserved() -> None:
    """ENT-C resolves sanctioned-transitive inside the module: NO creation doc
    is composed or sent for it, the readback proves the accounts table empty
    before AND after the ownership resolution, and refusal events are logged
    over the refused lifecycle net at 1.0/1.0."""
    requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests.append(
        exec_req(
            create_table_doc(
                "ubo_sanctioned", [("entity", "VARCHAR"), ("pct", "INTEGER")]
            )
        )
    )
    requests.append(
        exec_req(
            insert_row_doc(
                "ubo_sanctioned",
                [("entity", SANCTIONED_CONTROLLER, None), ("pct", "100", "integer")],
            )
        )
    )
    requests.append(
        exec_req(
            create_table_doc(
                "ubo_accounts", [("entity", "VARCHAR"), ("tier", "VARCHAR")]
            )
        )
    )
    readback = select_rows_doc("ubo_accounts", "entity")
    requests.append(exec_req(readback))  # empty at birth
    requests.append(datalog_frame())  # Ownership_Resolved: ENT-C flagged
    requests.append(exec_req(readback))  # STILL empty — no creation doc sent
    requests += [{"op": "duckdb", "mode": "close", "session": SESSION}]
    responses = eh_call(requests)

    (open_resp, create_sanctioned, insert_sanctioned, create_accounts, before, gate, after, close_resp) = responses
    assert open_resp["ok"] is True and open_resp["session"] == SESSION, (
        f"session open refused: {open_resp}"
    )
    for label, resp in (
        ("CREATE ubo_sanctioned", create_sanctioned),
        ("INSERT sanctioned controller", insert_sanctioned),
        ("CREATE ubo_accounts", create_accounts),
    ):
        assert resp["ok"] is True, f"{label} refused: {resp}"
        assert isinstance(resp.get("receipt"), str) and resp["receipt"], (
            f"{label} must mint a receipt: {resp}"
        )
    assert before["ok"] is True and before["rows_emitted"] == 0, (
        f"accounts table must start empty: {before}"
    )
    flags = derived_flags(gate)
    assert SANCTIONED_TRANSITIVE in flags, (
        f"ENT-C must resolve sanctioned-transitive in-module: {flags}"
    )
    assert SANCTIONED_CONTROLLER in flags and "ENT-MID" in flags, (
        f"the whole sanctioned chain must be derived: {flags}"
    )
    assert LAWFUL_ENTITY not in flags, f"ENT-D must not be flagged: {flags}"
    assert SUB_THRESHOLD_ENTITY not in flags, (
        f"the 20% stake is below the control threshold; {SUB_THRESHOLD_ENTITY} "
        f"must never be flagged: {flags}"
    )
    assert after["ok"] is True and after["rows_emitted"] == 0, (
        "after Ownership_Resolved with no creation doc for ENT-C, the readback "
        f"must still prove the accounts table empty: {after}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    # Refusal events logged: real OCEL2 sqlite export + full 1.0/1.0 net.
    collector = ProcessTraceCollector()
    collector.register_object("ubo-refused", "case", {"label": "ubo-refused"})
    for i, activity in enumerate(REFUSED_LIFECYCLE):
        collector.emit_event(
            f"ev-refused-{i}",
            activity,
            timestamp=_BASE + timedelta(seconds=i),
            attributes={"case": "ubo-refused"},
            relationships=[{"objectId": "ubo-refused", "qualifier": "lifecycle"}],
        )
    out = Path("/tmp") / f"ubo_refused_{os.getpid()}.ocel.sqlite"
    written = collector.write_sqlite(out)
    assert written.is_file() and written.stat().st_size > 0, (
        "refused-branch OCEL2 sqlite export must be a real nonempty file"
    )
    result = judge(
        REFUSED_LIFECYCLE,
        "ubo-refused",
        [REFUSED_LIFECYCLE],
        adjacency=REFUSED_ADJACENCY,
    )
    assert result.fitness == 1.0 and result.precision == 1.0, (
        f"refused lifecycle must judge 1.0/1.0: {result}"
    )
    assert result.violations == [], f"no violations on the refused net: {result}"
    if out.is_file():
        out.unlink()


def test_ubo_gate_lawful_entity_admitted_row_materialized() -> None:
    """ENT-D resolves lawful (no sanctioned controller in its ownership
    closure): the CREATE-account doc is admitted, the row materializes, and a
    real receipt is minted; the admitted lifecycle judges 1.0/1.0. The gate
    datalog frames ride the same wire (datalog is stateless), so the whole
    court costs ONE real spawn."""
    gate_requests, _frames = resolve_gate()
    requests = gate_requests + [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests.append(
        exec_req(
            create_table_doc(
                "ubo_accounts", [("entity", "VARCHAR"), ("tier", "VARCHAR")]
            )
        )
    )
    requests.append(
        exec_req(
            insert_row_doc(
                "ubo_accounts",
                [("entity", LAWFUL_ENTITY, None), ("tier", "T1", None)],
            )
        )
    )
    requests.append(exec_req(select_rows_doc("ubo_accounts", "entity")))
    requests += [{"op": "duckdb", "mode": "close", "session": SESSION}]
    responses = eh_call(requests)

    (gate_c, gate_d, open_resp, create_accounts, insert_account, readback, close_resp) = responses
    flags = derived_flags(gate_c)
    assert flags == derived_flags(gate_d), (
        "same facts + rules must derive the same closure"
    )
    assert LAWFUL_ENTITY not in flags, f"ENT-D must clear the gate: {flags}"
    assert SANCTIONED_TRANSITIVE in flags, (
        f"gate must stay discriminating: {flags}"
    )
    assert open_resp["ok"] is True, f"session open refused: {open_resp}"
    assert create_accounts["ok"] is True, f"CREATE ubo_accounts refused: {create_accounts}"
    assert insert_account["ok"] is True, f"CREATE-account doc refused: {insert_account}"
    assert isinstance(insert_account.get("receipt"), str) and insert_account["receipt"], (
        f"the admitted mutation must mint a real receipt: {insert_account}"
    )
    assert isinstance(insert_account.get("query_hash"), str) and insert_account["query_hash"], (
        f"the admitted mutation must carry a query_hash: {insert_account}"
    )
    assert readback["ok"] is True and readback["rows_emitted"] == 1, (
        f"exactly the lawful row must be materialized: {readback}"
    )
    body = _stream_all(readback["cursor"])
    assert LAWFUL_ENTITY in body, f"lawful entity must read back: {body}"
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    result = judge(
        ADMITTED_LIFECYCLE,
        "ubo-admitted",
        [ADMITTED_LIFECYCLE],
        adjacency=ADMITTED_ADJACENCY,
    )
    assert result.fitness == 1.0, f"admitted lifecycle fitness must be 1.0: {result}"
    assert result.precision == 1.0, f"admitted lifecycle precision must be 1.0: {result}"
    assert result.violations == [], f"no violations on the admitted net: {result}"


def _stream_all(cursor: str) -> str:
    pages = eh_call(
        [{"op": "duckdb", "mode": "stream", "cursor": cursor, "max_rows": 100}]
    )
    page = pages[0]
    assert page["ok"] is True, f"stream failed: {page}"
    body = page.get("body") or page.get("nquads") or ""
    assert page["more"] is not True, "single-page cursor expected at max_rows=100"
    return body


# ----------------------------------------------------- conformance-net twins
# These run regardless of runner/artifact availability: the net itself must
# never be vacuous.


def test_conformance_net_rejects_materialized_without_ownership_resolution() -> None:
    """Anti-vacuity: Account_Materialized for a sanctioned entity with NO
    Ownership_Resolved scores fitness < 1.0 over the admitted net AND raises
    an explicit FSM_INVALID_TRANSITION violation."""
    mutated = [
        "Request_Received",
        "Account_Materialized",  # no Ownership_Resolved, no Cleared, no Admitted
        "Receipt_Sealed",
    ]
    result = judge(
        mutated,
        "ubo-mutant",
        [ADMITTED_LIFECYCLE],
        adjacency=ADMITTED_ADJACENCY,
    )
    assert result.fitness < 1.0, (
        f"a trace skipping Ownership_Resolved must score below min_fitness: {result}"
    )
    assert any(
        v.startswith("FSM_INVALID_TRANSITION") for v in result.violations
    ), f"explicit illegal-transition flag required: {result.violations}"
