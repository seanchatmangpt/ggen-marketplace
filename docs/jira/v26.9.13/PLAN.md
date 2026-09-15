# v26.9.13 Jira Plan & Release Specification — ggen-marketplace

## 1. Charter (Define)

This milestone (`v26.9.13`) executes the comprehensive transformation of `ggen-marketplace` from a collection of isolated pack sources into a rigorous, versioned, closed-loop semantic manufacturing and discovery substrate.

### Core Objectives:
1. **Root Context Refactor**: Reduce agent rediscovery and instruction bloat by converting `AGENTS.md` into a ~75-line navigation map and constitutional invariants document, backed by specialized workspace rules (`.agents/rules/`), role instructions (`.agents/agents/`), context documents (`docs/context/`), and Architectural Decision Records (`docs/adr/`).
2. **First-Class Pattern Catalog**: Introduce `patterns/` and `domains/` as first-class architectural primitives, independent of the 12 consolidated capability packs:
   $$\boxed{\text{12-Pack Capability Topology} \neq \text{Pattern Catalog}}$$
   Admit the **`fond-hddl-mx-loop@v26.9.13`** (FOND–HDDL Machine Experience Loop) pattern, with **`repo-closure@v26.9.13`** as its first production domain instantiation.
3. **CalVer vs Semantic Compatibility Decoupling**:
   $$\boxed{\text{VersionIdentity} \neq \text{CompatibilitySemantics}}$$
   Enforce CalVer ($vYY.M.D$, `v26.9.13`) as the timestamped admission token, while encoding compatibility strictly as machine-checkable RDF predicates (`compatibleWith`, `supersedes`, `requires`, `projects`, `conformsTo`, `breakingAgainst`).
4. **Ecosystem Topology Formalization**:
   Codify the unidirectional, leak-free dependency chain:
   $$\text{ggen-marketplace} \longrightarrow \text{ash\_*} \longrightarrow \text{XaaS (sole DO crown)} \longrightarrow \text{ZOELA (tenant projection)}$$
   Auditing and mapping all 8 `ash_*` repositories (`ash_a2a`, `ash_ex4pm`, `ash_expo`, `ash_kudzu`, `ash_planning_center`, `ash_pplan`, `ash_r2rml`, `ash_surface`) against their governing marketplace packs.

---

## 2. Measure (Authoritative Baseline Evidence)

- **Base Repository Head**: `00f14b1b966900aa129f16a2e51727ef697823ec`
- **Active Purpose Branch**: `docs/rewrite-agents-contract`
- **Marketplace Subject Inventory**:
  - Packs: `312`
  - Manifests (`pack.toml`): `312`
  - Ontologies (`.ttl`): `463`
  - Templates (`.tmpl` / `.tera`): `1800`
  - Native SPARQL Gates (`.rq`): `1470`
  - Verifier Python Gates (`.py`): `37`
  - Profiles: `{"project": 124, "projection": 150, "semantic": 38}`
  - Required Diátaxis Pages: `20`
- **Admitted SHA-256 Corpus Fingerprint**:
  `sha256:920b3868d75bdf0bed6abcb1422d29f7e785d945c43d11af6e0f455bfd4299cf` (`files=13742`)
- **Pytest Baseline**: `16 passed in 0.07s`

---

## 3. Analyze: The 6-Identity Closed-Loop Pattern

Operational automation requires a closed-loop pattern where machine experience refines admissible machinery:
$$\boxed{O_t \rightarrow \text{HDDL} \rightarrow \text{FOND} \rightarrow \text{SELECT} \rightarrow \text{CONSTRUCT} \rightarrow \text{BRCE} \rightarrow R_t \rightarrow \text{Replay} \rightarrow \text{MX} \rightarrow O_{t+1}}$$

### The 6 Independent Semantic Identities
To prevent "best-effort" drift, replay binds to exact CalVer identities across six separate dimensions:

