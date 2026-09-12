# ex-noun-verb-cli-pack

Elixir-native noun-verb CLI framework port (ex_noun_verb_cli): declarative noun/verb dispatch, capability standing, command chaining/stdin extraction, generated via ggen from RDF rather than hand-authored.

Scaffolded by `ggen pack new ex-noun-verb-cli-pack` from `ggen-self-pack`
(`pack.toml`, `ontology.ttl`, `README.md` were generator output, not
hand-typed), then populated with this pack's real facts.

This pack's deliverable is not a Tera-templated generator — it's the concrete
evidence that `ex_noun_verb_cli` can displace `scripts/marketplace.py`. See
`pack.toml`'s `description` for the full charter. The real consumer app lives
at `packages/marketplace-cli/`; `ontology.ttl`'s `nvc:CliVerb` facts are read
back for real by `queries/cli_verbs.rq` and `queries/capability_shape.rq`,
executed by that app's own test suite
(`test/marketplace_cli/cli_verbs_query_test.exs`).

Formerly named `noun-verb-cli-pack` (renamed — a pack name repeating
"marketplace" is redundant with the pack already living in this marketplace).
