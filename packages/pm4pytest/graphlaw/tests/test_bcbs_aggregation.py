"""Case 2 — BCBS 239 three-jurisdiction exposure aggregation conformance.

Same harness law as test_packet4_eh_fibo.py: packet-4 stdio framing against
`graphlaw-run-eh` (wasmtime 48 host) driving the DuckDB-linked wasm artifact;
frame()/parse_frames() imported from test_packet4_framing.py (single source of
the framing law); typed SKIPs (RUNNER-MISSING / ARTIFACT-NOT-EH-LINKED /
RUNNER-SPAWN-FAILED) name the reason and are never a pass; every wasm-touching
court emits its lifecycle as OCEL events via ProcessTraceCollector, exports a
real OCEL2 SQLite file, and is judged by ConformanceSpec.from_fsm at
min_fitness=1.0 AND min_precision=1.0.

Petri net (valid path):

    Sub_Receipt_1 → Sub_Receipt_2 → Sub_Receipt_3 → Receipts_Verified
      → Consolidation_Fold → Consolidated_Risk_Established

Refusal path (tamper leg): Sub_Receipt_1..3 → Rogue_Exposure_Rejected — the
pipeline HALTS before Consolidation_Fold (no parent SUM is emitted after a
refused jurisdiction exec).

BCBS monotonic fold: three jurisdiction sessions (j1/j2/j3), each executing
CREATE / INSERT drawdown rows / SELECT SUM(amount) over its own named
in-module DB session (local receipt R_i with query_hash per leg); a parent
session then folds the three local sums — materialized as rows in a
`consolidated_exposure` table (the sql-rdf grammar carries no UNION / CREATE
VIEW arm, so the union view is the folded table) — and the parent SUM must
equal EXACTLY the sum of the three local SUM readbacks read from real cursor
streams.

Module-state law (witnessed 2026-10-23): the DuckDB session and cursor
registries live INSIDE the wasm instance (src/duckdb_op.rs `sessions()` /
`cursors()` are in-process statics) — a stream frame is only answerable by
the same module instance that minted the cursor. The whole pipeline
therefore rides ONE persistent graphlaw-run-eh process over binary pipes
(the same shape as tests/bcbs_aggregation_court.rs, one Host, gl_call per
request), never one process per frame.

Chicago: real runner subprocess, real wasm artifact, real frozen-duckdb inside
the module, real cursor streams, real pm4py nets; no mocks, no sleeps.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import struct
import subprocess
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from pm4pytest.conformance import ConformanceSpec
from pm4pytest.ocel import ProcessTraceCollector

# Canonical packet-4 framing, imported from the framing court (single source
# of the frame() law).
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
    return frame(b'{"op":"capabilities"}')


_RUNNER_STATE: dict | None = None


def runner_state() -> dict:
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
                "SKIP(typed: RUNNER-SPAWN-FAILED): capabilities probe timed out"
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
        # 900s: fleet-load tolerance — concurrent lanes have observed load
        # averages >180 on this host; the runner itself exits on EOF.
        timeout=int(os.environ.get("GRAPHLAW_EH_TIMEOUT", "900")),
    )


class PacketSession:
    """One persistent graphlaw-run-eh process over binary pipes.

    Binary-only framing: request/reply bodies are length-prefixed raw bytes,
    so no text-mode transcode (latin1/UTF-8) can desync the reader — this is
    the same law test_packet4_framing.py enforces for one-shot runs, held
    across an interactive session.
    """

    def __init__(self) -> None:
        state = runner_state()
        if not state["ok"]:
            pytest.skip(state["reason"])
        self.proc = subprocess.Popen(
            [GRAPHLAW_RUN_EH, "--wasm", WASM_ARTIFACT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def call(self, request: dict) -> dict:
        assert self.proc.stdin is not None and self.proc.stdout is not None
        self.proc.stdin.write(frame(json.dumps(request).encode()))
        self.proc.stdin.flush()
        prefix = self.proc.stdout.read(4)
        assert len(prefix) == 4, (
            f"runner closed mid-frame (exit={self.proc.poll()}): "
            f"{self._stderr()}"
        )
        (n,) = struct.unpack(">I", prefix)
        body = self.proc.stdout.read(n)
        assert len(body) == n, (
            f"truncated reply body ({len(body)} of {n}); "
            f"exit={self.proc.poll()}: {self._stderr()}"
        )
        envelope = json.loads(body)
        assert envelope["ok"] is True, f"runner-level fault: {envelope}"
        return envelope["result"]

    def close(self) -> None:
        if self.proc.stdin is not None:
            self.proc.stdin.close()
        code = self.proc.wait(timeout=120)
        assert code == 0, f"runner exited {code}: {self._stderr()}"

    def __enter__(self) -> PacketSession:
        return self

    def __exit__(self, *exc: object) -> None:
        try:
            self.close()
        except Exception:
            self.proc.kill()
            raise

    def _stderr(self) -> str:
        if self.proc.stderr is None:
            return ""
        try:
            self.proc.stderr.close()
        except Exception:
            pass
        return "(stderr piped)"


# --------------------------------------------------- sql-rdf document builders
# The admitted surface is the same bare-aggregate select shape as
# tests/fixtures/fibo/tc05_select_sum.ttl (section 7: sql:function
# <http://graphlaw.org/functions#SUM> + sql:argument column node) and the
# expression-form CREATE / scalar INSERT of tc01_create/tc01_insert.


def create_doc(table: str) -> str:
    return (
        "@prefix ex: <http://example.org/bcbs#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "ex:stmt1 a sql:CreateStatement ;\n"
        "    sql:statementIndex 0 ;\n"
        "    sql:tableDefinition [\n"
        f'        sql:tableName "{table}" ;\n'
        "        sql:columns (\n"
        '            [ sql:columnName "id" ; sql:columnType "INTEGER" ]\n'
        '            [ sql:columnName "amount" ; sql:columnType "DECIMAL" ]\n'
        '            [ sql:columnName "jurisdiction" ; sql:columnType "VARCHAR" ]\n'
        "        ) ;\n"
        "    ] .\n"
    )


def insert_doc(table: str, ident: int, amount: str, jurisdiction: str) -> str:
    return (
        "@prefix ex: <http://example.org/bcbs#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n"
        "ex:stmt1 a sql:InsertStatement ;\n"
        "    sql:statementIndex 1 ;\n"
        f'    sql:targetTable "{table}" ;\n'
        '    sql:assignColumn "id" ;\n'
        f'    sql:assignValue "{ident}"^^xsd:integer ;\n'
        '    sql:assignColumn "amount" ;\n'
        f'    sql:assignValue "{amount}"^^xsd:decimal ;\n'
        '    sql:assignColumn "jurisdiction" ;\n'
        f'    sql:assignValue "{jurisdiction}" .\n'
    )


def sum_doc(table: str, index: int = 5) -> str:
    return (
        "@prefix ex: <http://example.org/bcbs#> .\n"
        "@prefix sql: <http://graphlaw.org/sql#> .\n"
        "ex:stmt1 a sql:SelectStatement ;\n"
        f"    sql:statementIndex {index} ;\n"
        '    sql:fromTable [ sql:tableName "%s" ] ;\n'
        "    sql:selectList ( [ sql:expression [\n"
        "        sql:function <http://graphlaw.org/functions#SUM> ;\n"
        '        sql:argument [ sql:columnName "amount" ] ] ] ) .\n'
    ) % table


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


def stream_all(sess: PacketSession, session: str, cursor: str) -> str:
    """Drain one real cursor on the SAME session that minted it (the registry
    is module-instance state — see module docstring)."""
    pages: list[dict] = []
    while True:
        page = sess.call(
            {
                "op": "duckdb",
                "mode": "stream",
                "session": session,
                "cursor": cursor,
                "max_rows": 100,
            }
        )
        assert page["ok"] is True, f"stream failed: {page}"
        pages.append(page.get("nquads") or page.get("body") or "")
        if page.get("more") is not True:
            return "".join(pages)


def drain_decimal(body: str) -> str:
    m = re.search(r"[0-9]+\.[0-9]{2}", body)
    assert m, f"no decimal amount in cursor body: {body}"
    return m.group(0)


# ---------------------------------------------------------------- OCEL net

VALID_PIPELINE = [
    "Sub_Receipt_1",
    "Sub_Receipt_2",
    "Sub_Receipt_3",
    "Receipts_Verified",
    "Consolidation_Fold",
    "Consolidated_Risk_Established",
]
REFUSAL_PIPELINE = [
    "Sub_Receipt_1",
    "Sub_Receipt_2",
    "Sub_Receipt_3",
    "Rogue_Exposure_Rejected",
]


def pipeline_collector(path: list[str]) -> ProcessTraceCollector:
    collector = ProcessTraceCollector()
    collector.register_object("bcbs-aggregation", "case", {"label": "bcbs"})
    base = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)
    for i, activity in enumerate(path):
        collector.emit_event(
            f"ev-{i}",
            activity,
            timestamp=base + timedelta(seconds=i),
            attributes={"case": "bcbs-aggregation"},
            relationships=[{"objectId": "bcbs-aggregation", "qualifier": "pipeline"}],
        )
    return collector


def judge(net_paths: list[list[str]], path: list[str]):
    """Judge `path` against a spec whose FSM is `net_paths` — the refusal
    pipeline is judged on the refusal net (its own lifecycle), the valid
    pipeline on the valid net; a foreign trace is a violation, not a pass."""
    spec = ConformanceSpec.from_fsm(net_paths, min_fitness=1.0, min_precision=1.0)
    events = [
        {"concept:name": ev.type, "time:timestamp": ev.time}
        for ev in pipeline_collector(path).events
    ]
    return spec.evaluate(events)


# ------------------------------------------------------------ shared legs


def run_leg(
    sess: PacketSession, session: str, amounts: tuple[str, str], table: str
) -> tuple[str, dict, dict]:
    """One jurisdiction: open → CREATE → INSERT ×2 → SELECT SUM → stream the
    local SUM off the SAME process → close. Returns (sum, receipt, qhash)."""
    open_resp = sess.call({"op": "duckdb", "mode": "open", "session": session})
    assert open_resp["ok"] is True and open_resp["session"] == session, (
        f"{session} open refused: {open_resp}"
    )
    for label, doc in (
        ("CREATE", create_doc(table)),
        ("INSERT a", insert_doc(table, 1, amounts[0], session)),
        ("INSERT b", insert_doc(table, 2, amounts[1], session)),
        ("SUM", sum_doc(table)),
    ):
        resp = sess.call(exec_req(doc, session))
        assert resp["ok"] is True, f"{session} {label} refused: {resp}"
        assert isinstance(resp.get("receipt"), str) and resp["receipt"], (
            f"{session} {label} must mint a receipt: {resp}"
        )
        assert isinstance(resp.get("query_hash"), str) and resp["query_hash"], (
            f"{session} {label} must carry a query_hash: {resp}"
        )
        if label == "INSERT a":
            receipt_a, hash_a = resp["receipt"], resp["query_hash"]
        if label == "SUM":
            sum_resp = resp
    assert sum_resp["rows_emitted"] == 1, (
        f"{session} local SUM must emit one row: {sum_resp}"
    )
    local_sum = drain_decimal(stream_all(sess, session, sum_resp["cursor"]))
    close_resp = sess.call({"op": "duckdb", "mode": "close", "session": session})
    assert close_resp["ok"] is True, f"{session} close refused: {close_resp}"
    return local_sum, receipt_a, hash_a


# ------------------------------------------------------------ wasm courts


def test_bcbs_three_jurisdiction_monotonic_fold() -> None:
    """j1/j2/j3 local SUMs fold into a parent session whose consolidated SUM
    equals EXACTLY the sum of the three local readbacks (BCBS monotonic fold,
    receipt-backed per leg). One persistent runner process for the whole
    pipeline (module-state law)."""
    amounts = {
        "j1": ("1000.25", "2000.75"),
        "j2": ("500.50", "1500.25"),
        "j3": ("800.00", "1200.00"),
    }
    locals_: dict[str, str] = {}
    receipts: dict[str, str] = {}
    hashes: dict[str, str] = {}
    with PacketSession() as sess:
        for j, amt in amounts.items():
            local_sum, receipt, query_hash = run_leg(sess, j, amt, f"drawdowns_{j}")
            locals_[j] = local_sum
            receipts[j], hashes[j] = receipt, query_hash

        assert locals_["j1"] == "3001.00", f"j1 local SUM: {locals_}"
        assert locals_["j2"] == "2000.75", f"j2 local SUM: {locals_}"
        assert locals_["j3"] == "2000.00", f"j3 local SUM: {locals_}"
        for j in ("j1", "j2", "j3"):  # R_i legs carry receipt + query_hash
            assert receipts[j] and hashes[j], f"{j} leg receipt/hash: {receipts}"

        expected_total = (
            Decimal(locals_["j1"]) + Decimal(locals_["j2"]) + Decimal(locals_["j3"])
        )
        assert expected_total == Decimal("7001.75")

        # Parent fold session: the three local sums materialize as rows of the
        # consolidated_exposure table (the union-view fold), then parent SUM.
        open_resp = sess.call({"op": "duckdb", "mode": "open", "session": "parent"})
        assert open_resp["ok"] is True, f"parent open refused: {open_resp}"
        create = sess.call(exec_req(create_doc("consolidated_exposure"), "parent"))
        assert create["ok"] is True, f"parent CREATE refused: {create}"
        for i, j in enumerate(("j1", "j2", "j3"), start=1):
            fold = sess.call(
                exec_req(insert_doc("consolidated_exposure", i, locals_[j], j), "parent")
            )
            assert fold["ok"] is True, f"parent fold {j} INSERT refused: {fold}"
            assert fold.get("receipt") and fold.get("query_hash"), (
                f"parent fold {j} must mint a fold receipt with query_hash: {fold}"
            )
        sum_resp = sess.call(exec_req(sum_doc("consolidated_exposure"), "parent"))
        assert sum_resp["ok"] is True and sum_resp["rows_emitted"] == 1, (
            f"parent SUM must emit one row: {sum_resp}"
        )
        consolidated = drain_decimal(
            stream_all(sess, "parent", sum_resp["cursor"])
        )
        close_resp = sess.call(
            {"op": "duckdb", "mode": "close", "session": "parent"}
        )
        assert close_resp["ok"] is True, f"parent close refused: {close_resp}"

    assert consolidated == str(expected_total), (
        f"BCBS monotonic fold violated: parent {consolidated} != "
        f"sum of locals {expected_total}"
    )

    result = judge([VALID_PIPELINE], VALID_PIPELINE)
    assert result.fitness >= 1.0 and result.precision >= 1.0, (
        f"valid BCBS pipeline must score full fitness/precision: {result}"
    )


def test_bcbs_tampered_leg_halts_before_fold() -> None:
    """Tamper leg: one jurisdiction exec against an unknown session yields the
    typed refusal; the pipeline emits Rogue_Exposure_Rejected and HALTS — no
    parent fold SUM runs afterward. The refusal-path trace is judged on the
    refusal net's own lifecycle."""
    with PacketSession() as sess:
        open_resp = sess.call({"op": "duckdb", "mode": "open", "session": "j1"})
        assert open_resp["ok"] is True, f"j1 open refused: {open_resp}"
        for doc in (
            create_doc("drawdowns_j1"),
            insert_doc("drawdowns_j1", 1, "1000.25", "j1"),
            insert_doc("drawdowns_j1", 2, "2000.75", "j1"),
        ):
            resp = sess.call(exec_req(doc, "j1"))
            assert resp["ok"] is True, f"seed step refused: {resp}"
        tamper = sess.call(exec_req(create_doc("drawdowns_j2"), "j2-tampered"))

    assert tamper["ok"] is False, f"unknown-session exec must be refused: {tamper}"
    message = tamper.get("error", {}).get("message", "")
    assert "unknown or expired session" in message, (
        f"refusal must name the unknown session: {message}"
    )

    # Pipeline halts: the parent fold is NOT emitted after the refusal.
    result = judge([REFUSAL_PIPELINE], REFUSAL_PIPELINE)
    assert result.fitness >= 1.0 and result.precision >= 1.0, (
        f"refusal-path pipeline (halt before fold) must conform at 1.0: {result}"
    )


def test_bcbs_fold_net_rejects_receipts_verified_skip() -> None:
    """Anti-vacuity: a synthetic trace where Consolidation_Fold occurs with a
    Receipts_Verified skip must score below min_fitness on the VALID net —
    the net is not vacuous."""
    result = judge(
        [VALID_PIPELINE],
        [
            "Sub_Receipt_1",
            "Sub_Receipt_2",
            "Sub_Receipt_3",
            "Consolidation_Fold",
            "Consolidated_Risk_Established",
        ],
    )
    assert result.fitness < 1.0, (
        f"a fold with a Receipts_Verified skip must score < 1.0: {result}"
    )


def test_bcbs_ocel2_sqlite_export_is_real(tmp_path) -> None:
    collector = pipeline_collector(VALID_PIPELINE)
    out = tmp_path / "bcbs_aggregation.ocel.sqlite"
    written = collector.write_sqlite(out)
    assert written.is_file() and written.stat().st_size > 0, (
        "OCEL2 sqlite export must be a real nonempty file"
    )
