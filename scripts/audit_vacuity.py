#!/usr/bin/env python3
"""Deterministic, read-only audit for stub and vacuous repository implementations.

The scanner can inspect either the current filesystem or an immutable Git ref.
For Git refs it uses ``git archive`` so every tracked file is inspected without
checking out or executing the subject.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import re
import subprocess
import tarfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable, Iterator

SOURCE_SUFFIXES = {
    ".py", ".rs", ".sh", ".bash", ".rq", ".ttl", ".toml", ".yml", ".yaml",
    ".tmpl", ".tera",
}
SKIP_ROOTS = {".git", ".cache", "target", "dist", "__pycache__", ".venv", "venv"}
REFERENCE_PARTS = {"reference", "vendor", "third_party"}
DOC_PARTS = {"docs"}
MARKERS = (
    ("TODO", "TODO"),
    ("FIX" + "ME", "FIXME"),
    ("STUB", "STUB"),
    ("PLACE" + "HOLDER", "PLACEHOLDER"),
    ("NOT IMPLEMENTED", "NOT_IMPLEMENTED"),
)
RUST_VACUITY = (
    (re.compile(r"\btodo!\s*\("), "RUST_TODO_MACRO"),
    (re.compile(r"\bunimplemented!\s*\("), "RUST_UNIMPLEMENTED_MACRO"),
    (re.compile(r"\bpanic!\s*\(\s*[\"'][^\"']*(?:todo|stub|not implemented)", re.I), "RUST_PLACEHOLDER_PANIC"),
)
RUST_VACUOUS_FN = re.compile(
    r"(?ms)\bfn\s+(?P<name>(?:validate|verify|check|admit|qualify)[A-Za-z0-9_]*)"
    r"\s*(?:<[^>{}]*>)?\s*\([^)]*\)\s*(?:->[^{]+)?\{\s*(?P<body>Ok\s*\(\s*\(\s*\)\s*\)|true|0)\s*\}"
)
SHELL_VACUOUS = re.compile(r"(?ms)\A\s*(?:#![^\n]+\n)?(?:set\s+-[A-Za-z]+\s*\n)?(?:exit\s+0|:)\s*\Z")


@dataclass(frozen=True)
class Finding:
    subject: str
    path: str
    line: int
    rule: str
    severity: str
    detail: str


@dataclass(frozen=True)
class SubjectReport:
    subject: str
    total_files: int
    text_files: int
    source_files: int
    findings: tuple[Finding, ...]


def _is_reference(path: str) -> bool:
    parts = set(PurePosixPath(path).parts)
    return bool(parts & (REFERENCE_PARTS | DOC_PARTS))


def _is_test(path: str) -> bool:
    pure = PurePosixPath(path)
    return (
        any(part in {"test", "tests", "fixtures"} for part in pure.parts)
        or pure.name.startswith("test_")
        or pure.name.endswith("_test.py")
        or pure.name.endswith("_test.rs")
    )


def _is_source(path: str) -> bool:
    name = PurePosixPath(path).name
    return any(name.endswith(suffix) for suffix in SOURCE_SUFFIXES)


def _line(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _real_statements(body: list[ast.stmt]) -> list[ast.stmt]:
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        return body[1:]
    return body


def _constant_success(node: ast.AST) -> bool:
    if not isinstance(node, ast.Return):
        return False
    value = node.value
    if value is None:
        return True
    if isinstance(value, ast.Constant):
        return value.value in (True, 0, None)
    if isinstance(value, (ast.List, ast.Tuple, ast.Dict, ast.Set)):
        return len(getattr(value, "elts", getattr(value, "keys", ()))) == 0
    return False


def _exception_names(node: ast.expr | None) -> set[str]:
    if node is None:
        return {"<bare>"}
    if isinstance(node, ast.Name):
        return {node.id}
    if isinstance(node, ast.Attribute):
        return {node.attr}
    if isinstance(node, ast.Tuple):
        names: set[str] = set()
        for item in node.elts:
            names.update(_exception_names(item))
        return names
    return {"<dynamic>"}


def _swallows_broad_exception(node: ast.ExceptHandler) -> bool:
    names = _exception_names(node.type)
    return bool(names & {"<bare>", "Exception", "BaseException"})


def _python_findings(subject: str, path: str, text: str) -> list[Finding]:
    try:
        tree = ast.parse(text, filename=path)
    except SyntaxError as exc:
        return [Finding(subject, path, exc.lineno or 1, "PYTHON_SYNTAX_INVALID", "error", exc.msg)]

    out: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body = _real_statements(node.body)
            if len(body) == 1:
                stmt = body[0]
                if isinstance(stmt, ast.Pass) or (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Constant)
                    and stmt.value.value is Ellipsis
                ):
                    out.append(Finding(subject, path, stmt.lineno, "PYTHON_EMPTY_FUNCTION", "error", node.name))
                elif (
                    isinstance(stmt, ast.Raise)
                    and isinstance(stmt.exc, ast.Call)
                    and isinstance(stmt.exc.func, ast.Name)
                    and stmt.exc.func.id == "NotImplementedError"
                ):
                    out.append(Finding(subject, path, stmt.lineno, "PYTHON_NOT_IMPLEMENTED", "error", node.name))
                elif (
                    re.match(r"^(?:validate|verify|check|admit|qualify)", node.name, re.I)
                    and _constant_success(stmt)
                ):
                    out.append(Finding(subject, path, stmt.lineno, "PYTHON_CONSTANT_SUCCESS", "error", node.name))
            for child in ast.walk(node):
                if isinstance(child, ast.Raise):
                    exc = child.exc
                    if (
                        isinstance(exc, ast.Name) and exc.id == "NotImplementedError"
                    ) or (
                        isinstance(exc, ast.Call)
                        and isinstance(exc.func, ast.Name)
                        and exc.func.id == "NotImplementedError"
                    ):
                        out.append(Finding(subject, path, child.lineno, "PYTHON_NOT_IMPLEMENTED", "error", node.name))
        elif isinstance(node, ast.ExceptHandler):
            body = _real_statements(node.body)
            if len(body) == 1 and isinstance(body[0], ast.Pass) and _swallows_broad_exception(node):
                names = ",".join(sorted(_exception_names(node.type)))
                out.append(Finding(
                    subject,
                    path,
                    body[0].lineno,
                    "PYTHON_SWALLOWED_EXCEPTION",
                    "error",
                    f"broad except handler contains only pass: {names}",
                ))
        elif isinstance(node, ast.Assert):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                out.append(Finding(subject, path, node.lineno, "PYTHON_VACUOUS_ASSERT", "error", "assert True"))
    return out


def scan_content(subject: str, path: str, data: bytes) -> list[Finding]:
    if not data or b"\x00" in data:
        if not data and _is_source(path):
            return [Finding(subject, path, 1, "EMPTY_SOURCE_FILE", "error", "zero-byte source")]
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []

    out: list[Finding] = []
    reference = _is_reference(path)
    source = _is_source(path)
    test_fixture = _is_test(path)

    if path != "scripts/audit_vacuity.py":
        upper = text.upper()
        for needle, rule in MARKERS:
            start = 0
            while True:
                idx = upper.find(needle, start)
                if idx < 0:
                    break
                out.append(Finding(
                    subject,
                    path,
                    _line(text, idx),
                    f"MARKER_{rule}",
                    "warning" if reference or test_fixture or not source else "error",
                    f"contains {needle}",
                ))
                start = idx + len(needle)

    name = PurePosixPath(path).name
    if name.endswith(".py") and "{{" not in text and "{%" not in text:
        out.extend(_python_findings(subject, path, text))

    if name.endswith(".rs") or name.endswith(".rs.tmpl") or name.endswith(".rs.tera"):
        for pattern, rule in RUST_VACUITY:
            for match in pattern.finditer(text):
                out.append(Finding(
                    subject,
                    path,
                    _line(text, match.start()),
                    rule,
                    "warning" if reference else "error",
                    match.group(0)[:120],
                ))
        if not reference:
            for match in RUST_VACUOUS_FN.finditer(text):
                out.append(Finding(subject, path, _line(text, match.start()), "RUST_CONSTANT_SUCCESS", "error", match.group("name")))

    if name.endswith((".sh", ".bash")) and SHELL_VACUOUS.fullmatch(text):
        out.append(Finding(subject, path, 1, "SHELL_NOOP_SCRIPT", "error", "script has no effect"))

    uniq = {(f.subject, f.path, f.line, f.rule, f.severity, f.detail): f for f in out}
    return sorted(uniq.values(), key=lambda f: (f.path, f.line, f.rule, f.detail))


def _filesystem_files(root: Path) -> Iterator[tuple[str, bytes]]:
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_ROOTS for part in rel.parts):
            continue
        yield rel.as_posix(), path.read_bytes()


def _git_ref_files(ref: str) -> Iterator[tuple[str, bytes]]:
    proc = subprocess.run(
        ["git", "archive", "--format=tar", ref],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        detail = proc.stderr.decode("utf-8", "replace").strip()
        raise SystemExit(f"REFUSED:VACUITY_AUDIT_GIT_ARCHIVE:{ref}:{detail}")
    with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:") as archive:
        for member in sorted((m for m in archive.getmembers() if m.isfile()), key=lambda m: m.name):
            handle = archive.extractfile(member)
            if handle is None:
                raise SystemExit(f"REFUSED:VACUITY_AUDIT_ARCHIVE_MEMBER:{ref}:{member.name}")
            yield member.name, handle.read()


def audit_subject(subject: str, files: Iterable[tuple[str, bytes]]) -> SubjectReport:
    findings: list[Finding] = []
    total = text = source = 0
    for path, data in files:
        total += 1
        if _is_source(path):
            source += 1
        if b"\x00" not in data:
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                pass
            else:
                text += 1
        findings.extend(scan_content(subject, path, data))
    findings.sort(key=lambda f: (f.path, f.line, f.rule, f.detail))
    return SubjectReport(subject, total, text, source, tuple(findings))


def _remote_refs() -> list[str]:
    proc = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc.returncode:
        raise SystemExit(f"REFUSED:VACUITY_AUDIT_REF_ENUMERATION:{proc.stderr.strip()}")
    return sorted(
        ref.strip() for ref in proc.stdout.splitlines()
        if ref.strip() and ref.strip() != "origin/HEAD"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--git-ref", action="append", default=[])
    parser.add_argument("--all-remote-branches", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--warnings-as-errors", action="store_true")
    args = parser.parse_args(argv)

    refs = list(args.git_ref)
    if args.all_remote_branches:
        refs.extend(ref for ref in _remote_refs() if ref not in refs)

    if refs:
        reports = [audit_subject(ref, _git_ref_files(ref)) for ref in sorted(set(refs))]
    else:
        reports = [audit_subject("filesystem", _filesystem_files(args.root.resolve()))]

    payload = {
        "schema": "https://ggen.dev/marketplace/vacuity-audit/v1",
        "standing": "REFUSED" if any(
            f.severity == "error" or args.warnings_as_errors
            for report in reports for f in report.findings
        ) else "ADMITTED",
        "subjects": [
            {
                "subject": r.subject,
                "total_files": r.total_files,
                "text_files": r.text_files,
                "source_files": r.source_files,
                "findings": [asdict(f) for f in r.findings],
            }
            for r in reports
        ],
    }
    encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded, encoding="utf-8")
    print(encoded, end="")

    errors = [
        f for r in reports for f in r.findings
        if f.severity == "error" or args.warnings_as_errors
    ]
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
