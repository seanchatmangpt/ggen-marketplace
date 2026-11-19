# Semantic Jira → Marketplace Feedback Pack

Standing: VERIFIED

See `STANDING.md` for exact commands and exit codes (GAP follow-up 2026-11-19,
ggen 26.11.5). Preferred SHACL court is the **union** file
(`ontology.ttl`∪`qualification/consumer.ttl`); comma `--files` also EXIT=0
after consumer carries local `mf:DeltaState` individuals + typed
`recurrenceCount`.

## Evidence path (coordinator court)

1. `cat ontology.ttl qualification/consumer.ttl > /tmp/mf-union.ttl && ggen graph validate --files /tmp/mf-union.ttl --shapes shapes/mf.shacl.ttl` (preferred); also `ontology.ttl,qualification/consumer.ttl` comma form
2. Per-gate rdflib (any returned row = refusal):
   - ontology ∪ `qualification/consumer.ttl` → **0** rows on `gates/010..030`
   - ontology ∪ each `tests/mutations/*.ttl` → **≥1** row on the paired gate
3. Scratch `ggen sync run --skip-ea-admission` projecting `templates/010_marketplace_backlog.md.tera`
4. Peer packs when composing end-to-end courts: Industry Closure vocabulary
   (`ic:`) + Semantic Jira / requirements work-order types (`req:WorkOrder`).
   Absence of those ontologies → **BLOCKED:missing-peer-ontology**, not PASS.

This pack owns the feedback edge that turns an Industry Closure residual into
durable marketplace capital.

```text
future requirement
  -> Industry Closure
  -> exact residual
  -> Semantic Jira work order
  -> marketplace capability delta
  -> pack / ontology / verifier change
  -> requalification
  -> residual closed
```

A residual is not an implementation permission. It is a typed statement of what
the current closure frontier cannot yet represent or manufacture.

## Invariants

- every unresolved `ic:ClosureResidual` has an admitted Semantic Jira work order;
- the work order grants only `SELECT_CONSTRUCT_ONLY` authority;
- every work order points at a marketplace capability delta;
- backlog rank is evidence-bearing: recurrence and impact are explicit facts;
- a residual cannot be marked resolved until a realized pack and independent
  requalification evidence are bound to the delta;
- requalification expands the closure frontier for later requirements instead
  of recording a one-off project exception.

## Layout

- `ontology.ttl` — `mf:` vocabulary
- `shapes/mf.shacl.ttl` — SHACL NodeShapes (under `shapes/`; root `shapes.ttl` refused)
- `gates/*.rq` — fail-closed SPARQL twins
- `queries/marketplace_backlog.rq` — backlog SELECT (template twin)
- `templates/010_marketplace_backlog.md.tera` — markdown backlog projection
- `qualification/consumer.ttl` — positive consumer (0-row gate court)
- `tests/mutations/*.ttl` — one falsifier family per gate
- `pack.toml` — identity

This is intentionally not a Jira SaaS integration. Semantic Jira is the
machine-readable work-order contract; Jira Cloud may be one projection of it.

Authority ceiling: `SELECT_CONSTRUCT_ONLY`. Coordinator owns sync and courts.
