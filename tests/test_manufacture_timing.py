"""Chicago-style tests for scripts/manufacture_timing.py: real report files, no doubles."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import manufacture_timing as mt  # noqa: E402


def report(packs: list[dict], seconds: dict[str, float], ggen: str = "ggen 1", workers: int = 8) -> dict:
    return {
        "ggen": ggen,
        "pack_count": len(packs),
        "packs": packs,
        "schema": mt.QUALIFICATION_SCHEMA,
        "timings": {"pack_seconds": seconds, "schema": mt.TIMINGS_SCHEMA, "workers": workers},
    }


def alive(name: str, sha: str = "a") -> dict:
    return {"name": name, "profile": "semantic", "source_sha256": sha, "status": "ALIVE", "version": "1.0.0"}


def write(tmp_path: Path, name: str, payload: dict) -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_summarize_counts_statuses_and_percentiles():
    r = report(
        [alive("a"), alive("b"), alive("c"), {"name": "d", "status": "REFUSED", "profile": "semantic", "version": "1"}],
        {"a": 1.0, "b": 2.0, "c": 3.0, "d": 99.0},
    )
    s = mt.summarize(r)
    assert s["status_counts"] == {"ALIVE": 3, "REFUSED": 1}
    # REFUSED timings never enter the ALIVE distribution.
    assert s["alive_seconds"] == {"count": 3, "max": 3.0, "p50": 2.0, "p95": 3.0, "total_serial": 6.0}


def test_compare_pairs_only_identical_alive_sources():
    base = report(
        [alive("same"), alive("moved", "x"), alive("broke"), alive("gone")],
        {"same": 4.0, "moved": 1.0, "broke": 1.0, "gone": 1.0},
    )
    cand = report(
        [
            alive("same"),
            alive("moved", "y"),
            {"name": "broke", "status": "REFUSED", "profile": "semantic", "version": "1"},
            alive("new"),
        ],
        {"same": 2.0, "moved": 1.0, "broke": 1.0, "new": 1.0},
        ggen="ggen 2",
    )
    result = mt.compare(base, cand)
    assert [p["name"] for p in result["pairs"]] == ["same"]
    assert result["comparable"]["total_ratio"] == 0.5
    reasons = {e["name"]: e["reason"] for e in result["excluded"]}
    assert reasons == {
        "moved": "source_changed",
        "broke": "not_alive_in_both:ALIVE->REFUSED",
        "gone": "missing_in_candidate",
        "new": "missing_in_baseline",
    }
    assert result["caveats"] == {"toolchain_changed": True, "workers_match": True}
    assert result["claims_not_made"]


def test_compare_flags_unchanged_toolchain_and_worker_mismatch():
    base = report([alive("a")], {"a": 1.0}, workers=8)
    cand = report([alive("a")], {"a": 1.0}, workers=2)
    caveats = mt.compare(base, cand)["caveats"]
    assert caveats == {"toolchain_changed": False, "workers_match": False}


def test_zero_baseline_yields_null_ratio_not_division_error():
    result = mt.compare(report([alive("a")], {"a": 0.0}), report([alive("a")], {"a": 1.0}))
    assert result["pairs"][0]["ratio"] is None
    assert result["comparable"]["total_ratio"] is None


def test_load_report_refuses_missing_timings_and_bad_schema(tmp_path: Path):
    no_timings = report([alive("a")], {"a": 1.0})
    del no_timings["timings"]
    with pytest.raises(mt.TimingContractError, match="HAS_NO_TIMINGS"):
        mt.load_report(write(tmp_path, "t.json", no_timings))
    bad_schema = report([alive("a")], {"a": 1.0})
    bad_schema["schema"] = "nope"
    with pytest.raises(mt.TimingContractError, match="SCHEMA"):
        mt.load_report(write(tmp_path, "s.json", bad_schema))
    negative = report([alive("a")], {"a": -1.0})
    with pytest.raises(mt.TimingContractError, match="PACK_SECONDS_INVALID"):
        mt.load_report(write(tmp_path, "n.json", negative))


def test_cli_exit_codes(tmp_path: Path, capsys):
    a = write(tmp_path, "a.json", report([alive("a")], {"a": 2.0}))
    b = write(tmp_path, "b.json", report([alive("a")], {"a": 1.0}, ggen="ggen 2"))
    assert mt.main(["compare", str(a), str(b), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["comparable"]["total_ratio"] == 0.5
    assert mt.main(["summarize", str(a)]) == 0
    assert mt.main(["summarize", str(tmp_path / "missing.json")]) == 2
