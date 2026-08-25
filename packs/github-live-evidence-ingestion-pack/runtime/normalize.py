#!/usr/bin/env python3
import hashlib
import json
import re
import sys

SHA40 = re.compile(r"^[0-9a-f]{40}$")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def normalize(envelope):
    repo = envelope.get("repository")
    head = envelope.get("head_sha")
    kind = envelope.get("kind")
    payload = envelope.get("payload")
    if not isinstance(repo, str) or "/" not in repo:
        raise ValueError("REFUSED[INVALID_REPOSITORY]")
    if not isinstance(head, str) or not SHA40.fullmatch(head):
        raise ValueError("REFUSED[INEXACT_HEAD_SHA]")
    if kind not in {"run", "job", "pull_request", "commit_status"}:
        raise ValueError("REFUSED[UNSUPPORTED_EVIDENCE_KIND]")
    if not isinstance(payload, dict):
        raise ValueError("REFUSED[INVALID_PAYLOAD]")
    raw_digest = digest(envelope)
    return {
        "actuation_performed": False,
        "authority": "OBSERVE|VERIFY|CONSTRUCT",
        "evidence_kind": kind,
        "exact_subject": f"{repo}@{head}",
        "payload": payload,
        "raw_digest": raw_digest,
        "receipt_digest": digest({"subject": f"{repo}@{head}", "kind": kind, "raw_digest": raw_digest}),
    }


if __name__ == "__main__":
    try:
        source = json.load(sys.stdin)
        print(canonical(normalize(source)))
    except (ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
