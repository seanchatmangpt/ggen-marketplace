# ash-reactor-domain-error-contract-pack (DEPRECATED)

This pack is superseded by `ash-runtime-integration-contract-pack`.

## What this pack did

Generated `Generated.ReactorDomainErrorNormalizer.normalize/1`: a function that unwraps a
`%Reactor.Error.Invalid{}` exception to pull the real domain error out of a nested
`Reactor.Error.Invalid.RunStepError`, falling back to `{:reactor_failed, original}` when no
such nested error is present.

## Where the functionality moved

`ash-runtime-integration-contract-pack` now carries the same `Reactor.Error.Invalid` unwrapping
logic as its own `domain-error-normalizer` generation rule:

- Ontology property: `rt:domainErrorNormalizerModule` (`ontology.ttl`)
- Query: `queries/54-domain-error-normalizer.rq`
- Template: `templates/domain_error_normalizer.ex.tmpl`
- Wired in `ggen.toml` under `[[generation.rules]]` (`name = "domain-error-normalizer"`)
- Enforced by `gates/01-core-vocabulary.rq` (the property is now a required core vocabulary term)

This consolidation was done only after confirming, by reading both packs' actual templates, that
`ash-runtime-integration-contract-pack`'s pre-existing `domain_error.ex.tmpl` (a generic
code/message/details contract map) and `errors.ex.tmpl` (a plain Elixir exception struct) did
**not** already perform the `Reactor.Error.Invalid` unwrapping — the two packs solved genuinely
different problems until this rule was added.

## Migration

Consumers of this pack should switch to `ash-runtime-integration-contract-pack` and populate
`rt:domainErrorNormalizerModule` on their `rt:Integration` subject instead of depending on this
pack's `ggen.toml`.
