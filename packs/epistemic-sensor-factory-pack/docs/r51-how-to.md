# How to qualify transitive propagation

1. Resolve every producer and consumer repository to an exact SHA.
2. Admit only independently observed receipt assertions; preserve UNKNOWN/PARTIAL_ALIVE where execution has not been observed.
3. Run the 50 R51 SPARQL sensors against the admitted graph.
4. Run `tests/test_r51_transitive_propagation.py` with the pinned RDF engine used by the owning workflow.
5. Generate the propagation plan from `ggen.toml`; treat it as a consequence, not an editing surface.
6. Require a new exact-subject court before promoting any downstream target to ALIVE.
