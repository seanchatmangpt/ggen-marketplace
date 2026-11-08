# CSCB Emission Hardening Receipt (Lane R15, AR6 P0/P1 closure)

Standing: PASS

Date: 2026-11-07 · Lane: R15 (P0 critical fix) · Repo: /Users/sac/ggen-marketplace
(no git commands run, per lane contract)

## Fixes per AR6 item

| AR6 item | Fix, layer, file |
|---|---|
| P0 label injection (RCE) | Gate 040: label charset law ^[A-Za-z0-9 _-]{1,64}$, sync-refusing (FM-LAW-018, pre-write) — gates/040_label_safety.rq, wired into ggen.toml [validation].gates |
| P0 (shape law) | SHACL sh:pattern + sh:maxLength 64 on ArcStage rdfs:label — shapes.ttl cscb:ArcStageShape |
| P1 rogue stages | Query scoped to ?arc a cscb:BenchmarkArc ; cscb:hasStage ?stage — queries/runner_profile.rq |
| P1 (refusal, not just omission) | Gate 050: typed ArcStage never arc-bound refuses the sync — gates/050_orphan_stage.rq |
| P2 10MB label | Same gate 040 (maxLength 64 in the charset law) — gates/040_label_safety.rq |
| Defense-in-depth | stage_name_rust: backslash/quote/control chars SPARQL-escaped in query; template interpolates only the escaped form — queries/runner_profile.rq + templates/rust/main.rs.tmpl |

ggen sync validation consumes SPARQL gates only ([validation].shacl was
removed upstream — legacy use is loud FM-LAW-017), so shapes.ttl is enforced
via the pyshacl path in verify.py and the gate form is the sync enforcement.

## Attack replay matrix (scratch copy /tmp/r15-court/pack, ggen 26.11.4)

| Attack (AR6 class) | Before R15 | After R15 |
|---|---|---|
| Hostile label `Warmer" ; cscb:pwned cscb:x ; rdfs:label "` | sync exit 0, payload compiled into main.rs (AR6: "written") | REFUSED exit 1, FM-LAW-018 gate 040, emitted sha256 unchanged |
| Rogue stage cscb:S7 (typed, never arc-bound) | sync exit 0, excluded silently | REFUSED exit 1, FM-LAW-018 gate 050, emitted sha256 unchanged |
| 10MB label (valid Turtle) | reached emission | REFUSED exit 1, FM-LAW-018 gate 040, emitted sha256 unchanged |
| Depth-2 witness: gates 040/050 bypassed + hostile label | payload into Rust literal | sync exit 0 but payload inert — emitted as escaped string literal; emitted crate `cargo check` exit 0 |

Before-column witness: pre-R15 config (gates 010/020/030 only) replayed —
injection synced exit 0 with "written" main.rs (matches AR6's finding).

## Commands / exits (all real runs)

- clean sync (scratch): `ggen sync --skip-ea-admission` → 0, all outputs
  "unchanged: content identical"
- attacks 1/2/3: exit 1 each, emitted sha256 -c untouched each
- depth-2 witness: bypassed-gates sync exit 0, `cargo check` exit 0
- canonical pack: verify.py → exit 0 (17 PASS lines incl. label-injection,
  orphan-stage, and emitted-label courts); `ggen sync --skip-ea-admission` → 0
  (all four outputs byte-identical); `cargo test` (emitted_rust) → 1 passed,
  exit 0
- repo: `python3.11 scripts/marketplace.py validate` → exit 0
  (355 packs / 2052 native gates)

## Pre-existing defects fixed en route (canonical pack was un-syncable)

- ontology.ttl: 6 rdfs:comment single-quote literals with raw newlines
  (invalid Turtle) → triple-quoted; parses clean (177 triples)
- shapes.ttl: 7 sh:message literals same defect → triple-quoted; parses clean
  (142 triples)
- ggen projection law: only SELECT-declared variables reach the Tera context —
  the escaping BIND must expose `?stage_name_rust` in the SELECT list.

Standing: PASS — every claim above backed by the listed command + exit.
