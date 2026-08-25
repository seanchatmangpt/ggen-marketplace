# Reference: R32 option-capital contract

Each candidate edge MUST carry: `candidate`, non-empty `composition`, `repository`, `marketplace_support`, non-empty `qualification`, `reversible=true`, `expected_reuse>=1`, and `expected_capability_space_delta>=1`. `missing_primitive` is nullable. `standing` is one of UNKNOWN, PARTIAL_ALIVE, ALIVE, BLOCKED, BUILD_BROKEN, or UNSUPPORTED.

`option-capital-r32.schema.json` is the JSON contract. `option-capital-r32.ttl` is the RDF projection. `option-capital-r32-ledger.jsonl` is the append-oriented observation ledger. Queries expose candidate, composition, provenance, marketplace, repository, and reversibility surfaces. Gates refuse ungrounded, stale, or authority-bearing candidate assertions.