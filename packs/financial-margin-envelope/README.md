# financial-margin-envelope

RDF/SHACL-governed financial margin-envelope capability pack.

Semantic source: `ontology.ttl` (fme: urn:fin:margin-envelope:) — NTE
(not-to-exceed), subcontractor quote, gross-margin invariant floor
(default 0.22), breach events, and a closed typed refusal vocabulary minted
as individuals (`REFUSED_BELOW_FLOOR`, `REFUSED_NTE_EXCEEDED`,
`REFUSED_MISSING_BINDING`, `ESCALATE_MULTISIG`). Monetary amount concepts are
FIBO-aligned via `rdfs:seeAlso` (no full FIBO import).

## Structure

- `pack.toml` / `ggen.toml` — identity + pack-local self-verification manifest
- `ontology.ttl` — semantic authority (78 triples, one positive-control
  envelope ENV-001: NTE 250000 / quote 180000 / floor 0.22, computed margin 0.28)
- `shapes.ttl` — SHACL structural contract complementing the SPARQL gates
- `queries/margin_envelopes.rq` — SELECT bindings for the template
- `templates/margin_envelope.ex.tmpl` — generates an ash_pplan-compatible
  `MarginEnvelope` module: `admit/1` (fail-closed REFUSED_MISSING_BINDING,
  REFUSED_NTE_EXCEEDED, escalate-to-multi-sig below floor), `margin/1`,
  `resolve_escalation/2` multi-sig gate shape
- `gates/*.rq` — SELECT rows = violation: envelope completeness, floor range,
  and the margin law `(nte - quote)/nte >= floor`
- `verify.py` — Chicago verifier: runs all gates, then an anti-vacuity court
  (mutates quote 180000 -> 220000 and PROVES gate 030 flips to violation; a
  gate that cannot flip = VACUOUS GATE, exit 1), then spot-checks the
  generated module including a real `elixir` evaluation of `admit/1` and
  `margin/1` (admit / 0.28 / escalate) against a compiled Decimal ebin
- `generated/margin_envelope.ex` — generated consequence, never hand-edited

## Usage

Pack-local self-verification:

```bash
ggen sync run --skip-ea-admission
python3 verify.py
```

Consumers copy `ggen.toml` into their own project, bind their own envelope
individuals in their ontology, and sync.

## Verification

```bash
python3 verify.py
```

Last run: all gates 0 rows, anti-vacuity flip PASS, elixir-eval
`['admit', '0.28', 'escalate']` PASS.
