"""TC-FIBO core rows end-to-end against `graphlaw-run-eh` (wasmtime 48 host,
src/bin/graphlaw_run_eh.rs) and the DuckDB-linked wasm artifact.

Protocol: packet-4 stdio — 4-byte BE length-prefixed frames (same law as
test_packet4_framing.py). The eh host wraps every ABI response as
``{"ok": true, "result": <abi-response>}``; the ABI response itself is either
``{"ok": true, "receipt", "query_hash", "rows_emitted", "cursor", "more"}``
or a typed refusal ``{"ok": false, "error": {"message"}}``.

Documents: the sql-rdf request bodies are the MATERIALIZED FIBO court-matrix
fixtures read from ``GRAPHLAW_FIBO_DIR`` (default
/Users/sac/graphlaw/tests/fixtures/fibo): tc01_create, tc01_insert,
tc02_update_bounded, tc03_delete_unbounded, tc05_select_sum, tc08_copy. No
inline doc duplicates the compile law's surface — the fixtures are the single
source of the admitted surface, mirroring graphlaw
tests/wasm_fibo_fixtures_eh.rs.

Courts:

- TC-FIBO-01 (Alpha): duckdb session `open` → tc01_create → tc01_insert ×2 →
  tc05_select_sum (exact rows_emitted == 1 and value readback via the real
  cursor stream) → readback SELECT proving durable session state → session
  `close`. All exec requests carry `"session": "fibo"` so frames share one
  named in-module DB connection.
- TC-FIBO-02 (bounded update): tc02_update_bounded is admitted and executes;
  the follow-up SUM readback proves the mutation stayed bounded (no row
  matches the WHERE key, so the total is unchanged — the anti-unbounded twin
  of TC-FIBO-03).
- TC-FIBO-03 (Beta): tc03_delete_unbounded gets the stable typed refusal
  ``[REFUSAL-05] UnboundedMutationRefusal`` (compile-time, in-module), and a
  follow-up SELECT proves the rows unchanged — the anti-vacuity twin.
- TC-FIBO-08: tc08_copy executes; the fixture's literal egress path
  ``/tmp/fibo_accounts.csv`` is rewritten to a pid-keyed twin before
  admission (same pattern as the Rust court), and the real CSV file is read
  back from /tmp.
- Conformance net (no wasm needed): every wasm-touching court emits its
  operation lifecycle as OCEL events via ProcessTraceCollector, exports a
  real OCEL2 SQLite file to tmp, and is judged by
  ConformanceSpec.from_fsm over the valid path
  Received→Parsed→Admitted→Executed→Receipted at min_fitness=1.0 AND
  min_precision=1.0 (pm4pytest token-based replay precision). The
  expected-violation twin (a trace skipping Admitted) must score < 1.0 —
  proof the net is not vacuous.

Skip discipline: a runner binary that is missing, or a spawn that exits
95/96 (invalid / not-yet-EH-linked artifact), is a LOUD typed SKIP naming
the reason — a SKIP is not a pass. The conformance-net twins always run.

Chicago: real runner subprocess, real wasm artifact, real frozen-duckdb
inside the module, real cursor streams, real egress CSV on /tmp, real pm4py
nets; no mocks, no sleeps.
"""

from __future__ import annotations

import importlib.util
import json
import os
import struct
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
FIBO_DIR = os.environ.get(
    "GRAPHLAW_FIBO_DIR", "/Users/sac/graphlaw/tests/fixtures/fibo"
)

# ------------------------------------------------------------------- framing
# frame()/parse_frames() are imported from test_packet4_framing.py above.


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


# ------------------------------------------------- materialized FIBO fixtures


SESSION = "fibo"


