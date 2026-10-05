#!/usr/bin/env python3
"""
Projection runner script to project aaif-vanilla-pack templates into concrete artifacts
using rdflib and jinja2, conforming strictly to vanilla AAIF standards.
Supports configurable fixture source and output target directory.

RETIRED: the modern projection path is `ggen sync run` driven by ggen.toml
in this pack directory (see tests/test_aaif_vanilla_pack_court.py::TestRealGgenSyncReplay).
Pack templates no longer carry render frontmatter, so this script emits 0
manifests by design and is retained only as a retirement witness.
"""

import argparse
import os
import re
import sys
from pathlib import Path
import rdflib
import jinja2

PACK_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = PACK_DIR / "templates"
FIXTURES_DIR = PACK_DIR / "fixtures"

def render_pack(fixture_path: Path, output_dir: Path) -> dict:
    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture not found: {fixture_path}")

    g = rdflib.Graph()
    g.parse(str(fixture_path), format="turtle")
    g.parse(str(PACK_DIR / "ontology.ttl"), format="turtle")

    jinja_env = jinja2.Environment()
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered_files = {}

    for tmpl_path in sorted(TEMPLATES_DIR.glob("*.tmpl")):
        content = tmpl_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue

        parts = content.split("---", 2)
        header = parts[1]
        body = parts[2].lstrip("\n")

        m_to = re.search(r'to:\s*"([^"]+)"', header)
        if not m_to:
            continue
        rel_target = m_to.group(1)

        m_sparql = re.search(r'sparql:\s*\n\s*(\w+):\s*\|\n(.*)', header, re.DOTALL)
        context = {}
        if m_sparql:
            alias = m_sparql.group(1)
            raw_query = m_sparql.group(2)
            query_lines = [line.strip() for line in raw_query.splitlines()]
            query = " ".join(query_lines)

            q_res = list(g.query(query))
            if q_res:
                first_row = q_res[0]
                row_dict = {str(var): str(val) for var, val in first_row.asdict().items()}
                context.update(row_dict)
                context[alias] = row_dict

        out_path = output_dir / rel_target
        out_path.parent.mkdir(parents=True, exist_ok=True)

        template = jinja_env.from_string(body)
        rendered = template.render(**context)

        out_path.write_text(rendered, encoding="utf-8")
        rendered_files[rel_target] = rendered

    return rendered_files

def main():
    parser = argparse.ArgumentParser(description="Render AAIF Vanilla Pack")
    parser.add_argument("--fixture", type=Path, default=FIXTURES_DIR / "marketplace_agent.ttl",
                        help="Path to Turtle RDF fixture")
    parser.add_argument("--out", type=Path, default=PACK_DIR / "dist",
                        help="Output directory for generated manifests")
    args = parser.parse_args()

    print(f"Rendering {PACK_DIR.name} with fixture: {args.fixture.name} -> {args.out}...")
    rendered = render_pack(args.fixture, args.out)
    for target in rendered:
        print(f"  Emitted: {target}")
    print(f"Materialized {len(rendered)} AAIF manifests successfully.")

if __name__ == "__main__":
    main()
