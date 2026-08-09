# Explanation: pack lifecycle

A pack moves through four distinct concerns:

1. **Author** — establish identity, RDF facts, templates, and admission gates.
2. **Admit** — marketplace validation proves structural and catalog invariants at an exact repository subject.
3. **Execute** — the ggen runtime combines the pack with consumer facts and manufactures files.
4. **Verify consequence** — the consumer's native tests, compilers, or external oracles establish whether the manufactured artifact has the required behavior.

Keeping these concerns separate prevents a marketplace green check from being mistaken for proof of an external consequence. It also makes failures easier to route: manifest/layout failures belong here; rendering/runtime failures belong at the ggen execution boundary; consumer behavior failures belong at the consumer verification boundary.
