#!/usr/bin/env python3
"""gen_doc_surface.py - deterministic code/doc fact extractor (doc-hdit v1).

v1 is a rigorous deterministic symbol scanner (stdlib only: regex + ast).
tree-sitter/oxigraph is the v2 path; see scripts/doc_surface_conventions.md
for scope and disclosed limits.

Usage:
  gen_doc_surface.py code REPO
  gen_doc_surface.py doc REPO [--code-json FILE] [--docs-dir DIR1,DIR2]
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {"deps", "_build", "node_modules", "target", ".git", ".venv", "priv"}

ELIXIR_MODULE = re.compile(r"defmodule\s+([A-Z][A-Za-z0-9._]*)\s+do")
ELIXIR_DEF = re.compile(r"^\s*def\s+([a-z_][a-zA-Z0-9_?!]*)(\([^)]*\))?", re.M)
ELIXIR_SPEC = re.compile(r"^\s*@\s*spec\s+(.+)$")
ELIXIR_VERSION = re.compile(r'@version\s+"([^"]+)"|@?\s*version\s*:\s*"([^"]+)"')
ELIXIR_DOC_LINE = re.compile(r"@\s*doc\s+(false|true)?\s*$")
HEREDOC = re.compile(r'@\s*doc\s+"""(.*?)"""', re.S)
ASH_BLOCK = re.compile(r"\b(attributes|actions)\s+do(.*?)\bend\b", re.S)
ASH_ATTR = re.compile(r"^\s*\w+\s+:([a-z_][a-zA-Z0-9_]*)", re.M)
ASH_ACTION = re.compile(r"^\s*(read|create|update|destroy|action)\s+:([a-z_][a-zA-Z0-9_]*)", re.M)

RUST_FN = re.compile(
    r"\bpub\s+(?:const\s+)?(?:unsafe\s+)?(?:async\s+)?fn\s+"
    r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(\([^)]*\))",
)
RUST_ITEM = re.compile(r"\bpub\s+(struct|enum|trait)\s+([A-Z][A-Za-z0-9_]*)")
CARGO_PACKAGE = re.compile(r'\[package\][^\[]{0,600}?name\s*=\s*"([^"]+)"', re.S)
CARGO_VERSION = re.compile(r'\[package\][^\[]{0,600}?version\s*=\s*"([^"]+)"', re.S)
CARGO_WS_VERSION = re.compile(r'\[workspace\.package\][^\[]{0,600}?version\s*=\s*"([^"]+)"', re.S)


def iter_files(root, pattern):
    for p in sorted(Path(root).rglob(pattern)):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file():
            yield p


def count_args(argstr):
    if not argstr or not argstr.strip():
        return 0
    depth = 0
    n = 1
    for ch in argstr:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch == "," and depth == 0:
            n += 1
    return n


# ---------------------------------------------------------------- Elixir ---


def scan_elixir(repo):
    modules = []
    versions = {}
    for path in iter_files(repo, "mix.exs"):
        vm = ELIXIR_VERSION.search(path.read_text(errors="replace"))
        if vm:
            val = vm.group(1) or vm.group(2)
            versions[str(path.relative_to(repo))] = val
    for path in iter_files(repo, "*.ex"):
        if path.name == "mix.exs":
            continue
        rel = str(path.relative_to(repo))
        text = path.read_text(errors="replace")
        lines = [re.sub(r"#.*$", "", ln) for ln in text.splitlines()]
        depth = 0
        stack = []  # (module_dict, depth_at_open)
        pending_doc = None
        pending_spec = None
        for line in lines:
            mod = ELIXIR_MODULE.search(line)
            if mod:
                stack.append(({"name": mod.group(1), "items": []}, depth))
            do_n = len(re.findall(r"\bdo\b", line))
            end_n = len(re.findall(r"\bend\b", line))
            depth += do_n - end_n
            while stack and depth < stack[-1][1]:
                done = stack.pop()[0]
                modules.append({"name": done["name"], "file": rel, "items": done["items"]})
            if not stack:
                pending_doc = pending_spec = None
                continue
            cur = stack[-1][0]
            docm = ELIXIR_DOC_LINE.search(line)
            if docm:
                pending_doc = docm.group(1)
                continue
            hd = re.search(r'@\s*doc\s+"""', line)
            if hd:
                start = lines.index(line)
                body = []
                for ln2 in lines[start + 1:]:
                    if '"""' in ln2:
                        break
                    body.append(ln2)
                pending_doc = next((b.strip() for b in body if b.strip()), "")
                continue
            if " @spec " in line or line.startswith("@spec"):
                pending_spec = line.split(None, 1)[1].strip() if " " in line.strip() else ""
            fm = ELIXIR_DEF.match(line)
            if fm:
                args = fm.group(2) or ""
                arity = count_args(args[1:-1] if args else "")
                item = {
                    "kind": "function",
                    "ident": fm.group(1),
                    "signature": fm.group(1) + "/" + str(arity),
                    "doc": pending_doc or "",
                }
                if pending_spec:
                    item["spec"] = pending_spec
                cur["items"].append(item)
                pending_doc = None
                pending_spec = None
            if re.search(r"\buse\s+Ash\.Resource\b", line):
                tail = "\n".join(lines[lines.index(line):])
                ash = {}
                for bm in ASH_BLOCK.finditer(tail):
                    kind = bm.group(1)
                    body = bm.group(2)
                    if kind == "attributes":
                        entries = [":" + a for a in ASH_ATTR.findall(body)]
                    else:
                        entries = [k + ":" + n for k, n in ASH_ACTION.findall(body)]
                    ash[kind] = entries
                cur["items"].append({
                    "kind": "ash_resource",
                    "ident": cur["name"],
                    "signature": "",
                    "doc": "",
                    "invariants": ash,
                })
        while stack:
            done = stack.pop()[0]
            modules.append({"name": done["name"], "file": rel, "items": done["items"]})
    return modules, versions


