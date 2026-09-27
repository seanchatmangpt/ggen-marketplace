# CS2 semantic-work pack

Manufactures deterministic, authority-free work projections from canonical CS2 RDF.

The pack separates canonical semantic identity from consumer representation. A projection carries exact subject, repository, source SHA and digest; it cannot grant consequential authority.

Pipeline:

RDF -> SPARQL projection -> admission gates -> JSON schema -> JSON/Elixir consumer templates.

Consumers should bind the generated projection to their local admission boundary rather than duplicating CS2 work semantics by hand.
