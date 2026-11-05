# canonical-ash-projection-generator

ggen pack projecting the canonical Ash semantic map as Turtle:
`generated/ash/semantic_map.ttl` (resources, attributes, Ash types, primary
keys, semantic predicates, source digests) and
`generated/ash/semantic_map_a2a.ttl` (A2A capability surface —
`apg:Skill`/`apg:SkillArgument` individuals under
`<urn:ash-a2a:vocab:>` / `<https://a2a-protocol.org/ontology#>`, grounded in
the compiled capability index of `lib/ash_a2a/capability_index/compiler.ex`).

The pack ships an ontology (`ontology.ttl`), projection SPARQL queries
(`queries/`), cardinality gates (`gates/`), and three render templates under
`templates/`.

## Consumer Contract (v0.3.0)

Derived mechanically from `templates/` content: an import/require/from census
over all three templates returns **zero code imports** — the pack projects
Turtle only, so `runtime = []` in `[consumer_contract]`. No hex or npm
package is required to consume the outputs.

What the consumer provides:

- **Vocabulary individuals** (`peer_context`): the consumer ontology must
  declare the `apg:` individuals its profile uses — `ProjectionProfile`,
  `Resource`, `Attribute`, `Skill`, `SkillArgument` — with `moduleName`,
  `attributeName`, `ashType`, `primaryKey`, `semanticPredicate`,
  `skillId`, `skillAction`, `consequence`, `authorityGate` literals.
- **Render runtime**: `ggen sync run` (ggen >= 26.9.28) with a `[packs]`
  path reference; renders both `.ttl` outputs.
- **Elixir tier**: the projected TTL is parsed by `AshA2A.Semantic` code
  inside the consumer app itself (`ash_a2a`); the pack pins no hex deps.
  Without a compiled Elixir consumer, the Elixir tier is honestly
  **UNVERIFIED** at pack level — structural validity is courted via
  rapper/rdflib instead.

Failure modes:

- A resource without an explicit `apg:primaryKey true` attribute is refused
  by gate `gates/020_primary_key.rq` (fail-closed, non-vacuous — see
  Verification Court).
- A skill missing `skillId` / `skillAction` / `consequence`, an ungated
  resource link, or a malformed `SkillArgument` is refused by
  `gates/030_skill_shape.rq`.
- Duplicate skill ids are refused by `gates/040_skill_id_uniqueness.rq`.

## Verification Court

Per the shadcn v0.2.0 / F3 house pattern (receipt:
`docs/jira/v26.11.5/receipts/G10.md`):

1. `rapper -q -i turtle packs/canonical-ash-projection-generator/ontology.ttl`
   — parse gate on pack ontology, must exit 0.
2. Scratch consumer at `/tmp/g10-court`: consumer `ggen.toml` binding the
   pack by path + a witness ontology declaring one `apg:ProjectionProfile`,
   one gated `apg:Resource` with a primary-key attribute and one
   `apg:Skill` with two `apg:SkillArgument`s → `ggen sync run --skip-ea-admission`
   must exit 0 and write both `generated/ash/*.ttl` files.
3. Structural validity: `rapper` / rdflib parse both projected TTLs — must
   exit 0 (TTL parse tier).
4. Anti-vacuity flip: `gates/020_primary_key.rq` run via rdflib on the
   witness graph → 0 rows (baseline); strip the primary-key triple → 1 row
   naming the resource. The gate flips; not vacuous.
5. Elixir tier (`command -v mix` present): UNVERIFIED at pack level — no
   mix project is compiled in the scratch court; the projected TTL's
   Elixir-side consumption is exercised by the ash_a2a consumer repo, not
   by this pack.

See Also: `docs/pack-consumer-contract.md` (F4 convention),
`docs/jira/v26.11.5/receipts/G10.md` (court receipt).