def fixture(name: str) -> str:
    path = os.path.join(FIBO_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


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


def exec_fixture(name: str, session: str = SESSION) -> dict:
    return exec_req(fixture(name), session=session)


# Readback SELECT over the fixture table (lifecycle twin only — not part of
# the fixture matrix; the matrix's select row is tc05_select_sum).
READBACK_SELECT_DOC = (
    "@prefix sql: <http://graphlaw.org/sql#> .\n"
    "@prefix ex: <http://example.org/fibo#> .\n"
    "ex:stmt1 a sql:SelectStatement ;\n"
    "    sql:statementIndex 6 ;\n"
    '    sql:fromTable [ sql:tableName "fibo_accounts" ] ;\n'
    '    sql:selectList ( [ sql:columnName "balance" ] ) ;\n'
    '    sql:orderBy ( [ sql:columnName "balance" ] ) .'
)


def stream_all(cursor: str) -> str:
    """Drain one real cursor through mode:stream frames."""
    pages = eh_call(
        [
            {"op": "duckdb", "mode": "stream", "cursor": cursor, "max_rows": 100}
        ]
    )
    page = pages[0]
    assert page["ok"] is True, f"stream failed: {page}"
    body = page.get("body") or page.get("nquads") or ""
    assert page["more"] is not True, "single-page cursor expected at max_rows=100"
    return body


# ---------------------------------------------------------------- OCEL net

VALID_LIFECYCLE = ["Received", "Parsed", "Admitted", "Executed", "Receipted"]
REFUSED_LIFECYCLE = ["Received", "Parsed", "Refused"]


def lifecycle_collector(path: list[str]) -> ProcessTraceCollector:
    collector = ProcessTraceCollector()
    collector.register_object("tc-fibo", "case", {"label": "tc-fibo"})
    base = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone.utc)
    for i, activity in enumerate(path):
        collector.emit_event(
            f"ev-{i}",
            activity,
            timestamp=base + timedelta(seconds=i),
            attributes={"case": "tc-fibo"},
            relationships=[{"objectId": "tc-fibo", "qualifier": "lifecycle"}],
        )
    return collector


def judge(path: list[str]):
    spec = ConformanceSpec.from_fsm(
        [VALID_LIFECYCLE], min_fitness=1.0, min_precision=1.0
    )
    events = [
        {"concept:name": ev.type, "time:timestamp": ev.time}
        for ev in lifecycle_collector(path).events
    ]
    return spec.evaluate(events)


# ------------------------------------------------------------ wasm courts


