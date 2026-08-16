#!/usr/bin/env python3
"""Cross-pack instance reference lint.

Real defect this catches (SLP-QUAL-001, PR #21/#22): a pack's ontology.ttl can
assert a fact about an individual IRI that is really typed only in a
*different* pack's ontology.ttl. scripts/qualify_packs.py deliberately
qualifies every pack in isolation -- it unions only that pack's own
ontology.ttl plus its own opt-in qualification/consumer.ttl fixture, never a
sibling pack's real ontology -- so a gate checking "does this referenced fact
exist and carry a type" sees nothing and (correctly, by its own logic)
refuses. The fix for one instance of this (packs/standing-ladder-pack) was a
minimal synthetic stub in qualification/consumer.ttl restating just the one
triple the gate needed. This script finds every OTHER pack with the same
unqualified cross-pack reference shape, before CI's sharded qualify suite
happens to exercise it.

This is intentionally NOT a general RDF/Turtle parser. This repository's
packs/*/ontology.ttl files are hand-authored in one consistent, flat dialect
(a header of `@prefix` lines, then subject/predicate/object statements
terminated by top-level `.`, no blank nodes, no collections, no nested
`[...]`) -- a targeted tokenizer over that dialect is enough, and safer than
adding an RDF dependency this repo doesn't otherwise have. Anything the
tokenizer cannot confidently parse is excluded and reported as
SKIPPED_UNPARSEABLE_STATEMENT, never silently treated as safe.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from marketplace import Pack, require_admitted
from qualify_packs import qualification_consumer_rdf

PREFIX_RE = re.compile(r"^\s*@prefix\s+([A-Za-z][\w-]*):\s+<([^>]+)>\s*\.\s*$", re.MULTILINE)
CURIE_RE = re.compile(r"\b([A-Za-z][\w-]*):([A-Za-z_][\w-]*)\b")

TYPE_PREDICATES = {"a", "rdf:type"}
SCHEMA_TYPE_OBJECTS = {
    "rdfs:Class",
    "owl:Class",
    "rdf:Property",
    "owl:ObjectProperty",
    "owl:DatatypeProperty",
}

# Well-known public standard vocabularies (W3C, DCMI, ...) that no single
# marketplace pack "owns", even if that pack's own ontology.ttl happens to
# retype one term from it locally (e.g. `prov:wasDerivedFrom a rdf:Property`
# as a documentation-only re-declaration) -- confirmed real false-positive
# case: dspy-pack types exactly one PROV-O term, which without this
# exclusion made every OTHER pack's legitimate `rdfs:subClassOf prov:Entity`
# usage look like an unqualified reference to dspy-pack. This matches the
# ecosystem's own stated design principle (gymact's README: "public W3C
# vocabularies over custom ontology") -- these namespaces are meant to be
# used by many packs simultaneously with no single owner, structurally the
# same exclusion already applied to a namespace typed by >1 pack
# (shared_taxonomy in namespace_owners), just for the single-pack-typed-once
# case a purely count-based rule can't catch on its own.
STANDARD_VOCAB_NAMESPACES = {
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "http://www.w3.org/2000/01/rdf-schema#",
    "http://www.w3.org/2001/XMLSchema#",
    "http://www.w3.org/2002/07/owl#",
    "http://www.w3.org/ns/prov#",
    "http://www.w3.org/ns/shacl#",
    "http://www.w3.org/ns/dcat#",
    "http://www.w3.org/ns/odrl/2/",
    "http://www.w3.org/2004/02/skos/core#",
    "http://www.w3.org/2006/time#",
    "http://www.w3.org/ns/sosa/",
    "http://www.w3.org/ns/ssn/",
    "http://www.w3.org/ns/earl#",
    "http://www.w3.org/ns/dqv#",
    "http://www.w3.org/ns/td#",
    "http://qudt.org/schema/qudt/",
    "http://purl.org/dc/terms/",
    "http://purl.org/dc/elements/1.1/",
    "http://xmlns.com/foaf/0.1/",
    "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "http://www.w3.org/ns/org#",
}


def is_standard_vocab_namespace(ns: str) -> bool:
    return any(ns.startswith(prefix) for prefix in STANDARD_VOCAB_NAMESPACES)


@dataclass(frozen=True)
class Statement:
    subject: str
    predicate: str
    objects: tuple[str, ...]


@dataclass
class ParseResult:
    prefixes: dict[str, str]
    statements: tuple[Statement, ...]
    skipped: int


LONG_QUOTES = ('"""', "'''")
SHORT_QUOTES = ('"', "'")


