# fastmcp-pack

Ontology-driven FastMCP server generation (ggen marketplace pack). Projects a
runnable Python MCP server from `fmcp:Server` / `fmcp:Tool` RDF individuals —
typed tools, descriptions, arguments, and deterministic tool behavior.

## Projection surface

Exactly one file: `src/fastmcp_server.py` (generated, do not hand-edit).

## Consumer contract

Declare `fmcp:Server` and `fmcp:Tool` individuals in your own RDF graph
(your namespace works — the gate checks are namespace-exact on class and
property IRIs), then compose the pack:

```toml
[project]
name = "my-consumer"

[ontology]
source = "fixture.ttl"

[templates]
dir = "templates"

[packs]
fastmcp-pack = { path = "<path-to>/packs/fastmcp-pack" }
```

`ggen sync run --skip-ea-admission` renders `src/fastmcp_server.py`: one
`@mcp.tool(...)` function per `fmcp:Tool`, `FastMCP("<server name>")` from the
`fmcp:Server` individual.

### Runtime dependencies

Derived mechanically from template imports: `runtime = ["fastmcp"]`. The
generated server imports only `fastmcp` (FastMCP 3.x API) plus stdlib.
`pip install fastmcp` is the consumer's only runtime obligation. Transport,
auth, deployment, and any hand-written additional tools are consumer-side.

## Gates

`gates/010_admission.rq` — SPARQL admission gate over the merged graph; any
row is a refusal. Enforces: servers carry name, hasTool, title, description;
tools carry name, function, argument, argumentDescription, returnTemplate,
description; `fmcp:hasTool` targets are `fmcp:Tool`; `fmcp:function` and
`fmcp:argument` are valid Python identifiers.

## Court (v0.2.0 qualification)

Scratch consumer (`/tmp/g13-consumer`, disposable) with consumer-namespace
individuals (`ex:g13-server` + `ex:hello-tool`) composed via `[packs]` path:

- `ggen sync run --skip-ea-admission` → exit 0, wrote `src/fastmcp_server.py`
  (2 tools: pack's `greet` + consumer's `hello`).
- `python3 -m py_compile src/fastmcp_server.py` → exit 0.
- Import + `mcp.list_tools()` → `['greet', 'hello']`; direct calls return
  deterministic strings (`'Hello, World!'`, `'Hello, G13!'`) on fastmcp
  3.4.6 / Python 3.14.3.
- Anti-vacuity flip: clean venv without fastmcp → `ModuleNotFoundError: No
  module named 'fastmcp'` (typed). pip tier: venv `pip install fastmcp` →
  re-import passes (see receipts/G13.md for the exit-checked outcome).

Receipt: `docs/jira/v26.11.5/receipts/G13.md`.
