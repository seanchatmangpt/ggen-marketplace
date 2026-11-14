# L28 notes: structural gates A

Standing: UNVERIFIED

Gates (rows = violation, style of gates/010):

- `L28_010_agent_without_domain.rq`: aap:Agent with neither aap:forDomain nor aap:inDomain.
  Columns: agent, module_name.
- `L28_020_duplicate_resource_module_name.rq`: two aap:Resource nodes share aap:moduleName.
  Columns: a, b, module_name.
- `L28_030_duplicate_agent_skill_name.rq`: two skills (aap:skill/aap:name or
  aap:skillSpec/aap:specName) across the resources of an agent's forDomain domain share a name.
  Columns: agent, a, b, name.

Existing coverage, not duplicated:

- Unknown ashType: `L01_010` (attr kind vocabulary), `L01_040` (attr type resolution) and
  `L20_040_unknown_ash_type`. Nothing in L28 touches ashType.
- `L20_041_duplicate_module_name` already flags any two nodes sharing a moduleName, so L28_020
  is a resource-scoped subset kept for named, resource-only diagnostics.
- `L20_042_duplicate_action_or_skill_name` covers aap:skill pairs within a domain only;
  L28_030 adds aap:skillSpec and mixed pairs, keyed per agent.

Fixtures: `fixtures/L28-legal.ttl` (zero rows everywhere) and
`fixtures/L28-refuse-010-*.ttl`, `-020-*.ttl`, `-030-*.ttl` (expected row in each header comment).