def scan_literal(text: str, i: int) -> int | None:
    """Given that `text[i]` opens a Turtle string literal, return the index
    just past its closing delimiter, or None if it is never terminated.

    Turtle has four literal forms; this corpus really uses three of them:
    short `"..."`, and the *long* forms `\"\"\"...\"\"\"` / `'''...'''` that may
    span lines and may contain unescaped `"`, `#`, `[`, `]`, `{`, `}`.
    Long-literal support is load-bearing, not theoretical: level-five-book-pack
    stores whole markdown book chapters in `\"\"\"...\"\"\"` literals, and a scanner
    that toggles state on each single `"` reads `\"\"\"` as open-then-close and so
    treats the chapter body as ordinary Turtle syntax -- which is exactly how
    markdown checklists (`- [ ]`) and SPARQL braces inside those chapters used
    to be misread as blank nodes/collections and discarded.

    Escaping follows Turtle: a delimiter preceded by an odd number of
    backslashes is escaped and does not close the literal.
    """
    for quote in LONG_QUOTES:
        if text.startswith(quote, i):
            return _closing(text, i + len(quote), quote)
    for quote in SHORT_QUOTES:
        if text.startswith(quote, i):
            return _closing(text, i + len(quote), quote)
    return None


def _closing(text: str, start: int, quote: str) -> int | None:
    j = start
    n = len(text)
    while j < n:
        if text.startswith(quote, j) and not _escaped(text, j):
            return j + len(quote)
        j += 1
    return None


def _escaped(text: str, i: int) -> bool:
    backslashes = 0
    k = i - 1
    while k >= 0 and text[k] == "\\":
        backslashes += 1
        k -= 1
    return backslashes % 2 == 1


def strip_comments(text: str) -> str:
    """Remove `#`-to-end-of-line comments, conservatively: a `#` inside a
    string literal (short or long) OR inside an IRI's `<...>` delimiters
    (e.g. `<http://example.org/ns#>`, which every namespace IRI in this
    corpus uses) is not a comment start. Literal and angle-bracket state
    must persist across lines -- a long `\"\"\"...\"\"\"` literal spanning fifty
    markdown lines is one token, and an unterminated `<` on one line should
    not resume "outside" on the next.

    Line structure is preserved (newlines inside a literal are kept verbatim)
    so downstream statement tokenization sees the same text shape.
    """
    out: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in SHORT_QUOTES:
            end = scan_literal(text, i)
            if end is None:
                # Unterminated literal: copy the remainder verbatim and let
                # the statement tokenizer account for it as unparseable.
                out.append(text[i:])
                break
            out.append(text[i:end])
            i = end
            continue
        if ch == "<":
            end = text.find(">", i)
            if end == -1:
                out.append(text[i:])
                break
            out.append(text[i : end + 1])
            i = end + 1
            continue
        if ch == "#":
            end = text.find("\n", i)
            if end == -1:
                break
            i = end  # keep the newline itself on the next pass
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def parse_prefixes(text: str) -> dict[str, str]:
    return dict(PREFIX_RE.findall(text))


def tokenize_statements(text: str) -> tuple[tuple[str, ...], int]:
    """Split comment-stripped ontology text into raw statement token groups.

    Returns (list of token-tuples per statement, skipped-statement count).
    A "statement" is everything between top-level `.` characters (a `.` is
    top-level when not inside `<...>`, `"..."`, and not immediately preceded
    by a digit run that looks like part of a decimal number). Within a
    statement, `;` starts a new predicate-object group sharing the same
    subject, and `,` separates multiple objects for the same predicate.
    """
    stmts: list[list[str]] = [[]]
    depth_angle = 0
    buf = []
    skipped = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in SHORT_QUOTES and depth_angle == 0:
            # Consume the whole literal (short or long) as one opaque token,
            # so `.`/`;`/`,`/`[`/`{`/`#` inside it are never read as syntax.
            end = scan_literal(text, i)
            if end is None:
                skipped += 1  # unterminated literal -- drop the rest
                buf = []
                break
            buf.append(text[i:end])
            i = end
            continue
        if ch == "<":
            depth_angle += 1
            buf.append(ch)
            i += 1
            continue
        if ch == ">":
            depth_angle = max(0, depth_angle - 1)
            buf.append(ch)
            i += 1
            continue
        if depth_angle > 0:
            buf.append(ch)
            i += 1
            continue
        if ch == ".":
            # Not top-level end-of-statement if it's a decimal point between digits.
            prev_ch = text[i - 1] if i > 0 else ""
            next_ch = text[i + 1] if i + 1 < n else ""
            if prev_ch.isdigit() and next_ch.isdigit():
                buf.append(ch)
                i += 1
                continue
            stmts[-1].append("".join(buf).strip())
            stmts.append([])
            buf = []
            i += 1
            continue
        if ch in "[]{}":
            # Blank nodes / collections not supported by this targeted
            # tokenizer -- drop the whole in-progress statement rather than
            # mis-parse it.
            skipped += 1
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    tail = "".join(buf).strip()
    if tail:
        skipped += 1  # trailing content with no closing `.` -- unparseable
    parsed = [s for s in stmts if s and "".join(s).strip()]
    return tuple("".join(s) for s in parsed), skipped