# ------------------------------------------------------------------ Rust ---


def scan_rust(repo):
    modules = []
    versions = {}
    crate_roots = []
    ws = repo / "Cargo.toml"
    is_ws = ws.exists() and "members" in ws.read_text(errors="replace")
    if is_ws:
        for cargo in iter_files(repo, "Cargo.toml"):
            if (cargo.parent / "src").is_dir():
                crate_roots.append(cargo.parent)
    elif (repo / "src").is_dir():
        crate_roots.append(repo)
    ws_ver = None
    if ws.exists():
        wmt = ws.read_text(errors="replace")
        m = CARGO_WS_VERSION.search(wmt)
        ws_ver = m.group(1) if m else None
    for crate in crate_roots:
        cargo = crate / "Cargo.toml"
        name = crate.name
        ver = ws_ver
        if cargo.exists():
            ct = cargo.read_text(errors="replace")
            pm = CARGO_PACKAGE.search(ct)
            vm = CARGO_VERSION.search(ct)
            if pm:
                name = pm.group(1)
            if vm:
                ver = vm.group(1)
        if name and ver:
            versions[name] = ver
        for path in iter_files(crate, "*.rs"):
            rel = str(path.relative_to(repo))
            text = path.read_text(errors="replace")
            text = re.sub(r"//[^\n]*", "", text)  # strip line comments
            text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
            items = []
            for m in RUST_FN.finditer(text):
                items.append({
                    "kind": "function",
                    "ident": m.group(1),
                    "signature": m.group(1) + m.group(2),
                })
            for m in RUST_ITEM.finditer(text):
                items.append({"kind": m.group(1).lower(), "ident": m.group(2), "signature": ""})
            seen = set()
            uniq = []
            for it in items:
                key = (it["kind"], it["ident"])
                if key not in seen:
                    seen.add(key)
                    uniq.append(it)
            if uniq:
                modules.append({"name": rel, "file": rel, "items": uniq})
    return modules, versions


# ------------------------------------------------------------ Node/Python ---


def scan_node(repo):
    modules = []
    versions = {}
    for pj in iter_files(repo, "package.json"):
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


def scan_python(repo):
    modules = []
    for path in iter_files(repo, "*.py"):
        rel = str(path.relative_to(repo))
        try:
            tree = ast.parse(path.read_text(errors="replace"))
        except SyntaxError:
            continue
        items = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                items.append({"kind": "class", "ident": node.name, "signature": "class " + node.name})
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                try:
                    sig = node.name + ast.unparse(node.args)
                except Exception:
                    sig = node.name
                items.append({"kind": "function", "ident": node.name, "signature": sig})
        if items:
            modules.append({"name": rel, "file": rel, "items": uniq_items(items)})
    return modules, {}


def uniq_items(items):
    seen = set()
    out = []
    for it in items:
        key = (it["kind"], it["ident"])
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out


# ------------------------------------------------------------- code mode ---


def extract_code(repo):
    repo = Path(repo)
    modules = []
    versions = {}
    if (repo / "mix.exs").exists() or next(iter_files(repo, "mix.exs"), None):
        m, v = scan_elixir(repo)
        modules += m
        versions.update(v)
    if (repo / "Cargo.toml").exists():
        m, v = scan_rust(repo)
        modules += m
        versions.update(v)
    if next(iter_files(repo, "package.json"), None):
        m, v = scan_node(repo)
        modules += m
        versions.update(v)
    if (repo / "pyproject.toml").exists() or (repo / "setup.py").exists():
        m, v = scan_python(repo)
        modules += m
        versions.update(v)
    modules.sort(key=lambda x: x["name"])
    return {"repo": repo.name, "path": str(repo), "version": versions, "modules": modules}


