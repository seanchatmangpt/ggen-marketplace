# ash-a2a-app-pack lanes (v26.11.13 wave 2)

Each lane owns ONLY files prefixed with its lane id (L01..L20). Shared files (ontology.ttl,
templates/resource.ex.tmpl, domain.ex.tmpl, config.exs.tmpl, mix.exs.tmpl) are read-only to
lanes; coordinator merges. Extension seam: Spark fragments (`use Spark.Dsl.Fragment,
of: Ash.Resource`) emitted per lane as separate modules listed in `fragments:`.
