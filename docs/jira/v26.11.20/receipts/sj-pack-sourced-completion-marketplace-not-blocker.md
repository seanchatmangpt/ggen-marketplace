# SJ pack-sourced completion — marketplace is not the finish blocker

Subject SHA: `7ad4b6db7a2c2aa8eb1b0aadd72006a65c126d0e` (marketplace `main` tip at court).  
Court identity: ambient `ggen 26.11.5` (built from tag `v26.11.5` / commit `193cc9eb`).  
Date: 2026-11-20.

## Verdict

**Marketplace does not block Semantic Jira pack-sourced completion.**

`mix semantic_jira.complete` / ggen validate consumers of
`smalt-substrate-pack`, `smalt-semconv-pack`, and
`sjira-marketplace-feedback-pack` are admitted at this tip. Residual finish
work (if any) lives outside this repository (consumer tree, alias/base pins,
xaas-fabric ALIVE ceiling) — not in pack gates, SHACL, or qualification.

## Per-pack standing

| Pack | Tip standing | Evidence |
|---|---|---|
| `smalt-substrate-pack` 26.10.14 | **VERIFIED / ALIVE** | gates 0 rows; verify unbound 0 rows; SHACL conform; mutation FLIP; `qualify_packs` ALIVE (+ terraform root verified) |
| `smalt-semconv-pack` 26.10.16 | **VERIFIED / ALIVE** | gate `010_semconv_census` 0 rows; verify unbound 0 rows; name-rename FLIP → 2 rows; `qualify_packs` ALIVE |
| `sjira-marketplace-feedback-pack` 0.1.0 | **VERIFIED / ALIVE** | gates 010–030 clean; 3/3 mutation FLIP; ontology/union/comma SHACL EXIT=0; `qualify_packs` ALIVE |

Historical igniter witness (`docs/jira/v26.10.19/receipts/smalt-completion-witness.md`
in ggen_igniter) closed substrate + semconv legs after pack-side gate repairs
(ZD-65 violation-style rewrite). Tip re-court confirms those packs remain
admitted.

## Commands / exits (paste-grade)

```text
# marketplace structural
python3 scripts/marketplace.py validate
→ EXIT 0; packs=380

# ggen 26.11.5 SHACL
ggen graph validate --files ontology.ttl --shapes shapes/mf.shacl.ttl
  (sjira) → EXIT 0; shapes_conform: true; 57 quads
union ontology∪qualification → EXIT 0; 80 quads
comma ontology.ttl,qualification/consumer.ttl → EXIT 0
ggen graph validate --files ontology.ttl --shapes shapes/smalt-shapes.ttl
  (substrate) → EXIT 0; shapes_conform: true; 2354 quads

# rdflib gates + verify unbound (SJ complete path)
smalt-substrate gates/{config_coverage,shapes-coverage}.rq → 0 rows
smalt-substrate verify/*.unbound.rq + api_admission.rq → 0 rows each
smalt-semconv gates/010_semconv_census.rq → 0 rows
smalt-semconv verify/semconv-coverage.unbound.rq → 0 rows
sjira gates/010..030 ∪ qualification/consumer → 0 rows

# mutation FLIP
semconv: rename smalt.arm.admit → .MUT → 010_semconv_census 2 rows
substrate: ConfigKey → ConfigKeyOLD → config_coverage 1 row (census-empty)
substrate: drop one apiVersion → shapes-coverage ≥1 row
sjira tests/mutations/{010,020,030}.ttl → matching gate ≥1 row (3/3)

# real manufacture court
python3 scripts/qualify_packs.py --ggen <ggen-26.11.5> \
  --pack smalt-semconv-pack --pack smalt-substrate-pack \
  --pack sjira-marketplace-feedback-pack
→ all three status=ALIVE (substrate needs terraform on PATH for TF root check)
```

## Explicit non-claims

- Does not claim `mix semantic_jira.complete` ran end-to-end in this lane
  (that court lives in ggen_igniter + consumer trees).
- Does not claim xaas-fabric ALIVE; local completion ceiling remains
  PARTIAL_ALIVE per igniter law.
- Active catalog scope (`marketplace.active.toml`, 29 packs) omits these
  packs by design; `catalog --scope all` / `show` still report
  `qualification: ALIVE`, `tier: verified`. Scope omission is not an SJ
  finish refusal.
