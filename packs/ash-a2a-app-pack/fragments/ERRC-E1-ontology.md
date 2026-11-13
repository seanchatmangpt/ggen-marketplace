# ERRC-E1 ontology merge

Standing: UNVERIFIED

Subject: `/Users/sac/ggen-marketplace/packs/ash-a2a-app-pack/ontology.ttl` rewritten as the single
declaration site for every `aap:` term. `ontology.d/L01..L20-*.ttl` untouched (read-only lane
sources). No Bash, no ggen/parser run: syntax and graph load are not machine-checked.

## Method

Read ontology.ttl (legacy), all 20 `ontology.d/*.ttl` (L17 present), LANES.md, then enumerated
every `aap:` token in `templates/` (1562 occurrences), `gates/` (~1370), and fixtures L10-L20
(fixtures L01-L09 were not enumerated; only the conflict-class terms were grepped there).
Compared each token to the merged declaration set by reading, not by script.

## Conflicts found and resolution

| # | Term | Conflict | Resolution |
|---|------|----------|------------|
| 1 | `aap:enumValue` | L01 `owl:ObjectProperty` (EnumType -> EnumValue node; fixture L01 uses `ex:TS_open` nodes) vs L12 `owl:DatatypeProperty` (atom literals; fixture L12 uses `"low"`) | one declaration, `rdf:Property`, both uses documented |
| 2 | `aap:calculation` | L03 `ObjectProperty` (Resource -> Calculation node; fixture ex:Note_shout) vs L10 `DatatypeProperty` (CalculationInterface -> name literal; fixture `"age"`) | `rdf:Property`, dual use documented |
| 3 | `aap:fromState`, `aap:toState` | L13 `ObjectProperty` (Transition -> State node; gates L13_*) vs L20 `DatatypeProperty` (TransitionCase -> raw Elixir literal `":open"`) | `rdf:Property`, dual use documented |
| 4 | `aap:mountAgent` | L08 `DatatypeProperty` (module-name literal; fixture L08) vs L10 and L17 `ObjectProperty` (Mount -> aap:Agent) | `rdf:Property`, dual use documented |
| 5 | `aap:ofRelationship` | L02 `ObjectProperty` (RelManage -> Relationship node) vs L09 `DatatypeProperty` (Reference -> name literal) | `rdf:Property`, dual use documented |
| 6 | `aap:Relationship` class | L02 (any kind) vs L08 (belongs_to tenant owner), different comments | one class; comment records both; L08 keeps its parallel `relName/relDestination/relSourceAttribute/relAttributeType/relAllowNil` terms (distinct IRIs, no clash) |
| 7 | `aap:relationship`, `aap:destination` | declared in L02, L04 (minimal re-declaration, "dedupe with the relationships lane") and L08 (`relationship`) | single declaration; L02 definition kept (domain Resource, range Relationship); L04/L08 copies dropped |
| 8 | `aap:Mount` class | declared in L08, L10, L17 | one class; comment records both shapes (Domain -mount-> Mount from L08/L17; Mount -mountOf-> Domain from L10) |
| 9 | `aap:mount`, `mountPath`, `mountBinding`, `mountTenant`, `mountProtocolVersion` | L08, L10, L17 re-declare | one declaration each (L17 section; `mount` keeps L08's domain/range) |
| 10 | `aap:allowNil` | L01, L02, L03, L12 (all `DatatypeProperty`) | one declaration, comment lists the four uses |
| 11 | `aap:public`, `sensitive`, `filterable`, `sortable`, `constraints` | L01 and L03 | one declaration each, comment lists both |
| 12 | `aap:relPublic` | L02 (`public?`) vs L08 (`attribute_public?`) | one declaration, both uses noted |
| 13 | `aap:argName` | L15 (reactor binding) and L17 (ActionArgument) | one declaration, both uses noted |
| 14 | `aap:argOrder` | L03 and L15 | one declaration |
| 15 | L01 `aap:attrSpec` vs legacy `aap:attribute` | not a clash (distinct IRIs, disjoint by design; gates 010/L01_020/L20 read both) | both kept, comments state the split |
| 16 | L06 `aap:l06Action` vs `aap:action` | not a clash (distinct IRIs); gate 020_skill_targets_action unions `action`, `manage`, `l06Action`, `reactorAction` | all four kept |
| 17 | `aap:setupAppPath` (L09) | only declared in L09; used by Project-level L09 templates and gate L09_070 | kept once, `rdfs:domain aap:Project` |
| 18 | `aap:Project` | legacy ontology declared; L08/L14 reference it as domain/range | kept once |
| 19 | L13 `aap:transitionTarget` comment | string literal contained a raw newline inside `"..."` (invalid Turtle short string) | joined to one line in the merged file; `ontology.d/L13-statemachine.ttl` still carries the defect |
| 20 | L19 `aap:eaDeclare` comment | `""""true"|..."""` triple-quoted string beginning with a quote | rewritten as a single-line escaped string |
| 21 | L05 file | comment block precedes `@prefix` lines | harmless; merged file has prefixes first |

Kind-neutral `rdf:Property` was chosen for items 1-5 because both usages are exercised by committed
fixtures and gates (OWL object/datatype typing on one IRI is OWL-Full-illegal; no SPARQL in the pack
filters on `owl:ObjectProperty`/`owl:DatatypeProperty`; not machine-confirmed beyond reading the
templates, gates and fixtures listed above).

## Used but undeclared (found)

| Term | Used by | Action |
|------|---------|--------|
| `aap:ashPPlanDep` | `templates/mix.exs.tmpl:11` (OPTIONAL) | declared on `aap:Project` (flagged by ERRC-R2 residual 1) |
| `aap:securityProfile` | `templates/config.exs.tmpl:9` (OPTIONAL) | declared on `aap:Project` (flagged by ERRC-R2 residual 1) |

Every other `aap:` token in templates/ and gates/ resolved to a declaration (one pass, by reading;
not scripted). `aap:step*Body` in `L15_step_module.ex.tmpl:23` is a comment glob, not a term.
Fixtures L10-L20 resolved; fixtures L01-L09 are UNVERIFIED for undeclared terms.

## Residuals

- Could not resolve without editing another owner's file:
  - `/Users/sac/ggen-marketplace/packs/ash-a2a-app-pack/ontology.d/L13-statemachine.ttl` line 50-51
    (raw newline inside `rdfs:comment` string). Harmless if `ontology.d` is no longer loaded.
  - `ontology.d/L01..L20` still contain the original conflicting declarations (items 1-5, 6-14). If
    the manifest imports both `ontology.ttl` and `ontology.d/*.ttl`, the dual-typed IRIs reappear as
    both `owl:ObjectProperty` and `owl:DatatypeProperty` in the loaded union. Fix is to stop importing
    `ontology.d/` (or delete it) once this merge lands; coordinator decision, not done here.
  - `pack.toml` / manifest import list was not read or changed.
- Not verified: Turtle parses (no parser run); `ggen graph validate` not run; fixtures L01-L09 not
  enumerated for undeclared terms; no duplicate-declaration scan by tool (duplicates avoided by
  construction while merging).
- Coordinator to run: `ggen graph validate` on the pack, then the pack's sync.
