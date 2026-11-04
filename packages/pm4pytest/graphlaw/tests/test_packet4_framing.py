"""Packet-4 stdio framing law for graphlaw-run, ported from the Rust wire
courts (graphlaw tests/temprun_framing.rs wire half + src/bin/graphlaw_run.rs
module docs).

Protocol (src/bin/graphlaw_run.rs, "Protocol" section): each frame is a
4-byte big-endian length prefix followed by that many body bytes. Requests
are read from stdin, replies written to stdout under the same framing.
Exit taxonomy (module docs, "Modes and exit codes"):

  0  clean EOF at a frame boundary
  2  usage / artifact I/O fault
  84 artifact digest mismatch refusal
  86 guest trap (crash mode / memory wall)
  90 EOF mid-frame
  91 stdin read error
  93 malformed eval envelope (undecodable base64 payload)
  94 module returned non-JSON (guest fault; not reachable from the wire)

Framing is binary: the length prefix is raw bytes, so the pipes are opened
in binary mode and bodies are latin1-decodable text at most. No text-mode
stdio anywhere (a text-mode pipe silently transcodes and desyncs the
length framing).

Chicago: real graphlaw-run subprocess, real pinned wasm artifact, real
exit codes and reply frames; no mocks, no sleeps.
"""

from __future__ import annotations

import os
import struct
import subprocess

GRAPHLAW_RUN = os.environ.get(
    "GRAPHLAW_RUN", "/Users/sac/graphlaw/target/debug/graphlaw-run"
)
WASM_ARTIFACT = os.environ.get(
    "GRAPHLAW_WASM", "/Users/sac/graphlaw/priv/graphlaw.wasm"
)


def _args(*extra: str) -> list[str]:
    return [GRAPHLAW_RUN, "--wasm", WASM_ARTIFACT, *extra]


def frame(body: bytes) -> bytes:
    """One packet-4 frame: 4-byte BE length prefix + body."""
    return struct.pack(">I", len(body)) + body


def run(
    wire: bytes, *extra: str, stdin_fd: int | None = None
) -> subprocess.CompletedProcess:
    """Drive one real graphlaw-run process to completion with `wire` bytes."""
    return subprocess.run(
        _args(*extra),
        input=wire if stdin_fd is None else None,
        stdin=stdin_fd,
        capture_output=True,
        timeout=120,
    )


def parse_frames(stream: bytes) -> list[bytes]:
    """Parse a reply stream back into frame bodies, asserting the framing law
    holds for every prefix boundary (the stream must decompose exactly)."""
    bodies: list[bytes] = []
    off = 0
    while off < len(stream):
        assert off + 4 <= len(stream), f"truncated length prefix at offset {off}"
        (n,) = struct.unpack(">I", stream[off : off + 4])
        off += 4
        assert off + n <= len(stream), f"truncated frame body at offset {off}"
        bodies.append(stream[off : off + n])
        off += n
    return bodies


def capabilities_request() -> bytes:
    return frame(b'{"op":"capabilities"}')


def capabilities_reply(proc: subprocess.CompletedProcess) -> dict:
    bodies = parse_frames(proc.stdout)
    assert len(bodies) == 1, f"expected exactly one reply frame, got {len(bodies)}"
    import json

    reply = json.loads(bodies[0])
    assert reply["ok"] is True
    assert "result" in reply
    return reply


def test_binary_present_and_artifact_exists() -> None:
    assert os.path.isfile(GRAPHLAW_RUN), GRAPHLAW_RUN
    assert os.path.isfile(WASM_ARTIFACT), WASM_ARTIFACT


def test_clean_eof_at_frame_boundary_exits_zero_with_no_reply() -> None:
    proc = run(b"")
    assert proc.returncode == 0
    assert proc.stdout == b""
    assert proc.stderr == b""


def test_capabilities_request_gets_one_framed_reply() -> None:
    reply = capabilities_reply(run(capabilities_request()))
    ops = reply["result"]["ops"]
    assert isinstance(ops, list) and len(ops) == 14


def test_two_pipelined_frames_get_two_framed_replies_in_order() -> None:
    wire = capabilities_request() + capabilities_request()
    proc = run(wire)
    assert proc.returncode == 0
    bodies = parse_frames(proc.stdout)
    assert len(bodies) == 2, "one reply frame per request frame"
    import json

    for body in bodies:
        reply = json.loads(body)
        assert reply["ok"] is True
        assert len(reply["result"]["ops"]) == 14


def test_eval_envelope_reply_echoes_predicate_frames_count() -> None:
    import base64
    import json

    payload = base64.b64encode(json.dumps({"op": "capabilities"}).encode()).decode()
    body = json.dumps(
        {"op": "eval", "payload_b64": payload, "predicate_frames": ["a", "b", "c"]}
    ).encode()
    proc = run(frame(body))
    assert proc.returncode == 0
    bodies = parse_frames(proc.stdout)
    assert len(bodies) == 1
    reply = json.loads(bodies[0])
    assert reply["ok"] is True
    assert reply["predicate_frames_count"] == 3
    assert reply["result"]["ok"] is True


def test_exit_90_eof_mid_frame() -> None:
    # Prefix declares 100 body bytes; only 5 arrive before EOF.
    proc = run(struct.pack(">I", 100) + b"short")
    assert proc.returncode == 90, proc.stderr
    assert proc.stdout == b""
    assert b"EOF mid-frame" in proc.stderr


def test_exit_91_stdin_read_error() -> None:
    # A directory fd is a real read error (EISDIR), not EOF: exit 91.
    fd = os.open("/tmp", os.O_RDONLY)
    try:
        proc = run(b"", stdin_fd=fd)
    finally:
        os.close(fd)
    assert proc.returncode == 91, proc.stderr
    assert b"stdin read error" in proc.stderr


def test_exit_93_malformed_envelope_bad_base64() -> None:
    body = b'{"op":"eval","payload_b64":"!!!not-base64!!!"}'
    proc = run(frame(body))
    assert proc.returncode == 93, proc.stderr
    assert proc.stdout == b""
    assert b"malformed envelope" in proc.stderr


def test_exit_2_usage_unknown_argument() -> None:
    proc = subprocess.run(
        [GRAPHLAW_RUN, "--definitely-not-a-flag"],
        capture_output=True,
        timeout=120,
    )
    assert proc.returncode == 2, proc.stderr
    assert b"unknown argument" in proc.stderr


def test_exit_84_artifact_digest_mismatch_refusal() -> None:
    proc = run(
        b"",
        "--expect-blake3",
        "00" * 32,
    )
    assert proc.returncode == 84, proc.stderr
    assert b"ARTIFACT DIGEST MISMATCH" in proc.stderr


def test_exit_86_crash_mode_traps_after_one_frame() -> None:
    proc = run(capabilities_request(), "--crash")
    assert proc.returncode == 86, proc.stderr
    assert proc.stdout == b"", "crash mode must not emit a reply frame"


def test_reply_frame_length_prefix_matches_body_exactly() -> None:
    proc = run(capabilities_request())
    assert proc.returncode == 0
    (n,) = struct.unpack(">I", proc.stdout[:4])
    assert len(proc.stdout) == 4 + n, "reply is exactly prefix + body, no padding"
