#!/usr/bin/env python3
"""Derive an MCP-surface ontology from AutoFDE Lab's REAL hand-written bridge.

Sources (read, never invented):
  vendor/autofde-lab/src/autofde_lab/openclaw_bridge.py  -> _TOOL_SPECS (names,
      descriptions, JSON input schemas) and runtime.TOOL_NAME_PREFIX
  vendor/autofde-lab/integrations/openclaw/openclaw.plugin.json -> toolMetadata
      replaySafe flags

_TOOL_SPECS is a module-level literal; we import the module's AST rather than the
module itself so no scikit-decide runtime import is required.
"""
import ast
import json
import pathlib
import sys

ROOT = pathlib.Path("/Users/sac/gym-ecosystem/vendor/autofde-lab")
BRIDGE = ROOT / "src/autofde_lab/openclaw_bridge.py"
PLUGIN = ROOT / "integrations/openclaw/openclaw.plugin.json"

tree = ast.parse(BRIDGE.read_text())
raw = {}
for node in tree.body:
    if isinstance(node, ast.Assign):
        name = node.targets[0]
        if isinstance(name, ast.Name) and name.id in ("_SUBJECT_SCHEMA", "_TOOL_SPECS"):
            raw[name.id] = node.value


class _Inline(ast.NodeTransformer):
    """_TOOL_SPECS references _SUBJECT_SCHEMA by name; splice the real node in."""

    def visit_Name(self, node):
        return raw["_SUBJECT_SCHEMA"] if node.id == "_SUBJECT_SCHEMA" else node


specs = ast.literal_eval(_Inline().visit(raw["_TOOL_SPECS"]))
assert len(specs) == 4, specs

plugin = json.loads(PLUGIN.read_text())
meta = plugin["toolMetadata"]
# plugin.json keys carry the legacy skdecide_ prefix.
replay = {k.split("_", 1)[1]: v["replaySafe"] for k, v in meta.items()}

NS = "autofde_lab"
lines = [
    "@prefix dct: <http://purl.org/dc/terms/> .",
    "@prefix prov: <http://www.w3.org/ns/prov#> .",
    "@prefix sosa: <http://www.w3.org/ns/sosa/> .",
    "",
    "# DERIVED by scripts/derive_autofde.py from AutoFDE Lab's real OpenClaw bridge.",
    "# Every title, description, parameter name and JSON type below is read out of",
    "# src/autofde_lab/openclaw_bridge.py::_TOOL_SPECS; every replaySafe flag out of",
    "# integrations/openclaw/openclaw.plugin.json::toolMetadata. Nothing is invented.",
    "",
    "<urn:autofde-lab:mcp:server>",
    f'    a <urn:gymmcp:McpServer> ;',
    f'    dct:identifier "{NS}" ;',
    '    dct:title "scikit-decide" ;',
    '    dct:hasVersion "0.1.0" ;',
    "    prov:wasDerivedFrom <urn:autofde-lab:src:openclaw_bridge.py> .",
    "",
]
for spec in specs:
    name = spec["name"]
    rs = replay[name]
    # Consequence: the plugin's own metadata is the ground truth. A tool the real
    # bridge marks replaySafe is observational READ; one it marks not-replay-safe
    # (and optional) constructs or executes, so it is consequential DO.
    consequence = "read" if rs else "do"
    base = f"urn:autofde-lab:mcp:op:{name}"
    lines.append(f"<{base}>")
    lines.append("    a sosa:Procedure ;")
    lines.append(f'    dct:title "{name}" ;')
    lines.append(f'    dct:description "{spec["description"]}" ;')
    lines.append(f"    dct:type <urn:gymact:consequence:{consequence}> ;")
    lines.append(f"    <urn:gymmcp:replaySafe> {str(rs).lower()} ;")
    if consequence == "do":
        lines.append("    <urn:gymmcp:requiresAdmission> true ;")
    props = spec["inputSchema"].get("properties", {})
    required = set(spec["inputSchema"].get("required", []))
    params = sorted(props)
    for i, p in enumerate(params):
        term = ";" if i < len(params) - 1 else "."
        lines.append(f"    <urn:gymmcp:hasParameter> <{base}:param:{p}> {term}")
    if not params:
        lines[-1] = lines[-1].rstrip(" ;") + " ."
    lines.append("")
    for p in params:
        schema = props[p]
        jt = schema.get("type") or ("string" if "enum" in schema else "object")
        lines.append(f"<{base}:param:{p}>")
        lines.append("    a <urn:gymmcp:Parameter> ;")
        lines.append(f'    dct:identifier "{p}" ;')
        lines.append(f'    dct:type "{jt}" ;')
        lines.append(f"    <urn:gymmcp:required> {str(p in required).lower()} .")
        lines.append("")

out = pathlib.Path(sys.argv[1])
out.write_text("\n".join(lines))
print(f"wrote {out} ({len(specs)} operations, {sum(1 for l in lines if 'a <urn:gymmcp:Parameter>' in l)} parameters)")
