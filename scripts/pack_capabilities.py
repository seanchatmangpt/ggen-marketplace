#!/usr/bin/env python3
"""Static capability scan of every Python script shipped inside packs/.

Reports, per pack and per file, which ambient capabilities the script uses
(network, exec, fs-write, env) by AST inspection only -- nothing is executed.
Also counts packs lacking a LICENSE file or an SPDX identifier.

Usage:
  python3 scripts/pack_capabilities.py            # deterministic JSON to stdout
  python3 scripts/pack_capabilities.py --check    # fail on NEW network use in gates/
  python3 scripts/pack_capabilities.py --markdown # render docs/reference page body

Stdlib only.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = ROOT / "packs"
ALLOWLIST = Path(__file__).resolve().parent / "pack_capabilities.allow.json"
SCHEMA = "ggen.pack-capabilities/1"

NETWORK_MODULES = {
    "socket", "ssl", "urllib", "urllib3", "http", "requests", "httpx", "aiohttp",
    "ftplib", "smtplib", "poplib", "imaplib", "telnetlib", "xmlrpc", "websockets",
    "websocket", "paramiko",
}
EXEC_MODULES = {"subprocess", "pty"}
EXEC_OS_CALLS = {
    "system", "popen", "execv", "execve", "execvp", "execl", "execle", "execlp",
    "spawnv", "spawnl", "spawnlp", "spawnvp", "startfile", "posix_spawn",
}
FS_WRITE_MODULES = {"shutil"}
FS_WRITE_ATTRS = {"write_text", "write_bytes"}
FS_WRITE_OS_CALLS = {"remove", "unlink", "rename", "replace", "rmdir", "makedirs", "mkdir"}
ENV_OS_ATTRS = {"environ", "getenv", "putenv", "unsetenv"}
CAPS = ("network", "exec", "fs-write", "env", "dynamic")
DYNAMIC_BUILTINS = {"exec", "eval", "compile", "__import__"}
VERIFIER_HINTS = ("verif", "qualif", "check", "court", "witness", "validate", "audit")


def _open_writes(node: ast.Call) -> bool:
    mode = None
    if len(node.args) >= 2:
        mode = node.args[1]
    for kw in node.keywords:
        if kw.arg == "mode":
            mode = kw.value
    return (
        isinstance(mode, ast.Constant)
        and isinstance(mode.value, str)
        and any(c in mode.value for c in "wax+")
    )


def scan_source(source: str) -> dict[str, list[str]]:
    """Return {capability: sorted evidence list} for one script."""
    found: dict[str, set[str]] = {c: set() for c in CAPS}
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                _classify_module(root, f"import {alias.name}", found)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            _classify_module(root, f"from {node.module} import ...", found)
            if root == "os":
                for alias in node.names:
                    _classify_os(alias.name, f"from os import {alias.name}", found)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name) and node.value.id == "os":
                _classify_os(node.attr, f"os.{node.attr}", found)
            if node.attr in FS_WRITE_ATTRS:
                found["fs-write"].add(f".{node.attr}()")
        elif isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open" and _open_writes(node):
                found["fs-write"].add("open(..., write mode)")
            elif isinstance(func, ast.Attribute) and func.attr == "open" and _open_writes_path(node):
                found["fs-write"].add(".open(write mode)")
            elif isinstance(func, ast.Name) and func.id == "__import__" and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    _classify_module(arg.value.split(".")[0], f"__import__({arg.value!r})", found)
                else:
                    found["dynamic"].add("__import__(non-literal)")
            elif isinstance(func, ast.Name) and func.id in DYNAMIC_BUILTINS:
                found["dynamic"].add(f"{func.id}()")
            elif isinstance(func, ast.Attribute) and func.attr in ("import_module", "find_spec", "spec_from_file_location", "load_module"):
                found["dynamic"].add(f".{func.attr}()")
    return {c: sorted(found[c]) for c in CAPS if found[c]}


def _open_writes_path(node: ast.Call) -> bool:
    mode = node.args[0] if node.args else None
    for kw in node.keywords:
        if kw.arg == "mode":
            mode = kw.value
    return (
        isinstance(mode, ast.Constant)
        and isinstance(mode.value, str)
        and any(c in mode.value for c in "wax+")
    )


def _classify_module(root: str, evidence: str, found: dict[str, set[str]]) -> None:
    if root in NETWORK_MODULES:
        found["network"].add(evidence)
    if root in EXEC_MODULES:
        found["exec"].add(evidence)
    if root in FS_WRITE_MODULES:
        found["fs-write"].add(evidence)


def _classify_os(attr: str, evidence: str, found: dict[str, set[str]]) -> None:
    if attr in EXEC_OS_CALLS:
        found["exec"].add(evidence)
    if attr in FS_WRITE_OS_CALLS:
        found["fs-write"].add(evidence)
    if attr in ENV_OS_ATTRS:
        found["env"].add(evidence)


def role_of(rel_in_pack: Path) -> str:
    if "gates" in rel_in_pack.parts[:-1]:
        return "gate"
    name = rel_in_pack.name.lower()
    if any(h in name for h in VERIFIER_HINTS) or any(
        h in part.lower() for part in rel_in_pack.parts[:-1] for h in ("verif", "qualif")
    ):
        return "verifier"
    return "other"


def license_state(pack: Path) -> dict[str, bool]:
    has_file = False
    has_spdx = False
    for path in sorted(pack.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        upper = path.name.upper()
        if upper.startswith(("LICENSE", "LICENCE", "COPYING")):
            has_file = True
        if not has_spdx:
            try:
                if "SPDX-License-Identifier" in path.read_text(encoding="utf-8", errors="ignore"):
                    has_spdx = True
            except OSError:
                pass
    return {"license_file": has_file, "spdx": has_spdx}


def scan(packs_dir: Path = PACKS) -> dict:
    packs: dict[str, dict] = {}
    parse_errors: list[str] = []
    for pack in sorted(p for p in packs_dir.iterdir() if p.is_dir()):
        files: dict[str, dict] = {}
        for py in sorted(pack.rglob("*.py")):
            if py.is_symlink() or not py.is_file():
                continue
            rel = py.relative_to(pack)
            try:
                caps = scan_source(py.read_text(encoding="utf-8"))
            except (SyntaxError, UnicodeDecodeError, ValueError) as error:
                parse_errors.append(f"{pack.name}/{rel.as_posix()}: {type(error).__name__}")
                caps = {}
            files[rel.as_posix()] = {"role": role_of(rel), "capabilities": caps}
        used = sorted({c for f in files.values() for c in f["capabilities"]})
        packs[pack.name] = {
            "python_files": len(files),
            "capabilities": used,
            "license": license_state(pack),
            "files": {k: v for k, v in files.items() if v["capabilities"]},
        }
    return {"schema": SCHEMA, "packs": packs, "parse_errors": sorted(parse_errors)}


def gate_users(report: dict, cap: str) -> list[str]:
    users = []
    for name, info in report["packs"].items():
        for rel, f in info["files"].items():
            if f["role"] == "gate" and cap in f["capabilities"]:
                users.append(f"packs/{name}/{rel}")
    return sorted(users)


def gate_network_users(report: dict) -> list[str]:
    return gate_users(report, "network")


def gate_dynamic_users(report: dict) -> list[str]:
    return gate_users(report, "dynamic")


def unparsed_gates(report: dict) -> list[str]:
    """Parse failures under a gates/ directory (or unreadable): cannot be proven network-free."""
    return sorted(e.split(":")[0] for e in report["parse_errors"] if "/gates/" in e.split(":")[0])


def load_allowlist(path: Path = ALLOWLIST) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(data.get("network_in_gates", []))


def load_dynamic_allowlist(path: Path = ALLOWLIST) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return sorted(data.get("dynamic_in_gates", []))


def check(report: dict, allowed: list[str]) -> tuple[list[str], list[str]]:
    users = gate_network_users(report)
    new = [u for u in users if u not in set(allowed)]
    stale = [a for a in allowed if a not in set(users)]
    return new, stale


def render_markdown(report: dict) -> str:
    packs = report["packs"]
    n = len(packs)
    py_total = sum(p["python_files"] for p in packs.values())
    with_py = sum(1 for p in packs.values() if p["python_files"])
    cap_packs = {c: sorted(k for k, p in packs.items() if c in p["capabilities"]) for c in CAPS}
    role_counts: dict[str, dict[str, int]] = {}
    for p in packs.values():
        for f in p["files"].values():
            for c in f["capabilities"]:
                role_counts.setdefault(f["role"], {}).setdefault(c, 0)
                role_counts[f["role"]][c] += 1
    lic_file = sum(1 for p in packs.values() if p["license"]["license_file"])
    spdx = sum(1 for p in packs.values() if p["license"]["spdx"])
    neither = sorted(
        k for k, p in packs.items() if not p["license"]["license_file"] and not p["license"]["spdx"]
    )
    no_file = n - lic_file
    no_spdx = n - spdx
    out = [
        "# Pack capabilities",
        "",
        "Generated by `python3 scripts/pack_capabilities.py --markdown`; do not edit by hand.",
        "The scan is static (AST only): it reports what a script *can* reach, not what it did.",
        "Known limit: names built at runtime (for example `importlib.import_module('soc'+'ket')`)",
        "cannot be resolved. Gates using `importlib`, non-literal `__import__`, `exec`, `eval` or",
        "`compile` are reported as capability `dynamic` and `--check` refuses them unless listed",
        "under `dynamic_in_gates` in the allowlist; gates that fail to parse are also refused.",
        "",
        "## Contents",
        "",
        "- [Summary](#summary)",
        "- [Capability by role](#capability-by-role)",
        "- [Packs using each capability](#packs-using-each-capability)",
        "- [Network use in gates](#network-use-in-gates)",
        "- [License coverage](#license-coverage)",
        "- [See Also](#see-also)",
        "",
        "## Summary",
        "",
        "| metric | value |",
        "|---|---|",
        f"| packs | {n} |",
        f"| packs with Python scripts | {with_py} |",
        f"| Python files scanned | {py_total} |",
        f"| files failing to parse | {len(report['parse_errors'])} |",
        "",
        "## Capability by role",
        "",
        "Files using each capability, by inferred role (`gate` = under a `gates/` directory,",
        "`verifier` = name or directory suggests verification, `other` = the rest).",
        "",
        "| role | " + " | ".join(CAPS) + " |",
        "|---|" + "---|" * len(CAPS),
    ]
    for role in ("gate", "verifier", "other"):
        row = role_counts.get(role, {})
        out.append(f"| {role} | " + " | ".join(str(row.get(c, 0)) for c in CAPS) + " |")
    out += ["", "## Packs using each capability", "", "| capability | packs |", "|---|---|"]
    for c in CAPS:
        out.append(f"| {c} | {len(cap_packs[c])} |")
    users = gate_network_users(report)
    dyn = gate_dynamic_users(report)
    out += ["", "## Network use in gates", ""]
    if users:
        out += ["Gate scripts importing a network module (allowlisted in", "`scripts/pack_capabilities.allow.json`):", ""]
        out += [f"- `{u}`" for u in users]
    else:
        out += [
            "No gate script under `packs/**/gates/` imports a network module. The allowlist",
            "`scripts/pack_capabilities.allow.json` is empty, so `--check` fails on the first",
            "gate that does.",
        ]
    out += ["", f"Gates with dynamic code loading (`dynamic_in_gates` allowlist): {len(dyn)}", ""]
    out += [f"- `{u}`" for u in dyn]
    out += [
        "",
        "## License coverage",
        "",
        "A pack is counted as licensed if any file in its tree is named `LICENSE*`,",
        "`LICENCE*` or `COPYING*`; it has SPDX if any text file in its tree contains",
        "`SPDX-License-Identifier`.",
        "",
        "| state | packs |",
        "|---|---|",
        f"| with LICENSE file | {lic_file} |",
        f"| lacking LICENSE file | {no_file} |",
        f"| with SPDX identifier | {spdx} |",
        f"| lacking SPDX identifier | {no_spdx} |",
        f"| lacking both | {len(neither)} |",
        "",
    ]
    if neither:
        out += ["<details><summary>Packs lacking both</summary>", ""]
        out += [f"- `{k}`" for k in neither]
        out += ["", "</details>", ""]
    out += [
        "## See Also",
        "",
        "- [Pack contract](pack-contract.md)",
        "- [Workflow map](workflow-map.md)",
        "",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="fail on new network use in gates/")
    ap.add_argument("--markdown", action="store_true", help="emit the reference page body")
    ap.add_argument("--packs-dir", type=Path, default=PACKS)
    ap.add_argument("--allowlist", type=Path, default=ALLOWLIST)
    args = ap.parse_args(argv)
    if not args.packs_dir.is_dir():
        print(f"REFUSED:PACKS_DIR_MISSING {args.packs_dir}", file=sys.stderr)
        return 2
    report = scan(args.packs_dir)
    if args.check:
        try:
            allowed = load_allowlist(args.allowlist)
            allowed_dyn = load_dynamic_allowlist(args.allowlist)
        except (OSError, ValueError) as error:
            print(f"REFUSED:ALLOWLIST_UNREADABLE {args.allowlist}: {type(error).__name__}", file=sys.stderr)
            return 2
        new, stale = check(report, allowed)
        for u in new:
            print(f"REFUSED:UNDECLARED_NETWORK {u}", file=sys.stderr)
        new_dyn = [u for u in gate_dynamic_users(report) if u not in set(allowed_dyn)]
        for u in new_dyn:
            print(f"REFUSED:UNDECLARED_DYNAMIC_CODE {u}", file=sys.stderr)
        bad = unparsed_gates(report)
        for u in bad:
            print(f"REFUSED:UNPARSEABLE_GATE {u}", file=sys.stderr)
        for s in stale:
            print(f"note: stale allowlist entry {s}", file=sys.stderr)
        if new or new_dyn or bad:
            return 1
        print(f"ok: {len(gate_network_users(report))} network gate(s), all allowlisted")
        return 0
    if args.markdown:
        sys.stdout.write(render_markdown(report))
        return 0
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
