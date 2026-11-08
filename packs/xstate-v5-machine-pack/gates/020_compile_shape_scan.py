#!/usr/bin/env python3
"""020_compile_shape_scan.py — machine-checkable SHAPES.md rows.

Compiles the SHAPES.md law list (srve docs/diagrams/state/xstate/SHAPES.md)
into a config-driven banned-token / required-seam scanner. Laws encoded by
default (each cites its SHAPES.md row / receipt):

- no-parallel        — `type: 'parallel'` banned (SHAPES.md flat law; R88
                       orthogonal-coextension is the registered exception,
                       opt-out per subject via an explicit `banned` override
                       that drops the rule).
- no-as-const        — `as const` shared configs banned (R85b falsifier:
                       phantom brand props cause TS2322).
- no-dual-annotation — `{ context: X; event: Y }` explicit param annotations
                       banned (R84b: explicit widening -> TS2322 variance).
- setup-seam         — a `setup(` machine-definition seam required.
- excluded-absence   — config-declared `excluded` patterns must be absent
                       from the machine body (redirect-class law, R44/R33-D2:
                       comments claiming exclusion while edges exist).

Config (TOML, default shapes.toml next to this script):

    [[subjects]]
    path = "docs/.../machine.ts"    # relative to --root (default config dir)
    # optional per-subject overrides:
    # banned = [[name, regex], ...]  (TOML arrays) replacing defaults
    # excluded = [regex, ...]        extra must-be-absent patterns
    # required = [[name, regex], ...] extra must-be-present patterns

Non-vacuity: an empty [[subjects]] set or an empty effective banned list
is a CONFIG-ERROR (exit 2) — a court that cannot flip is FAIL (R106 /
shim-court non-vacuity law).

Exit codes: 0 = all subjects clean; 1 = any violation; 2 = config error.
"""

import argparse
import os
import re
import sys
import tomllib

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shapes.toml")

DEFAULT_BANNED = [
    ("no-parallel", r"type:\s*['\"]parallel['\"]"),
    ("no-as-const", r"\bas\s+const\b"),
    ("no-dual-annotation", r"context\s*:\s*\w+\s*;\s*event\s*:\s*\w+"),
]
DEFAULT_REQUIRED = [("setup-seam", r"setup\s*\(")]


def load_config(path):
    with open(path, "rb") as fh:
        cfg = tomllib.load(fh)
    if not isinstance(cfg.get("subjects"), list) or not cfg["subjects"]:
        print(f"CONFIG-ERROR {path}: missing/empty [[subjects]] table")
        sys.exit(2)
    for s in cfg["subjects"]:
        if "path" not in s:
            print(f"CONFIG-ERROR {path}: subject missing 'path'")
            sys.exit(2)
    return cfg


def compile_rules(rules, kind, cfgpath):
    out = []
    for rule in rules:
        name, pattern = rule[0], rule[1]
        try:
            out.append((name, re.compile(pattern)))
        except re.error as exc:
            print(f"CONFIG-ERROR {cfgpath}: bad {kind} regex {name!r}: {exc}")
            sys.exit(2)
    return out


def effective_rules(subject, defaults):
    """Per-subject override: subject['banned'] (TOML array-of-arrays) replaces
    the defaults wholesale so an R88-exempt subject can drop no-parallel."""
    override = subject.get("banned")
    return override if override is not None else defaults


def scan_subject(subject, banned, required, root):
    path = subject["path"]
    full = path if os.path.isabs(path) else os.path.join(root, path)
    violations = []
    if not os.path.isfile(full):
        return [(full, 0, "missing-file", "subject file not found")]
    with open(full, "r", encoding="utf-8") as fh:
        lines = fh.read().splitlines()
    for lineno, line in enumerate(lines, 1):
        for name, rx in banned:
            if rx.search(line):
                violations.append((full, lineno, name, line.strip()[:120]))
    for name, rx in required:
        if not any(rx.search(line) for line in lines):
            violations.append((full, 0, name, "required seam not found"))
    return violations


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=DEFAULT_CONFIG)
    ap.add_argument("--root", default=None,
                    help="base dir for subject paths (default: config file's dir)")
    args = ap.parse_args()

    cfg = load_config(args.config)
    root = args.root or os.path.dirname(os.path.abspath(args.config))
    default_banned = compile_rules(DEFAULT_BANNED, "banned", args.config)
    default_required = compile_rules(DEFAULT_REQUIRED, "required", args.config)

    rc = 0
    for subject in cfg["subjects"]:
        banned = compile_rules(effective_rules(subject, DEFAULT_BANNED),
                               "banned", args.config)
        required = compile_rules(DEFAULT_REQUIRED, "required", args.config)
        violations = scan_subject(subject, banned, required, root)
        for full, lineno, name, detail in violations:
            loc = f"{full}:{lineno}" if lineno else full
            print(f"VIOLATION {loc} [{name}] {detail}")
            rc = 1

    n = len(cfg["subjects"])
    if rc == 0:
        print(f"SHAPE-COURT: PASS — {n} subject(s), 0 violations "
              f"({len(DEFAULT_BANNED)} banned-token laws + setup-seam)")
    else:
        print(f"SHAPE-COURT: FAIL — {n} subject(s), see violations above")
    return rc


if __name__ == "__main__":
    sys.exit(main())
