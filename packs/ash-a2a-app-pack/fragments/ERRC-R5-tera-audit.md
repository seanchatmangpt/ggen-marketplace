# ERRC-R5 Tera and SPARQL capability audit

Standing: PARTIAL

Subject: ggen-engine at /Users/sac/ggen/crates/ggen-engine (tera 1.20.1, oxigraph 0.5.9,
spareval 0.2.6, spargebra 0.4.6 per /Users/sac/ggen/Cargo.lock:7585 and Cargo.toml:100).
Method: Read/Grep only; nothing executed. The tera 1.20.1 crate source is NOT in
`~/.cargo/registry/src` on this machine, so claims about Tera built-ins marked
`(tera-doc)` come from Tera 1.x semantics, not a local file read. Claims marked `(src)` or
`(precedent)` are grounded in ggen source or in packs with e2e tests that already render.
Probe: templates/Z_tera_probe.tmpl (inert unless `<urn:r5:probe> <urn:r5:enabled> true`
is in the main graph) settles every `(tera-doc)` row in one `ggen sync run`.

## Engine facts (src)

- Tera env: `build_tera_with_packs`, template.rs:598-674. Registered functions: `sparql`,
  `local`, `sparql_first`, `sparql_values`, `sparql_empty`, `sparql_count`. Registered
  filters: snake/pascal/camel/kebab/shouty (+`_case`), `title`/`title_case` (shadows Tera
  `title`), pluralize, singularize, ordinalize, demodulize, foreign_key, tableize,
  classify, hex_to_u64. Zero `register_tester` calls: testers are Tera built-ins only.
- Default features of tera 1.20.1 (builtins: chrono, humansize, percent-encoding, regex)
  are on (Cargo.lock:7589-7597 lists chrono/humansize/percent-encoding).
- Body is rendered with `tera.render_str(&tpl.body, &ctx)` (sync.rs:1622, 1665, 3337,
  3260). Frontmatter is stripped first; only the body is the one-off template.
- No autoescape code anywhere in ggen-engine/src (grep `autoescape`: 0 hits). Tera escapes
  only for template names ending .html/.htm/.xml; `render_str`/`add_raw_template` names
  here are `__tera_one_off` / `generation_rule::<name>`. Result: `{{ x }}` is NOT escaped;
  `| safe` is a harmless no-op (137 uses).
- Glob load (template.rs:703-792) parses each file in `templates/` whole (frontmatter
  included) with `tera::Template::new`, WARN-skips parse failures, then
  `build_inheritance_chains` + `check_macro_files`. Only matters for import/include.
- Per-template ctx (sync.rs:3192-3245, 1514-1684):
  - every named `sparql:` key is inserted as an array (SELECT) / bool (ASK) / triple rows
    (CONSTRUCT/DESCRIBE); limit 4096 rows per query (envelope.rs:28, FM-TPL-021).
  - `results` = rows of `for_each:` query; with no `for_each:` it is the FIRST ARRAY IN
    ALPHABETICAL KEY ORDER (BTreeMap, sync.rs:3218). All 69 templates declare for_each
    or are single-render, so no template relies on the implicit driver (checked).
  - `to:` containing `{{` fans out one render per row; ctx = named keys + `results` +
    `row` + every column flattened to top level (row columns override named keys, fresh
    ctx per row, so no leak between rows).
  - static `to:` + `for_each:` = AGGREGATE: body rendered once per row and CONCATENATED
    (sync.rs:3326-3358); output-phase frontmatter must be row-invariant (FM-TPL-020).
    No pack template uses this (checked: every for_each template has a `{{` in `to:`).
  - zero rows on the driver = typed skip, not error (sync.rs:1526-1553, 1594-1618).
  - static `to:` without for_each: single render with `base_context`; NO `row` binding.
- Row cell typing (template.rs:1138-1149, graph.rs:914-980): xsd:boolean -> Bool;
  integer family -> Number; decimal/float -> Number; everything else (IRI, string, lang,
  dateTime) -> String; language tag dropped.
- OPTIONAL-unbound: the key is ABSENT from the row (not null). `{{ row.x }}` on an absent
  key is a hard render error FM-TPL-017 (test:
  tests/sparql_feature_coverage_e2e.rs:97-118); `is defined`, `| default(value=)` and
  `{% if row.x %}` are safe (e2e :72-95).
- Single-query-per-key scoping: each key is an independent query against the same
  graph (or the per-template overlay from `rdf:`/`rdf_inline:`); no variable is shared
  between keys. Cross-query joins must be done in Tera (`filter(attribute=,value=)`).

## SPARQL engine (src)

