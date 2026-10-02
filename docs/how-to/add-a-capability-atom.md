# How to add a capability atom to the solver basis

Use this when a marketplace capability should take part in covers. Exact contracts are in [Composition solver contract](../reference/composition-solver-contract.md). Known limits SJ-CSP-002 and SJ-CSP-004 apply: the atom's authority class and its dependency edges are declared by you, not verified against the owning pack.

1. Pick the owning pack or external boundary, and write its name in `p:fromPack`. If no real owner exists, stop; do not invent one.
2. Name the one proposition it provides and every proposition it requires. Reuse existing `p:Proposition` individuals so chains connect.
3. Set `p:authorityClass`. Anything that causes external consequence is `DO`. When unsure, choose `DO`: the solver then reports `BLOCKED_AUTHORITY` rather than a cover.
4. Add the atom to `ontology/basis.ttl`. A given proposition needs `p:admittedFrom` naming a public source.
5. Run the gate court, then manufacture in a scratch copy and read `coverage.json`.
6. If sync is refused with `FM-LAW-018`, the chain is deeper than the stage bound. Do not raise it by hand without updating SJ-CSP-001 and the depth-bound test.
7. If two atoms now provide one proposition, expect both in `selected-atoms.json` (SJ-CSP-003).

Changes land by pull request. A generated cover is a candidate, never an approval.
