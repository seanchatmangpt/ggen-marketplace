# ggen Marketplace Agent Operating Contract

The canonical, reviewable corpus of reusable ggen pack source. This document provides cold-start navigation and non-negotiable repository invariants. Detailed rules and execution protocols live in `.agents/rules/` and `docs/`.

---

## 1. Mission & Ecosystem Topology

```text
ggen-marketplace (THIS REPO: reusable capability discovery & pack source)
    ↓
ash_* (reusable Ash/Elixir machinery)
    ↓
ZOELA / zoela_phx (admitted application composition root)
    ↓
ZOE Marketplace / Clients (running projections)
```

**Boundary Invariant**: This repository owns reusable pack source and marketplace documentation only. Consumer outputs and application composition logic do not belong here.

---

## 2. Read First & Source of Truth

1. **Operational Law**: [`marketplace.toml`](file:///Users/sac/ggen-marketplace/marketplace.toml) — authoritative pins, asset digests, qualification limits.
2. **Current Architecture**: [`docs/architecture.md`](file:///Users/sac/ggen-marketplace/docs/architecture.md) — observed components and pipelines.
3. **Current Standing**: [`docs/context/standing.md`](file:///Users/sac/ggen-marketplace/docs/context/standing.md) — exact-head evidence and verification matrix.
4. **Resumable Handoff**: [`docs/context/next.md`](file:///Users/sac/ggen-marketplace/docs/context/next.md) — machine handoff and active obligations.

---

## 3. Constitutional Invariants

- **Source Hierarchy**: `marketplace.toml` $\rightarrow$ `packs/<name>/pack.toml` $\rightarrow$ `ontology.ttl` $\rightarrow$ `templates/` $\rightarrow$ `gates/`.
- **Chesterton's Fence**: Apply Chesterton's fence before altering any rule, gate, or invariant.
- **Fail-Closed Admission**: Raw config, model outputs, templates, and hooks have **zero ambient execution authority**. Configuration executes only after `star-toml` admission ($q_{\text{config}}=1$).
- **Manufacture First**: Search `packs/` and `ggen_igniter` before inventing patterns ($\text{REUSE} \rightarrow \text{COMPOSE} \rightarrow \text{EXTEND} \rightarrow \text{INVENT}$).
- **No Duplicate Catalogs**: The catalog is a deterministic projection (`scripts/marketplace.py catalog`). Never commit a static `catalog.json`.
- **Path Safety**: No symlinks under `packs/`; all packs are self-contained.
- **Read-Only CI**: CI is read-only evidence; it must never rewrite or push pack corrections.

---

## 4. Operational Environment & Verification

- **Python Runtime**: Python 3.11+ is strictly required (`tomllib` stdlib). Run with `python3.11`.
- **Core CLI**: `scripts/marketplace.py` (zero external dependencies).
- **Canonical Validation Loop**:
  ```bash
  python3.11 scripts/marketplace.py validate
  python3.11 scripts/marketplace.py catalog > /tmp/a.json && python3.11 scripts/marketplace.py catalog > /tmp/b.json && cmp /tmp/a.json /tmp/b.json
  python3.11 scripts/marketplace.py fingerprint
  python3.11 -m pytest tests/ scripts/
  ```

---

## 5. Concurrency & Git Integration

- **Concurrency**: Serialize shared mutable trees. Isolated worktrees or separate repos may run concurrently (max 5 agents).
- **Repository Authority**: Discover remote default branch and ancestry; never assume `main`.
- **Baseline Before Blame**: Reproduce candidate failures on authoritative baseline before attributing regression.
- **Branch Discipline**: Work on purpose branches (`feat/`, `fix/`, `docs/`); atomic commits; non-force push; open draft PR.
- **Documentation Preservation**: A merge is not complete until code AND repository documentation are checked.

---

## 6. Where Detailed Rules & Decisions Live

- **Calculus & Evidence**: [`.agents/rules/evidence.md`](file:///Users/sac/ggen-marketplace/.agents/rules/evidence.md) ($A = \mu(O^*)$, evidence states).
- **Pack Manifest Contract**: [`.agents/rules/pack-contract.md`](file:///Users/sac/ggen-marketplace/.agents/rules/pack-contract.md) (`deny-unknown-fields`, profiles).
- **Git & Concurrency**: [`.agents/rules/git-integration.md`](file:///Users/sac/ggen-marketplace/.agents/rules/git-integration.md) (branch discovery, locking).
- **Security & Secrets**: [`.agents/rules/security.md`](file:///Users/sac/ggen-marketplace/.agents/rules/security.md) (token hygiene, path traversal).
- **Role Instructions**: [`.agents/agents/`](file:///Users/sac/ggen-marketplace/.agents/agents/) (`pack-developer`, `pack-integrator`, `verifier`, etc.).
- **Architectural Decisions**: [`docs/adr/`](file:///Users/sac/ggen-marketplace/docs/adr/) (`ADR-0001` through `ADR-0003`).