Executor: `SparqlEvaluator::new().parse_query(..).on_store(..)` (graph.rs:183-222) =
oxigraph 0.5.9 / spareval full SPARQL 1.1 query language. Refusals only: `GRAPH` clause
anywhere (FM-GRAPH-008, structural AST walk graph.rs:276-400), SPARQL UPDATE (FM-GRAPH-009),
`SERVICE` (fails at evaluation, no handler), illegal `BIND` rebind (FM-GRAPH-013,
graph.rs:446). Blank nodes are canonically relabelled in the store (graph.rs:117).

| construct | supported? | evidence | pack use | note |
|---|---|---|---|---|
| GROUP_CONCAT(DISTINCT ?x; separator=",") | yes | oxigraph; engine precedent: tests/sparql_feature_coverage_e2e.rs:131 (GROUP BY/COUNT) | L05 x2, L16 x5 templates + 6 gates | element ORDER is encounter order, stable per identical store, NOT semantic; empty group yields "" (key present) |
| SAMPLE(?x) | yes | oxigraph | L05 only | picks arbitrary row; all-unbound SAMPLE leaves the key ABSENT (guard it) |
| COUNT/MIN/MAX | yes (COUNT used) | e2e :131 gives Number | 1 template | result arrives as Number |
| property path `^p`, `p+`, `a/b`, `a\|b`, `(a\|b)` | yes | spargebra GP::Path (graph.rs:297) | gates (L13 `(^aap:fromState/aap:toState)+`), L07 | none in templates except `\|` alternatives |
| FILTER NOT EXISTS / EXISTS | yes, incl. in BIND(IF(EXISTS..)) | graph.rs:354-388 walks it | 82 gates, mix.exs, domain.ex | EXISTS-local variables are legal |
| subselect `{ SELECT ... }` | yes | oxigraph | 0 uses | fine if needed |
| VALUES (?a ?b) {...} | yes | GP::Values accepted (graph.rs:297); tests/k8s_pack_e2e.rs:162 | L15 x2, 7 gates | |
| UNION, OPTIONAL, FILTER, BIND/COALESCE/IF | yes | e2e :150,:170; sparql_refusals_e2e | pervasive | BIND target must be fresh (FM-GRAPH-013) |
| DESCRIBE / CONSTRUCT | yes | e2e :194 | 0 | rows = {subject,predicate,object} |
| GRAPH / SERVICE | REFUSED | graph.rs:186, :179 | 0 | |
| ORDER BY on bound-only vars | yes | blank nodes canonical (graph.rs:117) | pervasive | rows come back in ORDER BY order; always ORDER BY the driver |

## Tera constructs: audit of templates/*.tmpl

Counts are from grep over 69 templates (`L01..L20`, core). "Rewrite" is only needed when
the standing is not plain `yes`.

