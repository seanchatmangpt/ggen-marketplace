# ADR-0004: fond-hddl-mx-loop Closed-Loop Pattern & CalVer Admission

## Status
Accepted

## Context
The 12 capability packs consolidated in v26.9.12 define the authoritative semantic capability topology of the ggen marketplace. However, operational work (e.g. repository chores, release closure, incident recovery) requires executing a closed-loop pattern:
$$\boxed{O_t \rightarrow \text{HDDL} \rightarrow \text{FOND} \rightarrow \text{SELECT} \rightarrow \text{CONSTRUCT} \rightarrow \text{BRCE} \rightarrow R_t \rightarrow \text{Replay} \rightarrow \text{MX} \rightarrow O_{t+1}}$$

Crucially, **the 12-pack topology is not a pattern catalog**. Patterns represent versioned compositions across those capability boundaries. Furthermore, importing SemVer assumptions (such as "minor is backward compatible") into multi-agent closed loops obscures real semantic compatibility.

## Decision
1. **Establish `fond-hddl-mx-loop` as a First-Class Architectural Pattern**:
   - Released under the ecosystem CalVer (`v26.9.13`).
   - First production domain instantiation: `repo-closure@v26.9.13`.

2. **Decouple Version Identity from Compatibility Semantics**:
   $$\text{VersionIdentity} \neq \text{CompatibilitySemantics}$$
   - **CalVer** ($vYY.M.D$, `v26.9.13`) records when machinery was formally admitted.
   - **Ontology** explicitly defines compatibility using machine-checkable predicates:
     `compatibleWith`, `supersedes`, `requires`, `projects`, `conformsTo`, `breakingAgainst`.

3. **Six Independent Semantic Identities**:
   | Identity | Release Token | Semantic Meaning |
   |---|---|---|
   | Pattern | `fond-hddl-mx-loop@v26.9.13` | Semantic contract of the closed loop |
   | Domain | `repo-closure@v26.9.13` | Repository-closure ontology / chore actions |
   | Planner projection | `repo-closure-hddl@v26.9.13` | HDDL task methods and primitive operators |
   | Uncertainty policy | `repo-closure-fond@v26.9.13` | FOND outcomes, branch policies, recovery actions |
   | MX schema | `mx-episode-schema@v26.9.13` | Experience record schema and promotion calculus |
   | Verifier contract | `repo-closure-verifier@v26.9.13` | What admits a successful episode |

4. **Replay & Promotion Calculus**:
   - Replay is an exact function of the six identities:
     $$\text{Replay} = f(\text{SubjectHead}, \text{Pattern@v26.9.13}, \text{Domain@v26.9.13}, \text{HDDL@v26.9.13}, \text{FOND@v26.9.13}, \text{Verifier@v26.9.13})$$
   - Episodes ($MXEpisode/2026-09-13/000001$) are immutable data.
   - A new CalVer is cut **only** when admitted machinery changes.
   - $\text{Experience} \neq \text{Authority}$; $\text{LearnedCandidate} \neq \text{AdmittedMethod}$. No MX-derived rule enters exploitation without formal verification and admission.

## Consequences
- Patterns live under `patterns/` and domains under `domains/` rather than polluting single pack boundaries.
- Future closed loops (release-closure, migration, deployment, incident-recovery) instantiate `fond-hddl-mx-loop` without re-inventing the loop contract.