def split_statement(raw: str) -> tuple[str, tuple[tuple[str, tuple[str, ...]], ...]] | None:
    """subject ; then (predicate, (objects...)) groups, comma-splitting objects.
    Returns None if the statement doesn't look like a real subject-led triple
    group (e.g. it's just leftover prefix/whitespace noise)."""
    # First token = subject.
    parts = [p.strip() for p in raw.split(";")]
    if not parts or not parts[0]:
        return None
    head = parts[0]
    head_tokens = head.split(None, 1)
    if len(head_tokens) < 2:
        return None
    subject = head_tokens[0]
    first_pred_objs = head_tokens[1]
    groups = [first_pred_objs] + parts[1:]
    result = []
    for group in groups:
        group = group.strip()
        if not group:
            continue
        gtok = group.split(None, 1)
        if len(gtok) < 2:
            continue
        predicate = gtok[0]
        objects = tuple(o.strip() for o in gtok[1].split(",") if o.strip())
        result.append((predicate, objects))
    if not result:
        return None
    return subject, tuple(result)


def parse_ontology(text: str) -> ParseResult:
    prefixes = parse_prefixes(text)
    stripped = strip_comments(text)
    raw_statements, skipped = tokenize_statements(stripped)
    statements: list[Statement] = []
    for raw in raw_statements:
        if raw.lstrip().startswith("@prefix"):
            continue
        split = split_statement(raw)
        if split is None:
            skipped += 1
            continue
        subject, groups = split
        for predicate, objects in groups:
            statements.append(Statement(subject=subject, predicate=predicate, objects=objects))
    return ParseResult(prefixes=prefixes, statements=tuple(statements), skipped=skipped)


def resolve(curie: str, prefixes: dict[str, str]) -> str | None:
    curie = curie.strip().strip(",")
    m = CURIE_RE.fullmatch(curie)
    if not m:
        return None
    prefix, local = m.groups()
    ns = prefixes.get(prefix)
    if ns is None:
        return None
    return f"{ns}{local}"


def load_pack_ontology_text(pack: Pack) -> str:
    parts = []
    for path in pack.ontologies:
        try:
            parts.append(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError):
            continue
    return "\n\n".join(parts)


@dataclass
class PackModel:
    pack: Pack
    prefixes: dict[str, str]
    statements: tuple[Statement, ...]
    typed_subjects: set[str] = field(default_factory=set)  # full IRIs this pack asserts rdf:type for
    schema_iris: set[str] = field(default_factory=set)  # full IRIs this pack types as class/property


def build_pack_model(pack: Pack) -> PackModel:
    text = load_pack_ontology_text(pack)
    parsed = parse_ontology(text)
    model = PackModel(pack=pack, prefixes=parsed.prefixes, statements=parsed.statements)
    for stmt in parsed.statements:
        if stmt.predicate not in TYPE_PREDICATES:
            continue
        subj_iri = resolve(stmt.subject, parsed.prefixes)
        if subj_iri is None:
            continue
        model.typed_subjects.add(subj_iri)
        for obj in stmt.objects:
            if obj in SCHEMA_TYPE_OBJECTS:
                model.schema_iris.add(subj_iri)
    return model


