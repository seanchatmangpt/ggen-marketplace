# chatman-ecosystem-release-pack

Reusable release-composition law for dependency-closed, exact-SHA ecosystem releases, plus
(0.2.0) the projections a successor release needs to dispose of every role of its predecessor
without erasing the old topology. The pack holds law, vocabulary, rules and templates only;
every release-instance fact (component SHAs, role names, decisions) is consumer-owned.

Version 0.2.0 serves the Chatman Ecosystem v26.9.23 requirements CE23-1 (independent release
subject) and CE23-2 (explicit disposition of all 16 roles of `release/v26.9.1/manifest.toml`).

## Consumer shape

A consumer's `ggen.toml` (frontmatter schema) takes the pack by path or by `git` + `subdir`
pinned to an exact marketplace SHA, and feeds its independent inputs through
`extra_ontologies`, which join the sync closure hash:

```toml
[project]
name = "chatman-ecosystem-release-v26-9-23"

[ontology]
source = "release.ttl"          # the er:Release, its er:Component rows and role mappings

[templates]
dir = "templates"               # tracked, may be empty (.gitkeep)

[packs]
chatman-ecosystem-release-pack = { path = "../..", lock = false, extra_ontologies = [
  "imports/legacy-v26.9.1.ttl",       # lift/manifest_to_er.py output
  "imports/fleet-classification.ttl", # byte copy, identity in er:classificationSource
  "imports/court-references.ttl",     # er:courtReferencesComponent observations
  "imports/ce23-orders.ttl",          # sj:WorkOrder graph for requirements.toml
] }
```

`qualification/consumer-v26.9.23/` is a complete, runnable instance of this shape built from
real inputs (see its `SOURCES.md`).

## Vocabulary added in 0.2.0

- `er:LegacyRelease` / `er:LegacyComponent`: lifted predecessor facts. They are not
  `er:Release` / `er:Component`, so gates 010-060 never re-judge frozen facts.
- `er:RoleDisposition` with `er:boundary` in the value class `er:RoleBoundary`
  (`er:ROLE_REQUIRED`, `er:ROLE_SUCCESSOR`, `er:ROLE_BLOCKED`, `er:ROLE_UNSUPPORTED`,
  `er:ROLE_REFUSED`). `er:ROLE_UNCLASSIFIED` is an untyped sentinel that gate 070 refuses.
  Component dispositions (`er:Disposition`) and standings (`er:StandingState`) are unchanged.
- `er:crosswalkFrom` binds the successor release to the predecessor it must dispose.
- Row properties: `er:legacyRole`, `er:legacyComponent`, `er:legacySha`, `er:legacyStanding`,
  `er:sourceRelease`, `er:targetRelease`, `er:reason`, `er:decidedBy`, `er:derivedBy`,
  `er:suppliedBy`, `er:classificationSource`, plus `er:legacyRequiredRole`,
  `er:courtReferencesComponent`, `er:componentId`, `er:sourceSha256`.
- Constitutional mapping: `er:RoleMapping` (`er:releaseRole`, `er:primary`, `er:capability`,
  `er:authorityCeiling`, `er:brceExclusive`) over the 11 `er:ConstitutionalRole` individuals.

## Disposition rule

`templates/role-disposition-rule.toml.tmpl` carries the rule as a `construct:` frontmatter
(Stage-2 enrich; `[[inference.rules]]` is refused FM-CONFIG-101 in the frontmatter schema).
For each required role of the predecessor without an explicit decision:

1. its repository is classified in the imported fleet classification (join on the basename of
   the `owner/name` slug; collisions are refused): CriticalPath -> REQUIRED, Successor ->
   SUCCESSOR, Blocked -> BLOCKED, Refused -> REFUSED, Unsupported -> UNSUPPORTED, any other
   class -> UNCLASSIFIED (refused);
2. otherwise, when no court of the governing checkpoint executes the repository: SUCCESSOR,
   `er:derivedBy "rule:no-GC23-court-reference"` (a successor repository becomes required only
   when a court executes it);
3. otherwise nothing is derived and gate 070 refuses the role as undisposed.

## Gates

| gate | refuses |
|---|---|
| 010-060 | release contract, component identity, dependency closure, required-role law, external ref observation, unique repository (unchanged) |
| 070_role_crosswalk_total | a predecessor role with 0 or >1 dispositions; an untyped/UNCLASSIFIED or multi-valued boundary; a row without reason or without derivedBy/decidedBy; REQUIRED not supplied by a required component of the target; an explicit decision for a classified repository; basename collisions |
| 075_constitutional_role_mapping | a required role or required component role without exactly one mapping; non-constitutional primary/capability; empty authority ceiling; Actuate without BRCE exclusivity |
| 080_critical_path_coverage | a CriticalPath repository, or a court-executed repository, that is not a required component of the release |
| 085_requirement_row_identity | a checkpointed sj:WorkOrder without owner/name repository, 40-hex base SHA or falsifier description |

Gates are enforced natively by `ggen sync run` (FM-PACK-013) when the pack is consumed through a
`[packs]` entry, and by the explicit rdflib runner `bin/run-gates.py <graph.ttl> [gates]`, which
unions the same inputs (pack ontology, the graph, the sibling `ggen.toml` imports) and applies the
templates' `construct:` rules before gating.

## Projections

All outputs go to `out/` and are written without `force`: an existing file that differs from the
render refuses the sync (FM-WRITE-005), so a hand edit is never silently kept or silently
overwritten. To regenerate after an input change, delete the stale output and run
`ggen sync run` again.

| template | output |
|---|---|
| release-manifest.toml.tmpl | `out/manifest.toml`: every verify_release field (id, repository, ref, ref_check, sha, role, disposition, standing, required, depends_on; version from er:version) |
| constitutional-role-crosswalk.toml.tmpl | `out/constitutional-role-crosswalk.toml` (release_role, primary, capabilities, authority_ceiling) |
| legacy-role-crosswalk.toml.tmpl | `out/legacy-role-crosswalk.toml`, one row per predecessor role through OPTIONAL joins |
| requirements.toml.tmpl | `out/requirements.toml`, one row per checkpointed WorkOrder: gate, repo@sha subject, falsifier |
| crosswalk.ttl.tmpl | `out/crosswalk.ttl`, every er:RoleDisposition as Turtle (ggen does not emit its enriched graph) |
| role-disposition-rule.toml.tmpl | the disposition rule, and `out/role-derivations.toml` (derived vs decided rows) |

## Qualification

`qualification/qualify.sh` runs everything in a scratch copy with the real ggen and rdflib:
the synthetic `consumer.ttl`, a double render of `consumer-v26.9.23` (byte-identical), a control
and a positive explicit-decision witness, and the 12 mutants of `qualification/mutants/`
(expected code, gate and reason in `EXPECTED.tsv`). Removing gates 070-085 lets all eleven
graph mutants (every mutant except M6) render with exit 0, so those refusals come from the new
gates; M6 is refused by the no-force write law.

## See also

- `HANDWRITTEN.md`: the code residue ledger (`lift/manifest_to_er.py`, `bin/run-gates.py`,
  `qualification/qualify.sh`).
- `qualification/consumer-v26.9.23/SOURCES.md`: provenance and sha256 of every imported input.
- `qualification/mutants/README.md`: each mutation as a one-change diff from the mutant base.
