# noun-verb-cli-pack: real marketplace_cli (Elixir port of scripts/marketplace.py) on ex_noun_verb_cli

## Summary

A real, runnable Elixir port of `scripts/marketplace.py` (`inspect_marketplace()`,
`validate()`, `catalog()`, `marketplace_version()`) was built as
`packages/marketplace-cli/`, wired through `ex_noun_verb_cli`'s
Registry/Dispatcher/Mix-task machinery and `ggen_igniter`'s
`Ontology.load!/1` + `Query.run/2` for its one genuinely SPARQL-shaped field
(`ontology_triple_count`). The port was verified for behavioral parity
against the real, live `python3 scripts/marketplace.py validate`/`catalog`
commands (not a captured snapshot), one real logic gap in
`marketplace_version/1`'s refusal codes was found and fixed, and a
follow-up formatting-only pass cleaned three files the fix's own audit
left `mix format`-unformatted. The four commits were merged into the
marketplace repo.

## Status

Done - already merged/committed.

## Commits

- `15aeadb52` merge: noun-verb-cli-pack -- real marketplace_cli
- `e72fdc8c8` style(marketplace-cli): mix format 3 files
- `ea82a8f1b` fix(marketplace-cli): real refusal codes for marketplace_version/1
- `603533487` feat(noun-verb-cli-pack): real marketplace CLI on ex_noun_verb_cli + ggen_igniter

## Changes

- Added `packs/noun-verb-cli-pack/{pack.toml,ontology.ttl}` -- the
  marketplace-pack entry, admitted by `scripts/marketplace.py` itself. No
  templates: the milestone's deliverable is a hand-built consumer
  application, not a Tera-templated generator.
- Added `packages/marketplace-cli/` as a real, runnable Mix project (kept
  as a sibling top-level dir alongside the existing `packages/` convention,
  outside `packs/`, after finding that nesting a compiled Mix project's
  `_build`/`deps` trees under `packs/` trips `scripts/marketplace.py`'s
  own `PACK_SYMLINK` admission refusal on hex packages' real
  `priv/src/include` symlinks).
  - `lib/marketplace_cli/graph_provider.ex` --
    `MarketplaceCli.GraphProvider.GgenIgniterProvider`, a real
    `ExNounVerbCli.GraphProvider` implementation wrapping
    `GgenIgniter.Ontology.load!/1` + `GgenIgniter.Query.run/2`, added as a
    real `ggen_igniter` `path:` dependency.
  - `lib/marketplace_cli/registry.ex` -- `MarketplaceCli.Registry`, a real
    `ExNounVerbCli.Registry.Generated`-backed registry for the
    `marketplace validate`/`catalog` verbs.
  - `lib/marketplace_cli/inspector.ex` -- `MarketplaceCli.Inspector`: a
    field-for-field Elixir port of `inspect_marketplace()`/`validate()`/
    `catalog()`, including the SemVer regex, `REQUIRED_DOCS` list,
    `fingerprint_paths` sha256 algorithm, and a deterministic `tar.gz`
    archive (via `:erl_tar`) for `catalog()`'s `digest`/`size_bytes`
    fields. Adds one enrichment beyond `marketplace.py`'s own schema:
    `ontology_triple_count`, computed via a real SPARQL `SELECT` through
    the `GraphProvider`.
  - `lib/mix/tasks/marketplace_cli.{validate,catalog}.ex` -- real
    `ex_noun_verb_cli`-based `Igniter.Mix.Tasks`
    (`mix marketplace_cli.validate` / `.catalog`), dispatching through
    `ExNounVerbCli.Dispatcher.dispatch/2` against
    `MarketplaceCli.Registry`.
  - `mix.exs`, `mix.lock`, `config/config.exs`, `.formatter.exs`,
    `.gitignore` -- standard Mix project scaffolding.
  - `test/marketplace_cli/{graph_provider,inspector}_test.exs`,
    `test/mix/tasks/marketplace_cli_test.exs`, `test/test_helper.exs`.
- `ea82a8f1b` fixed a real logic gap in `marketplace_version/1`: it had
  pattern-matched `{:ok, ...}` on `File.read` and `Toml.decode` directly,
  crashing with an uninformative `MatchError` on a missing/invalid
  `marketplace.toml` or missing/blank `[marketplace].version` instead of
  Python's typed `REFUSED:MARKETPLACE_TOML_MISSING` /
  `REFUSED:MARKETPLACE_TOML_INVALID` /
  `REFUSED:MARKETPLACE_VERSION_MISSING` refusal strings. Fixed to raise
  the same three typed refusal codes, in the same order of checks, as
  Python's `marketplace_version()`.
