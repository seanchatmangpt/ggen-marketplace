#!/usr/bin/env python3
"""Construct-proven gate for XState v5 machine definitions.

R149/R146 pattern: per-machine esbuild bundle + `createActor(machine).start()`
on the real xstate runtime. A count-only court is insufficient — construction
itself throws on static definition defects (missing `initial` on compound
state, invalid relative transition targets), so the gate proves each machine
constructs and records the constructed initial value or the exact throw.

Parameterized: file list (+ optional per-file expected export / initial
markers), xstate resolve path, temp/build dir. No project-specific vocabulary.

Usage:
  construct_gate.py --machine-file FILE[:EXPORT] ... \
      --xstate-resolve PATH [--expect "EXPORT=INITIAL_JSON"] ... \
      [--build-dir DIR] [--esbuild BIN]

Exit codes: 0 = all files construct OK and all markers matched;
1 = construct failure; 2 = marker mismatch; 3 = harness error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ENTRY_TEMPLATE = """\
import {{ createActor }} from 'xstate';
import {{ {export_name} }} from '{file_stem}';
const actor = createActor({export_name});
actor.start();
const snapshot = actor.getSnapshot();
process.stdout.write(JSON.stringify({{
  ok: true,
  machine: '{export_name}',
  initial: snapshot.value,
}}) + '\\n');
"""


def first_machine_export(source: str) -> str | None:
    m = re.search(r"export const (\w*[Mm]achine\w*)\s*=", source)
    if m:
        return m.group(1)
    m = re.search(r"export const (\w+)\s*=\s*setup\(", source)
    return m.group(1) if m else None


def run_one(file_path: str, export_name: str, esbuild: str, resolve: str,
            build_dir: str) -> dict:
    """Bundle one machine file with a real createActor().start() entry and run it."""
    source = open(file_path, encoding="utf-8").read()
    detected = first_machine_export(source)
    if detected is None:
        return {"file": file_path, "machine": None,
                "verdict": "FAIL", "error": "no machine export found"}
    export_name = detected

    stem = os.path.splitext(os.path.basename(file_path))[0]
    entry = os.path.join(build_dir, f"entry_{stem}.mjs")
    out = os.path.join(build_dir, f"out_{stem}.mjs")

    with open(entry, "w", encoding="utf-8") as f:
        f.write(ENTRY_TEMPLATE.format(
            export_name=export_name,
            file_stem=os.path.abspath(file_path).replace("\\", "\\\\").replace("'", "\\'"),
        ))

    cmd = [
        esbuild, entry,
        "--bundle",
        f"--outfile={out}",
        "--format=esm",
        "--platform=node",
        f"--alias:xstate={resolve}",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"file": file_path, "machine": export_name,
                "verdict": "FAIL", "error": f"esbuild: {proc.stderr.strip()}"}

    proc = subprocess.run(["node", out], capture_output=True, text=True,
                          timeout=30, cwd=build_dir)
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip().splitlines()
        msg = next((ln for ln in err if "Error" in ln or "error" in ln),
                   err[-1] if err else "unknown error")
        return {"file": file_path, "machine": export_name,
                "verdict": "FAIL", "error": msg}
    try:
        payload = json.loads(proc.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {"file": file_path, "machine": export_name,
                "verdict": "FAIL", "error": f"unparseable output: {proc.stdout!r}"}
    return {"file": file_path, "machine": export_name,
            "verdict": "OK", "initial": payload["initial"]}


def canonical(v) -> str:
    return json.dumps(v, sort_keys=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--machine-file", action="append", required=True,
                    help="machine .ts file; FILE:EXPORT overrides export detection")
    ap.add_argument("--xstate-resolve", required=True,
                    help="path to xstate package (esbuild --alias:xstate=...)")
    ap.add_argument("--expect", action="append", default=[],
                    help='expected marker "EXPORT=INITIAL_JSON", e.g. \'m="idle"\'')
    ap.add_argument("--build-dir")
    ap.add_argument("--esbuild", default="esbuild")
    args = ap.parse_args()
    expects = args.expect
    resolve = args.xstate_resolve
    build_dir = args.build_dir
    esbuild_bin = args.esbuild
    spec = args

    if shutil.which(esbuild_bin) is None and os.path.exists(esbuild_bin) is False:
        print(f"construct_gate: esbuild not found: {esbuild_bin}", file=sys.stderr)
        return 3

    build_dir = build_dir or tempfile.mkdtemp(prefix="construct_gate_")
    os.makedirs(build_dir, exist_ok=True)

    expected: dict[str, str] = {}
    for e in expects:
        name, _, val = e.partition("=")
        expected[name] = val

    results, rc = [], 0
    for spec in spec.machine_file:
        path, _, export_override = spec.partition(":")
        r = run_one(path, export_override, esbuild_bin, resolve, build_dir)
        results.append(r)
        status = r["verdict"]
        if status == "OK" and r["machine"] in expected:
            if canonical(r["initial"]) != canonical(json.loads(expected[r["machine"]])):
                status = "MARKER-MISMATCH"
                r["marker_expected"] = expected[r["machine"]]
                r["marker_actual"] = canonical(r["initial"])
                rc = max(rc, 2)
        if status == "FAIL" and rc == 0:
            rc = 1
        if status == "MARKER-MISMATCH":
            pass
        line = (f"{os.path.basename(path)} {r['machine']} {status}"
                + (f" initial={canonical(r['initial'])}" if status == "OK" else "")
                + (f" — {r['error']}" if r.get("error") else "")
                + (f" (expected {r['marker_expected']}, actual {r['marker_actual']})"
                   if status == "MARKER-MISMATCH" else ""))
        print(line)

    n_ok = sum(1 for r in results if r["verdict"] == "OK"
               and (r["machine"] not in expected
                    or canonical(r["initial"]) == canonical(json.loads(expected.get(r["machine"], "null")))))
    print(f"Tally: {n_ok}/{len(results)} construct OK"
          + (f"; markers checked: {len(expected)}" if expected else ""))
    return rc if rc != 0 else (0 if n_ok == len(results) else 1)


if __name__ == "__main__":
    sys.exit(main())
