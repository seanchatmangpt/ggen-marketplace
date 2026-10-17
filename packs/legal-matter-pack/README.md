# legal-matter-pack

Decision-simulation domain ontology for athena's private matter surface.
The RDF ontology (`ontology.ttl`, `lm:` namespace) is the source of truth;
the zod v3 `.strict()` TypeScript contract modules are projections.

## Layout

- `pack.toml` — pack identity + capabilities (requires refusal-vocabulary-pack's `rv:` pattern)
- `ontology.ttl` — classes (LegalMatter, JurorPersona, JudgeProfile, CaseSpec, Ruling, Motion, JudgeRuling, Positioning, CaseStrength, SimulationResult, CaseSpace, JurorLeanS/ExtraFactor/JurorPositioning/AggregateBreakdown), enums, one `lm:Field` row per projected zod line, the `lm:sumConstraint "100"` positioning law, the CaseSpace `lm:custodyBinding` law, and 9 typed-refusal individuals following refusal-vocabulary-pack's `rv:RefusalClass` pattern
- `queries/*.rq` — one SELECT per contract module (rows the templates project verbatim)
- `templates/*.contract.ts.tera` — Tera projections (zod enum/object/refine emission)
- `verify/*.unbound.rq` — inverted companions; ZERO ROWS is the pass condition. Deletion detectors: removing a required ontology row makes a companion fire.
- `generated/` — last render receipt (byte-exact copies of what athena consumes)

## Sync (athena side)

```bash
node /Users/sac/cai/athena/scripts/legal_gen.mjs
# = ggen sync run in this pack + byte-exact copy into
#   athena playground/src/lib/generated/legal/*.contract.ts
```

Consumers (re-export + keep logic):

- `playground/src/lib/jury/personas.ts` (JurorPersonaSchema/type)
- `playground/src/lib/judge/profile.ts` (Lean/JudgeProfile/CaseSpec/Motion/JudgeRuling schemas + types)
- `../../playground/src/lib/simulation/engine.ts` (Position/JurorLean/CaseStrength/Positioning/JurorPositioning/AggregateBreakdown/SimulationResult)
- `playground/src/lib/case-space/space.ts` (CaseSpaceIdentitySchema admission)

## Verify

```bash
cd /Users/sac/smalt && mix ggen_igniter.verify --pack /Users/sac/ggen-marketplace/packs/legal-matter-pack
# "verify: 0 unbound facts" = green (zero rows from every companion)
```

Companions: field-orphan, enum-totality, positioning-sum, custody-binding,
refusal-totality. All written WITHOUT `FILTER NOT EXISTS` (unsupported by the
sparql 0.3.12 engine) using the OPTIONAL + `FILTER(!bound(...))` polarity from
smalt-substrate-pack's `defaults-bijection.unbound.rq` precedent.
