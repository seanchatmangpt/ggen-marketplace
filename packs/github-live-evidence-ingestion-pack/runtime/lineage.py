#!/usr/bin/env python3
import json
import sys


def lineage(observations):
    by_subject = {}
    for item in observations:
        by_subject.setdefault(item["exact_subject"], []).append(item)
    edges = []
    for subject, items in sorted(by_subject.items()):
        ordered = sorted(items, key=lambda x: (x["evidence_kind"], x["receipt_digest"]))
        for left, right in zip(ordered, ordered[1:]):
            edges.append({"subject": subject, "from": left["receipt_digest"], "to": right["receipt_digest"], "relation": "same-exact-subject"})
    return edges


if __name__ == "__main__":
    observations = [json.loads(line) for line in sys.stdin if line.strip()]
    for edge in lineage(observations):
        print(json.dumps(edge, sort_keys=True, separators=(",", ":")))
