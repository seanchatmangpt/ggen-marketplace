"""Shared helpers for the industry-closure pack courts.

Real collaborators only: the real Turtle on disk parsed by rdflib, the real
SPARQL gates and queries executed by rdflib, and a Jinja2 environment that is
deliberately restricted to the template subset ggen's Tera also executes
(``for``/``if``/``else``/``elif`` over ``results``, ``loop.last`` and plain
interpolation of ``row.<column>``). Nothing here is a mock.

The Jinja2 proxy is PARTIAL evidence about manufacture: real Tera rendering
only happens under a real ggen binary, which this environment does not have
(standing: BLOCKED:ggen_binary_unavailable). The proxy proves the templates
stay inside the shared subset and that they are deterministic; it never
promotes anything to ALIVE.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from jinja2 import Environment, StrictUndefined
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
PACK = PACKS / "industry-closure-ledger-pack"
ONTOLOGY = PACK / "ontology.ttl"

IC = "https://seanchatmangpt.github.io/packs/industry-closure-ledger-pack#"
EA = "https://chatman.ai/ontology/enterprise-architecture#"
TOGAF = "http://www.semanticweb.org/ontologies/2020/4/OntologyTOGAFContentMetamodel.owl#"

REFUSED_LITERAL = re.compile(r'"(REFUSED:[A-Z0-9_]+)"')


# ---------------------------------------------------------------------------
# Graphs
# ---------------------------------------------------------------------------

def parse_into(graph: Graph, source: "Path | str") -> Graph:
    """Parse a Turtle file (Path) or Turtle text (str) into ``graph``."""
    if isinstance(source, Path):
        graph.parse(source, format="turtle")
    else:
        graph.parse(data=source, format="turtle")
    return graph


def world(*sources: "Path | str", ontology: bool = True) -> Graph:
    """The kernel ontology (unless disabled) plus the given Turtle sources."""
    graph = Graph()
    if ontology:
        parse_into(graph, ONTOLOGY)
    for source in sources:
        parse_into(graph, source)
    return graph


def merged(base: Graph, *sources: "Path | str") -> Graph:
    """A fresh graph holding ``base`` plus more Turtle sources."""
    out = Graph()
    for triple in base:
        out.add(triple)
    for source in sources:
        parse_into(out, source)
    return out


# ---------------------------------------------------------------------------
# Gates and queries
# ---------------------------------------------------------------------------

def declared_codes(gate_source: str) -> set[str]:
    """Every quoted ``REFUSED:*`` literal a gate can emit."""
    return set(REFUSED_LITERAL.findall(gate_source))


def gate_rows(graph: Graph, gate: Path) -> list[tuple[str, str]]:
    """Execute a gate; return sorted ``(subject, reason)`` string pairs."""
    result = graph.query(gate.read_text(encoding="utf-8"))
    return sorted((str(row["subject"]), str(row["reason"])) for row in result)


def gate_reasons(graph: Graph, gate: Path) -> set[str]:
    return {reason for _, reason in gate_rows(graph, gate)}


def query_rows(graph: Graph, query: Path) -> list[dict[str, str]]:
    """Execute a SELECT query; rows as ordered dicts of string values."""
    result = graph.query(query.read_text(encoding="utf-8"))
    variables = [str(v) for v in result.vars]
    rows: list[dict[str, str]] = []
    for row in result:
        rows.append({name: ("" if row[name] is None else str(row[name])) for name in variables})
    return rows


def rows_json(rows: list[dict[str, str]]) -> str:
    """Canonical, byte-stable JSON for golden comparison."""
    return json.dumps(rows, indent=2, sort_keys=True) + "\n"


# ---------------------------------------------------------------------------
# R_CORE and UNION-branch lints
# ---------------------------------------------------------------------------

_R_CORE = re.compile(r"#\s*BEGIN R_CORE\b(.*?)#\s*END R_CORE\b", re.S)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_r_core(source: str) -> list[str]:
    """Whitespace-normalised R_CORE blocks of a gate or query source."""
    return [normalise(match) for match in _R_CORE.findall(source)]


def _strip_comments(source: str) -> str:
    out = []
    for line in source.splitlines():
        in_string = False
        buf = []
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == '"' and (i == 0 or line[i - 1] != "\\"):
                in_string = not in_string
            if ch == "#" and not in_string:
                break
            buf.append(ch)
            i += 1
        out.append("".join(buf))
    return "\n".join(out)


def _matching_brace(text: str, start: int) -> int:
    depth = 0
    in_string = False
    for i in range(start, len(text)):
        ch = text[i]
        if ch == '"' and text[i - 1] != "\\":
            in_string = not in_string
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("unbalanced braces")


def _split_top_level_union(body: str) -> list[str]:
    """Split a group's inner text on UNION at brace depth 0."""
    parts: list[str] = []
    depth = 0
    in_string = False
    last = 0
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == '"' and (i == 0 or body[i - 1] != "\\"):
            in_string = not in_string
        elif not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            elif depth == 0 and body.startswith("UNION", i) and not body[i - 1].isalnum():
                parts.append(body[last:i])
                last = i + len("UNION")
                i += len("UNION") - 1
        i += 1
    parts.append(body[last:])
    return [p.strip() for p in parts]


