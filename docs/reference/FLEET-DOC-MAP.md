# Reference: Fleet Documentation Map

One canonical docs entry point per repository in the 20-repo fleet. Every path below was
verified to exist on disk at authoring time (v26.10.8 campaign, 2026-10-08). When a repo's
documentation shape changes, update its line here.

## Fleet map

| Repository | Canonical docs entry point | Shape |
|---|---|---|
| `ggen-marketplace` | `docs/book.ttl` | RDF book graph; `ggen sync run` projects `book.toml` + `docs/SUMMARY.md`; nav-coverage court `tests/test_book_nav_coverage.py` |
| `xaas` | `docs/claude/diataxis/README.md` | Diátaxis tree under `docs/claude/diataxis/`; nav-coverage court post-campaign |
| `ash_graphlaw` | `documentation/README.md` | Legacy `documentation/` tree (not `docs/`) |
| `ash_pplan` | `docs/diataxis/README.md` | Diátaxis tree under `docs/diataxis/` |
| `ash_surface` | `docs/diataxis/README.md` | Diátaxis tree under `docs/diataxis/`; nav-coverage court post-campaign |
| `ash_a2a` | `docs/README.md` | `docs/` tree rooted at README; nav-coverage court post-campaign |
| `ash_affidavit` | `documentation/README.md` + `docs/diataxis/README.md` | Dual shape: legacy `documentation/` tree plus Diátaxis tree |
| `ash_r2rml` | `documentation/README.md` | Legacy `documentation/` tree (not `docs/`) |
| `ash_ex4pm` | `docs/diataxis/index.md` | Diátaxis tree rooted at `index.md` |
| `ex4pm` | `docs/README.md` | `docs/` tree rooted at README |
| `beam4pm` | `docs/README.md` | `docs/` tree rooted at README |
| `wasm4pm` | `docs/DOCUMENTATION_POLICY.md` | Policy-first: `docs/DOCUMENTATION_POLICY.md` governs the tree |
| `frozen-duckdb` | `docs/index.md` | mdBook-style `docs/index.md` |
| `affidavit` | `docs/INDEX.md` | `docs/` tree rooted at INDEX.md |
| `ferroplan` | `docs/roadmap.md` + `book/` | Roadmap plus mdBook under `book/` |
| `graphlaw` | `docs/` | Plain `docs/` tree |
| `zcode-cli` | `docs/CONFIGURATION.md` | Configuration-first `docs/` tree |
| `gymact` | `docs/index.md` | mdBook-style `docs/index.md` |
| `castle` | `README.md` | README-only: no `docs/` tree |
| `autofde-lab` | `docs/STATUS.md` | Status-first `docs/` tree |

## Nav-coverage courts

A nav-coverage court fails when a docs file on disk is not covered by the repo's navigation
source of truth. Repos with one post-campaign:

- `ggen-marketplace`: `tests/test_book_nav_coverage.py` — every file under `docs/` must have
  an `mdp:NavigationEntry` in `docs/book.ttl`; `book.toml` + `docs/SUMMARY.md` are generated
  (`rm -f book.toml docs/SUMMARY.md && ggen sync run`).
- `xaas`, `ash_surface`, `ash_a2a`: nav-coverage courts exist post-campaign (see each repo's
  `tests/`).

## See Also

- OCEL train (`beam4pm`, `ex4pm`, `wasm4pm`, `ash_ex4pm`, `autofde-lab`): object-centric
  event logs, process mining, and the WASM-carried process kernels they feed. Cross-link the
  OCEL train's log-producing repos to the WASM train's `graphlaw` kernel consumer:
  `graphlaw docs/` ↔ `wasm4pm docs/DOCUMENTATION_POLICY.md`.
- WASM train (`graphlaw`, `ash_graphlaw`, `frozen-duckdb`, `wasm4pm`): one graphlaw law
  compiled to WASM, embedded via wasmex, with `frozen-duckdb` as the frozen storage engine
  and `wasm4pm` as the process-mining consumer. Cross-link back to the OCEL train's event-log
  producers: `beam4pm docs/README.md` ↔ `graphlaw docs/`.
- Ash capability train (`ash_*` + `xaas`): Diátaxis-shaped capability repos; see
  [ash-ecosystem-mapping.md](ash-ecosystem-mapping.md).