- `e72fdc8c8` ran `mix format` on three files
  (`lib/mix/tasks/marketplace_cli.{validate,catalog}.ex`,
  `test/marketplace_cli/inspector_test.exs`) left unformatted by the
  `ea82a8f1b` fix; caught by an independent re-verification pass
  (`mix format --check-formatted` failing), not self-reported. No logic
  change.
- `15aeadb52` merged the above three commits into the marketplace repo's
  main line; also carries small ancillary diffs to `.github/workflows/*`
  (1-2 line additions each to several workflow files and
  `source-correspondence.yml`) and one addition to
  `packs/ash-r2rml-paas-pack/qualification/consumer.ttl` and
  `templates/beam4pm_engine.erl.tmpl`, per its own `--stat` output.
- Cross-repo dependency fix (documented in `603533487`'s message, applied
  in a separate commit in `~/ex_noun_verb_cli`, `b5a8083`, not in this
  repo): `ex_noun_verb_cli`'s own `:igniter` dependency was marked
  `only: [:dev, :test]`, which broke compiling `ex_noun_verb_cli` as an
  external `path:` dependency (`module Igniter.Mix.Task is not loaded`);
  changed to `optional: true` alone.

## Verification

Per `603533487`'s commit message (real commands, real output stated in
the message):

- `mix compile --warnings-as-errors` -- exit 0 (pre-existing
  `ggen_igniter` dependency warnings only).
- `mix test` -- 8 tests, 0 failures.
- `grep -rn ... 'Mox|Mimic|Patch|:meck\.|mockall|MagicMock|Mock\(' lib test`
  -- zero matches.
- `python3 scripts/marketplace.py validate` reproduced live and compared
  string-for-string against `MarketplaceCli.Inspector.validate/1`'s
  output; `test/marketplace_cli/inspector_test.exs` asserts string
  equality against a live `System.cmd("python3", ...)` subprocess run,
  not a captured snapshot. Same live-subprocess-comparison approach for
  `catalog()`'s pack count/names.
- Disclosed, honest gap (not hidden): the `tar.gz` digest in `catalog()`
  differs from `marketplace.py`'s own digest byte-for-byte, because
  Erlang's `:erl_tar` and Python's `tarfile` emit different header bytes
  for identical content. Every count-shaped field (pack/ontology/
  template/gate counts, profile classification, SemVer/description
  validation) is stated as real behavioral parity, not the digest field.

Per `ea82a8f1b`'s commit message: `mix compile --warnings-as-errors`
(exit 0), `mix test` (8 tests, 0 failures), `mix format
--check-formatted` on the touched file (clean at that point -- the three
files fixed by `e72fdc8c8` were caught afterward), mock-hygiene grep over
lib/test (zero matches). Also states a direct probe against a scratch
marketplace with no `marketplace.toml`, confirming both the real Python
script and the fixed Elixir port produce
`REFUSED:MARKETPLACE_TOML_MISSING:marketplace.toml`, and an 8-probe-pack
scratch-marketplace comparison where the Python script and
`Inspector.inspect_marketplace/1` produce byte-identical issue sets
(one cosmetic quote-style difference: Python `repr()` single quotes vs
Elixir `inspect()` double quotes in one detail string).

Per `e72fdc8c8`'s commit message: caught by `mix format
--check-formatted` failing on re-verification; no test/compile output
restated in that commit's own message beyond the formatting check.

`15aeadb52` (the merge commit) states no additional verification beyond
what the three merged commits already state.

## Related

- Cross-repo commit `~/ex_noun_verb_cli` `b5a8083` (igniter dependency fix
  to `optional: true`), referenced in `603533487`'s message -- not in this
  repo.
- Design spec referenced in `603533487`:
  `~/ex_noun_verb_cli/docs/superpowers/specs/2026-09-11-ex-noun-verb-cli-design.md`,
  section 5 ("Milestone 2").
- Claude sessions referenced in commit trailers:
  `https://claude.ai/code/session_01Q9CxAziKRC59z9Z1YVQ2NW` (all three
  non-merge commits).
- No PR number stated in any of the four commit subjects or messages.
