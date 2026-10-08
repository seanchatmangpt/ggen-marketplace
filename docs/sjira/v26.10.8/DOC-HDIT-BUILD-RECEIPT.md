# DOC-HDIT-BUILD-RECEIPT — rust-doc-hdit-pack manufacturing receipt (v26.10.8)

Lane: hdit-receipt, 2026-10-08. Pack: `packs/rust-doc-hdit-pack/` (Rust CLI + court + scaffolded
docs); extractor: `scripts/gen_doc_surface.py`. Companion metrics doc:
`DOC-HDIT-PILOT.md` (per-run tables, replays). Every SHA below re-verified via `git log`
immediately before this commit.

## 1. Build chain (all SHAs verified in-repo)

| stage | SHA | commit |
|---|---|---|
| scaffold | 928e85887 | feat(pack): rust-doc-hdit-pack scaffold (ggen-first docs + VSA verification) |
| extractor | 9444aa91f | feat(scripts): gen_doc_surface deterministic code/doc fact extractor (doc-hdit v1) |
| VSA core | 97abea822 | feat(doc-hdit): VSA + information-theory verification core |
| VSA core | 0820e63ad | fix(doc-hdit): court-file threshold parsing (Phi_halluc_max) + Chicago test suite |
| VSA core | ff9ff8284 | fix(doc-hdit): track src/bin/doc-hdit.rs (CLI) — root gitignore bin/ rule |
| P0/P2 | 549c79e42 | feat(doc-hdit): P2 public-surface scope + external-deps allowlist in court core |
| P0/P2 | 81d45b07e | feat(gen_doc_surface): is_public flag + known_external emit (DOC-HDIT-PILOT P2) |
| P0/P2 | b45155147 | docs(sjira): DOC-HDIT-PILOT P2 addendum — rescored ex4pm + ferroplan |
| grounding fix | 67a283585 | fix(doc-hdit): deterministic exact-match phantom gate + object-only grounding (P0) |
| grounding fix | 42b031cfa | fix(gen_doc_surface): v2 over-extraction filter in doc-mode claim scan (P1) |
| certify | 20aadd175 | feat(doc-hdit): certify verb — BLAKE3 chained gate receipts (osx-clnr pattern) |
| set-coverage | 910cbdba9 | docs(sjira): DOC-HDIT-PILOT P3 addendum — set-coverage S_coverage rescore |
| param cells | 884f9468e | fix(extractor): param-table cells emit identifier claims, not sentence spans |
| backticks | 6f60a988d | fix(doc-hdit): backtick reference table identifiers (claim-visible scaffolds) |
| rollout runner | 714663087 | feat(doc-hdit): fleet rollout runner |
| TS scanner | 8f8316b1e | feat(scripts): TypeScript symbol scanner for doc-hdit (v1 deterministic) |

Also cited in the pilot receipt: 8effc8a5b (extractor prose-artifact filter, P3, explicit
pathspec).

## 2. Witnessed gates

- **cargo test** (pack core): 11 → 15 tests across the build; final state 15 passed / 0 failed
  (includes P2 public-scope, external-classification, legacy-inputs-default tests). Witnessed
  at 20aadd175+.
- **pytest** (`tests/test_gen_doc_surface.py`): 5 passed after P2; 8 passed at 8effc8a5b after
  the P3 prose-artifact filter.
- **Planted-phantom control**: invented symbol (`zzz_totally_fake_symbol_zzz`) initially showed
  NO separation from real references (alignment 0.2854 vs median 0.2894) — this failure is what
  drove the P0 exact-match grounding fix; post-fix the gate distinguishes grounded vs invented.
- **ex4pm full PASS + certify**: after P3 set-coverage + param-cell fixes, ex4pm passes
  coverage (0.9693/0.90) and density (0.9980/0.65) with certify receipt **f4104bfa**
  (BLAKE3 chained gate receipts, `certify` verb at 20aadd175; receipt minted in the ex4pm
  subject repo — not a ggen-marketplace object, verify there).

## 3. Honest failures en route

- **Pilot 3-gate failure**: the first real runs failed all three gates on both pilot repos
  (ex4pm exit 1 FAIL x3, ferroplan exit 1 FAIL x3). Ground-truthing the top-5 "phantoms" per
  repo showed zero true hallucinations — the failures were metric/extractor artifacts
  (uncalibrated Phi_halluc > 1, Q_density = (log2(n)−1)/n by construction, VSA cosine measuring
  subspace geometry instead of coverage). Fixed forward via P0/P1/P2/P3; thresholds were never
  relaxed.
- **zcode tautology caught and corrected**: a zcode-class doc run initially scored against a
  claim_grounded definition that could never fire (claim subjects are doc paths, never in the
  code token set) — a tautological metric read as PASS-shaped output. Caught during
  ground-truth review and corrected to object-only grounding (67a283585) before any admission.

## 4. Standing per repo (fleet rollout audit runs)

| repo | standing | note |
|---|---|---|
| ex4pm | PASS-certified | full gate PASS; certify receipt f4104bfa |
| ash_pplan | 0.99 | rollout audit coverage |
| ash_ex4pm | 0.906 | local-script caveat: scored via a local ad hoc script, not the packaged runner |
| ferroplan | FAIL-honest | coverage 0.2392/0.90 — 1288 of 1693 public items undocumented (crucible mass); remediation list in DOC-HDIT-PILOT.md |
| zcode | FAIL-honest | below coverage gate; remediation list from rollout audit output |
| graphlaw | FAIL-honest | below coverage gate; remediation list from rollout audit output |
| frozen-duckdb | FAIL-honest | below coverage gate; remediation list from rollout audit output |
| castle | FAIL-honest | below coverage gate; remediation list from rollout audit output |

FAIL-honest rows carry per-module remediation lists from the rollout runner's top-uncovered
output (`vectorize ... --report` / audit lines); they are documentation defects, not metric
artifacts.

## 5. v2 priorities

1. **Tree-sitter extraction**: replace regex/line-heuristic scanning in `gen_doc_surface.py`
   (and the TS scanner) with tree-sitter grammars for deterministic symbol spans.
2. **Struct fields as first-class claims**: field-level public surface (not just modules/fns)
   for coverage accounting.
3. **Arity fixes**: normalize `ident/2` arity forms across Elixir and Rust claim shapes so
   qualified/arity references match set coverage exactly.
4. **Generator-identity convergence**: canonical-binary-only regen — S_coverage/Phi rescoring
   admitted only when reproduced by a frozen doc-hdit binary, so metric standing does not
   depend on whichever local build produced the number.

## Replay

```sh
git log --format='%h %s' -1 928e85887 9444aa91f 97abea822 0820e63ad ff9ff8284 \
  549c79e42 81d45b07e b45155147 67a283585 42b031cfa 20aadd175 910cbdba9 \
  884f9468e 6f60a988d 714663087 8f8316b1e 8effc8a5b
cd packs/rust-doc-hdit-pack && cargo test
pytest packs/rust-doc-hdit-pack/tests/ 2>/dev/null || pytest tests/test_gen_doc_surface.py
```
