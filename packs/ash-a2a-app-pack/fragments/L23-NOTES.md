# L23 notes: a2a skill argument_mapping

Standing: UNVERIFIED

## DSL evidence

- /Users/sac/ash_a2a/lib/ash_a2a/dsl.ex:73-81 option `argument_mapping`, `{:map, :string, :atom}`,
  default `%{}`.
- /Users/sac/ash_a2a/lib/ash_a2a/verifiers/verify_skills.ex:373-397 refusal
  `refused_argument_mapping_target`; real names = action arguments plus accepted attributes (:399-411).
- /Users/sac/ash_a2a/lib/ash_a2a/executor.ex:242-256 applies mapping; lib/ash_a2a/schema.ex:119-140
  projects wire names; lib/ash_a2a/skill.ex:64-122 struct field.

## Files

- ontology.d/L23-argmap.ttl: `aap:skillArgMap` (aap:Skill -> aap:ArgMapping), reusing L17
  `aap:ArgMapping`, `aap:wireName`, `aap:targetArg`, `aap:actionArgument`, `aap:argName`.
- templates/L23_skill_argmap.ex.tmpl -> `lib/<app_path>/<resource_file>_a2a_l23.ex`, module
  `<Resource>.A2aL23`. Queries: resources(module_name app_path resource_file),
  skills(module_name skill_name skill_action description consequence lease),
  maps(module_name skill_name wire target).
- gates/L23_010_argmap_target_exists.rq (subject target reason),
  gates/L23_020_argmap_action_missing_or_wire_dup.rq (subject detail reason).
- fixtures/L23-argmap.ttl (legal, 0 rows expected), fixtures/L23-argmap-refusing.ttl.

## Seam (coordinator)

L17 already handles mappings on aap:SkillSpec; L23 covers the plain aap:Skill. resource.ex.tmpl
(line ~29 query) emits every aap:Skill in its own a2a block; a skill with `aap:skillArgMap` would be
declared twice (duplicate Spark :name). Coordinator must exclude skills having `aap:skillArgMap`
in resource.ex.tmpl (add `FILTER NOT EXISTS { ?s aap:skillArgMap ?_ }`), or let L23 own them.
The fragment must be listed in the resource `fragments:`.

## Known gaps

- Gate 010 uses aap:Action (legacy) only; L06 aap:l06Action actions are not consulted.
- Gate 010 requires the action to exist; missing action is reported by 020.
- Template skill options limited to description/consequence/lease_required?.
- Template unverified under ggen sync; coordinator build is the court.