def namespace_owners(models: list[PackModel]) -> dict[str, str | None]:
    """namespace IRI stem -> owning pack name, or None if shared (excluded).
    A namespace is owned by a pack only if that pack asserts rdf:type for at
    least one individual whose IRI falls under that namespace -- declaring
    the @prefix alone (vocabulary reuse, symmetric shared-taxonomy imports)
    does not confer ownership."""
    owner_by_ns: dict[str, str] = {}
    shared: set[str] = set()
    for model in models:
        # A namespace stem is any prefix's declared IRI within this pack.
        for ns in model.prefixes.values():
            if is_standard_vocab_namespace(ns):
                continue
            has_typed_individual = any(iri.startswith(ns) for iri in model.typed_subjects)
            if not has_typed_individual:
                continue
            existing = owner_by_ns.get(ns)
            if existing is None:
                owner_by_ns[ns] = model.pack.name
            elif existing != model.pack.name:
                shared.add(ns)
    result: dict[str, str | None] = dict(owner_by_ns)
    for ns in shared:
        result[ns] = None
    return result


@dataclass(frozen=True)
class Violation:
    pack: str
    predicate: str
    object_iri: str
    owner: str


def find_violations(packs: list[Pack]) -> tuple[list[Violation], int]:
    models = [build_pack_model(p) for p in packs]
    owners = namespace_owners(models)
    total_skipped = sum(len(parse_ontology(load_pack_ontology_text(p)).statements) * 0 for p in packs)
    # (re-derive skipped counts properly below, not via the throwaway above)
    total_skipped = 0
    violations: list[Violation] = []

    fixture_cache: dict[str, set[str]] = {}

    def fixture_types(pack: Pack) -> set[str]:
        if pack.name in fixture_cache:
            return fixture_cache[pack.name]
        typed: set[str] = set()
        for path in qualification_consumer_rdf(pack):
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            parsed = parse_ontology(text)
            for stmt in parsed.statements:
                if stmt.predicate not in TYPE_PREDICATES:
                    continue
                subj_iri = resolve(stmt.subject, parsed.prefixes)
                if subj_iri is not None:
                    typed.add(subj_iri)
        fixture_cache[pack.name] = typed
        return typed

    for model in models:
        own_namespaces = set(model.prefixes.values())
        for stmt in model.statements:
            if stmt.predicate in TYPE_PREDICATES:
                continue  # rdf:type object handling is vocabulary use, not a violation candidate
            candidates: list[str] = []
            for obj in stmt.objects:
                obj_iri = resolve(obj, model.prefixes)
                if obj_iri is not None:
                    candidates.append(obj_iri)
            # Also check subject-position external reference (this pack
            # asserting facts ABOUT another pack's individual as subject).
            subj_iri = resolve(stmt.subject, model.prefixes)
            if subj_iri is not None:
                candidates.append(subj_iri)
            for iri in candidates:
                if iri in own_namespaces:
                    continue
                owning_ns = next((ns for ns in owners if iri.startswith(ns)), None)
                if owning_ns is None:
                    continue
                owner = owners[owning_ns]
                if owner is None or owner == model.pack.name:
                    continue  # shared_taxonomy or self
                owner_model = next((m for m in models if m.pack.name == owner), None)
                if owner_model is not None and iri in owner_model.schema_iris:
                    continue  # vocabulary use (class/property), not an instance reference
                if iri not in fixture_types(model.pack):
                    violations.append(
                        Violation(
                            pack=model.pack.name,
                            predicate=stmt.predicate,
                            object_iri=iri,
                            owner=owner,
                        )
                    )
        total_skipped += parse_ontology(load_pack_ontology_text(model.pack)).skipped

    seen = set()
    unique: list[Violation] = []
    for v in violations:
        key = (v.pack, v.predicate, v.object_iri)
        if key in seen:
            continue
        seen.add(key)
        unique.append(v)
    unique.sort(key=lambda v: (v.pack, v.predicate, v.object_iri))
    return unique, total_skipped


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("warn", "gate"), default="warn")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    packs = require_admitted()
    violations, skipped = find_violations(packs)

    for v in violations:
        print(
            f"CROSS_PACK_REFERENCE_UNQUALIFIED: pack={v.pack} predicate={v.predicate} "
            f"object={v.object_iri} owner={v.owner}"
        )
    if skipped:
        print(f"SKIPPED_UNPARSEABLE_STATEMENT: count={skipped}", file=sys.stderr)

    if args.report:
        args.report.write_text(
            json.dumps(
                {
                    "violations": [
                        {"pack": v.pack, "predicate": v.predicate, "object": v.object_iri, "owner": v.owner}
                        for v in violations
                    ],
                    "skipped_unparseable_statements": skipped,
                    "mode": args.mode,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    if args.mode == "gate" and violations:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