| construct | supported? | evidence | affected templates (file:line) | rewrite |
|---|---|---|---|---|
| `{% macro %}` + `self::name(k=v)` in the body | yes | precedent: /Users/sac/ggen/packs/github-actions-pack/templates/workflow.yml.tmpl:28,37 renders via render_str with e2e tests/github_actions_pack_e2e.rs | L07_policies.ex.tmpl:92,120,123,132,141,150,164,166; L15_reactor.ex.tmpl:120,128,154-220 | none. Macros see ONLY their args (L15 passes all arrays explicitly: correct) |
| recursive `self::step` | yes (tera-doc) | not in precedent | L15_reactor.ex.tmpl:174,184 | probe P02. Fallback: flatten via `parent_key` depth column |
| macro kwarg expression `ind=ind ~ "  "` | AMBIGUOUS (tera-doc: concat is a basic expr, allowed) | no precedent pack uses `~` inside a macro call | L15_reactor.ex.tmpl:174,184,220 | `{% set ind2 = ind ~ "  " %}` then `ind=ind2` (set inside a macro body is legal) |
| macro kwarg with filter `x \| default(...)` / math `n - 1` | AMBIGUOUS | none | not used today (probe P02, P19 only) | pre-`set` the value |
| macro kwarg bound to an ABSENT var | ERROR (tera-doc: kwargs evaluate eagerly) | n/a | L07 calls `self::ref(a=g.arg2...)`; every such column is COALESCEd to "" in the queries (L07 lines 14-72) | keep COALESCE; L07 is safe |
| `{% endmacro name %}` named end | yes | precedent workflow.yml.tmpl:32 `endmacro reindent` | L07, L15 | none |
| `{#- ... -#}` comments | yes | tera_whitespace_census.rs header (`-}}`/`{#-` lawful in 1.20) ; open/close counts balanced in all 69 files (checked) | L15 x4 | none. Never put `#}` inside a comment |
| `x is starting_with("p")` | yes (tera-doc built-in) | precedent: github-actions-pack composite_action.yml.tmpl, graphlaw-ash-capability-pack | L10_resource_interface:65, L10_domain_config:124, L11_pubsub_fragment:72,74, L17_domain_a2a_fragment:124 | on an ABSENT var the tester errors: L17:124 `sign_card is starting_with` needs `sign_card \| default(value="") is starting_with(":")` unless sign_card is COALESCEd (check query) |
| `x is containing(",")` | yes (tera-doc) | precedent: elixir-mcp-a2a-pack mcp_descriptor.ex.tmpl | L07_policies:99 | tester errors on a Number var: a string-typed column only |
| `x is matching("re")` | yes (tera-doc; regex feature on) | precedent: graphlaw-ash-capability-pack result_struct.ex.tmpl | L09_data_layer_fragment:115 | none |
| `\| split(pat=",")` | yes | precedent widespread | 67 uses (L07:164, L09:115, L10, L11...) | on "" returns `[""]` (one empty element): L10/L11 guard with `!= ""` first; L09:115 does not (see below) |
| `\| trim`, `\| trim_start_matches(pat=)` | yes (tera-doc) | precedent: speedrun-talent-network-pack intent.rs.tmpl | L09:115, L10_resource_interface:65, L10_domain_config:124 | none |
| `\| replace(from=,to=)` | yes | built-in | L20_plan_court:16, L20_reactor_court:17 | none |
| `\| filter(attribute="a", value=v)` | yes (tera-doc) | precedent: chicago-xaas-surface-pack chicago_machine.json.tmpl, beam4pm_billing.ex.tmpl | 160 uses, all templates | equality is TYPE-STRICT: `Number 1 != "1"`; every pack `value=` is a string column (module_name etc.). Items lacking the attribute are dropped silently |
| `\| filter(attribute="target")` (no value) | AMBIGUOUS (tera-doc: keeps items whose attr is non-null) | none | L13_state_machine.tmpl:90 | `\| filter(attribute="target")` -> loop with `{% if t.target is defined %}`; probe P06 |
| `\| group_by(attribute="grp")` + `for g, xs in` | yes (tera-doc), key must be a string | none in marketplace precedent for objects iteration here | L17_resource_a2a_fragment.ex.tmpl:150 | group keys iterate in sorted order (serde_json BTreeMap, no preserve_order feature, Cargo.toml:83). Ensure `secGroup` literals are plain strings, not bare integers; probe P17 |
| `{% set_global %}` inside `for` | yes | precedent: ggen/packs/dspy-pack, clap-noun-verb-verification-pack | L18_fragment.ex.tmpl:45,49 | none. Plain `set` in a `for` is loop-scoped; `set` in `if` is not scoped |
| `{% set x = ... %}` in for / macro | yes | built-in | 174 uses | none |
| `\| safe` | yes, no-op (no autoescape) | engine facts above | 137 uses | none; keep (harmless, documents intent) |
| `\| json_encode` | yes | built-in | 39 uses | output is valid JSON string, `"` and control chars escaped, `#{` NOT escaped: Elixir would interpolate. Where a value can hold `#{`, append `\| replace(from="#{", to="\\#{")` after `json_encode` |
| `"{{ raw }}"` inside Elixir double quotes | yes but UNESCAPED | no autoescape | 54 lines (L09_data_layer_fragment 7, L16_pplan_manufacture_targets 5, L11_pubsub_fragment 5, L10_domain_config 5, L07 4, L05 4, L01_enum_type 4 ...) | `"` or `\` or `#{` in the ontology literal breaks the generated file. Rewrite to `{{ x \| json_encode \| safe }}` (emits its own quotes). Gate L05_message_quotes only covers L05 |
| `x \| default(value="")` on absent var | yes | e2e :72-95 pattern | 405 uses | does NOT fire on empty string (only absent/null) |
| `{% if x %}` on absent var | yes (false) | e2e | pervasive | safe |
| `{{ row.x }}` / `{{ s.x }}` on OPTIONAL var, unguarded | ERROR FM-TPL-017 | e2e :97 | see list below | `\| default(value=..)` or COALESCE in the query |
| `v[0]`, `v[1] \| default(value="0")` index on split result | yes | tera-doc | L09_repo.ex.tmpl:28, L09_config:28,34, L09_runtime | none; out-of-range index is "undefined" so default works |
| `ctx key == "true"` vs boolean literal | MISMATCH RISK | template.rs:1138 Bool cells | 39 `== "true"`, 5 `== "false"`, 2 `!= "false"` | fixtures use string `"true"` (OK). A consumer writing bare `true` (xsd:boolean) makes the cell Bool and `== "true"` is false. Fixture L13 uses bare `aap:a2aLifecycle true`, matched by gate L13_050 as boolean; templates do not read it. Rule: boolean-valued aap: properties are STRING literals; document in README |
| `set_global` name `first` | yes | no keyword clash | L18:49 | none |
| `{{ ... }}}` / `{%{` adjacency | yes | `}}` lexes first then literal `}` | L01:70, L09_repo:28, L10:65,79 | none; no `{%{` or `{{{` or `{#` appears in any Elixir body (checked) |
| `~` string concat in `{% set %}` / output | yes | tera-doc | L06_fragment:108-110 | none |
| `\| length > 0`, `loop.last`, `loop.index` | yes | built-in | pervasive | none |
| `\| first`, `\| group_by` on absent array | n/a | | | keys of a zero-row query are `[]` not absent |

