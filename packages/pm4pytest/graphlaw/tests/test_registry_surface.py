"""Registry-vs-dispatch surface court for graphlaw-run, ported from the Rust
registry surface half of graphlaw tests/registry_dispatch.rs.

The capability registry is the source of truth for the public op set; the
runner's raw-ABI pass-through (any frame that is not the smalt eval envelope
goes to the module verbatim) is the executable. These courts fail when they
drift. Chicago: real graphlaw-run subprocess over packet-4 framing, real
module responses, no doubles.

Expected op set (graphlaw registry, 14 entries, order-significant):
capabilities, sniff, parse, convert, canonical, sparql, shacl, shex, n3,
entail, datalog, hooks, law, policy.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess

GRAPHLAW_RUN = os.environ.get(
    "GRAPHLAW_RUN", "/Users/sac/graphlaw/target/debug/graphlaw-run"
)
WASM_ARTIFACT = os.environ.get(
    "GRAPHLAW_WASM", "/Users/sac/graphlaw/priv/graphlaw.wasm"
)

EXPECTED_OPS = [
    "capabilities",
    "sniff",
    "parse",
    "convert",
    "canonical",
    "sparql",
    "shacl",
    "shex",
    "n3",
    "entail",
    "datalog",
    "hooks",
    "law",
    "policy",
]

NT_DATA = (
    "<urn:a:C> <http://www.w3.org/2000/01/rdf-schema#subClassOf> <urn:a:D> .\n"
    "<urn:a:x> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <urn:a:C> .\n"
)


def abi_call(request: dict) -> dict:
    """One raw-ABI pass-through frame over packet-4 framing; returns the
    module's raw response (unwrapped from the {"ok":true,"result":...}
    runner envelope)."""
    body = json.dumps(request).encode()
    wire = struct.pack(">I", len(body)) + body
    proc = subprocess.run(
        [GRAPHLAW_RUN, "--wasm", WASM_ARTIFACT],
        input=wire,
        capture_output=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    stream = proc.stdout
    (n,) = struct.unpack(">I", stream[:4])
    assert len(stream) == 4 + n, "exactly one reply frame expected"
    envelope = json.loads(stream[4:])
    assert envelope["ok"] is True, envelope
    return envelope["result"]


def is_unknown_op(resp: dict) -> bool:
    return (
        resp.get("ok") is False
        and "unknown op" in (resp.get("error", {}).get("message") or "")
    )


def test_positive_control_capabilities_dispatches() -> None:
    resp = abi_call({"op": "capabilities"})
    assert resp["ok"] is True


def test_capabilities_ops_equal_expected_names_in_order_fourteen_entries() -> None:
    resp = abi_call({"op": "capabilities"})
    assert resp["ops"] == EXPECTED_OPS
    assert len(resp["ops"]) == 14


def test_op_absent_from_registry_is_unsupported_unknown_op() -> None:
    absent = "definitely_not_a_graphlaw_op"
    assert absent not in EXPECTED_OPS
    resp = abi_call({"op": absent})
    assert resp["ok"] is False
    assert resp["error"]["kind"] == "Unsupported"
    assert "unknown op" in resp["error"]["message"]
    assert is_unknown_op(resp)


def test_every_registry_op_is_dispatched_not_unknown() -> None:
    for name in EXPECTED_OPS:
        resp = abi_call({"op": name})
        assert not is_unknown_op(resp), f"registry op `{name}`: {resp}"


def test_parse_op_roundtrips_ntriples() -> None:
    resp = abi_call({"op": "parse", "text": NT_DATA, "dialect": "ntriples"})
    assert resp["ok"] is True, resp
    assert resp.get("quads"), "parse returns quads"


def test_unknown_dialect_is_refused_typed() -> None:
    resp = abi_call(
        {"op": "parse", "text": NT_DATA, "dialect": "definitely-not-a-dialect"}
    )
    assert resp["ok"] is False
    assert "unknown dialect" in resp["error"]["message"]


def test_entail_accepts_registry_regimes_and_refuses_unknown() -> None:
    regimes = ["simple", "rdf", "rdfs", "owl-rl", "d"]
    for regime in regimes:
        resp = abi_call(
            {
                "op": "entail",
                "regime": regime,
                "data": {"text": NT_DATA, "dialect": "ntriples"},
            }
        )
        # Registry regimes must route past the regime match; a refusal (if
        # any) comes from the entailment engine, never "unknown regime".
        assert "unknown regime" not in (
            resp.get("error", {}).get("message") or ""
        ), f"regime `{regime}`: {resp}"

    bad = abi_call(
        {
            "op": "entail",
            "regime": "definitely-not-a-regime",
            "data": {"text": NT_DATA, "dialect": "ntriples"},
        }
    )
    assert bad["ok"] is False
    assert "unknown regime" in bad["error"]["message"]
