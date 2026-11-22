# STATUS — htn-fond-powl2-compiler-pack

Standing: **UNVERIFIED / scaffold**

| Claim | Reality |
|---|---|
| Live HTN-FOND → `%Smalt.Powl2{}` compiler pack | **No** — scaffold only |
| Codegen / `.tera` manufacture | **Absent** — `templates/` empty |
| SPARQL query bodies under `queries/` | **Absent** — dir empty |
| Split ontology under `ontology/` | **Absent** — dir empty; root `ontology.ttl` vocabulary stub only |
| Gate witnesses | **Absent** — `qualification/witnesses/` empty |
| `fibo/packs.toml` pin | **Forbidden** until twice-qualified |
| DO / admit authority | **None** (manufacture fence only) |

Present on disk (honest inventory):

- `CONSTRAINTS.md` — go-locks (bcinr tape, three 64-bit surfaces, cgap marking,
  736 B PCCf, graphlaw SRL leaf, SELECT-only gates, cindy prefixes)
- `pack.toml` — `[pack]` = name / version / description only
- `ontology.ttl` — prefix-aligned vocabulary scaffold (no individuals / VIN domain)
- `gates/*.rq` — `SELECT ?violation ?subject` stubs (0 rows = PASS while graph empty)
- `RECEIPT.md` — scaffold receipt

Do **not** fake codegen to clear FAKE-ALIVE. Flip this file only from a receipt
citing real templates + twice-green
`python3.11 scripts/marketplace.py check htn-fond-powl2-compiler-pack`.
