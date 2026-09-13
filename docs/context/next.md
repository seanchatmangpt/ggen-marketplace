# Machine Handoff & Next Obligations

## 1. Active In-Flight Work
- **Branch**: `docs/rewrite-agents-contract`
- **Objective**: Refactor AI-agent context architecture into ~100-line `AGENTS.md` map, `.agents/rules/`, `.agents/agents/`, `docs/context/`, and `docs/adr/`.
- **Status**: Execution in progress.

## 2. Immediate Next Tasks
1. Complete `AGENTS.md` condensation to ~100 lines.
2. Add foundational ADRs (`ADR-0001`, `ADR-0002`, `ADR-0003`).
3. Run cold-start verification against the newly created structure.
4. Execute `python3.11 scripts/marketplace.py validate` and test suite.
5. Create atomic purpose commit.

## 3. Backlog Obligations
- Audit untracked directory `packages/marketplace-cli/` if scheduled for packaging.
- Legacy pack census consolidation follow-ups.
