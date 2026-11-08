#!/usr/bin/env python3
r"""020_compile_shape_scan.py — machine-checkable SHAPES.md rows.

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

JSON MODE: a subject whose path ends .json is scanned semantically, not
by TS tokens (S5 seal finding 2: the TS `setup\s*\(` seam regex is not
discriminating on JSON fixtures — the divergent rejection rode the same
arm as a comment string). The machine object is walked and these laws
are enforced on the object graph (each cites its planted V-DIV row):

- json-no-parallel         — machine.createMachine.type == 'parallel'
                             banned (flat-machine law; V-DIV-1)
- json-missing-initial     — 'initial' absent while 'states' present
                             (V-DIV-2; initial required at every level)
- json-as-const-ref        — any '$ref' shared-config key anywhere in the
                             machine object (inline-setup law; V-DIV-5)
- json-relative-target     — any 'target' string containing '../'
                             (targets must be state-local or
                             root-absolute '#id.state'; V-DIV-3)
- json-stray-comment       — '/*' or '*/' inside any machine string value
                             (balanced-token law; V-DIV-4)
- json-setup-seam          — a 'setup' key required at machine root
                             (JSON analogue of the TS setup-seam)

The subject's ledger/metadata (e.g. a top-level 'violations' array in a
divergent fixture) is NOT scanned — only the machine object — so the
fixture's own description of its violations can never be the rejection
arm. Per-subject `banned` overrides apply to TS mode only.

Non-vacuity: an empty [[subjects]] set or an empty effective banned list
is a CONFIG-ERROR (exit 2) — a court that cannot flip is FAIL (R106 /
shim-court non-vacuity law).

Exit codes: 0 = all subjects clean; 1 = any violation; 2 = config error.
"""

import argparse
import json
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


def _walk(obj, path="$"):
    """Yield (jsonpath, value) for every node in the machine object."""
    yield path, obj
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{path}[{i}]")


def scan_json_subject(full):
    """Semantic scan of a .json machine fixture's machine object.
    Laws are hardcoded here (each cites its divergent-notes V-DIV row);
    a violation is reported with its jsonpath so the rejection arm is
    named, never a regex artifact on ledger prose."""
    violations = []
    try:
        with open(full, "r", encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        return [(full, 0, "json-unreadable", str(exc)[:120])]
    machine = doc.get("machine")
    if not isinstance(machine, dict):
        return [(full, 0, "json-no-machine", "no 'machine' object in fixture")]
    cm = machine.get("createMachine")
    if not isinstance(cm, dict):
        return [(full, 0, "json-no-createMachine",
                 "no machine.createMachine object in fixture")]

    # json-no-parallel (V-DIV-1)
    if cm.get("type") == "parallel":
        violations.append((full, 0, "json-no-parallel",
                           "machine.createMachine.type == 'parallel' "
                           "(flat-machine law; V-DIV-1)"))
    # json-missing-initial (V-DIV-2)
    if "states" in cm and "initial" not in cm:
        violations.append((full, 0, "json-missing-initial",
                           "machine.createMachine has 'states' but no "
                           "'initial' (V-DIV-2)"))
    # json-setup-seam (JSON analogue of the TS setup seam)
    if "setup" not in machine:
        violations.append((full, 0, "json-setup-seam",
                           "no 'setup' key at machine root (inline-setup law)"))
    # json-as-const-ref / json-relative-target / json-stray-comment
    for jp, val in _walk(machine):
        if isinstance(val, dict):
            if "$ref" in val:
                violations.append((full, 0, "json-as-const-ref",
                                   f"shared-config '$ref' at {jp} "
                                   "(inline-setup law; V-DIV-5)"))
        elif isinstance(val, str):
            if "../" in val and jp.endswith(".target"):
                violations.append((full, 0, "json-relative-target",
                                   f"relative cross-level target {val!r} at "
                                   f"{jp} (V-DIV-3)"))
            if "/*" in val or "*/" in val:
                violations.append((full, 0, "json-stray-comment",
                                   f"comment token in string at {jp} "
                                   "(balanced-token law; V-DIV-4)"))
    return violations


def scan_subject(subject, banned, required, root):
    path = subject["path"]
    full = path if os.path.isabs(path) else os.path.join(root, path)
    if full.endswith(".json"):
        return scan_json_subject(full)
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
              f"(TS: {len(DEFAULT_BANNED)} banned-token laws + setup-seam; "
              f"JSON: 6 semantic laws)")
    else:
        print(f"SHAPE-COURT: FAIL — {n} subject(s), see violations above")
    return rc


if __name__ == "__main__":
    sys.exit(main())
