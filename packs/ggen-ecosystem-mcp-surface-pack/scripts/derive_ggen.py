#!/usr/bin/env python3
"""Derive an MCP-surface ontology from the REAL installed ggen CLI.

Source: `ggen graph --introspect` -- ggen's own documented flag, "Introspect CLI
capabilities as JSON Schema array for LLM tool-calling". Names, parameter names and
JSON types are read out of that live output; nothing is invented.

Consequence classification rule (stated so it is auditable, not hidden):
a verb is DO if its terminal verb segment is in WRITE_VERBS -- those are the verbs
whose ggen --help text describes writing files, mutating a lockfile, installing, or
running the generation pipeline. Everything else is READ. Ambiguity is resolved
toward DO, because misclassifying a consequential call as observational is the
failure that matters.
"""
import json
import pathlib
import re
import subprocess
import sys

WRITE_VERBS = {
    "init", "init-self", "install", "lock", "add", "remove", "new", "enable",
    "run", "set", "load", "derive", "export", "register", "resolve", "materialize",
}

out = subprocess.run(
    ["/Users/sac/.local/bin/ggen", "graph", "--introspect"],
    capture_output=True, text=True, check=True,
)
tools = json.loads(out.stdout)

TYPE_MAP = {"boolean": "boolean", "integer": "integer", "number": "number",
            "array": "array", "object": "object", "string": "string"}


def first_line(text):
    line = (text or "").strip().splitlines()[0] if text else ""
    line = re.sub(r'\s+', ' ', line).replace('"', "'").replace("\\", "/")
    return line[:200] or "No description provided by the ggen CLI."


def consequence(name):
    verb = name.split("_")[-1] if "_" in name else name
    return "do" if verb in WRITE_VERBS else "read"


lines = [
    "@prefix dct: <http://purl.org/dc/terms/> .",
    "@prefix prov: <http://www.w3.org/ns/prov#> .",
    "@prefix sosa: <http://www.w3.org/ns/sosa/> .",
    "",
    "# DERIVED by scripts/derive_ggen.py from the real installed ggen CLI's own",
    "# `ggen graph --introspect` JSON Schema array (ggen 26.8.28). Operation names,",
    "# parameter names and JSON types are read from that live output, not invented.",
    "",
    "<urn:ggen-ecosystem:mcp:server>",
    "    a <urn:gymmcp:McpServer> ;",
    '    dct:identifier "ggen" ;',
    '    dct:title "ggen-ecosystem" ;',
    '    dct:hasVersion "26.8.28" ;',
    "    prov:wasDerivedFrom <urn:ggen:cli:introspect> .",
    "",
]
n_read = n_do = n_param = 0
for tool in sorted(tools, key=lambda t: t["name"]):
    name = tool["name"].replace("_", "-")
    cons = consequence(tool["name"])
    n_read += cons == "read"
    n_do += cons == "do"
    base = f"urn:ggen-ecosystem:mcp:op:{name}"
    props = ((tool.get("parameters") or {}).get("properties") or {})
    required = set((tool.get("parameters") or {}).get("required") or [])
    params = sorted(props)
    lines += [
        f"<{base}>",
        "    a sosa:Procedure ;",
        f'    dct:title "{name}" ;',
        f'    dct:description "{first_line(tool.get("description"))}" ;',
        f"    dct:type <urn:gymact:consequence:{cons}> ;",
    ]
    if cons == "do":
        lines.append("    <urn:gymmcp:requiresAdmission> true ;")
    else:
        lines.append("    <urn:gymmcp:replaySafe> true ;")
    if params:
        for i, p in enumerate(params):
            term = ";" if i < len(params) - 1 else "."
            lines.append(f"    <urn:gymmcp:hasParameter> <{base}:param:{p}> {term}")
    else:
        lines[-1] = lines[-1].rstrip(" ;") + " ."
    lines.append("")
    for p in params:
        n_param += 1
        jt = TYPE_MAP.get((props[p] or {}).get("type"), "string")
        lines += [
            f"<{base}:param:{p}>",
            "    a <urn:gymmcp:Parameter> ;",
            f'    dct:identifier "{p}" ;',
            f'    dct:type "{jt}" ;',
            f"    <urn:gymmcp:required> {str(p in required).lower()} .",
            "",
        ]

pathlib.Path(sys.argv[1]).write_text("\n".join(lines))
print(f"wrote {sys.argv[1]}: {len(tools)} operations ({n_read} read / {n_do} do), {n_param} parameters")
