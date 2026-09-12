# errc-tracker.md — ex-noun-verb-cli-pack capability-parity extension

ERRC (Eliminate/Reduce/Raise/Create) pass over the 2026-09-11 extension that
added the real `nvc:PortedCapability`/`nvc:DeferredCapability` graph to
`ontology.ttl`. Every entry below cites a real source, quoted verbatim
where the source is short enough to quote — no paraphrase substituted for
a citation, per this ecosystem's source-of-truth-check discipline.

## Eliminate

None. This extension is purely additive documentation of real, already-
existing facts (verified `file:line` citations into `~/ex_noun_verb_cli`
and `~/clap-noun-verb`, and real gate counts from this marketplace's own
`packs/clap-noun-verb-*-pack` directories) — nothing in the pack's prior
content was removed. N/A for this cycle.

## Reduce

None identified. Every `nvc:DeferredCapability` below is a full-scope
deferral (either a real design-spec non-goal or a real in-code TODO), not
a partially-implemented capability that could be trimmed further.

## Raise (DEFERRED → PORTED promotion candidates, ranked)

1. **`nvc:StepRefCapability`** (`@{N.path}` cross-group substitution) —
   highest priority. This is a real in-code TODO, not a charter non-goal:
   `~/ex_noun_verb_cli/lib/ex_noun_verb_cli/chaining.ex`'s own moduledoc
   (lines 22-34) states the reason it isn't resolved there ("`expand/1`
   only ever sees the raw, not-yet-dispatched argv groups -- it has no
   access to any group's dispatch *result*... Resolving `@{N.path}`
   requires interleaving expansion with dispatch... which is legitimately
   `ExNounVerbCli.Dispatcher`'s job"). Promoting this closes a real parity
   gap against the Rust original's own working implementation at
   `~/clap-noun-verb/src/cli/preprocessor.rs:32-100`
   (`preprocess_args`'s "1. Resolve step references `@{step.key}`" block,
   verified present and real).

2. **`nvc:LevenshteinSuggestionCapability`** ("did you mean?" suggestions)
   — absent from both the design spec's non-goals section (verified:
   `docs/superpowers/specs/2026-09-11-ex-noun-verb-cli-design.md:109-121`
   names 5 non-goals, none of them this) and `~/ex_noun_verb_cli/lib/`
   (verified: `grep -rn -i 'levenshtein|did.you.mean|suggest' lib/` returns
   zero matches). Lower effort than item 1: the real Rust reference
   implementation is a single, self-contained, dependency-free function —
   `~/clap-noun-verb/src/error.rs:45-82`'s `levenshtein_distance` (a
   standard bounded-edit-distance DP over two char vectors) plus
   `find_best_matches` (filters candidates to distance ≤ 3, sorts by
   distance then lexicographically) — directly portable to Elixir with no
   architectural decision required.

## Create (net-new capital this extension manufactures)

- **The `nvc:` capability-parity graph itself**: 10 `nvc:PortedCapability`
  + 8 `nvc:DeferredCapability` + 10 `nvc:ExampleProgram` + 9 new
  `nvc:CliVerb` + 1 `nvc:LocalPack` + 12 `nvc:MarketplacePack` + 3 sampled
  `nvc:OntologyClass` individuals (55 total, plus their `nvc:Citation`
  support individuals) — the first RDF model of exactly how much of
  `~/clap-noun-verb` `~/ex_noun_verb_cli` implements, queryable rather than
  asserted only in prose.
- **7 gates** (`gates/010`–`070`) enforcing this graph's own structural
  integrity: every ported claim has file evidence, every deferred claim
  has spec evidence, every example demonstrates a verb or names a related
  capability, every verb has a real file path, every pack's gate count is
  present and non-negative, the PORTED/DEFERRED dichotomy is closed (no
  bare `nvc:Capability`), and no citation blurs both evidence shapes at
  once. All 7 verified clean (`ASK=False`) against the real `ontology.ttl`
  via `rdflib` at extension time (2026-09-11).
- **6 queries** (`queries/ported-capabilities.rq`,
  `deferred-capabilities.rq`, `example-verb-matrix.rq`,
  `pack-gate-totals.rq`, `marketplace-pack-catalog.rq`,
  `capability-standing-split.rq`), each designed to back one real `ExUnit`
  test in `packages/marketplace-cli/test/`. Verified (via `rdflib`, real
  oxigraph-equivalent SPARQL execution against the real `ontology.ttl`) to
  return exactly: 10 rows, 8 rows (containing the substring
  `"chaining.ex:22-34"` for `nvc:StepRefCapability`), 10 rows (containing
  `(CoreApiExample, ServicesStatusVerb)`), `26`, 12 rows, and
  `(ported=10, deferred=8)` respectively.
- **One corrected fact, propagated instead of an unverified estimate**:
  `nvc:SchemaPack`'s `nvc:packHasClassCount` is recorded as `14` (the real
  `grep -c 'a rdfs:Class' packs/clap-noun-verb-schema-pack/ontology.ttl`
  count, verified at extension time), not an earlier, lower estimate that
  was never itself grep-verified. Recorded here per this ecosystem's
  source-of-truth-check discipline: a stale/unverified count restated a
  second place is exactly the drift class that discipline exists to catch.

## Citations re-quoted verbatim (not paraphrased)

- `chaining.ex:22-34` (StepRefCapability): "A `\"@{N.path}\"`-shaped token
  (referencing a *prior chained group's* dispatch result) is left
  unresolved and returned as-is. This is a real TODO, not a faked
  resolution... Resolving `@{N.path}` requires interleaving expansion with
  dispatch... which is legitimately `ExNounVerbCli.Dispatcher`'s job."
- `docs/superpowers/specs/2026-09-11-ex-noun-verb-cli-design.md:111`
  (DynamicCompletionsCapability): "Dynamic shell completions (clap-noun-verb
  has this; real but deferred)."
- `docs/superpowers/specs/2026-09-11-ex-noun-verb-cli-design.md:119-121`
  (HexPublishCapability): "Actually publishing to Hex.pm for real -- this
  pass ends at `mix hex.publish --dry-run` (a real, verified dry-run
  build/package step), not a real publish."