### Unguarded OPTIONAL variables found by scan (candidate FM-TPL-017 on sparse ontologies)

Scan: SELECT variables bound only inside OPTIONAL, used in `{{ }}` with no `default`,
`is defined` or enclosing `{% if %}` mentioning the same token within 700 chars.
Re-derived list (27 hits; items 4-8 are loop-var false positives):

| file:line | token | verdict | rewrite |
|---|---|---|---|
| L01_attributes_fragment.ex.tmpl:70 | `a.ash_type` | REAL when no `ash_type_module`, `array_of*` set | `a.ash_type \| default(value="string")` |
| L11_pubsub_fragment.ex.tmpl:74 | `p.pub_action` | REAL if neither pub_type nor pub_action bound | `p.pub_action \| default(value="")` |
| L06_fragment.ex.tmpl:112-136 | `s.attr`, `s.value`, `s.step_module` | gated by `s.op` branch, gate L06_020 enforces presence; ABSENT value = hard error | add `\| default(value="nil")` to `s.value`, `s.attr` |
| L15_reactor.ex.tmpl:123 | `b.value` | gated by `b.kind == "value"`; same note | `b.value \| default(value="nil")` |
| L05_identities_validations.tmpl:82 | `a`, `o`, `w` | false positive (for-loop vars) | none |

## Required rewrites (blocking unknowns only)

1. None of the constructs in the pack is UNSUPPORTED by ggen 26.11.5. First real sync is
   not blocked by Tera syntax.
2. Highest risk of a runtime FM-TPL-017: L01:70 and L11:74 (above); apply the defaults.
3. L09_data_layer_fragment.ex.tmpl:115 splits `i.idx_fields` without the `!= ""` guard
   L10 uses: an empty string yields `[""]` and renders `""`. Wrap in
   `{% if i.idx_fields | default(value="") != "" %}`.
4. L15 recursion with `ind=ind ~ "  "` (L15:174,184,220): pre-`set` the indent if the
   probe (P02/P19) reports a parse error. It is the only AMBIGUOUS construct that blocks
   a whole template (reactor).
5. L17_resource_a2a_fragment.ex.tmpl:150 `group_by`: confirm `secGroup` is a plain string.
6. GROUP_CONCAT order: arbitrary but replay-stable. Safe for sets (identity keys, props,
   evidence, authorities). Order-sensitive lists (`after_ids` in L16_pplan_workflow:18,
   Reactor binds, index fields) must use an ordinal property + ORDER BY rows + Tera loop,
   not GROUP_CONCAT.
7. Treat boolean/number-valued `aap:` properties as STRING literals, or compare with
   `== true`; document it in the pack README.

## Probe usage

Add `<urn:r5:probe> <urn:r5:enabled> true .` to a consumer ontology, run one
`ggen sync run`, read `.r5/tera_probe.txt`. Expected: P01 `k(x)`; P02 nested n=2,1,0;
P03 `true true true`; P04 `[a][b]`; P05 `2`; P06 counts rows with a bound `parent`
(2); P07 `alpha,beta,gamma`; P08 identical raw text twice (no `&amp;`/`&quot;`); Tera strings have no backslash
escapes (use backticks to embed `"`); P09 shows
`#{c}` unescaped; P10 shows absent keys defaulted; P11 `flagBool` shows `true/false`
(Bool vs "true"); P12 tags/SAMPLE/COUNT; P13 `beta>alpha;gamma>alpha;`
(gamma>beta removed by NOT EXISTS, beta flag is false); P14-P16 trivial;
P17 groups 1,2,3; P18 `3` (first alpha key is `agg`, 3 rows);
P19 errors or prints `k(alpha)`. Any parse/render error names the exact construct to
rewrite. Standing for each `(tera-doc)` row stays UNVERIFIED until this runs.

## See Also

[[ERRC-R5 probe]] templates/Z_tera_probe.tmpl · L01-NOTES.md through L20-NOTES.md ·
/Users/sac/ggen/crates/ggen-engine/src/template.rs · sync.rs · graph.rs
