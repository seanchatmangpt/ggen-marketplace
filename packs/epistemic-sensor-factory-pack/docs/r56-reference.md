# R56 combinatorial consumer portfolio — reference

R56 consumes the grounded R55 `ConsumerAdmissionCandidate` graph and measures higher-order composition without transferring standing or authority between consumers.

The 50 executable queries are numbered 701–750. Queries 701–733 measure unordered consumer pairs: family diversity, identity correspondence, authority bounds, receipt-return compatibility, ggen manufacturability, dependency closure, replay, zero ambient DO, public-ontology alignment, projection capability, reusable courts, exact-head identity, standing, qualification-path diversity, adapter burden, and repository independence. Queries 734–749 lift the same invariants to unordered triples. Query 750 exposes the clean cross-family pair frontier whose members are exact-head, bounded, receipt-returning, ggen-manufacturable, dependency-closed, replayable, non-actuating, ontology-aligned, reusable-court and projection-capable.

The authority ceiling is `OBSERVE|SELECT|CONSTRUCT|VERIFY`; R56 never grants `DO`. R56 measures combinability only. A pair/triple result is evidence about composition candidates, not merge, deployment, standing, or actuation authority.

The permanent court is `tests/run_r56_combinatorial_consumer_portfolio.py`. It executes all 50 queries with RDFLib against `ontology.ttl` plus the exact R55 fixture and asserts expected cardinalities for the four-consumer specimen.
