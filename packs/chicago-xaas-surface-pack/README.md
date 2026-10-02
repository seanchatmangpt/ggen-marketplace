# chicago-xaas-surface-pack

Deterministic marketplace renderer for the XaaS v26.10.1 Chicago demo surface
(MARKETPLACE_RENDER.md contract, RESOLUTIONS R1/R2/R3). Manufactures four JSON
projections from the canonical sJira graphs — nothing about Chicago views is
hand-authored anywhere downstream. Every projection carries `authorityClaim:
"NONE"`, `generated: true`, the exact subject literal, source digests and
generator identity; every rendered standing is `UNKNOWN` until a real receipt
binds observed execution (RESOLUTIONS R8).

## Subject

`urn:chicago:agentic-payment:purchase-001` (semantic/demo entity — no real
payment rail is implied and none is created).

## Layout

- `ontology.ttl` — pack ontology header (catalog + semantic identity only; no
  duplicated canonical bytes).
- `source/goal.ttl`, `source/chicago.ttl`, `source/projections.ttl` — the
  canonical XaaS graphs (`docs/sjira/v26.10.1/`) vendored **byte-identically**
  (cp; `cmp`-checked). Edit upstream, re-vendor, never hand-edit a copy.
- `source/narrative.ttl` — pack-authored projection facts: executive narrative
  (audience/headline/customerProblem/desiredOutcome/semanticPath), layer
  contract-id slugs, scenario polarity, per-case failure recovery. Composed
  only from claims already in the canonical graphs; no outcomes pre-judged.
- `source/provenance.ttl` — sha256 digest chain for the four render inputs.
  Regenerate with `shasum -a 256` after any re-vendoring; never hand-edit.
- `queries/*.rq` — strict-mode SPARQL (SELECT ending in `ORDER BY`); UNION
  row-shapes keyed by `?rowKind`.
- `templates/*.json.tmpl` — Tera emitters for the pinned R2/R3 schemas.
- `ggen.toml` — pack-local render manifest (writes under `generated/` only).
- `consumer/ggen.toml` — consumer manifest run from the XaaS root; reads the
  CANONICAL `docs/sjira/v26.10.1/` TTLs, writes `priv/chicago/chicago.*.json`.
- `gate-court.toml` — witness court config for `gates/` (L3): SPARQL ASK gates
  where true = violation, with same-stem pass/fail witnesses under
  `test/fixtures/witnesses/{pass,fail}/`; typed refusals `REFUSED_CHICAGO_*`.
- `gates/`, `test/` — owned by the falsifier lane (empty shell here).

## Layer contract ids

| graph IRI | contract id | boundary | required |
|---|---|---|---|
| `chi:layer-sjira` | `sjira` | Core | true |
| `chi:layer-graphlaw` | `graphlaw` | Core | true |
| `chi:layer-sa2a` | `sa2a` | Core | true |
| `chi:layer-pplan` | `pplan` | Core | true |
| `chi:layer-xaas` | `xaas` | Core | true |
| `chi:layer-ocel` | `ex4pm` | Core | true |
| `chi:layer-beam4pm` | `beam4pm` | Core | true |
| `chi:layer-affidavit` | `affidavit` | Core | true |
| `chi:layer-surface` | `ashsurface` | LastMile | true |
| `chi:layer-marketplace` | `marketplace` | LastMile | true |
| `chi:layer-wasm4pm` | `wasm4pm` | Successor | false |
| `chi:layer-castle` | `castle` | Successor | false |

## Render law

```
source graph (vendored, digest-chained)
  -> SPARQL SELECT ... ORDER BY
  -> Tera template (pinned schema)
  -> generated artifact (authority NONE)
  -> second render -> byte identity
  -> pack gates + consumer validation
  -> receipt
```

Pack self-test:

```
cd packs/chicago-xaas-surface-pack && ggen sync run   # twice; diff generated/
```

Consumer render (coordinator-owned seam, from the XaaS canonical checkout):

```
cd ~/xaas && ggen sync run   # with consumer/ggen.toml installed as ggen.toml
```

The consumer commit of `priv/chicago/*.json` must be byte-reproducible by that
render. Fail-closed refusal targets (enforced by gates, RESOLUTIONS R5 /
MARKETPLACE_RENDER.md): missing exact subject; duplicate layer ids; missing
capability id; projection authority other than NONE; required layer without a
repository owner; a standing claim not backed by an input receipt; subject
drift across the four outputs; nondeterministic second render.
