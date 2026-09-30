"""Chicago tests for the marketplace human-equivalent-work claim court.

No mocks: positive/replay tests execute the real repository court; negative
tests use real temporary files and real parser/aggregation logic.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "chicago_work_equivalent.py"
LEDGER = ROOT / "evidence" / "chicago" / "marketplace-work-equivalent.json"

_spec = importlib.util.spec_from_file_location("chicago_work_equivalent", SCRIPT)
assert _spec is not None and _spec.loader is not None
court = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = court
_spec.loader.exec_module(court)


def run_real_court() -> tuple[int, dict]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(ROOT), "--ledger", str(LEDGER)],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else {}
    return proc.returncode, payload


def test_exact_head_real_corpus_and_replay_are_deterministic() -> None:
    first_code, first = run_real_court()
    second_code, second = run_real_court()

    assert first_code == 0
    assert second_code == 0
    assert first == second
    assert first["court"] == "CHICAGO_MARKETPLACE_WORK_EQUIVALENT_V1"
    assert first["subject"]["repository"] == "seanchatmangpt/ggen-marketplace"
    assert len(first["subject"]["exact_head"]) == 40
    assert first["subject"]["pack_subject_count"] > 0
    assert len(first["subject"]["corpus_sha256"]) == 64


def test_claim_can_only_be_alive_at_or_above_target() -> None:
    code, result = run_real_court()
    assert code == 0
    lower = result["observation"]["person_years_lower_bound"]
    target = result["claim"]["target_person_years"]
    if result["standing"] == "ALIVE":
        assert lower >= target
    else:
        assert result["standing"] == "UNSUPPORTED:INSUFFICIENT_INDEPENDENT_HUMAN_BASELINE_EVIDENCE"
        assert lower < target


def test_inventory_metrics_are_explicitly_excluded() -> None:
    _, result = run_real_court()
    exclusions = set(result["exclusions"])
    assert "commit_count_is_not_person_years" in exclusions
    assert "loc_is_not_person_years" in exclusions
    assert "pack_count_is_not_person_years" in exclusions
    assert "raw_combinatorics_is_not_person_years" in exclusions


def write_subject(root: Path) -> None:
    pack = root / "packs" / "demo-pack"
    pack.mkdir(parents=True)
    (pack / "pack.toml").write_text(
        '[pack]\nname = "demo-pack"\nversion = "0.1.0"\ndescription = "demo"\n',
        encoding="utf-8",
    )
    (pack / "ontology.ttl").write_text("@prefix ex: <urn:ex:> .\n", encoding="utf-8")


def item(
    *,
    evidence_id: str,
    hours: float,
    overlap_group: str,
    source_type: str = "published_study",
    source_uri: str = "https://example.org/study",
    subject_path: str = "packs/demo-pack",
) -> dict:
    return {
        "evidence_id": evidence_id,
        "capability": "demo",
        "person_hours_lower_bound": hours,
        "overlap_group": overlap_group,
        "source_type": source_type,
        "source_uri": source_uri,
        "source_digest_sha256": "a" * 64,
        "subject_paths": [subject_path],
    }


def ledger(items: list[dict]) -> dict:
    return {
        "schema_version": 1,
        "claim": {"person_years": 500_000_000, "hours_per_person_year": 2080},
        "evidence": items,
    }


def test_overlap_group_uses_max_not_sum(tmp_path: Path) -> None:
    write_subject(tmp_path)
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            ledger(
                [
                    item(evidence_id="a", hours=1000, overlap_group="same-work"),
                    item(evidence_id="b", hours=2500, overlap_group="same-work"),
                    item(evidence_id="c", hours=400, overlap_group="disjoint-work"),
                ]
            )
        ),
        encoding="utf-8",
    )
    _, _, items = court.load_ledger(tmp_path, path)
    total, groups = court.overlap_safe_hours(items)
    assert groups == {"disjoint-work": 400.0, "same-work": 2500.0}
    assert total == 2900.0


def test_self_assertion_is_refused(tmp_path: Path) -> None:
    write_subject(tmp_path)
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            ledger(
                [
                    item(
                        evidence_id="self",
                        hours=10**15,
                        overlap_group="self",
                        source_uri="self:I-say-so",
                    )
                ]
            )
        ),
        encoding="utf-8",
    )
    with pytest.raises(court.CourtRefusal, match="SELF_ASSERTION_NOT_EVIDENCE"):
        court.load_ledger(tmp_path, path)


def test_unapproved_source_type_is_refused(tmp_path: Path) -> None:
    write_subject(tmp_path)
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            ledger(
                [
                    item(
                        evidence_id="estimate",
                        hours=10**15,
                        overlap_group="estimate",
                        source_type="model_estimate",
                    )
                ]
            )
        ),
        encoding="utf-8",
    )
    with pytest.raises(court.CourtRefusal, match="SOURCE_TYPE_NOT_INDEPENDENT"):
        court.load_ledger(tmp_path, path)


def test_missing_subject_is_refused(tmp_path: Path) -> None:
    write_subject(tmp_path)
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            ledger(
                [
                    item(
                        evidence_id="missing",
                        hours=100,
                        overlap_group="missing",
                        subject_path="packs/does-not-exist",
                    )
                ]
            )
        ),
        encoding="utf-8",
    )
    with pytest.raises(court.CourtRefusal, match="SUBJECT_PATH_MISSING"):
        court.load_ledger(tmp_path, path)


def test_enforce_fails_closed_when_lower_bound_is_below_target(tmp_path: Path) -> None:
    # Use the real git repository as the exact-head subject while swapping only
    # the ledger. This keeps the CLI boundary real and avoids mocking git.
    path = tmp_path / "ledger.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "claim": {"person_years": 500_000_000, "hours_per_person_year": 2080},
                "evidence": [],
            }
        ),
        encoding="utf-8",
    )
    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--root",
            str(ROOT),
            "--ledger",
            str(path),
            "--enforce",
        ],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert proc.returncode == 3
    payload = json.loads(proc.stdout)
    assert payload["standing"].startswith("UNSUPPORTED:")
