#!/usr/bin/env python3
"""Reusable exact-subject replication consumer court.

This is producer-owned verification substrate. It never actuates a consumer;
a consumer repository invokes it inside its own authority domain.
"""
from __future__ import annotations
import argparse, hashlib, json, pathlib, subprocess, sys

def git(root: pathlib.Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

def refuse(code: str, detail: str) -> int:
    print(f"REFUSED[{code}] {detail}", file=sys.stderr)
    return 2

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--consumer-root", required=True)
    p.add_argument("--contract", required=True)
    p.add_argument("--repo", required=True)
    p.add_argument("--candidate-sha", required=True)
    p.add_argument("--producer-fixture", required=True)
    p.add_argument("--receipt", default="")
    a = p.parse_args()
    root = pathlib.Path(a.consumer_root).resolve()
    contract_path = pathlib.Path(a.contract).resolve()
    fixture_path = pathlib.Path(a.producer_fixture).resolve()
    c = json.loads(contract_path.read_text())
    if c.get("authority") != "VERIFY_ONLY" or c.get("consequential_do") is not False:
        return refuse("AUTHORITY", "consumer contract must be VERIFY_ONLY and non-actuating")
    if a.repo != c.get("consumer_repo"):
        return refuse("REPO_IDENTITY", f"expected {c.get('consumer_repo')} got {a.repo}")
    actual = git(root, "rev-parse", "HEAD")
    if actual != a.candidate_sha:
        return refuse("EXACT_SUBJECT", f"HEAD={actual} candidate={a.candidate_sha}")
    base = c.get("admitted_target_base", "")
    if subprocess.run(["git", "merge-base", "--is-ancestor", base, actual], cwd=root).returncode != 0:
        return refuse("LINEAGE", "candidate does not descend from admitted target base")
    fixture = fixture_path.read_bytes()
    fixture_text = fixture.decode()
    target_token = c.get("producer_target_token", "")
    if base not in fixture_text or target_token not in fixture_text:
        return refuse("PRODUCER_CORRESPONDENCE", "producer fixture does not bind this exact target")
    if "esf:eligible true" not in fixture_text:
        return refuse("PRODUCER_ELIGIBILITY", "producer fixture does not declare an eligible target")
    receipt = {
        "schema_version": 1,
        "standing": "ALIVE",
        "consumer_repo": c["consumer_repo"],
        "candidate_sha": actual,
        "admitted_target_base": base,
        "producer_repo": c["producer_repo"],
        "producer_sha": c["producer_sha"],
        "producer_fixture": c["producer_fixture"],
        "producer_fixture_sha256": hashlib.sha256(fixture).hexdigest(),
        "authority": "VERIFY_ONLY",
        "consequential_do": False,
        "court_version": "r48-v1",
    }
    encoded = json.dumps(receipt, sort_keys=True, indent=2) + "\n"
    if a.receipt:
        pathlib.Path(a.receipt).write_text(encoded)
    print(encoded, end="")
    return 0

if __name__ == "__main__": raise SystemExit(main())