def union_branches(source: str) -> list[str]:
    """Top-level UNION branches (inner text of each ``{ ... }``) of the
    outermost WHERE group; empty if the WHERE group has no UNION."""
    text = _strip_comments(source)
    where = re.search(r"\bWHERE\s*\{", text)
    if not where:
        return []
    open_at = where.end() - 1
    close_at = _matching_brace(text, open_at)
    inner = text[open_at + 1:close_at]
    parts = _split_top_level_union(inner)
    if len(parts) < 2:
        return []
    branches = []
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            branches.append(part[1:-1].strip())
        else:
            branches.append(part)
    return branches


def first_pattern_binds_subject(branch: str) -> bool:
    """True if ?subject appears in the branch's first triple block (before the
    first terminating '.' at depth 0), or the branch reads ?subject from a
    nested group that does."""
    text = branch.strip()
    if text.startswith("{"):
        end = _matching_brace(text, 0)
        return first_pattern_binds_subject(text[1:end])
    depth = 0
    in_string = False
    for i, ch in enumerate(text):
        if ch == '"' and (i == 0 or text[i - 1] != "\\"):
            in_string = not in_string
        if in_string:
            continue
        if ch in "{(":
            depth += 1
        elif ch in "})":
            depth -= 1
        elif ch == "." and depth == 0 and not text[i - 1].isdigit():
            return "?subject" in text[:i]
    return "?subject" in text


# ---------------------------------------------------------------------------
# Jinja2 proxy for the Tera subset
# ---------------------------------------------------------------------------

_TAG = re.compile(r"\{%(.*?)%\}", re.S)
_EXPR = re.compile(r"\{\{(.*?)\}\}", re.S)
_COND_TOKEN = re.compile(r'\s*(?:"[^"\n]*"|row\.[A-Za-z_][A-Za-z0-9_]*|loop\.last|==|!=|\band\b|\bor\b|\bnot\b)\s*')


class TemplateSubsetError(ValueError):
    """The template uses a construct outside the shared Tera/Jinja2 subset."""


def check_subset(source: str) -> None:
    if "{#" in source:
        raise TemplateSubsetError("comments are outside the subset")
    for tag in _TAG.findall(source):
        body = tag.strip()
        if body in {"endfor", "endif", "else"}:
            continue
        if body == "for row in results":
            continue
        match = re.fullmatch(r"(?:if|elif)\s+(.*)", body, re.S)
        if not match:
            raise TemplateSubsetError(f"tag outside subset: {{% {body} %}}")
        rest = match.group(1)
        pos = 0
        while pos < len(rest):
            token = _COND_TOKEN.match(rest, pos)
            if not token:
                raise TemplateSubsetError(f"condition outside subset: {body!r}")
            pos = token.end()
    for expr in _EXPR.findall(source):
        if not re.fullmatch(r"\s*row\.[A-Za-z_][A-Za-z0-9_]*\s*", expr):
            raise TemplateSubsetError(f"expression outside subset: {{{{ {expr.strip()} }}}}")


def render(template: Path, rows: Iterable[dict[str, str]]) -> str:
    """Render a template through the restricted Jinja2 proxy (PARTIAL evidence)."""
    source = template.read_text(encoding="utf-8")
    check_subset(source)
    env = Environment(
        autoescape=False,
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=False,
        lstrip_blocks=False,
    )
    return env.from_string(source).render(results=list(rows))


# ---------------------------------------------------------------------------
# Catalog binding (partial, explicit): SBB marketplacePack / packDigest versus
# the derived catalog. No script computes the closure from the catalog.
# ---------------------------------------------------------------------------

def catalog_bytes() -> bytes:
    """Bytes of ``marketplace.py catalog --scope all`` (the derived catalog)."""
    import subprocess
    import sys

    done = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "marketplace.py"), "catalog", "--scope", "all"],
        cwd=ROOT, capture_output=True, check=True,
    )
    return done.stdout


def catalog_entries(raw: bytes | None = None) -> dict[str, dict]:
    payload = json.loads(raw if raw is not None else catalog_bytes())
    return {entry["name"]: entry for entry in payload["packs"]}


def bound_sbbs(graph: Graph) -> list[tuple[str, str, str]]:
    """``(sbb, marketplacePack, packDigest)`` for every SBB carrying both."""
    rows = graph.query(
        f"SELECT ?sbb ?pack ?digest WHERE {{ ?sbb <{IC}marketplacePack> ?pack ; <{IC}packDigest> ?digest }} ORDER BY ?sbb"
    )
    return [(str(r["sbb"]), str(r["pack"]), str(r["digest"])) for r in rows]


def binding_status(pack: str, recorded_digest: str, entries: dict[str, dict]) -> tuple[str, str]:
    """``(coverage_state, reason)``: a bound SBB whose recorded digest equals the
    catalog digest is current (LIVE); any mismatch must mark the coverage STALE."""
    entry = entries.get(pack)
    if entry is None:
        return ("STALE", "PACK_NOT_IN_CATALOG")
    if entry.get("digest") != recorded_digest:
        return ("STALE", "PACK_DIGEST_MISMATCH")
    return ("LIVE", "")
