# L29 Notes: Name-Collision Gates (B)

Standing: UNVERIFIED

Gates in `gates/` (rows = violation); fixtures in `fixtures/`.

| gate | refusing fixture | rows expected |
|---|---|---|
| L29_010_attr_vs_rel_calc_agg | L29-refuse-attr-collision.ttl | 2 (notes, total) |
| L29_020_skill_name_shared_domain | L29-refuse-skill-collision.ttl | 1 |
| L29_030_action_name_cross_kind | L29-refuse-action-collision.ttl | 1 |
| L29_040_invalid_atom_name | L29-refuse-invalid-atom.ttl | 3 |

`fixtures/L29-legal.ttl` yields zero rows on all four.

## Existing gates not duplicated

- L01_020: attribute/attrSpec vs attribute/attrSpec. L29_010 covers only attribute vs
  relationship/calculation/aggregate.
- L03_030: calculation vs legacy attribute and calculation vs calculation. L29_010 additionally
  catches attrSpec vs calculation.
- L04_030: aggregate vs attribute/relationship/aggregate (overlaps L29_010 on aggregate vs
  legacy attribute; kept for the attrSpec side).
- L20_042: legacy action/action per resource and aap:skill/aap:skill per domain. L29_020 and
  L29_030 cover only the cross-kind pairs (skillSpec, l06Action, manage, reactorAction).

## Assumptions

- No agent-to-skill edge exists; "agents share a domain" is modeled as an aap:Agent with
  aap:forDomain on the skills' domain.
- aap:manage and aap:reactorAction nodes carry aap:name (not confirmed against their gates).
- L29_040 skips resources whose names are absent; it does not check relationship/calc names.
