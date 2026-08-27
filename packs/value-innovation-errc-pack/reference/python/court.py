#!/usr/bin/env python3
"""Independent stdlib conformance court for value-innovation-errc/1.

The court validates the portable ERRC calculus without parsing the pack's RDF or
calling ggen, so it is an independent oracle rather than a second renderer. It
has SELECT/CONSTRUCT authority only and never actuates a proposed consequence.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

MODES = ("ELIMINATE", "REDUCE", "RAISE", "CREATE")


class Refusal(ValueError):
    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"REFUSED:{code}:{detail}")


def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _direction(mode: str, baseline: float, target: float) -> bool:
    if not (0 <= baseline <= 10 and 0 <= target <= 10):
        return False
    if mode == "ELIMINATE":
        return baseline > 0 and target == 0
    if mode == "REDUCE":
        return 0 <= target < baseline
    if mode == "RAISE":
        return target > baseline
    if mode == "CREATE":
        return baseline == 0 and target > 0
    return False


def compile_grid(case: dict[str, Any]) -> dict[str, Any]:
    if case.get("direct_actuation") is not False:
        raise Refusal("AMBIENT_DO", "ERRC cannot self-authorize execution")

    findings = list(case.get("findings") or [])
    if not findings:
        raise Refusal("NO_FINDINGS", "grid has no findings")

    seen_modes: set[str] = set()
    seen_factors: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for finding in findings:
        mode = str(finding.get("mode", ""))
        factor = str(finding.get("factor", "")).strip()
        if mode not in MODES:
            raise Refusal("ACTION", mode)
        if not factor:
            raise Refusal("FACTOR", mode)
        if factor in seen_factors:
            raise Refusal("FACTOR_CONFLICT", factor)
        seen_factors.add(factor)
        seen_modes.add(mode)

        for field in ("baseline", "target", "rationale", "owner", "consumer", "evidence", "falsifier"):
            if not str(finding.get(field, "")).strip():
                raise Refusal("REQUIRED", f"{mode}:{field}")

        baseline_level = finding.get("baseline_level")
        target_level = finding.get("target_level")
        if (baseline_level is None) != (target_level is None):
            raise Refusal("LEVEL_PAIR", factor)
        if baseline_level is not None:
            baseline_num = float(baseline_level)
            target_num = float(target_level)
            if not _direction(mode, baseline_num, target_num):
                raise Refusal("DIRECTION", factor)

        normalized.append({
            "mode": mode,
            "factor": factor,
            "baseline": finding["baseline"],
            "target": finding["target"],
            "baseline_level": baseline_level,
            "target_level": target_level,
            "rationale": finding["rationale"],
            "owner": finding["owner"],
            "consumer": finding["consumer"],
            "evidence": finding["evidence"],
            "falsifier": finding["falsifier"],
        })

    missing = [mode for mode in MODES if mode not in seen_modes]
    if case.get("complete") is True and missing:
        raise Refusal("GRID_INCOMPLETE", ",".join(missing))

    result = {
        "protocol": "value-innovation-errc/1",
        "title": str(case.get("title", "")),
        "complete": case.get("complete") is True,
        "findings": sorted(normalized, key=lambda item: (MODES.index(item["mode"]), item["factor"])),
        "irreversible_selections": 0,
        "actuation": False,
    }
    result["receipt_sha256"] = digest(result)
    return result


def positive_case() -> dict[str, Any]:
    common = {"owner": "platform", "consumer": "team", "evidence": "receipt", "falsifier": "counterexample"}
    return {
        "title": "reference",
        "complete": True,
        "direct_actuation": False,
        "findings": [
            {**common, "mode": "ELIMINATE", "factor": "duplicates", "baseline": "many", "target": "none", "baseline_level": 7, "target_level": 0, "rationale": "remove duplicate authority"},
            {**common, "mode": "REDUCE", "factor": "bespoke logic", "baseline": "high", "target": "low", "baseline_level": 8, "target_level": 3, "rationale": "reuse portable calculus"},
            {**common, "mode": "RAISE", "factor": "evidence", "baseline": "partial", "target": "dense", "baseline_level": 4, "target_level": 9, "rationale": "raise verification standing"},
            {**common, "mode": "CREATE", "factor": "marketplace ERRC", "baseline": "absent", "target": "present", "baseline_level": 0, "target_level": 10, "rationale": "manufacture reusable strategy"},
        ],
    }


def expect_refusal(case: dict[str, Any], code: str) -> None:
    try:
        compile_grid(case)
    except Refusal as exc:
        assert exc.code == code, (exc.code, code)
    else:
        raise AssertionError(f"expected {code}")


def main() -> int:
    case = positive_case()
    first = compile_grid(case)
    second = compile_grid(case)
    assert first == second
    assert first["actuation"] is False
    assert first["irreversible_selections"] == 0
    assert len(first["receipt_sha256"]) == 64

    missing = positive_case()
    missing["findings"] = missing["findings"][:-1]
    expect_refusal(missing, "GRID_INCOMPLETE")

    wrong_direction = positive_case()
    wrong_direction["findings"][2]["target_level"] = 2
    expect_refusal(wrong_direction, "DIRECTION")

    duplicate = positive_case()
    duplicate["findings"][3]["factor"] = "evidence"
    expect_refusal(duplicate, "FACTOR_CONFLICT")

    ambient = positive_case()
    ambient["direct_actuation"] = True
    expect_refusal(ambient, "AMBIENT_DO")

    no_evidence = positive_case()
    no_evidence["findings"][0]["evidence"] = ""
    expect_refusal(no_evidence, "REQUIRED")

    print(json.dumps({"standing": "ADMITTED", "protocol": "value-innovation-errc/1", "vectors": 6}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
