# QUALIFICATION — ashdspy-pack 0.1.0

All evidence below is WITNESSED execution from episode ASHDSPY-001 lane 1,
2026-09-25, not inspection. Falsifier harness:
`MIX_BUILD_ROOT=_build-lane1 mix run ~/.zcode/workspace/default/ashdspy-001/lane-1/falsify_gates.exs`
(run from `~/ggen_igniter`, engines sparql 0.3.12 + oxigraph via GgenIgniter).
Real-binary admission ran through installed ggen 26.9.18.

## 1. Clean half — 0 rows everywhere (anti-vacuity: clean input admitted)

Conforming graphs: the pack's own `ontology.ttl` (including the shipped
ticket-triage fixture) and `qualification/fixtures/pos_ticket_triage_clean.ttl`.

| graph | gate | sparql 0.3.12 | oxigraph |
|---|---|---|---|
| ashdspy-pack-ontology | 010_closed_lattice | 0 rows | 0 rows |
| ashdspy-pack-ontology | 020_court_required_before_select | 0 rows | 0 rows |
| ashdspy-pack-ontology | 030_known_implies_no_llm | 0 rows | 0 rows |
| ashdspy-pack-ontology | 040_receipt_shape | 0 rows | 0 rows |
| pos_ticket_triage_clean | 010_closed_lattice | 0 rows | 0 rows |
| pos_ticket_triage_clean | 020_court_required_before_select | 0 rows | 0 rows |
| pos_ticket_triage_clean | 030_known_implies_no_llm | 0 rows | 0 rows |
| pos_ticket_triage_clean | 040_receipt_shape | 0 rows | 0 rows |

## 2. Violating half — every gate fires (anti-vacuity: mutated input refused)

| fixture | gate | sparql 0.3.12 | oxigraph | first offending row |
|---|---|---|---|---|
| neg_open_lattice_implementation | 010 | 2 rows | 2 rows | ex:mystery, bare_implementation_outside_lattice (+ ex:ghost, routed_implementation_without_lattice_type) |
| neg_route_without_verdict | 020 | 1 row | 1 row | ex:unverifiedRoute |
| neg_llm_despite_known | 030 | 1 row | 1 row | ex:llmRoute / ex:knownAlt=ex:ruleImpl |
| neg_route_missing_digests | 040 | 2 rows | 2 rows | ex:digestlessRoute, evidenceDigest + verdictDigest |

Injection falsifiers on a mutated copy of the shipped ontology (mutate must
fire, unmutated copy stays clean): injected bare `ashdspy:Implementation` +
route → 010 fires 2 rows both engines; injected LLMImplementation route over
the passing rule rung → 030 fires 1 row both engines.

Verdict: `ALL FALSIFIER CHECKS PASSED` (harness exit 0; the harness
`exit({:shutdown, 1})` on any failure).

## 3. Real admission — installed ggen 26.9.18, throwaway consumer

Consumer manifest (outside the marketplace repo,
`~/.zcode/workspace/default/ashdspy-001/lane-1/ggen-consumer/ggen.toml`,
`[packs] ashdspy-pack = { name = "ashdspy", path = ".../packs/ashdspy-pack" }`,
consumer source = fixture TTL):

- `ggen sync run` on the clean fixture: exit 0; all four gates PASS;
  `generated/lattice_summary.json` rendered from the union graph (template
  witnessed = FM-PACK-005 satisfied).
- Each neg fixture as consumer source: exit 1 with `[FM-PACK-013] pack
  'ashdspy-pack' gate '<name>' refused the sync`, naming the first violating
  row (010: 2 rows; 020: 1; 030: 1; 040: 2). The refusal half is witnessed by
  the real binary, not only the harness.

## 4. Marketplace contract

`python3.11 scripts/marketplace.py validate` → exit 0
(`validated packs=332 manifests=332 ontologies=490 templates=1877
native_gates=1561 verifier_gates=42`). Catalog determinism double-run:
`catalog > a; catalog > b; cmp a b` → identical; `fingerprint` → exit 0.

## 5. Engine / failed-edge notes recorded during qualification

- `RDF.Description.new(subject, [pairs])` (list-of-pairs init) silently
  produces an EMPTY description in rdf 3.0.1 — triple count unchanged;
  injections must use `RDF.Description.new(subject)` + chained `add/2` with
  explicit `{RDF.type(), ...}` tuples (extends the lane-5 rdf law).
- sparql 0.3.12 accepted every portable shape used here (OPTIONAL +
  group-level `FILTER(!BOUND(...))` chains, `VALUES` inside `OPTIONAL`,
  group-level `FILTER(BOUND(...))` for positive existence) — no
  FILTER-EXISTS forms anywhere in the pack.
