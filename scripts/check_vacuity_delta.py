#!/usr/bin/env python3
"""Fail closed only on vacuity findings introduced by an exact subject.

The exhaustive vacuity audit remains a corpus-wide observation. This comparator
turns that observation into a PR admission predicate by comparing an exact
subject with an exact baseline and refusing only newly introduced blocking
findings. Historical findings remain visible in the corpus receipt but cannot
make every unrelated PR permanently red.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import audit_vacuity as audit


def finding_key(finding: audit.Finding) -> tuple[str, int, str, str, str]:
    """Identity of a finding independent of the Git subject carrying it."""
    return (
        finding.path,
        finding.line,
        finding.rule,
        finding.severity,
        finding.detail,
    )


def blocking_findings(
    baseline: audit.SubjectReport,
    subject: audit.SubjectReport,
    *,
    warnings_as_errors: bool = False,
) -> tuple[audit.Finding, ...]:
    """Return blocking findings present in subject but absent from baseline."""
    baseline_keys = {finding_key(f) for f in baseline.findings}
    introduced = [f for f in subject.findings if finding_key(f) not in baseline_keys]
    return tuple(
        f
        for f in introduced
        if f.severity == "error" or warnings_as_errors
    )


def compare_refs(
    baseline_ref: str,
    subject_ref: str,
    *,
    warnings_as_errors: bool = False,
) -> tuple[audit.SubjectReport, audit.SubjectReport, tuple[audit.Finding, ...]]:
    baseline = audit.audit_subject(baseline_ref, audit._git_ref_files(baseline_ref))
    subject = audit.audit_subject(subject_ref, audit._git_ref_files(subject_ref))
    regressions = blocking_findings(
        baseline,
        subject,
        warnings_as_errors=warnings_as_errors,
    )
    return baseline, subject, regressions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--subject-ref", required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args(argv)

    baseline, subject, regressions = compare_refs(
        args.baseline_ref,
        args.subject_ref,
        warnings_as_errors=args.warnings_as_errors,
    )
    payload = {
        "schema": "https://ggen.dev/marketplace/vacuity-delta/v1",
        "standing": "REFUSED" if regressions else "ADMITTED",
        "baseline_ref": args.baseline_ref,
        "subject_ref": args.subject_ref,
        "baseline_findings": len(baseline.findings),
        "subject_findings": len(subject.findings),
        "blocking_regressions": [asdict(f) for f in regressions],
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 2 if regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
