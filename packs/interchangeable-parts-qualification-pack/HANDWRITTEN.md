# Generated/source ownership

Canonical executable law is **not** generated here and is not duplicated here.

Handwritten semantic source in this pack:
- ontology.ttl
- ontology/shapes.ttl
- gates/*.rq
- queries/*.rq
- templates/*.tera
- runners/*.py
- witnesses/**/*.ttl
- ggen.toml
- pack.toml

Generated projections:
- generated/unrdf-consumer-adapter.mjs
- generated/unrdf-consumer-adapter.test.mjs

Executable substitution semantics are owned by:
- @unrdf/core: PartRequirement, PartPassport, evaluateSubstitution
- @unrdf/receipts: substitution receipt manufacture + verification

The generated adapter imports those owners and contains no independent
substitution algorithm. Editing generated files is prohibited. A consumer
that cannot resolve the canonical UNRDF owner is UNSUPPORTED, not permission
to fork the law.