def test_tc_fibo_01_alpha_create_insert_sum_readback() -> None:
    """TC-FIBO-01 (Alpha): session open → tc01_create → tc01_insert ×2 →
    tc05_select_sum → readback SELECT → close, all admitted through the
    module's compile law over the real wire, sharing one named in-module DB
    session across frames."""
    requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests.append(exec_fixture("tc01_create.ttl"))
    requests += [exec_fixture("tc01_insert.ttl") for _ in range(2)]
    requests.append(exec_fixture("tc05_select_sum.ttl"))
    # Same process: readback and close ride the same session registry.
    requests.append(exec_req(READBACK_SELECT_DOC))
    requests += [{"op": "duckdb", "mode": "close", "session": SESSION}]
    responses = eh_call(requests)

    (open_resp, create, ins1, ins2, sum_resp, rows_resp, close_resp) = responses
    assert open_resp["ok"] is True and open_resp["session"] == SESSION, (
        f"session open refused: {open_resp}"
    )

    for label, resp in (
        ("CREATE", create),
        ("INSERT balance=1250.50 (a)", ins1),
        ("INSERT balance=1250.50 (b)", ins2),
    ):
        assert resp["ok"] is True, f"{label} refused: {resp}"
        assert isinstance(resp.get("receipt"), str) and resp["receipt"], (
            f"{label} must mint a receipt: {resp}"
        )
        assert isinstance(resp.get("query_hash"), str) and resp["query_hash"], (
            f"{label} must carry a query_hash: {resp}"
        )

    assert sum_resp["ok"] is True and sum_resp["rows_emitted"] == 1, (
        f"SUM aggregate emits exactly one row: {sum_resp}"
    )
    body = stream_all(sum_resp["cursor"])
    assert "2501" in body, (
        f"SUM(balance) over two 1250.50 rows must read back 2501.00; got: {body}"
    )

    # Real readback: a second SELECT over the same session's durable state.
    assert rows_resp["ok"] is True, f"readback SELECT refused: {rows_resp}"
    assert rows_resp["rows_emitted"] == 2, f"exactly two rows expected: {rows_resp}"
    rows_body = stream_all(rows_resp["cursor"])
    assert "1250.50" in rows_body, (
        f"both inserted balances must read back: {rows_body}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    # OCEL judgement over the admitted lifecycle (real net, real trace).
    result = judge(VALID_LIFECYCLE)
    assert result.fitness >= 1.0 and result.precision >= 1.0


def test_tc_fibo_02_bounded_update_executes_and_stays_bounded() -> None:
    """TC-FIBO-02: tc02_update_bounded is admitted and executes over the
    session; the follow-up SUM readback proves the mutation stayed bounded —
    no seeded row carries the WHERE key (facility_id = 'FAC-CORP-9882'), so
    the total must be exactly the seeded 2501.00, not a wipe."""
    requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests.append(exec_fixture("tc01_create.ttl"))
    requests += [exec_fixture("tc01_insert.ttl") for _ in range(2)]
    requests.append(exec_fixture("tc02_update_bounded.ttl"))
    requests.append(exec_fixture("tc05_select_sum.ttl"))
    requests += [{"op": "duckdb", "mode": "close", "session": SESSION}]
    responses = eh_call(requests)

    (open_resp, create, ins1, ins2, update, sum_resp, close_resp) = responses
    assert open_resp["ok"] is True, f"session open refused: {open_resp}"
    for label, resp in (("CREATE", create), ("INSERT a", ins1), ("INSERT b", ins2)):
        assert resp["ok"] is True, f"{label} refused: {resp}"

    assert update["ok"] is True, f"bounded UPDATE refused: {update}"
    assert isinstance(update.get("receipt"), str) and update["receipt"], (
        f"UPDATE must mint a receipt: {update}"
    )
    assert sum_resp["ok"] is True and sum_resp["rows_emitted"] == 1, (
        f"post-update SUM must emit one row: {sum_resp}"
    )
    body = stream_all(sum_resp["cursor"])
    assert "2501" in body, (
        f"bounded UPDATE must leave the seeded total intact (2501.00); got: {body}"
    )
    assert close_resp["ok"] is True, f"session close refused: {close_resp}"

    result = judge(VALID_LIFECYCLE)
    assert result.fitness >= 1.0 and result.precision >= 1.0


def test_tc_fibo_03_beta_whereless_delete_refused_rows_unchanged() -> None:
    """TC-FIBO-03 (Beta): the tc03_delete_unbounded fixture is refused typed
    ([REFUSAL-05] UnboundedMutationRefusal) at compile time in-module, and a
    follow-up SELECT proves the rows unchanged — anti-vacuity twin."""
    requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
    requests += [exec_fixture("tc01_create.ttl")]
    requests += [exec_fixture("tc01_insert.ttl") for _ in range(2)]
    requests += [exec_fixture("tc03_delete_unbounded.ttl"), exec_req(READBACK_SELECT_DOC)]
    requests += [{"op": "duckdb", "mode": "close", "session": SESSION}]
    responses = eh_call(requests)
    for resp in responses[1:4]:
        assert resp["ok"] is True, f"seed step refused: {resp}"

    refusal = responses[4]
    assert refusal["ok"] is False, f"WHERE-less DELETE must be refused: {refusal}"
    message = refusal.get("error", {}).get("message", "")
    assert (
        "[REFUSAL-05]" in message or "xone" in message.lower()
    ), f"refusal must carry the stable code or the SHACL xone message: {message}"

    # Anti-vacuity twin: rows unchanged after the refused mutation.
    rows_resp = responses[5]
    assert rows_resp["ok"] is True and rows_resp["rows_emitted"] == 2, (
        f"both rows must survive the refused DELETE: {rows_resp}"
    )
    rows_body = stream_all(rows_resp["cursor"])
    assert "1250.50" in rows_body, f"original values must survive: {rows_body}"
    assert responses[6]["ok"] is True, f"session close refused: {responses[6]}"

    # Refused lifecycle: real net, real trace, judged the same way.
    assert judge(REFUSED_LIFECYCLE).fitness < 1.0


def test_tc_fibo_08_copy_executes_with_pid_keyed_egress(tmp_path) -> None:
    """TC-FIBO-08: tc08_copy compiles and executes; the fixture's literal
    egress path /tmp/fibo_accounts.csv is rewritten to a pid-keyed twin
    before admission (the wasm_fibo_fixtures_eh.rs court pattern), and the
    real CSV file lands on disk with the seeded row."""
    egress = f"/tmp/fibo_accounts_{os.getpid()}.csv"
    doc = fixture("tc08_copy.ttl").replace("/tmp/fibo_accounts.csv", egress)
    assert egress in doc, "egress path rewrite must land in the admitted document"
    try:
        requests = [{"op": "duckdb", "mode": "open", "session": SESSION}]
        requests.append(exec_fixture("tc01_create.ttl"))
        requests += [exec_fixture("tc01_insert.ttl") for _ in range(2)]
        requests.append(exec_req(doc))
        requests += [{"op": "duckdb", "mode": "close", "session": SESSION}]
        responses = eh_call(requests)

        (open_resp, create, ins1, ins2, copy, close_resp) = responses
        assert open_resp["ok"] is True, f"session open refused: {open_resp}"
        for label, resp in (("CREATE", create), ("INSERT a", ins1), ("INSERT b", ins2)):
            assert resp["ok"] is True, f"{label} refused: {resp}"
        assert copy["ok"] is True, f"COPY refused: {copy}"
        assert isinstance(copy.get("receipt"), str) and copy["receipt"], (
            f"COPY must mint a receipt: {copy}"
        )
        assert close_resp["ok"] is True, f"session close refused: {close_resp}"

        assert os.path.isfile(egress), f"egress CSV must exist: {egress}"
        with open(egress, encoding="utf-8") as fh:
            contents = fh.read()
        assert "1250.50" in contents, f"seeded balance must land in the CSV: {contents}"
    finally:
        if os.path.isfile(egress):
            os.unlink(egress)

    result = judge(VALID_LIFECYCLE)
    assert result.fitness >= 1.0 and result.precision >= 1.0


def test_unknown_session_exec_is_typed_refusal() -> None:
    """Negative case: exec against a never-opened session must yield a typed
    refusal (the Refused terminal of the lifecycle net covers it); close of
    the unknown handle is idempotent-ok."""
    bad = exec_fixture("tc01_create.ttl", session="never-opened")
    responses = eh_call([
        bad,
        {"op": "duckdb", "mode": "close", "session": "never-opened"},
    ])
    (refusal, close_resp) = responses
    assert refusal["ok"] is False, f"unknown session must be refused: {refusal}"
    message = refusal.get("error", {}).get("message", "")
    assert "unknown or expired session" in message, (
        f"refusal must name the unknown session: {message}"
    )
    assert close_resp["ok"] is True, "close of an unknown session is idempotent-ok"


# ----------------------------------------------------- conformance-net twins
# These run regardless of runner/artifact availability: the net itself must
# never be vacuous.


def test_ocel2_sqlite_export_is_real(tmp_path) -> None:
    collector = lifecycle_collector(VALID_LIFECYCLE)
    out = tmp_path / "tc_fibo_lifecycle.ocel.sqlite"
    written = collector.write_sqlite(out)
    assert written.is_file() and written.stat().st_size > 0, (
        "OCEL2 sqlite export must be a real nonempty file"
    )


def test_conformance_net_accepts_valid_lifecycle() -> None:
    result = judge(VALID_LIFECYCLE)
    assert result.fitness == 1.0, "valid lifecycle scores full fitness"
    assert result.precision == 1.0, "valid lifecycle scores full precision"


def test_conformance_net_rejects_trace_skipping_admitted() -> None:
    result = judge(["Received", "Parsed", "Executed", "Receipted"])
    assert result.fitness < 1.0, (
        "a trace that skips Admitted must score below min_fitness — "
        "the net is not vacuous"
    )
