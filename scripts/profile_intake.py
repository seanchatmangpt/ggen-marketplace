#!/usr/bin/env python3
"""profile_intake.py -- normalize LinkedIn-profile-shaped input into JSON + RDF.

Phase-2 intake for the AAIF profile-tailoring pipeline (see
~/.claude/plans/i-had-you-running-memoized-parrot.md, Phase 2 / Lane 5 / Lane 17).

Usage:
    profile_intake.py <input.{json,html,txt}> --out <dir> [--lock]

Input formats:
    .json  LinkedIn-profile-shaped JSON
    .html  profile HTML (stdlib html.parser heuristics, no external deps)
    .txt   line-based heuristic text

Outputs (into --out):
    profile.json       normalized, sort_keys
    profile.ttl        vendored public vocabularies (foaf/schema-org/org) plus
                       parallel aaif:Agent individuals
    profile.lock.json  (with --lock) sha256 fingerprint over both outputs,
                       fingerprint_paths length-prefixed-fold idiom

Refusals (exit 2): REFUSED:<CODE>:<detail>
    REFUSED_PROFILE_UNREADABLE / REFUSED_PROFILE_EMPTY / REFUSED_PROFILE_NO_NAME

Privacy fence: no network I/O at all.
"""

import sys

if sys.version_info < (3, 11):
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED")

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, RDFS, OWL, URIRef

