#!/usr/bin/env python3
r"""030_conformance.py — conformance-matrix court for XState v5 machine JSON.

Validates a machine fixture's machine object against its conformance matrix
(S5 seal open item 1: three of the five planted V-DIV violations in
fixtures/divergent-machine.json had no runnable rejector — V-DIV-1, V-DIV-2,
V-DIV-3 — this gate closes all three):

- parallel-only-when-declared (V-DIV-1) — machine.type == 'parallel' is
  rejected unless the subject's conformance matrix explicitly declares
  `allow_parallel = true`. Checked at EVERY level, not just the root.
- root-initial-required (V-DIV-2) — any state node carrying a non-empty
  'states' table must also declare 'initial' (root and nested alike).
- no-relative-cross-level-target (V-DIV-3) — every 'target' string must be
  state-local ('counting', 'idle.idle') or root-absolute ('#counter.idle');
  '../' traversal is banned everywhere.

The subject's own ledger/metadata ('violations', 'expected_gates',
'$comment', 'comment_field') is NOT scanned — only the machine object —
so a fixture's description of its violations can never be the rejection
arm.

Config (TOML, mirror of 020's pattern):

    [rules]                       # optional; defaults shown
    allow_parallel = false        # pack law: flat guarded machines only

    [[subjects]]                  # optional if subjects given positionally
    path = "../fixtures/positive-machine.json"
    allow_parallel = false        # per-subject override wins over [rules]

Usage:
    python3 gates/030_conformance.py                       # default subject
    python3 gates/030_conformance.py ../fixtures/divergent-machine.json
    python3 gates/030_conformance.py --config gates/conformance.toml

Non-vacuity: zero subjects (no config subjects AND no positional args)
is a CONFIG-ERROR (exit 2) — a court that cannot flip is FAIL.

Exit codes: 0 = all subjects conform; 1 = any violation; 2 = config error.
"""

import argparse
import json
import os
import sys
import tomllib

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "conformance.toml")


def load_config(path):
    if not os.path.isfile(path):
        return {}
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def machine_of(full):
    """Load the fixture and return (machine_dict, error_tuple).

    The ledger/violations metadata is deliberately ignored: only the
    machine object is judged.
    """
    try:
        with open(full, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return None, (full, "conformance-unreadable", str(exc)[:120])
    machine = doc.get("machine")
    if not isinstance(machine, dict):
        return None, (full, "conformance-no-machine",
                      "no 'machine' object in fixture")
    cm = machine.get("createMachine")
    if not isinstance(cm, dict):
        return None, (full, "conformance-no-createMachine",
                      "no machine.createMachine object in fixture")
    return machine, None


def _walk(obj, path="$"):
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def check_subject(full, allow_parallel):
    """Return a list of (subject, rule_id, detail) violations."""
    machine, err = machine_of(full)
    if err is not None:
        return [(full, err[1], err[2])]
    violations = []
    root = machine.get("createMachine", {})

    def state_nodes(node, path):
        yield path, node
        for name, child in (node.get("states") or {}).items():
            if isinstance(child, dict):
                yield from state_nodes(child, f"{path}.states.{name}")

    # V-DIV-1: parallel only when declared (every level)
    if not allow_parallel:
        for jp, val in _walk(root):
            if isinstance(val, dict) and val.get("type") == "parallel":
                violations.append((full, "V-DIV-1",
                                   f"parallel state node at {jp} but matrix "
                                   "does not declare allow_parallel "
                                   "(flat-machine law)"))

    # V-DIV-2: initial required wherever a 'states' table exists
    for jp, node in state_nodes(root, "createMachine"):
        states = node.get("states")
        if isinstance(states, dict) and states and "initial" not in node:
            violations.append((full, "V-DIV-2",
                               f"state node at {jp} has 'states' but no "
                               "'initial' (initial required at every level)"))

    # V-DIV-3: no relative '../' cross-level targets
    for jp, val in _walk(root):
        if isinstance(val, str) and "../" in val and jp.endswith(".target"):
            violations.append((full, "V-DIV-3",
                               f"relative cross-level target {val!r} at {jp} "
                               "(state-local or root-absolute '#id...' only)"))
    return violations


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--root", default=None,
                    help="base dir for subject paths (default: config dir)")
    ap.add_argument("subjects", nargs="*",
                    help="machine fixture paths (override config subjects)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    rules = cfg.get("rules", {}) if isinstance(cfg.get("rules"), dict) else {}
    default_allow_parallel = bool(rules.get("allow_parallel", False))

    if args.subjects:
        subjects = [{"path": p} for p in args.subjects]
    else:
        subjects = cfg.get("subjects", [])
    if not isinstance(subjects, list) or not subjects:
        print("CONFIG-ERROR: zero subjects (no [[subjects]] in config and "
              "none positional) — vacuous court")
        return 2
    for s in subjects:
        if not isinstance(s, dict) or "path" not in s:
            print("CONFIG-ERROR: subject missing 'path'")
            return 2

    root = args.root or os.path.dirname(os.path.abspath(args.config))
    rc = 0
    n_viol = 0
    for s in subjects:
        path = s["path"]
        full = path if os.path.isabs(path) else os.path.join(root, path)
        allow = bool(s.get("allow_parallel", default_allow_parallel))
        for full_p, rule_id, detail in check_subject(full, allow):
            print(f"VIOLATION {full_p} [{rule_id}] {detail}")
            n_viol += 1
            rc = 1

    if rc == 0:
        print(f"CONFORMANCE-COURT: PASS — {len(subjects)} subject(s), "
              f"0 violations (V-DIV-1/2/3 rejectors armed, "
              f"allow_parallel={default_allow_parallel})")
    else:
        print(f"CONFORMANCE-COURT: FAIL — {len(subjects)} subject(s), "
              f"{n_viol} violation(s)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
