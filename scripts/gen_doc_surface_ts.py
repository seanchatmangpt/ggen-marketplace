#!/usr/bin/env python3
"""gen_doc_surface_ts.py - deterministic TypeScript/JavaScript symbol scanner
(doc-hdit v1, TS lane).

Same JSON schema as gen_doc_surface.py code mode:
  {"repo", "path", "version", "modules": [{"name", "file", "items": [
      {"kind", "ident", "signature"}]}]}

Stdlib only (regex + brace-depth, no tree-sitter). Scans `src/**/*.ts`
under the repo root; skips SKIP_DIRS and test fixtures (test/, tests/,
fixtures/, __tests__/, *.test.ts, *.spec.ts, *.d.ts). Also captures
package.json `bin` + `scripts`.

Determinism contract: same tree in -> byte-identical JSON out (sorted
iteration, sort_keys=True). No network, no clock, no randomness.

Disclosed limits (same class as gen_doc_surface.py): comment/string
stripping is naive; it may over-strip but only risks false negatives,
not false positives on `export` items.

Usage: gen_doc_surface_ts.py code REPO
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    "deps", "_build", "node_modules", "target", ".git", ".venv", "priv",
    "test", "tests", "fixtures", "__tests__", "dist", "build", "coverage",
}
TEST_FILE = re.compile(r"\.(test|spec)\.[tj]sx?$")

TS_EXPORT_FN = re.compile(
    r"^export\s+(?:declare\s+)?(?:default\s+)?(?:async\s+)?"
    r"function\s*\*?\s*([A-Za-z_$][\w$]*)\s*(\([^)]*\))",
)
TS_DEFAULT_FN = re.compile(
    r"^export\s+default\s+(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*(\([^)]*\))",
)
TS_EXPORT_CLASS = re.compile(
    r"^export\s+(?:declare\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Z][\w$]*)",
)
TS_DEFAULT_CLASS = re.compile(r"^export\s+default\s+(?:abstract\s+)?class\s+([A-Z][\w$]*)")
TS_EXPORT_INTERFACE = re.compile(r"^export\s+(?:declare\s+)?interface\s+([A-Z][\w$]*)")
TS_EXPORT_TYPE = re.compile(r"^export\s+(?:declare\s+)?type\s+([A-Z][\w$]*)")
TS_EXPORT_ENUM = re.compile(
    r"^export\s+(?:declare\s+)?(?:const\s+)?enum\s+([A-Z][\w$]*)",
)
TS_EXPORT_CONST = re.compile(
    r"^export\s+const\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=", re.M,
)
TS_INTERFACE_HEAD = re.compile(
    r"^export\s+(?:declare\s+)?interface\s+([A-Z][\w$]*)[^{;]*(?=\{)", re.M,
)
TS_ENUM_HEAD = re.compile(
    r"^export\s+(?:declare\s+)?(?:const\s+)?enum\s+([A-Z][\w$]*)[^{;]*(?=\{)", re.M,
)
TS_TYPE_ALIAS = re.compile(
    r"^export\s+(?:declare\s+)?type\s+([A-Z][\w$]*)[^=\n]*=\s*", re.M,
)
TS_CLASS_DECL = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?(?:abstract\s+)?class\s+([A-Z][\w$]*)")
TS_METHOD = re.compile(
    r"^\s+(?:public\s+|private\s+|protected\s+|readonly\s+|static\s+|"
    r"override\s+|async\s+|get\s+|set\s+)*"
    r"([A-Za-z_$][\w$]*)\s*(\([^)]*\))\s*(?::[^{=]+)?\s*{",
)
IDENT_BAD = {
    "if", "for", "while", "switch", "catch", "return", "function", "class",
    "constructor",
}


def iter_ts_files(root: Path):
    for p in sorted(root.rglob("*.ts")):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if not p.is_file() or p.name.endswith(".d.ts") or TEST_FILE.search(p.name):
            continue
        yield p


def strip_comments(text: str) -> str:
    """Char-scan comment removal that respects string/template literals."""
    out = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if ch == "/" and nxt == "/":
            while i < n and text[i] != "\n":
                i += 1
        elif ch == "/" and nxt == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                if text[i] == "\n":
                    out.append("\n")  # keep line numbers stable
                i += 1
            i += 2
        elif ch in ('"', "'", "`"):
            quote = ch
            out.append(ch)
            i += 1
            while i < n:
                if text[i] == "\\":
                    i += 2
                    continue
                if text[i] == quote:
                    break
                out.append(text[i])
                i += 1
            out.append(quote)
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def scan_class_methods(lines):
    """Yield (name, args) for methods inside `class ... {` blocks by depth."""
    depth = 0
    class_stack = []  # depth at which the class body opened
    for line in lines:
        cd = TS_CLASS_DECL.search(line)
        open_delta = line.count("{") - line.count("}")
        if cd and open_delta >= 0:
            class_stack.append(depth + open_delta if open_delta else depth + (1 if "{" in line else 0))
        depth += open_delta
        while class_stack and depth < class_stack[-1]:
            class_stack.pop()
        if class_stack:
            m = TS_METHOD.match(line)
            if m and m.group(1) not in IDENT_BAD:
                yield m.group(1), m.group(2)


def scan_file(path: Path, repo: Path):
    rel = str(path.relative_to(repo))
    text = strip_comments(path.read_text(errors="replace"))
    lines = text.splitlines()
    items = []
    for ln in lines:
        m = TS_EXPORT_FN.search(ln)
        if m:
            items.append({"kind": "function", "ident": m.group(1),
                          "signature": m.group(1) + m.group(2)})
            continue
        m = TS_DEFAULT_FN.search(ln)
        if m:
            items.append({"kind": "default_export", "ident": m.group(1),
                          "signature": m.group(1) + m.group(2)})
            continue
        m = TS_DEFAULT_CLASS.search(ln)
        if m:
            items.append({"kind": "default_export", "ident": m.group(1),
                          "signature": "class " + m.group(1)})
            continue
        m = TS_EXPORT_CLASS.search(ln)
        if m:
            items.append({"kind": "class", "ident": m.group(1),
                          "signature": "class " + m.group(1)})
            continue
        m = TS_EXPORT_INTERFACE.search(ln)
        if m:
            items.append({"kind": "interface", "ident": m.group(1),
                          "signature": "interface " + m.group(1)})
            continue
        m = TS_EXPORT_TYPE.search(ln)
        if m:
            items.append({"kind": "type", "ident": m.group(1),
                          "signature": "type " + m.group(1)})
            continue
        m = TS_EXPORT_ENUM.search(ln)
        if m:
            items.append({"kind": "enum", "ident": m.group(1),
                          "signature": "enum " + m.group(1)})
            continue
    for m in TS_EXPORT_CONST.finditer(text):
        items.append({"kind": "const", "ident": m.group(1), "signature": m.group(1)})
    # Populate struct/enum degenerate signatures (kind interface/type/enum).
    for m in TS_INTERFACE_HEAD.finditer(text):
        for it in items:
            if it["kind"] == "interface" and it["ident"] == m.group(1):
                it["signature"] = ts_members_signature(
                    "interface", it["ident"], text, m.end()
                )
    for m in TS_ENUM_HEAD.finditer(text):
        for it in items:
            if it["kind"] == "enum" and it["ident"] == m.group(1):
                it["signature"] = ts_members_signature(
                    "enum", it["ident"], text, m.end()
                )
    for m in TS_TYPE_ALIAS.finditer(text):
        for it in items:
            if it["kind"] == "type" and it["ident"] == m.group(1):
                it["signature"] = ts_members_signature(
                    "type", it["ident"], text, m.end()
                )
    for name, args in scan_class_methods(lines):
        if name not in {i["ident"] for i in items if i["kind"] != "method"}:
            items.append({"kind": "method", "ident": name,
                          "signature": name + args})
    return uniq_items(items), rel


def brace_body(text, i):
    """Balanced `{...}` body following index i, or None (refuses when a
    `;` separates — bodiless declaration, next `{` belongs elsewhere)."""
    j = text.find("{", i)
    if j == -1 or ";" in text[i:j]:
        return None
    depth = 0
    for k in range(j, len(text)):
        ch = text[k]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]
    return None


def split_members(body, sep):
    """Split on top-level `sep` chars (depth-aware over <>(){}[])."""
    parts, cur, depth = [], [], 0
    for ch in body:
        if ch in "<([{":
            depth += 1
            cur.append(ch)
        elif ch in ">)]}":
            depth = max(0, depth - 1)
            cur.append(ch)
        elif ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def ts_members_signature(kind, ident, text, i):
    """Populate interface/type/enum signatures with their members:
    `Name { m: T, n?: U }` / `Name { A, B }` / `Name = "a" | "b"`."""
    body = brace_body(text, i)
    if body is not None:
        members = split_members(body, ";" if kind == "interface" else ",")
        if not members:
            return ident
        return ident + " { " + ", ".join(members) + " }"
    if kind == "type":
        # non-brace alias: union/primitive RHS up to end of statement
        # (i is just past `=`); `| ...` continuation lines are folded in.
        end = len(text)
        for stop in (";", "\n"):
            k = text.find(stop, i)
            if k != -1:
                end = min(end, k)
        lines = [text[i:end].strip()]
        while end < len(text) and text[end:].lstrip().startswith("|"):
            nl = text.find("\n", end)
            line = text[end:nl if nl != -1 else len(text)].strip()
            lines.append(line)
            end = nl + 1 if nl != -1 else len(text)
        rhs = " ".join(" ".join(lines).split())
        if rhs:
            return ident + " = " + rhs
    return ""


def uniq_items(items):
    seen = set()
    out = []
    for it in items:
        key = (it["kind"], it["ident"])
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out


def scan_node(repo: Path):
    modules = []
    versions = {}
    for pj in sorted(repo.rglob("package.json")):
        if any(part in SKIP_DIRS for part in pj.parts) or not pj.is_file():
            continue
        try:
            data = json.loads(pj.read_text(errors="replace"))
        except json.JSONDecodeError:
            continue
        rel = str(pj.relative_to(repo))
        items = []
        bin_ = data.get("bin")
        if isinstance(bin_, str):
            items.append({"kind": "bin", "ident": data.get("name", rel), "signature": bin_})
        elif isinstance(bin_, dict):
            for k, v in sorted(bin_.items()):
                items.append({"kind": "bin", "ident": k, "signature": v})
        for k, v in sorted((data.get("scripts") or {}).items()):
            items.append({"kind": "script", "ident": k, "signature": v})
        if data.get("version"):
            versions[data.get("name", rel)] = data["version"]
        if items:
            modules.append({"name": data.get("name", rel), "file": rel, "items": items})
    return modules, versions


def extract_code(repo: Path):
    repo = Path(repo)
    modules = []
    for path in iter_ts_files(repo):
        items, rel = scan_file(path, repo)
        if items:
            modules.append({"name": rel, "file": rel, "items": items})
    node_modules, versions = scan_node(repo)
    modules += node_modules
    modules.sort(key=lambda x: x["name"])
    return {"repo": repo.name, "path": str(repo), "version": versions, "modules": modules}


def main(argv):
    if len(argv) < 3 or argv[1] != "code":
        print(__doc__, file=sys.stderr)
        return 2
    surface = extract_code(Path(argv[2]))
    print(json.dumps(surface, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
