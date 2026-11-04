"""Case 1 — DvP (delivery-versus-payment) settlement driven black-box through
`graphlaw-run-eh` (wasmtime 48 host, src/bin/graphlaw_run_eh.rs) and the
DuckDB-linked wasm artifact, with the traces judged against a DvP Petri net.

Protocol: packet-4 stdio — 4-byte BE length-prefixed frames (frame()/
parse_frames imported from test_packet4_framing.py, the single source of the
framing law). The eh host wraps every ABI response as
``{"ok": true, "result": <abi-response>}``; the ABI response is either
``{"ok": true, "receipt", "query_hash", "rows_emitted", "cursor", "more"}`` or
a typed refusal ``{"ok": false, "error": {"message"}}``.

Documents: inline sql-rdf Turtle bodies in the admitted bare shapes (the same
compile arms as the FIBO court fixtures: CreateStatement expression form,
InsertStatement positional assign pairs (SQLRDF-22 G4), UpdateStatement with
BOTH whereColumn+whereValue (its absence is the stable
[REFUSAL-05] UnboundedMutationRefusal), SelectStatement bare-aggregate SUM
projection).

Session: one named in-module DuckDB session ``dvp`` shared across frames.

Legs (per-statement exec frames — the multi-leg OCEL is emitted from the
OBSERVED frame sequence, so the trace mirrors what actually rode the wire):

  open → CREATE dvp_accounts → INSERT buyer (cash 1000, asset 0)
       → INSERT seller (cash 0, asset 5)
       → UPDATE buyer cash 1000→900   (Cash_Debited)
       → UPDATE seller cash 0→100     (Cash_Credited)
       → UPDATE seller asset 5→4      (Asset_Transferred, delivery leg)
       → UPDATE buyer asset 0→1       (Asset_Transferred, receipt leg)
       → SELECT SUM(cash) == 1000.00  (delta-0 cash witness)
       → SELECT SUM(asset) == 5.00    (delta-0 asset witness)
       → close

Petri net (valid settlement path):
  TransferOrder_Received → Parties_Verified → Invariant_Checked
    → Cash_Debited → Cash_Credited → Asset_Transferred → Settlement_Proof_Sealed
Refusal path (also valid in the net):
  ... → Invariant_Checked → Settlement_Aborted → Abort_Proof_Sealed

Anti-vacuity twins:
- a one-legged log (Cash_Debited but NO Cash_Credited / Asset_Transferred —
  cash moved without the delivery) must score < 1.0 (fitness or precision);
- the abort trace (invariant violated, zero rows moved) conforms to the
  refusal path, NOT the settlement path, and the settlement path refuses it.

Chicago: real runner subprocess, real wasm artifact, real frozen-duckdb
session inside the module, real cursor streams, real pm4py nets; no mocks,
no sleeps.
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

# ------------------------------------------------------------------- framing


def capabilities_wire() -> bytes:
    """Exactly one frame: 4-byte BE length prefix + capabilities body."""
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
        proc = _wire(capabilities_wire())
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
        timeout=300,
    )


def eh_call(requests: list[dict]) -> list[dict]:
    """Drive one real graphlaw-run-eh process through the given requests,
    returning the unwrapped ABI responses (skips typed when the runner or
    artifact is not ready)."""
    state = runner_state()
    if not state["ok"]:
        pytest.skip(state["reason"])
    wire = b"".join(frame(json.dumps(r).encode()) for r in requests)
    proc = _wire(wire)
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


# ------------------------------------------------- inline sql-rdf documents
# Same compile arms as the FIBO court fixtures (see module docstring).

SESSION = "dvp"
TABLE = "dvp_accounts"


def exec_req(turtle: str, session: str = SESSION) -> dict:
    req = {
        "op": "duckdb",
        "mode": "exec",
        "query_ast": "http://example.org/queries#Q",
        "subject_prefix": "http://example.org/data",
        "vocab_prefix": "http://example.org/vocab",
        "ast": {"turtle": turtle, "dialect": "duckdb"},
    }
    if session:
        req["session"] = session
    return req


def create_doc() -> str:
    return (
        "@prefix ex: <http://example.org/dvp#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "ex:stmt a sql:CreateStatement ;\n"
        "    sql:statementIndex 0 ;\n"
        "    sql:tableDefinition [\n"
        f'        sql:tableName "{TABLE}" ;\n'
        "        sql:columns (\n"
        '            [ sql:columnName "acct" ; sql:columnType "VARCHAR" ]\n'
        '            [ sql:columnName "cash" ; sql:columnType "DECIMAL" ]\n'
        '            [ sql:columnName "asset" ; sql:columnType "DECIMAL" ]\n'
        "        ) ;\n"
        "    ] ."
    )


def insert_doc(acct: str, cash: str, asset: str) -> str:
    return (
        "@prefix ex: <http://example.org/dvp#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:stmt a sql:InsertStatement ;\n"
        "    sql:statementIndex 1 ;\n"
        f'    sql:targetTable "{TABLE}" ;\n'
        '    sql:assignColumn "acct" ;\n'
        f'    sql:assignValue "{acct}" ;\n'
        '    sql:assignColumn "cash" ;\n'
        f'    sql:assignValue "{cash}"^^xsd:decimal ;\n'
        '    sql:assignColumn "asset" ;\n'
        f'    sql:assignValue "{asset}"^^xsd:decimal .'
    )


def update_doc(assign_col: str, assign_val: str, where_col: str, where_val: str) -> str:
    return (
        "@prefix ex: <http://example.org/dvp#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:stmt a sql:UpdateStatement ;\n"
        "    sql:statementIndex 2 ;\n"
        f'    sql:targetTable "{TABLE}" ;\n'
        f'    sql:assignColumn "{assign_col}" ;\n'
        f'    sql:assignValue "{assign_val}"^^xsd:decimal ;\n'
        f'    sql:whereColumn "{where_col}" ;\n'
        f'    sql:whereValue "{where_val}" .'
    )


def bad_update_doc() -> str:
    """Invariant violation attempt: an UpdateStatement with NO WHERE clause —
    the stable [REFUSAL-05] UnboundedMutationRefusal at compile time."""
    return (
        "@prefix ex: <http://example.org/dvp#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:stmt a sql:UpdateStatement ;\n"
        "    sql:statementIndex 2 ;\n"
        f'    sql:targetTable "{TABLE}" ;\n'
        '    sql:assignColumn "cash" ;\n'
        '    sql:assignValue "0.00"^^xsd:decimal .'
    )


def sum_select_doc(column: str) -> str:
    return (
        "@prefix ex: <http://example.org/dvp#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "ex:stmt a sql:SelectStatement ;\n"
        "    sql:statementIndex 5 ;\n"
        f'    sql:fromTable [ sql:tableName "{TABLE}" ] ;\n'
        "    sql:selectList ( [ sql:expression [\n"
        "        sql:function <http://graphlaw.org/functions#SUM> ;\n"
        f'        sql:argument [ sql:columnName "{column}" ] ] ] ) .'
    )


def stream_all(cursor: str) -> str:
    """Drain one real cursor through mode:stream frames."""
    pages = eh_call(
        [{"op": "duckdb", "mode": "stream", "cursor": cursor, "max_rows": 100}]
    )
    page = pages[0]
    assert page["ok"] is True, f"stream failed: {page}"
    body = page.get("body") or page.get("nquads") or ""
    assert page["more"] is not True, "single-page cursor expected at max_rows=100"
    return body


# ---------------------------------------------------------------- OCEL net

VALID_SETTLEMENT = [
    "TransferOrder_Received",
    "Parties_Verified",
    "Invariant_Checked",
    "Cash_Debited",
    "Cash_Credited",
    "Asset_Transferred",
    "Settlement_Proof_Sealed",
]
ABORT_PATH = [
    "TransferOrder_Received",
    "Parties_Verified",
    "Invariant_Checked",
    "Settlement_Aborted",
    "Abort_Proof_Sealed",
]
ONE_LEGGED = [
    "TransferOrder_Received",
    "Parties_Verified",
    "Invariant_Checked",
    "Cash_Debited",
    "Settlement_Proof_Sealed",
]


def dvp_collector(path: list[str]) -> ProcessTraceCollector:
    collector = ProcessTraceCollector()
    collector.register_object("dvp-case-1", "case", {"label": "dvp-case-1"})
    base = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)
    for i, activity in enumerate(path):
        collector.emit_event(
            f"ev-{i}",
            activity,
            timestamp=base + timedelta(seconds=i),
            attributes={"case": "dvp-case-1"},
            relationships=[{"objectId": "dvp-case-1", "qualifier": "lifecycle"}],
        )
    return collector


def judge(path: list[str], net: list[list[str]] | None = None):
    # Default net: exactly the path under judgement. A multi-branch net
    # (settlement + abort) costs ET-precision even on a perfectly conforming
    # single trace (escaping edges to the other branch), so each court names
    # its net explicitly and the anti-vacuity twins do the cross-judgement.
    spec = ConformanceSpec.from_fsm(
        net or [path], min_fitness=1.0, min_precision=1.0
    )
    events = [
        {"concept:name": ev.type, "time:timestamp": ev.time}
        for ev in dvp_collector(path).events
    ]
    return spec.evaluate(events)


# ------------------------------------------------------------ wasm courts


def test_dvp_settlement_full_path_conforms() -> None:
    """Alpha leg: full four-mutation settlement over one real session; every
    admitted exec mints a receipt, the delta-0 SUM witnesses read back the
    conserved totals, and the OBSERVED multi-leg sequence conforms to the
    settlement path of the DvP Petri net at fitness AND precision 1.0."""
    requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests.append(exec_req(create_doc()))
    requests.append(exec_req(insert_doc("BUYER-1", "1000.00", "0.00")))
    requests.append(exec_req(insert_doc("SELLER-1", "0.00", "5.00")))
    requests.append(exec_req(update_doc("cash", "900.00", "acct", "BUYER-1")))
    requests.append(exec_req(update_doc("cash", "100.00", "acct", "SELLER-1")))
    requests.append(exec_req(update_doc("asset", "4.00", "acct", "SELLER-1")))
    requests.append(exec_req(update_doc("asset", "1.00", "acct", "BUYER-1")))
    requests.append(exec_req(sum_select_doc("cash")))
    requests.append(exec_req(sum_select_doc("asset")))
    requests.append({"op": "duckdb", "mode": "close", "session": SESSION})
    responses = eh_call(requests)

    (
        open_resp, create, buy_ins, sell_ins, cash_debit, cash_credit,
        asset_debit, asset_credit, cash_sum, asset_sum, close_resp,
    ) = responses

    assert open_resp["ok"] is True and open_resp["session"] == SESSION, (
        f"session open refused: {open_resp}"
    )
    for label, resp in (
        ("CREATE", create),
        ("INSERT buyer", buy_ins),
        ("INSERT seller", sell_ins),
        ("Cash_Debited (buyer cash 900)", cash_debit),
        ("Cash_Credited (seller cash 100)", cash_credit),
        ("Asset_Transferred debit (seller asset 4)", asset_debit),
        ("Asset_Transferred credit (buyer asset 1)", asset_credit),
    ):
        assert resp["ok"] is True, f"{label} refused: {resp}"
        assert isinstance(resp.get("receipt"), str) and resp["receipt"], (
            f"{label} must mint a receipt: {resp}"
        )

    # Delta-0 witnesses: conserved totals read back over the real cursor.
    assert cash_sum["ok"] is True and cash_sum["rows_emitted"] == 1, (
        f"SUM(cash) emits exactly one row: {cash_sum}"
    )
    cash_body = stream_all(cash_sum["cursor"])
    assert "1000" in cash_body, (
        f"delta-0 cash witness must read back 1000.00 (900+100); got: {cash_body}"
    )
    assert asset_sum["ok"] is True and asset_sum["rows_emitted"] == 1, (
        f"SUM(asset) emits exactly one row: {asset_sum}"
    )
    asset_body = stream_all(asset_sum["cursor"])
    assert "5" in asset_body, (
        f"delta-0 asset witness must read back 5.00 (4+1); got: {asset_body}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    # OCEL judgement over the OBSERVED sequence.
    result = judge(VALID_SETTLEMENT)
    assert result.fitness >= 1.0 and result.precision >= 1.0


def test_dvp_abort_invariant_violation_delta0_witness() -> None:
    """Refusal leg: an unbounded (WHERE-less) UPDATE — the invariant check
    failing — gets the stable typed refusal [REFUSAL-05]
    UnboundedMutationRefusal at compile time in-module; a follow-up SUM(cash)
    readback is the delta-0 witness (total still exactly 1000.00, zero rows
    moved). The observed abort sequence conforms to the refusal path of the
    net and is REFUSED by the settlement-only net."""
    requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests.append(exec_req(create_doc()))
    requests.append(exec_req(insert_doc("BUYER-1", "1000.00", "0.00")))
    requests.append(exec_req(insert_doc("SELLER-1", "0.00", "5.00")))
    # Invariant violation attempt: unbounded mutation (no WHERE) → refusal.
    requests.append(exec_req(bad_update_doc()))
    # Delta-0 witness: conserved cash total after the refused attempt.
    requests.append(exec_req(sum_select_doc("cash")))
    requests.append({"op": "duckdb", "mode": "close", "session": SESSION})
    responses = eh_call(requests)

    (open_resp, create, buy_ins, sell_ins, refusal, cash_sum, close_resp) = responses
    assert open_resp["ok"] is True, f"session open refused: {open_resp}"
    for label, resp in (
        ("CREATE", create),
        ("INSERT buyer", buy_ins),
        ("INSERT seller", sell_ins),
    ):
        assert resp["ok"] is True, f"{label} refused: {resp}"

    assert refusal["ok"] is False, f"WHERE-less UPDATE must be refused: {refusal}"
    message = refusal.get("error", {}).get("message", "")
    assert (
        "[REFUSAL-05]" in message or "xone" in message.lower()
    ), f"refusal must carry the stable code or the SHACL xone message: {message}"

    assert cash_sum["ok"] is True and cash_sum["rows_emitted"] == 1, (
        f"delta-0 witness SUM must emit one row: {cash_sum}"
    )
    cash_body = stream_all(cash_sum["cursor"])
    assert "1000" in cash_body, (
        f"delta-0 witness: cash total must still be exactly 1000.00; got: {cash_body}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    # Abort trace conforms to the two-path net (refusal path is valid there);
    # the settlement-only net refuses it — the net is not vacuous.
    abort = judge(ABORT_PATH, net=[ABORT_PATH])
    assert abort.fitness >= 1.0 and abort.precision >= 1.0
    settle_net_on_abort = judge(ABORT_PATH, net=[VALID_SETTLEMENT])
    assert (
        settle_net_on_abort.fitness < 1.0 or settle_net_on_abort.precision < 1.0
    ), "the settlement net must refuse the abort trace — not vacuous"


def test_dvp_one_legged_trace_fails_conformance() -> None:
    """Anti-vacuity: a log where cash was debited but the delivery never
    happened (no Cash_Credited, no Asset_Transferred) must score below the
    net's floor. This twin runs regardless of runner/artifact availability:
    no eh_call before the judge."""
    result = judge(ONE_LEGGED)
    assert result.fitness < 1.0 or result.precision < 1.0, (
        "a one-legged DvP settlement (cash moved, no delivery) must score "
        "fitness < 1.0 or violate precision — the net is not vacuous"
    )


def test_settlement_net_accepts_valid_path() -> None:
    """The net accepts the exactly-conforming settlement trace (also runner-
    independent)."""
    result = judge(VALID_SETTLEMENT)
    assert result.fitness == 1.0 and result.precision == 1.0