AAIF = Namespace("https://aaif.io/ontology#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("https://schema.org/")
ORG = Namespace("https://www.w3.org/ns/org#")

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_ONTOLOGIES = ROOT / "ontologies" / "public"

SCHEMA_V1 = "https://ggen.dev/marketplace/profile-intake/v1"


def refusal(code: str, detail: str) -> str:
    return f"REFUSED:{code}:{detail}"


# ---------------------------------------------------------------------------
# fingerprint (fingerprint_paths idiom from scripts/marketplace.py)
# ---------------------------------------------------------------------------


def fingerprint_paths(paths, base: Path) -> str:
    digest = hashlib.sha256()
    ordered = sorted(paths, key=lambda path: Path(path).relative_to(base).as_posix())
    for path in ordered:
        path = Path(path)
        relative = path.relative_to(base).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Text helpers shared by the html/txt parsers
# ---------------------------------------------------------------------------

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(r"https?://[^\s<>\"']+")
_NAME_RE = re.compile(r"^[A-Z][A-Za-z'’\-]+(?:\s+[A-Z][A-Za-z'’\-]+){0,3}$")
_PERIOD_RE = re.compile(
    r"(?:[A-Za-z]{3,9}\.?\s+)?\d{4}\s*(?:-|–|—|to)\s*(?:(?:[A-Za-z]{3,9}\.?\s+)?\d{4}|[Pp]resent)"
)


def _looks_like_name(line: str) -> bool:
    if not (2 <= len(line) <= 60):
        return False
    if any(ch.isdigit() for ch in line):
        return False
    if "@" in line or "http" in line.lower():
        return False
    if "|" in line or "·" in line:
        return False
    return bool(_NAME_RE.match(line))


def _looks_like_period(line: str) -> bool:
    return bool(_PERIOD_RE.search(line))


def _clean(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


# ---------------------------------------------------------------------------
# HTML extraction (stdlib html.parser)
# ---------------------------------------------------------------------------


class _ProfileHTMLParser(HTMLParser):
    """Collect visible text, <title>, and mailto links; nothing else."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str = ""
        self._in_title = False
        self._skip_depth = 0
        self.chunks: list[str] = []
        self.mailtos: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style", "noscript", "svg"):
            self._skip_depth += 1
        elif tag == "title":
            self._in_title = True
        elif tag == "a":
            href = attrs.get("href") or ""
            if href.lower().startswith("mailto:"):
                self.mailtos.append(href[len("mailto:"):].strip())

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self._skip_depth:
            self._skip_depth -= 1
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif not self._skip_depth:
            text = _clean(data)
            if text:
                self.chunks.append(text)


def _parse_html_profile(text: str) -> dict:
    parser = _ProfileHTMLParser()
    parser.feed(text)

    title = _clean(parser.title)
    # Heuristic: "<Name> - <headline>" or "<Name> | <headline>" in <title>,
    # else "Profile of <Name>" etc. -- strip boilerplate prefixes.
    name = ""
    headline = ""
    for sep in (" - ", " | ", " – ", " — "):
        if sep in title:
            left, right = title.split(sep, 1)
            if _looks_like_name(left):
                name, headline = left, right.strip()
                break
    if not name:
        candidate = re.sub(r"^(profile of|resume of|cv of)\s+", "", title, flags=re.I)
        candidate = _clean(candidate)
        if _looks_like_name(candidate):
            name = candidate

    # Fall back to first title-ish line of visible text.
    if not name:
        for chunk in parser.chunks[:10]:
            if _looks_like_name(chunk):
                name = chunk
                break

    # Headline: first non-name line mentioning a role-ish word, else the line
    # right after the name.
    role_words = ("engineer", "developer", "manager", "architect", "scientist",
                  "designer", "consultant", "director", "lead", "analyst",
                  "founder", "cto", "ceo", "vp", "president")
    if not headline:
        for chunk in parser.chunks[:10]:
            low = chunk.lower()
            if chunk != name and any(w in low for w in role_words):
                headline = chunk
                break
    if not headline and name and name in parser.chunks:
        idx = parser.chunks.index(name)
        if idx + 1 < len(parser.chunks):
            headline = parser.chunks[idx + 1]

    summary_lines = [
        chunk
        for chunk in parser.chunks
        if len(chunk) > 80 and chunk != name and chunk != headline
    ]
    summary = " ".join(summary_lines[:3])

    emails = sorted(set(_EMAIL_RE.findall(text)))
    urls = _URL_RE.findall(text)
    url = urls[0] if urls else ""

    positions = _extract_positions(parser.chunks)

    profile = {
        "name": name,
        "headline": headline,
        "summary": summary,
        "url": url,
        "positions": positions,
        "skills": [],
    }
    if emails:
        profile["email"] = sorted(set(emails))[0]
    return profile


def _extract_positions(lines: list[str]) -> list[dict]:
    """A position is anchored on a period line (e.g. "1843 - Present");
    the two preceding lines are taken as title and organization."""
    positions: list[dict] = []
    for idx, line in enumerate(lines):
        match = _PERIOD_RE.search(line)
        if match is None:
            continue
        period = match.group(0)
        preceding = [
            candidate
            for candidate in lines[max(0, idx - 2):idx]
            if not _looks_like_period(candidate)
            and not candidate.lower().startswith("skills")
            and "@" not in candidate
            and not candidate.startswith("http")
        ]
        title = preceding[0] if preceding else line[:match.start()].strip(" -–—")
        organization = preceding[1] if len(preceding) > 1 else ""
        if not title or _looks_like_name(title):
            # name alone above the period is not a position title
            if len(preceding) > 1:
                title, organization = preceding[0], preceding[1]
            else:
                continue
        positions.append(
            {"title": title, "organization": organization, "period": period}
        )
    return positions[:10]


# ---------------------------------------------------------------------------
# Text extraction (line-based heuristics)
# ---------------------------------------------------------------------------


def _parse_text_profile(text: str) -> dict:
    lines = [_clean(line) for line in text.splitlines()]
    lines = [line for line in lines if line]

    name = ""
    for line in lines[:5]:
        if _looks_like_name(line):
            name = line
            break

    headline = ""
    role_words = ("engineer", "developer", "manager", "architect", "scientist",
                  "designer", "consultant", "director", "lead", "analyst",
                  "founder", "cto", "ceo", "vp", "president")
    if name and name in lines:
        idx = lines.index(name)
        for line in lines[idx + 1: idx + 4]:
            if line != name and len(line) <= 120:
                headline = line
                break
    if not headline:
        for line in lines[:10]:
            low = line.lower()
            if any(w in low for w in role_words):
                headline = line
                break

    emails = sorted(set(_EMAIL_RE.findall(text)))
    urls = [u for u in _URL_RE.findall(text) if not u.lower().startswith("mailto")]
    url = urls[0] if urls else ""

    positions = _extract_positions(lines)

    summary_lines = [
        line
        for line in lines
        if len(line) > 80 and line != name and line != headline
        and not _looks_like_period(line)
    ]
    summary = " ".join(summary_lines[:3])

    skills: list[str] = []
    for line in lines:
        low = line.lower().rstrip(":")
        if low.startswith("skills"):
            rest = line.split(":", 1)[1] if ":" in line else line[len("skills"):]
            skills = [s.strip() for s in re.split(r"[,;|]", rest) if s.strip()]
            break

    profile = {
        "name": name,
        "headline": headline,
        "summary": summary,
        "url": url,
        "positions": positions,
        "skills": skills,
    }
    if emails:
        profile["email"] = emails[0]
    return profile


# ---------------------------------------------------------------------------
# JSON input
# ---------------------------------------------------------------------------


def _parse_json_profile(text: str) -> dict:
    raw = json.loads(text)
    if not isinstance(raw, dict):
        raise ValueError("top-level JSON value is not an object")

    positions = []
    for item in raw.get("experience", []) or []:
        if not isinstance(item, dict):
            continue
        positions.append(
            {
                "title": str(item.get("title", "")).strip(),
                "organization": str(item.get("company", "")).strip(),
                "period": str(item.get("period", "")).strip(),
            }
        )

    profile = {
        "name": str(raw.get("name", "")).strip(),
        "headline": str(raw.get("headline", "")).strip(),
        "summary": str(raw.get("summary", "")).strip(),
        "url": str(raw.get("url", "")).strip(),
        "positions": positions,
        "skills": [str(s).strip() for s in (raw.get("skills", []) or []) if str(s).strip()],
    }
    if raw.get("email"):
        profile["email"] = str(raw["email"]).strip()

    deployment = raw.get("deployment")
    if isinstance(deployment, dict) and deployment.get("residencyRegionLock"):
        profile["residencyRegionLock"] = str(deployment["residencyRegionLock"]).strip()
    return profile


# ---------------------------------------------------------------------------
# Normalization + admission
# ---------------------------------------------------------------------------


def normalize(profile: dict) -> dict:
    normalized = {
        "schema": SCHEMA_V1,
        "name": profile.get("name", ""),
        "headline": profile.get("headline", ""),
        "summary": profile.get("summary", ""),
        "url": profile.get("url", ""),
        "positions": [
            {
                "title": p.get("title", ""),
                "organization": p.get("organization", ""),
                "period": p.get("period", ""),
            }
            for p in profile.get("positions", [])
        ],
        "skills": list(profile.get("skills", [])),
    }
    if profile.get("email"):
        normalized["email"] = profile["email"]
    if profile.get("residencyRegionLock"):
        normalized["residencyRegionLock"] = str(profile["residencyRegionLock"]).strip()
    return normalized


def admit(normalized: dict) -> None:
    """Fail-closed admission: a profile without a name cannot be manufactured."""
    if not normalized.get("name"):
        raise SystemExit(refusal("PROFILE_NO_NAME", "no name could be extracted"))


# ---------------------------------------------------------------------------
# RDF projection
# ---------------------------------------------------------------------------


def _pascal_case(value: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def build_graph(normalized: dict) -> Graph:
    graph = Graph()
    graph.bind("aaif", AAIF)
    graph.bind("foaf", FOAF)
    graph.bind("schema", SCHEMA)
    graph.bind("org", ORG)

    name = normalized["name"]
    slug = _pascal_case(name) or "UnknownPerson"
    person = URIRef(f"https://aaif.io/ontology#{slug}")

    # Vendored public vocabularies.
    graph.add((person, RDF.type, FOAF.Person))
    graph.add((person, FOAF.name, Literal(name)))
    if normalized.get("email"):
        graph.add((person, FOAF.mbox, URIRef(f"mailto:{normalized['email']}")))
    if normalized.get("url"):
        graph.add((person, FOAF.homepage, URIRef(normalized["url"])))
    if normalized.get("headline"):
        graph.add((person, SCHEMA.jobTitle, Literal(normalized["headline"])))
    if normalized.get("summary"):
        graph.add((person, RDFS.comment, Literal(normalized["summary"])))

    for position in normalized["positions"]:
        title = position.get("title", "")
        organization = position.get("organization", "")
        period = position.get("period", "")
        if organization:
            org_iri = URIRef(f"https://aaif.io/ontology#{_pascal_case(organization)}")
            graph.add((org_iri, RDF.type, ORG.Organization))
            graph.add((org_iri, FOAF.name, Literal(organization)))
            graph.add((person, ORG.memberOf, org_iri))
            if title:
                role = URIRef(
                    f"https://aaif.io/ontology#{_pascal_case(organization)}{_pascal_case(title)}"
                )
                graph.add((role, RDF.type, SCHEMA.OrganizationRole))
                graph.add((role, SCHEMA.jobTitle, Literal(title)))
                if period:
                    graph.add((role, SCHEMA.startDate, Literal(period)))
                graph.add((person, SCHEMA.worksFor, org_iri))
        elif title:
            graph.add((person, SCHEMA.jobTitle, Literal(title)))

    for skill in normalized["skills"]:
        graph.add((person, SCHEMA.knowsAbout, Literal(skill)))

    # Parallel aaif:Agent individual (flat PascalCase IRI, camelCase props).
    graph.add((AAIF.Agent, RDF.type, OWL.Class))
    graph.add((AAIF.Agent, RDFS.label, Literal("Agent")))
    agent = URIRef(f"https://aaif.io/ontology#{slug}Agent")
    graph.add((agent, RDF.type, AAIF.Agent))
    graph.add((agent, AAIF.name, Literal(name)))
    if normalized.get("headline"):
        graph.add((agent, AAIF.description, Literal(normalized["headline"])))
    if normalized.get("url"):
        graph.add((agent, AAIF.url, URIRef(normalized["url"])))
    graph.add((agent, AAIF.version, Literal("1.0.0")))
    if normalized.get("residencyRegionLock"):
        graph.add(
            (agent, AAIF.residencyRegionLock, Literal(normalized["residencyRegionLock"]))
        )

    return graph


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="profile_intake.py")
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--lock", action="store_true")
    args = parser.parse_args(argv)

    input_path: Path = args.input
    out_dir: Path = args.out

    if not input_path.is_file():
        print(refusal("PROFILE_UNREADABLE", f"{input_path} is not a readable file"),
              file=sys.stderr)
        return 2
    try:
        text = input_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        print(refusal("PROFILE_UNREADABLE", str(exc)), file=sys.stderr)
        return 2
    if not text.strip():
        print(refusal("PROFILE_EMPTY", f"{input_path} contains no content"), file=sys.stderr)
        return 2

    suffix = input_path.suffix.lower()
    try:
        if suffix == ".json":
            profile = _parse_json_profile(text)
        elif suffix == ".html" or suffix == ".htm":
            profile = _parse_html_profile(text)
        elif suffix == ".txt":
            profile = _parse_text_profile(text)
        else:
            print(refusal("PROFILE_UNREADABLE",
                          f"unsupported input format: {suffix or '(none)'}"),
                  file=sys.stderr)
            return 2
    except (json.JSONDecodeError, ValueError) as exc:
        print(refusal("PROFILE_UNREADABLE", f"malformed input: {exc}"), file=sys.stderr)
        return 2

    normalized = normalize(profile)
    try:
        admit(normalized)
    except SystemExit as exc:
        print(exc, file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "profile.json"
    ttl_path = out_dir / "profile.ttl"

    json_path.write_text(
        json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    graph = build_graph(normalized)
    ttl_path.write_text(graph.serialize(format="turtle") + "\n", encoding="utf-8")

    if args.lock:
        digest = fingerprint_paths([json_path, ttl_path], out_dir)
        lock = {
            "schema": "https://ggen.dev/marketplace/profile-intake-lock/v1",
            "algorithm": "sha256",
            "chain_rule": "fingerprint_paths/v1 length-prefixed fold",
            "files": {
                "profile.json": {"sha256": hashlib.sha256(json_path.read_bytes()).hexdigest()},
                "profile.ttl": {"sha256": hashlib.sha256(ttl_path.read_bytes()).hexdigest()},
            },
            "digest": f"sha256:{digest}",
        }
        (out_dir / "profile.lock.json").write_text(
            json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    print(f"profile-intake: wrote {json_path} {ttl_path}"
          + (" profile.lock.json" if args.lock else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
