#!/usr/bin/env python3
"""Deterministic RFC-CS2-001 projection and replay-receipt constructor.

This is a pure CONSTRUCT utility: it reads an exact subject manifest and emits
canonical JSON projections. It never grants or exercises DO authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

SUBJECT = "RFC-CS2-001"
AUTHORITY_CEILING = "OBSERVE|SELECT|CONSTRUCT"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


@dataclass(frozen=True)
class ExactSubject:
    subject: str
    source_repo: str
    source_sha: str
    source_digest: str
    root_digest: str

    @classmethod
    def parse(cls, raw: dict[str, Any]) -> "ExactSubject":
        required = ("subject", "source_repo", "source_sha", "source_digest", "root_digest")
        missing = [key for key in required if not raw.get(key)]
        if missing:
            raise ValueError("MISSING_EXACT_SUBJECT:" + ",".join(missing))
        if raw["subject"] != SUBJECT:
            raise ValueError(f"DIVERGENT_SUBJECT:{raw['subject']}!={SUBJECT}")
        for key in ("source_digest", "root_digest"):
            if not str(raw[key]).startswith("sha256:"):
                raise ValueError(f"NON_SHA256_DIGEST:{key}")
        return cls(**{key: str(raw[key]) for key in required})


def projection(subject: ExactSubject, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
    body = {
        "contract": SUBJECT,
        "projection_kind": kind,
        "subject": asdict(subject),
        "payload": payload,
        "authority_ceiling": AUTHORITY_CEILING,
        "grants_do_authority": False,
    }
    return {**body, "projection_digest": sha256(canonical(body))}


def witness(proj: dict[str, Any], entry: str) -> dict[str, Any]:
    body = {
        "contract": SUBJECT,
        "projection_digest": proj["projection_digest"],
        "executable_entry": entry,
        "authority_ceiling": AUTHORITY_CEILING,
        "grants_do_authority": False,
    }
    return {**body, "witness_digest": sha256(canonical(body))}


def replay_receipt(subject: ExactSubject, projections: Iterable[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted((p["projection_digest"] for p in projections))
    body = {
        "contract": SUBJECT,
        "exact_subject": asdict(subject),
        "projection_digests": ordered,
        "authority_ceiling": AUTHORITY_CEILING,
        "grants_do_authority": False,
    }
    return {**body, "receipt_digest": sha256(canonical(body))}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", type=Path)
    parser.add_argument("--kind", action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    exact = ExactSubject.parse(json.loads(args.subject.read_text()))
    kinds = args.kind or ["conformance", "consumer"]
    projections = [
        projection(exact, kind, {"subject_id": exact.subject, "root_digest": exact.root_digest})
        for kind in sorted(set(kinds))
    ]
    receipt = replay_receipt(exact, projections)
    result = {"subject": asdict(exact), "projections": projections, "receipt": receipt}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
