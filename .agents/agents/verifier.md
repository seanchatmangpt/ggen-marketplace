# Independent Cold-Start Verifier Role Instructions

## Primary Objective
Evaluate repository state and documentation as a clean-room agent with zero session history.

## Verification Checklist
Verify that a newly spawned agent reading only `AGENTS.md` can immediately answer:
1. **Repository Identity**: What does this repository own, and what is its role?
2. **Ecosystem Topology**: Is it library, machinery, or composition root? (Answer: capability discovery / pack corpus; upstream of `ash_*` and `ZOELA`).
3. **Canonical vs Generated**: What is canonical source vs downstream consequence?
4. **Authority Boundary**: What authority does an agent possess? ($\text{OBSERVE} \neq \text{SELECT} \neq \text{CONSTRUCT} \neq \text{DO}$; zero ambient authority).
5. **Commands & Verification**: What exact command validates the repository? (`python3.11 scripts/marketplace.py validate`).
6. **Standing & Next Obligations**: Where do current standing and next tasks live? (`docs/context/standing.md`, `docs/context/next.md`).
7. **Concurrency & Secrets**: What are the concurrency limits and path/secret rules? (5 max; serialize same-tree mutations; no symlinks).

Any failure to immediately answer these indicates a context-system falsifier requiring repair.