# --------------------------------------------------------------- doc mode ---


def known_symbols(surface):
    syms = set()
    for mod in surface["modules"]:
        name = mod["name"]
        if name and name[0].isupper():
            syms.add(name.split(".")[-1])
        for it in mod["items"]:
            syms.add(it["ident"])
            sig = it.get("signature", "")
            if "/" in sig:
                syms.add(sig)
    return syms


def match_span(span, syms):
    span = span.strip()
    if span in syms:
        return span
    if span.startswith("--"):
        return span
    base = span.split("/")[0]
    if base in syms:
        return span
    last = span.split(".")[-1].split("::")[-1].strip("()")
    if last in syms:
        return span
    return None


HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
INLINE_SPAN = re.compile(r"`([^`\n]+)`")
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)


def extract_doc(repo, surface, docs_dirs=None):
    repo = Path(repo)
    syms = known_symbols(surface)
    module_names = {m["name"] for m in surface["modules"] if m["name"] and m["name"][0].isupper()}
    claims = []
    if docs_dirs:
        roots = [Path(d) for d in docs_dirs]
    else:
        roots = [d for d in [repo / "docs", repo / "book"] if d.is_dir()] or [repo]
    for root in roots:
        for path in iter_files(root, "*.md"):
            text = path.read_text(errors="replace")
            rel = str(path.relative_to(repo))
            fences = [(m.group(1), m.group(2)) for m in FENCE.finditer(text)]
            prose = FENCE.sub("", text)
            section = None
            for line in prose.splitlines():
                hm = HEADING.match(line)
                if hm:
                    section = hm.group(2).strip()
                for sm in INLINE_SPAN.finditer(line):
                    hit = match_span(sm.group(1), syms)
                    if hit:
                        claims.append({
                            "subject": rel + "#" + section if section else rel,
                            "predicate": "mentions",
                            "object": hit,
                            "kind": "inline_span",
                        })
            for lang, block in fences:
                hits = sorted({
                    mn.split(".")[-1] for mn in module_names
                    if re.search(r"\b" + re.escape(mn.split(".")[-1]) + r"\b", block)
                })
                if hits:
                    claims.append({
                        "subject": rel,
                        "predicate": "references_block",
                        "object": hits[0],
                        "kind": "fenced:" + (lang or "text"),
                    })
            header = None
            for line in text.splitlines():
                if line.strip().startswith("|"):
                    cells = [c.strip() for c in line.strip().strip("|").split("|")]
                    if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                        continue
                    low = [c.lower() for c in cells]
                    if any("param" in c for c in low) and any("default" in c for c in low):
                        header = cells
                        continue
                    if header:
                        try:
                            pi = next(i for i, c in enumerate(header) if "param" in c.lower())
                            di = next(i for i, c in enumerate(header) if "default" in c.lower())
                        except StopIteration:
                            header = None
                            continue
                        if pi < len(cells) and di < len(cells):
                            claims.append({
                                "subject": rel,
                                "predicate": "has_param",
                                "object": {"param": cells[pi], "default": cells[di]},
                                "kind": "param_table",
                            })
                else:
                    header = None
    claims.sort(key=lambda c: (c["subject"], c["predicate"], json.dumps(c["object"], sort_keys=True)))
    return {"repo": repo.name, "doc_roots": [str(r) for r in roots], "claims": claims}


# ------------------------------------------------------------------- CLI ---


def main(argv):
    if len(argv) < 2 or argv[0] not in ("code", "doc"):
        print(__doc__, file=sys.stderr)
        return 2
    mode, repo = argv[0], Path(argv[1])
    if not repo.is_dir():
        print("error: " + str(repo) + " is not a directory", file=sys.stderr)
        return 2
    if mode == "code":
        json.dump(extract_code(repo), sys.stdout, indent=2, sort_keys=True)
        print()
        return 0
    code_json = None
    docs_dirs = None
    args = argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--code-json":
            code_json = json.loads(Path(args[i + 1]).read_text())
            i += 2
        else:
            if args[i] == "--docs-dir":
                docs_dirs = args[i + 1].split(",")
            i += 1
    if code_json is None:
        code_json = extract_code(repo)
    json.dump(extract_doc(repo, code_json, docs_dirs), sys.stdout, indent=2, sort_keys=True)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
