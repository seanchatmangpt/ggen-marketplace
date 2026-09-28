#!/usr/bin/env python3
"""Echo/sum/sleep stdio JSON-lines bridge -- bpm:PortBridge qualification fixture.

Ships with beam4pm-process-model-pack so a rendered port-bridge client can be
exercised END TO END (request/reply/timeout/kill -9 recovery) without any lab
checkout. Speaks the witnessed BEAM port protocol, envelope-for-envelope:

- in:  {"op": "ping"}                 -> {"ok": True, "pong": True}
- in:  {"op": "sum", "a": x, "b": y}  -> {"ok": True, "sum": x + y}
- in:  {"op": "echo_map", "payload": {...}, "items": [...]}
                                      -> {"ok": True, "echoed": {...}, "items": [...]}
- in:  {"op": "sleep", "ms": n}       -> {"ok": True, "slept": n}   (after n ms)
- in:  any other op                   -> {"ok": False, "error": "unknown_op: <op>"}

The port protocol requires every failure to become an {"ok": false} envelope
LINE, never a dead port -- the BEAM caller reads exactly one reply per request
line and cannot recover a crashed interpreter. Same law as autofde-lab's
beam_port_bridge.py, stdlib only, no third-party imports.
"""

import json
import sys
import time


def handle_request(req):
    op = req.get("op")
    if op == "ping":
        return {"ok": True, "pong": True}

    if op == "sum":
        return {"ok": True, "sum": req.get("a", 0) + req.get("b", 0)}

    if op == "echo_map":
        # exercises the stringify/stringify_list arg encodings: the client
        # deep-rewrites atom-keyed maps to string keys before sending.
        return {
            "ok": True,
            "echoed": req.get("payload", {}),
            "items": req.get("items", []),
        }

    if op == "sleep":
        ms = req.get("ms", 0)
        time.sleep(float(ms) / 1000.0)
        return {"ok": True, "slept": ms}

    return {"ok": False, "error": f"unknown_op: {op}"}


def main() -> None:
    for line in sys.stdin:
        text = line.strip()
        if not text:
            continue
        try:
            resp = handle_request(json.loads(text))
        except Exception as e:  # noqa: BLE001 -- the port protocol requires
            # one reply line per request line, even for malformed requests.
            resp = {"ok": False, "error": str(e), "exception_type": type(e).__name__}
        sys.stdout.write(json.dumps(resp) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
