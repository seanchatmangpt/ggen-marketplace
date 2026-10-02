#!/usr/bin/env python3
"""Court runner for chicago-xaas-surface-pack (L3 lane, v26.10.1).

  run_courts.py witnesses   gate x same-stem pass/fail witness matrix; exit 1 on any no-fire
  run_courts.py corpus [ttl...]  gates over explicit TTLs, or pack source/*.ttl, or the
                            default fixture corpus; ADMITTED only if zero violations
  run_courts.py json        R2/R3 JSON courts over test/fixtures/rendered/canonical
                            (+ anti-vacuity selftests + determinism court)
  run_courts.py all         witnesses + corpus + json (default)

Exit 0 = courts hold. Exit 1 = a court fired (or a witness failed to fire). Exit 2 = setup
gap (missing inputs/fixtures) - never a silent pass.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import courts  # noqa: E402


def cmd_witnesses():
    rows, bad = courts.run_witnesses()
    print("\n".join(rows))
    return 1 if bad else 0


def cmd_corpus(args):
    rows, bad = courts.run_corpus(args)
    print("\n".join(rows))
    return 1 if bad else 0


def cmd_json():
    import importlib

    bad = 0
    rendered = courts.RENDERED_CANONICAL
    for module_name in (
        "test_subject_integrity",
        "test_layer_courts",
        "test_authority_evidence_court",
        "test_render_determinism",
    ):
        module = importlib.import_module(module_name)
        print(f"== {module_name} ==")
        errors = list(module.run(rendered))
        for err in errors:
            print(f"  VIOLATION: {err}")
        print(f"  run: {'REFUSED' if errors else 'ok'} ({len(errors)} violations)")
        bad += len(errors)
        selftest_errors = list(module.selftest(rendered))
        for err in selftest_errors:
            print(f"  ANTIVACUITY: {err}")
        print(f"  selftest (mutant must fire): {'BAD' if selftest_errors else 'fired'} ({len(selftest_errors)} gaps)")
        bad += len(selftest_errors)
    print("RESULT: " + ("REFUSED" if bad else "JSON_COURTS_OK") + f" ({bad} problems)")
    return 1 if bad else 0


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    args = sys.argv[2:]
    if mode == "witnesses":
        sys.exit(cmd_witnesses())
    if mode == "corpus":
        sys.exit(cmd_corpus(args))
    if mode == "json":
        sys.exit(cmd_json())
    if mode == "all":
        rc = cmd_witnesses()
        rc |= cmd_corpus(args)
        rc |= cmd_json()
        sys.exit(rc)
    print(f"unknown mode: {mode} (witnesses|corpus|json|all)", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
