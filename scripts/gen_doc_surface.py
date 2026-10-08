#!/usr/bin/env python3
"""gen_doc_surface.py - deterministic code/doc fact extractor (doc-hdit v1).

v1 is a rigorous deterministic symbol scanner (stdlib only: regex + ast).
tree-sitter/oxigraph is the v2 path; see scripts/doc_surface_conventions.md
for scope and disclosed limits.

Usage:
  gen_doc_surface.py code REPO [--engine auto|ts|regex]
  gen_doc_surface.py doc REPO [--code-json FILE] [--docs-dir DIR1,DIR2]

Engines: `auto` (default) uses the optional tree-sitter path when the
packages in scripts/requirements-doc-surface-ts.txt are importable and
falls back to the stdlib regex scanner otherwise (zero behavior change
without the dependency); `ts`/`regex` force one path explicitly.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

# ------------------------------------------------- optional tree-sitter v2 ---
# OPTIONAL acceleration only: the regex scanner below is the default surface
# when these imports fail. tree-sitter adds full-signature fidelity (return
# types, struct fields, doc comments) the regex path cannot recover.
try:
    from tree_sitter import Language, Parser

    import tree_sitter_elixir as _ts_elixir
    import tree_sitter_rust as _ts_rust

    TS_AVAILABLE = True
    TS_IMPORT_ERROR = None
except ImportError as _exc:  # pragma: no cover - exercised via engine=regex
    TS_AVAILABLE = False
    TS_IMPORT_ERROR = _exc

SKIP_DIRS = {"deps", "_build", "node_modules", "target", ".git", ".venv", "priv"}

ELIXIR_MODULE = re.compile(r"defmodule\s+([A-Z][A-Za-z0-9._]*)\s+do")
ELIXIR_DEF = re.compile(
    r"^\s*def(p|macrop|guardp)?\s+([a-z_][a-zA-Z0-9_?!]*)\s*(\()?"
)


def def_head_args(lines, i):
    """Balanced-paren capture of a def head argument list across newlines.

    Joins lines from index ``i`` until the paren opened after the function
    name closes, and returns ``(args_inner, next_i)`` where ``args_inner`` is
    the text between the outer parens and ``next_i`` is the index of the line
    holding the closing paren (scanning resumes there).
    """
    buf = lines[i]
    open_idx = buf.find("(")
    j = i
    while open_idx == -1 and j + 1 < len(lines):
        j += 1
        buf += "\n" + lines[j]
        open_idx = buf.find("(")
    if open_idx == -1:
        return None, i  # headless def (e.g. `def foo`) — zero arity
    depth = 0
    close_idx = -1
    for k in range(open_idx, len(buf)):
        ch = buf[k]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
            if depth == 0:
                close_idx = k
                break
    while close_idx == -1 and j + 1 < len(lines):
        j += 1
        prev_len = len(buf)
        buf += "\n" + lines[j]
        for k in range(prev_len + 1, len(buf)):
            ch = buf[k]
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if depth == 0:
                    close_idx = k
                    break
    if close_idx == -1:
        return None, i
    return buf[open_idx + 1:close_idx], j
ELIXIR_SPEC = re.compile(r"^\s*@\s*spec\s+(.+)$")
ELIXIR_VERSION = re.compile(r'@version\s+"([^"]+)"|@?\s*version\s*:\s*"([^"]+)"')
ELIXIR_DOC_LINE = re.compile(r"@\s*doc\s+(false|true)?\s*$")
HEREDOC = re.compile(r'@\s*doc\s+"""(.*?)"""', re.S)
ASH_BLOCK = re.compile(r"\b(attributes|actions)\s+do(.*?)\bend\b", re.S)
ASH_ATTR = re.compile(r"^\s*\w+\s+:([a-z_][a-zA-Z0-9_]*)", re.M)
# Phoenix router verb calls: `post("/execution/runs", ...)`, `get "/health"`.
ROUTE = re.compile(r'\b(get|post|put|patch|delete|live)\s*\(\s*"(/[^"]*)"')
ROUTE_BARE = re.compile(r'\b(get|post|put|patch|delete|live)\s+"(/[^"]*)"')
ASH_ACTION = re.compile(r"^\s*(read|create|update|destroy|action)\s+:([a-z_][a-zA-Z0-9_]*)", re.M)

RUST_FN = re.compile(
    r"\bpub\s+(?:const\s+)?(?:unsafe\s+)?(?:async\s+)?fn\s+"
    r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(\([^)]*\))",
)
RUST_ITEM = re.compile(r"\bpub\s+(struct|enum|trait)\s+([A-Z][A-Za-z0-9_]*)")
ELIXIR_DEFSTRUCT = re.compile(r"^\s*defstruct\s+(.+)$")
ELIXIR_TYPE = re.compile(r"^\s*@(type|typep)\s+([a-z_][a-zA-Z0-9_]*)\s*::\s*(.*)$")
ELIXIR_TYPE_CONT = re.compile(r"^\s*\|\s*(.+)$")
CARGO_PACKAGE = re.compile(r'\[package\][^\[]{0,600}?name\s*=\s*"([^"]+)"', re.S)
CARGO_VERSION = re.compile(r'\[package\][^\[]{0,600}?version\s*=\s*"([^"]+)"', re.S)
CARGO_WS_VERSION = re.compile(r'\[workspace\.package\][^\[]{0,600}?version\s*=\s*"([^"]+)"', re.S)
CARGO_DEP = re.compile(r'\[dependencies\]([^\[]*)', re.S)
CARGO_DEP_NAME = re.compile(r'^([a-zA-Z0-9_-]+)\s*=', re.M)
MIX_DEP = re.compile(r'\{:\s*([a-z_][a-zA-Z0-9_]*)\s*,')
MIX_DEP_BARE = re.compile(r'^\s*:([a-z_][a-zA-Z0-9_]*)\s*[,}]', re.M)


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


def dedup_clauses(items):
    """One item per (kind, ident, signature) with the clause count noted.

    Elixir heads may have many clauses (`from_map/2` x N); the surface emits
    a single item carrying ``clauses: N`` instead of N duplicates.
    """
    counts = {}
    order = []
    for it in items:
        key = (it["kind"], it["ident"], it.get("signature", ""))
        if key not in counts:
            counts[key] = 0
            order.append(it)
        counts[key] += 1
    out = []
    for it in order:
        n = counts[(it["kind"], it["ident"], it.get("signature", ""))]
        if n > 1:
            it = dict(it)
            it["clauses"] = n
        out.append(it)
    return out


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
        is_router = "router" in path.name.lower()
        i = 0
        while i < len(lines):
            line = lines[i]
            i += 1
            mod = ELIXIR_MODULE.search(line)
            if mod:
                stack.append(({"name": mod.group(1), "items": []}, depth))
            do_n = len(re.findall(r"\bdo\b", line))
            end_n = len(re.findall(r"\bend\b", line))
            depth += do_n - end_n
            while stack and depth < stack[-1][1]:
                done = stack.pop()[0]
                modules.append({
                    "name": done["name"],
                    "file": rel,
                    "is_public": True,
                    "items": dedup_clauses(done["items"]),
                })
            if not stack:
                pending_doc = pending_spec = None
                continue
            cur = stack[-1][0]
            if is_router:
                rm = ROUTE.search(line) or ROUTE_BARE.search(line)
                if rm:
                    rpath = rm.group(2).strip("/")
                    if rpath:
                        cur["items"].append({
                            "kind": "route",
                            "ident": rpath,
                            "signature": rm.group(1) + " /" + rpath,
                            "doc": "",
                            "is_public": True,
                        })
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
            tm = ELIXIR_TYPE.match(line)
            if tm and stack:
                tname, tbody = tm.group(2), tm.group(3).strip()
                # `@type t :: ...` unions often continue with `| ...` lines.
                while i < len(lines):
                    cm = ELIXIR_TYPE_CONT.match(lines[i])
                    if cm is None:
                        break
                    tbody += " | " + cm.group(1).strip()
                    i += 1
                if not tbody.strip():
                    continue
                cur["items"].append({
                    "kind": "type",
                    "ident": tname,
                    "signature": "@type " + tname + " :: " + " ".join(tbody.split()),
                    "doc": "",
                    "is_public": True,
                })
            dm = ELIXIR_DEFSTRUCT.match(line)
            if dm and stack:
                body = dm.group(1).strip()
                if body.startswith("[") and "]" not in body:
                    while i < len(lines) and "]" not in body:
                        body += " " + lines[i].strip()
                        i += 1
                fields = []
                for f in split_top(body.strip("[]")):
                    f = f.strip()
                    if f.startswith(":"):
                        fields.append(f[1:])
                    elif re.match(r"^[a-z_]", f):
                        fields.append(f)
                if fields:
                    cur["items"].append({
                        "kind": "struct",
                        "ident": cur["name"],
                        "signature": "defstruct " + ", ".join(fields),
                        "doc": pending_doc or "",
                        "is_public": True,
                    })
                pending_doc = None
            fm = ELIXIR_DEF.match(line)
            if fm:
                args_inner, close_i = def_head_args(lines, i - 1)
                if close_i > i - 1:
                    i = close_i + 1
                arity = count_args(args_inner or "")
                # Private forms (defp/defmacrop/defguardp) are internal
                # implementation, never the public code surface: excluded
                # from emission entirely, not merely flagged.
                if fm.group(1):
                    pending_doc = pending_spec = None
                    continue
                # P2 scope: an item is public iff it is not a private form
                # and not `@doc false`.
                is_public = pending_doc != "false"
                item = {
                    "kind": "function",
                    "ident": fm.group(2),
                    "signature": fm.group(2) + "/" + str(arity),
                    "doc": pending_doc or "",
                    "is_public": bool(is_public),
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
                    "is_public": True,
                    "invariants": ash,
                })
        while stack:
            done = stack.pop()[0]
            modules.append({
                "name": done["name"],
                "file": rel,
                "is_public": True,
                "items": dedup_clauses(done["items"]),
            })
    return modules, versions


# ------------------------------------------------------------------ Rust ---


def brace_body(text, i):
    """Return the balanced `{...}` body following index i, or None.

    Guards: if a `;` appears before the opening brace the construct was
    bodiless (unit struct / trait method stub) and the next `{` belongs to
    something else — refuse rather than over-capture.
    """
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


def paren_body(text, i):
    """Return the balanced `(...)` body following index i, or None."""
    j = text.find("(", i)
    if j == -1 or ";" in text[i:j] or "{" in text[i:j]:
        return None
    depth = 0
    for k in range(j, len(text)):
        ch = text[k]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[j + 1:k]
    return None


def split_top(s):
    """Split on top-level commas (depth-aware over <> () [])."""
    parts, cur, depth = [], [], 0
    for ch in s:
        if ch in "<([":
            depth += 1
            cur.append(ch)
        elif ch in ">)]":
            depth = max(0, depth - 1)
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p.strip() for p in parts if p.strip()]


def rust_type_signature(kind, ident, text, i):
    """Populate struct/enum signatures: `Name { field: Type, ... }` /
    `Name { Variant, ... }`. Returns "" when no body can be recovered.
    Traits are out of scope (method bodies are not field signatures)."""
    if kind not in ("struct", "enum"):
        return ""
    body = brace_body(text, i)
    if body is None and kind == "struct":
        body = paren_body(text, i)  # tuple struct: pub struct Foo(pub A, B);
    if body is None:
        return ""
    members = split_top(body)
    if not members:
        return ident
    return ident + " { " + ", ".join(" ".join(m.split()) for m in members) + " }"


def rust_crate_roots(repo):
    """Yield (crate_dir, crate_name, version) for every rust crate in repo."""
    ws = repo / "Cargo.toml"
    is_ws = ws.exists() and "members" in ws.read_text(errors="replace")
    if is_ws:
        crate_roots = [
            cargo.parent for cargo in iter_files(repo, "Cargo.toml")
            if (cargo.parent / "src").is_dir()
        ]
    elif (repo / "src").is_dir():
        crate_roots = [repo]
    else:
        crate_roots = []
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
        yield crate, name, ver


def scan_rust(repo):
    modules = []
    versions = {}
    for crate, name, ver in rust_crate_roots(repo):
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
                    "is_public": True,
                })
            for m in RUST_ITEM.finditer(text):
                items.append({
                    "kind": m.group(1).lower(),
                    "ident": m.group(2),
                    "signature": rust_type_signature(
                        m.group(1).lower(), m.group(2), text, m.end()
                    ),
                    "is_public": True,
                })
            seen = set()
            uniq = []
            for it in items:
                key = (it["kind"], it["ident"])
                if key not in seen:
                    seen.add(key)
                    uniq.append(it)
            if uniq:
                # P2 scope: a Rust file module is public/documented iff it is
                # part of the shipped crate surface — not tests, benches,
                # examples, or binaries.
                parts = path.parts
                is_public = not any(
                    p in ("tests", "benches", "examples", "bin") for p in parts
                )
                modules.append({
                    "name": rel,
                    "file": rel,
                    "is_public": is_public,
                    "items": uniq,
                })
    return modules, versions


# --------------------------------------------- optional tree-sitter scanner ---
# v2 fidelity path (doc-hdit): same JSON schema as the regex scanners above,
# richer signatures. Regex-path extras that depend on ad hoc heuristics
# (Phoenix router verbs, Ash resource blocks) are regex-only and simply
# absent from the TS elixir surface; ident parity holds for def/type/struct.
#
# tree-sitter node API (0.23+): node.type, node.text, node.children,
# child_by_field_name, prev_sibling. Parsers are built lazily and cached.

_TS_PARSERS = {}


def _ts_parser(lang_mod):
    key = lang_mod.__name__
    if key not in _TS_PARSERS:
        _TS_PARSERS[key] = Parser(Language(lang_mod.language()))
    return _TS_PARSERS[key]


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


def _first_child(node, *types):
    for child in node.children:
        if child.type in types:
            return child
    return None


def _clean(text):
    """Whitespace-normalize and strip comments from a captured span."""
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"#(?!\{)[^\n]*", "", text)  # elixir comments, not #{}
    return " ".join(text.split())


def _rust_pub(node):
    vis = _first_child(node, "visibility_modifier")
    only = vis is not None and vis.text == b"pub"
    return only


def _rust_doc(node):
    """Concatenated `///` doc lines preceding an item ('' if none)."""
    lines = []
    prev = node.prev_sibling
    while prev is not None and prev.type == "line_comment":
        if not prev.text.startswith(b"///"):
            break
        lines.append(prev.text.decode().lstrip("/").strip())
        prev = prev.prev_sibling
    return "\n".join(reversed(lines))


def scan_rust_ts(repo):
    modules = []
    versions = {}
    for crate, name, ver in rust_crate_roots(repo):
        if name and ver:
            versions[name] = ver
        for path in iter_files(crate, "*.rs"):
            rel = str(path.relative_to(repo))
            tree = _ts_parser(_ts_rust).parse(path.read_bytes())
            items = []
            for node in _walk(tree.root_node):
                if node.type in ("function_item", "function_signature_item"):
                    if not _rust_pub(node):
                        continue
                    fname = node.child_by_field_name("name").text.decode()
                    params = node.child_by_field_name("parameters").text.decode()
                    ret_node = node.child_by_field_name("return_type")
                    sig = _clean(fname + params)
                    if ret_node is not None:
                        sig += " -> " + _clean(ret_node.text.decode())
                    items.append({
                        "kind": "function",
                        "ident": fname,
                        "signature": sig,
                        "doc": _rust_doc(node),
                        "is_public": True,
                    })
                elif node.type == "struct_item":
                    if not _rust_pub(node):
                        continue
                    sname = node.child_by_field_name("name").text.decode()
                    body = node.child_by_field_name("body")
                    sig = sname
                    if body is not None:
                        members = split_top(_clean(
                            body.text.decode().strip("{}()")))
                        if members:
                            sig = sname + " { " + ", ".join(members) + " }"
                    items.append({
                        "kind": "struct",
                        "ident": sname,
                        "signature": sig,
                        "doc": _rust_doc(node),
                        "is_public": True,
                    })
                elif node.type == "enum_item":
                    if not _rust_pub(node):
                        continue
                    ename = node.child_by_field_name("name").text.decode()
                    body = node.child_by_field_name("body")
                    sig = ename
                    if body is not None:
                        variants = split_top(_clean(
                            body.text.decode().strip("{}")))
                        if variants:
                            sig = ename + " { " + ", ".join(variants) + " }"
                    items.append({
                        "kind": "enum",
                        "ident": ename,
                        "signature": sig,
                        "doc": _rust_doc(node),
                        "is_public": True,
                    })
                elif node.type == "trait_item":
                    if not _rust_pub(node):
                        continue
                    tname = node.child_by_field_name("name").text.decode()
                    items.append({
                        "kind": "trait",
                        "ident": tname,
                        "signature": "",
                        "doc": _rust_doc(node),
                        "is_public": True,
                    })
            if items:
                parts = path.parts
                is_public = not any(
                    p in ("tests", "benches", "examples", "bin") for p in parts
                )
                modules.append({
                    "name": rel,
                    "file": rel,
                    "is_public": is_public,
                    "items": uniq_items(items),
                })
    return modules, versions


def _ex_args(call):
    return _first_child(call, "arguments")


def _ex_target(call):
    return call.children[0].text.decode()


def _ex_quoted(node):
    """First non-empty line of the first quoted_content under `node`."""
    for sub in _walk(node):
        if sub.type == "quoted_content":
            for line in sub.text.decode().splitlines():
                line = line.strip()
                if line:
                    return line
    return ""


def scan_elixir_ts(repo):
    modules = []
    versions = {}
    for path in iter_files(repo, "mix.exs"):
        vm = ELIXIR_VERSION.search(path.read_text(errors="replace"))
        if vm:
            val = vm.group(1) or vm.group(2)
            versions[str(path.relative_to(repo))] = val

    def emit(name, items, rel):
        modules.append({
            "name": name,
            "file": rel,
            "is_public": True,
            "items": dedup_clauses(items),
        })

    def collect(node, mod_name, rel, items):
        """Recurse through do_block bodies tracking the innermost module."""
        for child in node.children:
            cur = child
            if cur.type == "unary_operator":
                # `@type t :: ...` — attribute call in unary form
                inner = cur.children[1] if len(cur.children) > 1 else None
                if inner is not None and inner.type == "call" and \
                        _ex_target(inner) in ("type", "typep"):
                    targs = _ex_args(inner)
                    if targs is None:
                        continue
                    text = " ".join(targs.text.decode().split())
                    if "::" not in text:
                        continue
                    tname, tbody = text.split("::", 1)
                    items.append({
                        "kind": "type",
                        "ident": tname.strip(),
                        "signature": "@type " + tname.strip() + " :: " + tbody.strip(),
                        "doc": "",
                        "is_public": True,
                    })
                continue
            if cur.type != "call":
                continue
            target = _ex_target(cur)
            do = _first_child(cur, "do_block")
            if target == "defmodule":
                args = _ex_args(cur)
                alias = _first_child(args, "alias")
                sub = alias.text.decode() if alias is not None else cur.text.decode()
                items_out = []
                if do is not None:
                    body = _first_child(do, "body") or do
                    collect(body, sub, rel, items_out)
                if items_out:
                    pending.append((sub, items_out))
                continue
            if do is not None and target not in ("def", "defp", "defstruct"):
                # a non-def call with its own do_block (e.g. `for ... do`)
                # may contain nested defs; recurse, keep module scope
                body = _first_child(do, "body") or do
                collect(body, mod_name, rel, items)
                continue
            if target in ("def", "defp", "defmacrop", "defguardp", "defmacro"):
                args = _ex_args(cur)
                head = _first_child(args, "call")
                if head is None:
                    continue
                hname = head.children[0].text.decode()
                hargs = _ex_args(head)
                arity = count_args(hargs.text.decode().strip("()")) if hargs else 0
                if target != "def":
                    continue
                item = {
                    "kind": "function",
                    "ident": hname,
                    "signature": hname + "/" + str(arity),
                    "doc": "",
                    "is_public": True,
                }
                attrs = _ex_prev_attrs(cur)
                doc = attrs.get("doc")
                if doc == "false":
                    item["is_public"] = False
                elif doc:
                    item["doc"] = doc
                if attrs.get("spec"):
                    item["spec"] = attrs["spec"]
                items.append(item)
            elif target == "defstruct":
                args = _ex_args(cur)
                body = args.text.decode().strip("[]") if args is not None else ""
                fields = []
                for f in split_top(body):
                    f = f.strip()
                    if f.startswith(":"):
                        fields.append(f[1:])
                    elif re.match(r"^[a-z_]", f):
                        fields.append(f)
                if fields:
                    items.append({
                        "kind": "struct",
                        "ident": mod_name,
                        "signature": "defstruct " + ", ".join(fields),
                        "doc": "",
                        "is_public": True,
                    })
            elif target in ("type", "typep"):
                args = _ex_args(cur)
                if args is None:
                    continue
                text = " ".join(args.text.decode().split())
                if "::" not in text:
                    continue
                tname, tbody = text.split("::", 1)
                items.append({
                    "kind": "type",
                    "ident": tname.strip(),
                    "signature": "@type " + tname.strip() + " :: " + tbody.strip(),
                    "doc": "",
                    "is_public": True,
                })

    def _ex_prev_attrs(call_node):
        """{attr: text} for the `@attr ...` run immediately before a def."""
        attrs = {}
        prev = call_node.prev_sibling
        while prev is not None and prev.type == "unary_operator":
            inner = prev.children[1] if len(prev.children) > 1 else None
            if inner is None or inner.type != "call":
                break
            attr = _ex_target(inner)
            if attr not in ("doc", "spec"):
                break
            args = _ex_args(inner)
            if args is None:
                attrs[attr] = "true"
            elif attr == "doc":
                text = args.text.decode().strip()
                attrs[attr] = (
                    "false" if text == "false"
                    else "true" if text == "true"
                    else _ex_quoted(inner)
                )
            else:
                attrs[attr] = _clean(args.text.decode())
            prev = prev.prev_sibling
        return attrs

    for path in iter_files(repo, "*.ex"):
        if path.name == "mix.exs":
            continue
        rel = str(path.relative_to(repo))
        pending = []
        tree = _ts_parser(_ts_elixir).parse(path.read_bytes())
        collect(tree.root_node, None, rel, [])
        for name, items in pending:
            emit(name, items, rel)
    return modules, versions


# ------------------------------------------------------ external allowlist ---
    return "".join(p.capitalize() for p in dep.split("_"))


def known_external(repo):
    """Module prefixes of documented external dependencies (P2 allowlist).

    Elixir deps (`{:ash, ...}`) -> `Ash.`, Rust deps (`serde_json = ...`) ->
    `serde_json::`. Claims referencing these prefixes resolve against the
    dependency's own documentation, not the repo's code surface.
    """
    prefixes = set()
    for path in iter_files(repo, "mix.exs"):
        text = path.read_text(errors="replace")
        for m in MIX_DEP.finditer(text):
            prefixes.add(camelize(m.group(1)) + ".")
        for m in MIX_DEP_BARE.finditer(text):
            prefixes.add(camelize(m.group(1)) + ".")
    for cargo in iter_files(repo, "Cargo.toml"):
        text = cargo.read_text(errors="replace")
        for sec in CARGO_DEP.finditer(text):
            for m in CARGO_DEP_NAME.finditer(sec.group(1)):
                prefixes.add(m.group(1) + "::")
    return sorted(prefixes)


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
            modules.append({
                "name": data.get("name", rel),
                "file": rel,
                "is_public": True,
                "items": items,
            })
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
                items.append({
                    "kind": "class",
                    "ident": node.name,
                    "signature": "class " + node.name,
                    "is_public": not node.name.startswith("_"),
                })
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name.startswith("_") and not node.name.startswith("__"):
                    continue
                try:
                    sig = node.name + ast.unparse(node.args)
                except Exception:
                    sig = node.name
                items.append({
                    "kind": "function",
                    "ident": node.name,
                    "signature": sig,
                    "is_public": not node.name.startswith("_"),
                })
        if items:
            modules.append({
                "name": rel,
                "file": rel,
                "is_public": True,
                "items": uniq_items(items),
            })
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


def extract_directories(repo):
    """All repo directories (relative paths, sorted) minus build/hidden dirs.

    Emitted as a top-level `directories` array in code mode: the audit core
    checks trailing-slash doc references (`receipts/engine_ops/`) against it
    by exact membership — directory existence, never fuzzy matching.
    """
    dirs = set()
    for p in Path(repo).rglob("*"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if any(part.startswith(".") for part in p.parts):
            continue
        if p.is_dir():
            dirs.add(str(p.relative_to(repo)))
    return sorted(dirs)


# ------------------------------------------------------------- code mode ---


def extract_code(repo, engine="auto"):
    repo = Path(repo)
    if engine == "auto":
        engine = "ts" if TS_AVAILABLE else "regex"
    if engine == "ts" and not TS_AVAILABLE:
        raise RuntimeError(
            "engine=ts requested but tree-sitter is not importable "
            "(install scripts/requirements-doc-surface-ts.txt): "
            + str(TS_IMPORT_ERROR)
        )
    use_ts = engine == "ts"
    modules = []
    versions = {}
    if (repo / "mix.exs").exists() or next(iter_files(repo, "mix.exs"), None):
        m, v = scan_elixir_ts(repo) if use_ts else scan_elixir(repo)
        modules += m
        versions.update(v)
    if (repo / "Cargo.toml").exists():
        m, v = scan_rust_ts(repo) if use_ts else scan_rust(repo)
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
    return {
        "repo": repo.name,
        "path": str(repo),
        "version": versions,
        "known_external": known_external(repo),
        "directories": extract_directories(repo),
        "modules": modules,
    }


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


# v2 over-extraction filter: backticked spans that are CLI flags, version
# strings, boolean-ish single words, or too-short tokens are prose artifacts,
# not code-surface symbol references (DOC-HDIT-PILOT P1). P3 extends the
# filter to path fragments and version-tagged paths (`release/v26.8.23`,
# `stream/metrics.ex`, `stage/{id}.jsonl`) — the residual classes from the P2
# receipt: these are not emitted as symbol claims at all.
VERSION_RE = re.compile(r"^v?\d+(\.\d+)+")
SOURCE_EXTS = (
    ".ex", ".exs", ".rs", ".py", ".ts", ".tsx", ".js", ".json", ".jsonl",
    ".toml", ".yaml", ".yml", ".md", ".ttl", ".sql", ".sh", ".wasm",
)
BOOLISH = {"true", "false", "yes", "no", "on", "off", "nil", "null", "ok", "valid", "enabled", "disabled"}


def looks_like_version(seg):
    t = seg.lstrip("vV")
    if not t or "." not in t:
        return False
    return all(p.isdigit() for p in t.split("."))


# `stream/ingest.ex:19`, `runtime.ex:64` — a source path plus a line number is
# a location pointer, not a symbol reference (DOC-HDIT-PILOT P4).
PATH_LINE_RE = re.compile(r"\.\w+:\d")


def is_noise_span(span):
    s = span.strip()
    if s.startswith("--"):                     # CLI flags: --json, --mode <auto|ff>
        return True
    if len(s) < 3:                             # <3-char tokens
        return True
    if VERSION_RE.match(s) or re.fullmatch(r"[0-9][0-9._]*", s):
        return True
    if PATH_LINE_RE.search(s):                 # path:line location pointers
        return True
    if s.lower() in BOOLISH:                   # boolean-ish single words
        return True
    if "/" in s:
        segs = s.split("/")
        # Version-tagged path fragments: `release/v26.8.23`.
        if any(looks_like_version(seg) for seg in segs):
            return True
        # Source-file path fragments: `stream/metrics.ex`, `stage/{id}.jsonl`.
        if len(segs) > 1 and segs[-1].rstrip(")").endswith(SOURCE_EXTS):
            return True
    return False


# `execute/4,5` — an arity list, not a single signature. The list form is
# resolved to its head `execute/4` (a real signature form) when that grounds;
# the raw comma-list span is never claimed as-is (DOC-HDIT-PILOT P4).
ARITY_LIST_RE = re.compile(r"^([A-Za-z0-9_.?!]+/\d+),(?:\d+(?:,\d+)*)$")


def match_span(span, syms):
    span = span.strip()
    if is_noise_span(span):
        return None
    if span in syms:
        return span
    m = ARITY_LIST_RE.match(span)
    if m and m.group(1) in syms:
        return m.group(1)
    base = span.split("/")[0]
    if base in syms:
        # Only return the whole span when it is identifier-shaped; a span
        # like `name/4,5` (arity list) or `path/file.ex:19` (location
        # pointer) is emitted as its matched identifier, never as raw
        # whole-span sentence text.
        if ARITY_LIST_RE.match(span) or PATH_LINE_RE.search(span):
            return base
        return span
    last = span.split(".")[-1].split("::")[-1].strip("()")
    if last in syms:
        return span
    return None


HEADING = re.compile(r"^(#{1,6})\s+(.*)$", re.M)
INLINE_SPAN = re.compile(r"`([^`\n]+)`")
FENCE = re.compile(r"```(\w*)\n(.*?)```", re.S)

# Scaffolded reference tables (markdown pipe tables of signatures) are claims
# too: each row that names a code-surface symbol in identifier, qualified, or
# arity form counts as a `mentions` claim (DOC-HDIT-PILOT P4). A symbol-shaped
# cell under a Function/Signature header that matches nothing on the surface is
# still a doc-level claim (`table_row_scaffold`) — the audit gate classifies it
# as a phantom, which is exactly the channel that should catch fabricated rows.
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*(/[0-9]+)?")


def cell_candidates(cell):
    """Candidate symbol spans inside a table cell: backticked spans first,
    else the whole cell stripped of backticks."""
    spans = INLINE_SPAN.findall(cell)
    if spans:
        return spans
    s = cell.replace("`", "").strip()
    return [s] if s else []


def table_claims(rel, header, cells, syms):
    header_low = [c.lower() for c in header] if header else []
    fi = next((i for i, c in enumerate(header_low)
               if "function" in c or "signature" in c), None)
    pi = next((i for i, c in enumerate(header_low) if "param" in c), None)
    di = next((i for i, c in enumerate(header_low) if "default" in c), None)

    out = []
    row_symbol = None
    scaffold_symbol = None
    for i, cell in enumerate(cells):
        in_sig_col = fi is not None and i == fi
        for cand in cell_candidates(cell):
            if not IDENT_RE.fullmatch(cand):
                # table cells are structured: only identifier/qualified/arity
                # forms are symbol claims (prose cells, paths, ranges excluded)
                continue
            hit = match_span(cand, syms)
            if hit:
                out.append({
                    "subject": rel,
                    "predicate": "mentions",
                    "object": hit,
                    "kind": "table_row",
                })
                if row_symbol is None:
                    row_symbol = hit
            elif in_sig_col and IDENT_RE.fullmatch(cand) and not is_noise_span(cand):
                out.append({
                    "subject": rel,
                    "predicate": "mentions",
                    "object": cand,
                    "kind": "table_row_scaffold",
                })
                if scaffold_symbol is None:
                    scaffold_symbol = cand
    sym = row_symbol or scaffold_symbol
    if sym is not None and pi is not None and pi < len(cells):
        # P4: the has_param object is the identifier itself (a code-surface
        # symbol string, groundable by the audit gate) — not a whole-cell
        # span and not a nested dict; parameter/default cell prose stays
        # unclaimed non-symbol text (DOC-HDIT-PILOT P4).
        out.append({
            "subject": rel,
            "predicate": "has_param",
            "object": sym,
            "kind": "param_table",
        })
    return out


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
            # markdown pipe tables: a header row is only a header when followed
            # by a `|---|` separator row; headerless generated tables (one `|`
            # row per blank-line-separated block) yield mentions from every
            # data row with header=None.
            table_block = []
            for line in text.splitlines() + [""]:
                if line.strip().startswith("|"):
                    table_block.append(line)
                    continue
                if table_block:
                    rows = []
                    seps = set()
                    for j, tl in enumerate(table_block):
                        cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                        if all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                            seps.add(j)
                            continue
                        rows.append((j, cells))
                    header = None
                    if (len(rows) >= 2 and rows[0][0] + 1 in seps
                            and rows[1][0] == rows[0][0] + 2):
                        header = rows.pop(0)[1]
                    for _, cells in rows:
                        claims.extend(table_claims(rel, header, cells, syms))
                    table_block = []
                # non-pipe line: block ended; header re-derived per block
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
        engine = "auto"
        args = argv[2:]
        i = 0
        while i < len(args):
            if args[i] == "--engine" and i + 1 < len(args):
                if args[i + 1] not in ("auto", "ts", "regex"):
                    print("error: --engine must be auto|ts|regex", file=sys.stderr)
                    return 2
                engine = args[i + 1]
                i += 2
            else:
                i += 1
        json.dump(extract_code(repo, engine), sys.stdout, indent=2, sort_keys=True)
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
