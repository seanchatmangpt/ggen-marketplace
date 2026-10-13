#!/usr/bin/env python3
"""Institutionalized doc link checker (R152).

Consolidates the three throwaway R148a/b/c /tmp checkers into one canonical
script. Walks a directory tree of Markdown files, extracts inline links
(`[text](target)`) and reference-style links, resolves relative targets
(including directory -> index.md and `.md` elision), verifies heading
anchors, and verifies image file existence. External schemes
(http/https/mailto/etc.) and pure-fragment links are skipped.

Output is a JSON report:

    {"root": ..., "files": N, "links": N, "broken": [
        {"file": ..., "target": ..., "reason": ...}]}

Exit 0 iff no broken links are found (exit 1 otherwise; exit 2 on usage
or root errors).

Usage:

    python3 scripts/check_doc_links.py --root docs/reference
    python3 scripts/check_doc_links.py --root docs > /tmp/links.json
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.parse

# Inline links: [text](target). Target may contain spaces if angle-wrapped:
# [text](<my file.md>) — handled by the ANGLE_RE alternative.
MD_RE = re.compile(r"\[[^\]]*\]\(<([^>]+)>\)")
MD_PLAIN_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# Reference definitions: [id]: target
REF_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(<[^>]+>|[^)\s]+)", re.M)
# Images share the same target syntax; existence is checked per-file.
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")

SKIP_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "file://",
    "ftp://",
    "tel:",
    "data:",
    "#",
)

# Extensions that exist as real files on disk (images, data, code).
FILE_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".json", ".toml", ".yaml", ".yml", ".ttl", ".sh",
    ".py", ".rs", ".ex", ".exs", ".txt", ".csv", ".md", ".markdown",
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def slugify_github(text: str) -> str:
    """GitHub-style heading anchor slug."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\- ]", "", s)  # drop punctuation, keep word chars/space/hyphen
    s = s.replace(" ", "-")
    return s


def iter_markdown_files(root: str):
    for dirpath, _dirnames, filenames in os.walk(root):
        # Skip hidden directories (e.g. .git).
        _dirnames[:] = [d for d in _dirnames if not d.startswith(".")]
        for fn in sorted(filenames):
            if fn.lower().endswith((".md", ".markdown")):
                yield os.path.join(dirpath, fn)


def read_text(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def extract_targets(text: str):
    """Yield raw link targets from a Markdown document."""
    # Strip fenced code blocks — links inside ``` fences are examples.
    stripped = re.sub(r"```.*?```", "", text, flags=re.S)
    # Strip inline code spans.
    stripped = re.sub(r"`[^`\n]*`", "", stripped)

    for m in MD_RE.finditer(stripped):
        yield m.group(1)
    # Remove angle-form matches before plain matching to avoid double-count.
    stripped = MD_RE.sub("", stripped)
    for m in MD_PLAIN_RE.finditer(stripped):
        yield m.group(1)
    for m in REF_DEF_RE.finditer(stripped):
        t = m.group(1)
        yield t[1:-1] if t.startswith("<") and t.endswith(">") else t
    for m in IMAGE_RE.finditer(stripped):
        yield m.group(1)


def anchor_exists(path: str, anchor: str) -> bool:
    try:
        text = read_text(path)
    except OSError:
        return False
    wanted = anchor.lower()
    for line in text.splitlines():
        m = HEADING_RE.match(line)
        if not m:
            continue
        if slugify_github(m.group(2)) == wanted:
            return True
    return False


def resolve_target(link_file: str, path_part: str, anchor: str = ""):
    """Resolve a relative target to an existing file, or None.

    Handles directory -> index.md, .md elision, and URL-encoded chars.
    Returns (resolved_path_or_None, exists_as_is_bool).
    """
    resolved = os.path.normpath(
        os.path.join(os.path.dirname(link_file), path_part)
    )
    # Exact file (covers non-.md suffixes and full .md names).
    if os.path.isfile(resolved):
        return resolved, True
    # .md elision: [x](./page) means page.md
    if os.path.isfile(resolved + ".md"):
        return resolved + ".md", True
    # Directory target: prefer index.md for anchor checks; a bare
    # directory link (no anchor) to an existing directory is valid.
    if os.path.isdir(resolved):
        idx = os.path.join(resolved, "index.md")
        if os.path.isfile(idx):
            return idx, True
        if not anchor:
            return resolved, True
        return None, False
    # No file found.
    return None, False


def check_root(root: str):
    files = list(iter_markdown_files(root))
    broken = []
    link_count = 0
    for f in files:
        text = read_text(f)
        for raw in extract_targets(text):
            target = urllib.parse.unquote(raw)
            if target.startswith(SKIP_PREFIXES) or not target:
                continue
            # Absolute filesystem paths are not portable doc links — flag
            # them as a class of breakage rather than silently skipping.
            link_count += 1
            path_part, _, anchor = target.partition("#")
            if not path_part:
                # Pure-fragment link within the same file.
                if anchor and not anchor_exists(f, anchor):
                    broken.append(
                        {"file": os.path.relpath(f, root),
                         "target": raw,
                         "reason": f"anchor not found: #{anchor}"}
                    )
                continue
            hit, _ = resolve_target(f, path_part, anchor)
            if hit is None:
                broken.append(
                    {"file": os.path.relpath(f, root),
                     "target": raw,
                     "reason": "target file not found"}
                )
            elif anchor and not anchor_exists(hit, anchor):
                broken.append(
                    {"file": os.path.relpath(f, root),
                     "target": raw,
                     "reason": f"anchor not found in target: #{anchor}"}
                )
    return {
        "root": root,
        "files": len(files),
        "links": link_count,
        "broken": broken,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check Markdown doc links.")
    ap.add_argument("--root", required=True, help="directory tree to check")
    ap.add_argument("--pretty", action="store_true", help="pretty-print JSON")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2

    report = check_root(root)
    print(json.dumps(report, indent=2 if args.pretty else None))
    return 1 if report["broken"] else 0


if __name__ == "__main__":
    sys.exit(main())
