# Semantic Full-Stack Factory Pack

A reusable deterministic projection from admitted RDF application/scenario facts into a FastAPI backend, a JavaScript Next.js frontend, and a Playwright qualification court.

The pack is deliberately domain-neutral. WD Case Study 2 is only the qualification fixture.

## Invariants

- runtime intelligence is explicitly `NONE`;
- manufacture mode is `DETERMINISTIC`;
- every rendered scenario is `SELECT_CONSTRUCT_ONLY`;
- consequential disposition remains `ENGINEER_DISPOSITION_REQUIRED`;
- transitions must close over declared scenarios;
- templates manufacture consumer outputs; generated files are never authoritative pack source.

This proves code manufacture from admitted semantics. It does **not** by itself prove deployment, customer authority, or a complete Fortune-500 program.

## Consumer contract (v0.2.0)

This is a **multi-target pack**: two independent target families, each with
its own runtime. Dependencies are derived mechanically per family from
`templates/*.tmpl` imports (non-relative, non-stdlib), per the house
convention in `docs/pack-consumer-contract.md`; the `pack.toml`
`[consumer_contract]` section scopes them with per-family sub-tables:

| Family | runtime | test | optional_runtime |
|---|---|---|---|
| `[consumer_contract.backend]` | `fastapi` | `pytest`, `httpx` | `uvicorn[standard]` |
| `[consumer_contract.frontend]` | `next`, `react`, `react-dom`, `zod` | `@playwright/test` | — |

Derivation notes:

- **backend**: the only non-stdlib import in `fastapi_app.py.tmpl` is
  `fastapi` (`FastAPI`, `HTTPException`, `Query`, `CORSMiddleware`).
  `uvicorn` is never imported — it is the run process (pinned in the
  projected `requirements.txt`), so it is `optional_runtime`, not runtime.
  `backend_test.py.tmpl` imports `fastapi.testclient.TestClient`, which
  requires `httpx`; `pytest` is the runner the projected requirements file
  assumes, so both are contract `test` deps.
- **frontend**: `frontend_page.js.tmpl` bare-imports `react` and `zod`;
  `next`/`react-dom` provide the app-router shell that the projected
  `app/page.js` and `app/layout.js` run under. `@playwright/test` is the
  `test` family (e2e spec + playwright config projections), never a
  runtime import.

`[consumer_contract]` loader admission remains UNVERIFIED (P2/F4
disclosure): the key is prose-grade until the ggen loader is proven to
admit it. It does not change sync behavior.

## Qualification court

`qualification/` is a scratch consumer that renders the full stack from
`consumer.ttl` (WD Case Study 2 fixture: KNOWN / PARTIAL / UNKNOWN
scenarios, every scenario `SELECT_CONSTRUCT_ONLY`, every human gate
`ENGINEER_DISPOSITION_REQUIRED`). The court has two tiers:

1. **Frontend tier**: `tsc --noEmit --strict` (typescript 5.9) plus zod
   over the projected frontend, then an anti-vacuity flip (remove a
   projected file, expect a typed failure).
2. **Backend tier**: parse-import the projected FastAPI app with real
   `fastapi`/`httpx` installed; without those deps the tier is recorded
   as typed UNVERIFIED (parse-only), never fake-passed.

Wave-2 court receipts: `docs/jira/v26.11.5/receipts/G06.md`.
