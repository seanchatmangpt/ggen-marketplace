from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "warn_ratchet.py"


def report(tmp: Path, name: str, statuses: dict[str, str]) -> Path:
    packs = []
    for pack, status in statuses.items():
        record = {"name": pack, "status": status}
        if status == "WARN":
            record["warn_reason"] = "missing path dependency: ../x"
        packs.append(record)
    path = tmp / name
    path.write_text(json.dumps({"ggen": "ggen 1.0", "packs": packs}), encoding="utf-8")
    return path


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def record(tmp: Path, statuses: dict[str, str]) -> Path:
    base = tmp / "baseline.json"
    proc = run("baseline", str(report(tmp, "base.json", statuses)), "--out", str(base))
    assert proc.returncode == 0, proc.stderr
    return base


def test_baseline_is_deterministic_and_shaped(tmp_path):
    src = report(tmp_path, "r.json", {"b": "WARN", "a": "ALIVE"})
    one, two = tmp_path / "1.json", tmp_path / "2.json"
    assert run("baseline", str(src), "--out", str(one)).returncode == 0
    assert run("baseline", str(src), "--out", str(two)).returncode == 0
    assert one.read_bytes() == two.read_bytes()
    data = json.loads(one.read_text())
    assert data["counts"]["ALIVE"] == 1 and data["counts"]["WARN"] == 1
    assert data["ggen_version"] == "ggen 1.0"
    assert data["packs"]["b"] == {"status": "WARN", "warn_reason": "missing path dependency: ../x"}
    assert data["packs"]["a"] == {"status": "ALIVE"}
    assert list(data["packs"]) == ["a", "b"]


def test_unchanged_passes(tmp_path):
    base = record(tmp_path, {"a": "ALIVE", "b": "WARN"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "ALIVE", "b": "WARN"})), "--baseline", str(base))
    assert proc.returncode == 0, proc.stderr


def test_alive_to_warn_regression_refused(tmp_path):
    base = record(tmp_path, {"a": "ALIVE", "b": "WARN"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "WARN", "b": "WARN"})), "--baseline", str(base))
    assert proc.returncode == 2
    assert "REFUSED:WARN_RATCHET" in proc.stderr and "a: ALIVE -> WARN" in proc.stderr


def test_warn_to_refused_regression_refused(tmp_path):
    base = record(tmp_path, {"a": "ALIVE", "b": "WARN"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "ALIVE", "b": "REFUSED"})), "--baseline", str(base))
    assert proc.returncode == 2
    assert "b: WARN -> REFUSED" in proc.stderr


def test_new_warn_pack_raises_count_refused(tmp_path):
    base = record(tmp_path, {"a": "ALIVE"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "ALIVE", "z": "WARN"})), "--baseline", str(base))
    assert proc.returncode == 2


def test_improvement_allowed_with_rerecord_hint(tmp_path):
    base = record(tmp_path, {"a": "ALIVE", "b": "WARN"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "ALIVE", "b": "ALIVE"})), "--baseline", str(base))
    assert proc.returncode == 0
    assert "re-record the baseline" in proc.stdout


def test_subset_report_not_compared_on_absent_packs(tmp_path):
    base = record(tmp_path, {"a": "ALIVE", "b": "WARN"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "ALIVE"})), "--baseline", str(base), "--subset")
    assert proc.returncode == 0, proc.stderr
    regress = run("check", str(report(tmp_path, "d.json", {"a": "WARN"})), "--baseline", str(base), "--subset")
    assert regress.returncode == 2


def test_partial_report_without_subset_refused(tmp_path):
    base = record(tmp_path, {"a": "ALIVE", "b": "WARN"})
    proc = run("check", str(report(tmp_path, "c.json", {"a": "ALIVE"})), "--baseline", str(base))
    assert proc.returncode == 2 and "REFUSED:WARN_RATCHET" in proc.stderr


def test_empty_report_refused(tmp_path):
    base = record(tmp_path, {"a": "ALIVE"})
    empty = tmp_path / "e.json"
    empty.write_text(json.dumps({"ggen": "x", "packs": []}))
    for extra in ([], ["--subset"]):
        proc = run("check", str(empty), "--baseline", str(base), *extra)
        assert proc.returncode == 2 and "REFUSED:WARN_RATCHET" in proc.stderr


def test_non_object_and_malformed_entries_refused_typed(tmp_path):
    base = record(tmp_path, {"a": "ALIVE"})
    for i, body in enumerate(["[]", '"x"', "null", '{"packs": ["a"]}', '{"packs": [{"name": "a"}]}',
                              '{"packs": [{"name": "a", "status": "BOGUS"}]}']):
        f = tmp_path / f"m{i}.json"
        f.write_text(body)
        proc = run("check", str(f), "--baseline", str(base))
        assert proc.returncode == 2, (body, proc.stderr)
        assert "REFUSED:WARN_RATCHET" in proc.stderr and "Traceback" not in proc.stderr


def test_missing_baseline_and_bad_report_refused(tmp_path):
    good = report(tmp_path, "c.json", {"a": "ALIVE"})
    assert run("check", str(good), "--baseline", str(tmp_path / "nope.json")).returncode == 2
    bad = tmp_path / "bad.json"
    bad.write_text("{}")
    assert run("baseline", str(bad), "--out", str(tmp_path / "o.json")).returncode == 2
