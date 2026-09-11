"""Generated binary materializer for the admitted planner IR.

Serializes the admitted action catalog to a compact, real binary encoding
(length-prefixed UTF-8 fields) and back -- no external serialization
dependency.

Source: ggen-marketplace planning-federation-pack (queries/model.rq).
Do not edit by hand -- regenerate via `ggen sync run`.
"""

import struct

ACTIONS = [
    {"id": "admit-observation", "precondition": "observed", "effect": "admitted", "cost": 1},
    {"id": "verify-goal", "precondition": "admitted", "effect": "verified", "cost": 1},
]


def _pack_str(s: str) -> bytes:
    encoded = s.encode("utf-8")
    return struct.pack(">I", len(encoded)) + encoded


def _unpack_str(buf: bytes, offset: int):
    (length,) = struct.unpack_from(">I", buf, offset)
    offset += 4
    value = buf[offset : offset + length].decode("utf-8")
    return value, offset + length


def to_bytes() -> bytes:
    out = struct.pack(">I", len(ACTIONS))
    for action in ACTIONS:
        out += _pack_str(action["id"])
        out += _pack_str(action["precondition"])
        out += _pack_str(action["effect"])
        out += struct.pack(">i", action["cost"])
    return out


def from_bytes(buf: bytes):
    (count,) = struct.unpack_from(">I", buf, 0)
    offset = 4
    actions = []
    for _ in range(count):
        action_id, offset = _unpack_str(buf, offset)
        precondition, offset = _unpack_str(buf, offset)
        effect, offset = _unpack_str(buf, offset)
        (cost,) = struct.unpack_from(">i", buf, offset)
        offset += 4
        actions.append(
            {"id": action_id, "precondition": precondition, "effect": effect, "cost": cost}
        )
    return actions