| Identity Dimension | Canonical Release Token | Primary Artifact |
|---|---|---|
| **1. Pattern Contract** | `fond-hddl-mx-loop@v26.9.13` | [`patterns/fond-hddl-mx-loop/pattern.ttl`](file:///Users/sac/ggen-marketplace/patterns/fond-hddl-mx-loop/pattern.ttl) |
| **2. Domain Taxonomy** | `repo-closure@v26.9.13` | [`domains/repo-closure/domain.ttl`](file:///Users/sac/ggen-marketplace/domains/repo-closure/domain.ttl) |
| **3. Planner Projection** | `repo-closure-hddl@v26.9.13` | [`domains/repo-closure/closure.hddl`](file:///Users/sac/ggen-marketplace/domains/repo-closure/closure.hddl) |
| **4. Uncertainty Policy** | `repo-closure-fond@v26.9.13` | [`domains/repo-closure/closure.fond`](file:///Users/sac/ggen-marketplace/domains/repo-closure/closure.fond) |
| **5. MX Schema** | `mx-episode-schema@v26.9.13` | [`patterns/fond-hddl-mx-loop/contracts/mx.ttl`](file:///Users/sac/ggen-marketplace/patterns/fond-hddl-mx-loop/contracts/mx.ttl) |
| **6. Verifier Contract** | `repo-closure-verifier@v26.9.13` | [`domains/repo-closure/verifier/verify_closure_episode.py`](file:///Users/sac/ggen-marketplace/domains/repo-closure/verifier/verify_closure_episode.py) |

### Formal Replay Equation
$$\text{Replay} = f(\text{SubjectHead}, \text{Pattern@v26.9.13}, \text{Domain@v26.9.13}, \text{HDDL@v26.9.13}, \text{FOND@v26.9.13}, \text{Verifier@v26.9.13})$$

### Machine Experience Promotion Calculus
$$\text{Episode} \longrightarrow \text{CandidateKnowledge} \longrightarrow \text{EvidenceAccumulation} \longrightarrow \text{FormalAdmission} \longrightarrow \Delta \text{Machinery}$$
- **Invariant**: $\text{Experience} \neq \text{Authority}$; $\text{LearnedCandidate} \neq \text{AdmittedMethod}$.
- Episodes ($MXEpisode/2026-09-13/000001$) are immutable experience data.
- A new CalVer is cut **only** when admitted machinery changes. No MX-derived heuristic enters active execution without independent verifier admission.

---

## 4. Work Breakdown (Jira Epics & Issues)

### Epic JIRA-26913-01: Agent Operating Context Refactor
- **TASK-01.1**: Condense root `AGENTS.md` to ~75 lines of pure navigation map + constitutional invariants.
- **TASK-01.2**: Implement specialized Antigravity workspace rules under `.agents/rules/` (`evidence.md`, `pack-contract.md`, `git-integration.md`, `security.md`).
- **TASK-01.3**: Implement specialized role definitions under `.agents/agents/` (`pack-developer`, `pack-integrator`, `market-architect`, `context-compiler`, `verifier`).
- **TASK-01.4**: Establish dynamic context boundaries in `docs/context/standing.md` and `docs/context/next.md`.

### Epic JIRA-26913-02: Pattern Catalog & CalVer Admission
- **TASK-02.1**: Establish `patterns/fond-hddl-mx-loop/` with `pattern.ttl`, `compatibility.ttl`, `pattern.shacl.ttl`, and contracts (`mx.ttl`).
- **TASK-02.2**: Implement SPARQL gate `patterns/fond-hddl-mx-loop/gates/010_select_ceiling.rq` enforcing the SELECT ceiling on loop proposals.
- **TASK-02.3**: Establish `domains/repo-closure/` with `domain.ttl`, `closure.hddl`, `closure.fond`, and `verify_closure_episode.py`.
- **TASK-02.4**: Create `ADR-0004-fond-hddl-mx-loop-pattern-and-calver.md`.

### Epic JIRA-26913-03: Ecosystem Topology & Platform Boundaries
- **TASK-03.1**: Create `ADR-0001-deterministic-catalog-projection.md` (catalog as deterministic projection, never static file).
- **TASK-03.2**: Create `ADR-0002-star-toml-admission-boundary.md` (`marketplace.toml` raw observation until `star-toml` admission).
- **TASK-03.3**: Create `ADR-0003-ecosystem-topology-and-composition-boundary.md` (XaaS sole platform crown vs ZOELA tenant projection).
- **TASK-03.4**: Update `docs/architecture.md` and `docs/target-architecture.md`.

### Epic JIRA-26913-04: `ash_*` Machinery Audit & Mapping
- **TASK-04.1**: Live audit of all 8 `~/ash_*` repositories (`mix.exs`, DSL extensions, ontologies, git states).
- **TASK-04.2**: Produce `docs/reference/ash-ecosystem-mapping.md` cross-referencing packages to marketplace packs.
- **TASK-04.3**: Codify generator tooling boundaries (`mix ggen_igniter.sync` vs `ggen sync run`).

---

## 5. Definition of Done (DoD) & Quality Gates

Every deliverable in the `v26.9.13` milestone must satisfy all seven non-negotiable gates:

1. **Gate 1 — Fail-Closed Admission**:
   `python3.11 scripts/marketplace.py validate` must exit `0`, reporting:
   - Zero syntax, manifest, or identity errors.
   - `deny-unknown-fields` enforced across all manifests.
   - Required Diátaxis surface complete (20/20 files present and non-empty).
2. **Gate 2 — Catalog Projection Determinism**:
   Generating the catalog twice consecutively must yield byte-for-byte identical output:
   ```bash
   python3.11 scripts/marketplace.py catalog > /tmp/a.json
   python3.11 scripts/marketplace.py catalog > /tmp/b.json
   cmp /tmp/a.json /tmp/b.json
   ```
3. **Gate 3 — Corpus Fingerprint Verification**:
   `python3.11 scripts/marketplace.py fingerprint` must successfully compute a deterministic SHA-256 digest over the entire visible pack corpus.
4. **Gate 4 — Repository Test Suite**:
   `python3.11 -m pytest tests/ scripts/` must pass with 100% success rate.
5. **Gate 5 — Pattern & Episode Conformance**:
   The independent episode verifier `domains/repo-closure/verifier/verify_closure_episode.py` must execute cleanly and return `[VALID]`.
6. **Gate 6 — Authority Separation (`SELECT ≠ DO`)**:
   All planner outputs, HDDL methods, and FOND branch recovery proposals must enforce `pp:hasDOAuthority false` via gate `010_select_ceiling.rq`.
7. **Gate 7 — Git Discipline & Documentation Preservation**:
   - Work conducted on dedicated purpose branch (`docs/rewrite-agents-contract`).
   - Atomic commits with clear rationale.
   - Documentation contracts preserved across all merges.

---

## 6. Control & Rollout Plan

1. **Local Acceptance Execution**:
   Run the canonical 5-step loop on Python 3.11+.
2. **Machine Handoff Synchronization**:
   Update `docs/context/standing.md` and `docs/context/next.md` with exact commit SHAs, test results, and remaining obligations.
3. **Downstream Consumption**:
   - `XaaS`: Consumes `v26.9.13` marketplace release for capability profiles and consequence IR.
   - `ash_*`: Compiles against marketplace ontologies via `ggen_igniter` / `ggen`.
   - `ZOELA`: Connects to XaaS GraphQL / A2A interfaces using experience projection and dynamic UI contracts.
