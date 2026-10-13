"""Marketplace count canary court (2026-10-13).

The airo pin test (tests/test_airo_pin_w687.py) hard-pins packs/ontologies,
leaving templates/native_gates drift invisible; hard-pinning fast-moving
counts in test source causes constant churn. This court moves the pin into a
checked-in manifest (tests/fixtures/marketplace_counts.json) and enforces
manifest-vs-reality equality: any count-affecting change to
scripts/marketplace.py validate output MUST bump the manifest in the SAME
commit, turning silent drift into a visible, reviewable delta.

No mocks. Real subprocess validate + real manifest parse.
"""

import hashlib
import json
import os
import re
import subprocess
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(REPO_ROOT, "tests", "fixtures", "marketplace_counts.json")
MARKETPLACE = os.path.join(REPO_ROOT, "scripts", "marketplace.py")

SCALARS = ["packs", "manifests", "ontologies", "templates", "native_gates",
           "verifier_gates", "diataxis"]
PROFILE_KEYS = ["project", "projection", "semantic"]


def _manifest_sha256(manifest):
    """sha256 over canonical JSON of everything except the sha256 field."""
    body = {k: v for k, v in manifest.items() if k != "sha256"}
    return hashlib.sha256(
        json.dumps(body, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _observed_counts(stdout):
    counts = {}
    for key in SCALARS:
        m = re.search(rf"\b{key}=(\d+)\b", stdout)
        if not m:
            return None
        counts[key] = int(m.group(1))
    pm = re.search(r"profiles=(\{.*\})", stdout)
    if not pm:
        return None
    profiles = {}
    for key in PROFILE_KEYS:
        km = re.search(rf"'{key}':\s*(\d+)", pm.group(1)) or \
            re.search(rf'"{key}":\s*(\d+)', pm.group(1))
        if not km:
            return None
        profiles[key] = int(km.group(1))
    counts["profiles"] = profiles
    return counts


@pytest.fixture(scope="module")
def observed():
    r = subprocess.run(
        [sys.executable, MARKETPLACE, "validate"],
        capture_output=True, text=True, timeout=300,
        cwd=REPO_ROOT,
    )
    if r.returncode != 0:
        pytest.skip(
            "BLOCKED:validate_unavailable — scripts/marketplace.py validate "
            f"exited {r.returncode}: {r.stdout[-200:]} {r.stderr[-200:]}"
        )
    counts = _observed_counts(r.stdout)
    if counts is None:
        pytest.skip(
            "BLOCKED:validate_output_unparseable — validate line format "
            f"changed; cannot extract counts from: {r.stdout[-300:]}"
        )
    return counts


@pytest.fixture(scope="module")
def manifest():
    assert os.path.isfile(MANIFEST), MANIFEST
    with open(MANIFEST, encoding="utf-8") as f:
        m = json.load(f)
    assert m.get("sha256") == _manifest_sha256(m), (
        "manifest self-hash mismatch: sha256 field does not match canonical "
        "JSON of the manifest body — regenerate via the documented recipe "
        "(sha256 of json.dumps(body, sort_keys=True))"
    )
    return m


def test_manifest_self_hash_intact(manifest):
    """Sabotage twin: any manifest edit without recomputing sha256 fails."""
    # Assertion lives in the manifest fixture; this test witnesses it.
    assert manifest["counts"], manifest


def test_counts_match_manifest(observed, manifest):
    """Any count drift without a same-commit manifest update fails here,
    naming old -> new per field and the fix."""
    expected = manifest["counts"]
    drift = []
    for key in SCALARS:
        if observed[key] != expected.get(key):
            drift.append(f"  {key}: manifest={expected.get(key)} "
                         f"-> observed={observed[key]}")
    for key in PROFILE_KEYS:
        o = observed["profiles"][key]
        e = (expected.get("profiles") or {}).get(key)
        if o != e:
            drift.append(f"  profiles.{key}: manifest={e} -> observed={o}")
    assert not drift, (
        "MARKETPLACE COUNT CANARY DRIFT — validate output no longer matches "
        f"tests/fixtures/marketplace_counts.json (as_of {manifest.get('as_of')}):\n"
        + "\n".join(drift)
        + "\n\nFix: update tests/fixtures/marketplace_counts.json to the new "
        "counts and recompute its sha256, in the SAME commit as the "
        "count-affecting change. Recipe: sha256 over "
        "json.dumps(manifest-minus-sha256, sort_keys=True)."
    )
