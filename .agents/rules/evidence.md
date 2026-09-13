# Evidence and Refusal Calculus

## 1. Evidence Taxonomy

Every operational claim regarding a pack, workflow, or acceptance boundary must be classified into an explicit evidence state:

| State | Definition |
|---|---|
| `UNKNOWN` | No direct verification attempt has been executed at the current boundary. |
| `PARTIAL_ALIVE` | Sub-checks passed, but the complete acceptance boundary has not executed. |
| `ALIVE` | Exact admitted execution succeeded against real runtime boundaries. |
| `BLOCKED` | Execution is halted on an external dependency or unmet prerequisite. |
| `BUILD_BROKEN` | Repository or pack build/syntax/validation failed. |
| `UNSUPPORTED` | Capability is explicitly out of scope for the target profile or platform. |
| `REFUSED_*` | Failed closed on a formal contract or admission gate (e.g. `REFUSED_PYTHON_3_11_REQUIRED`). |

## 2. Formal Calculus

$$A = \mu(O^*)$$
$$R = \text{receipt}(A)$$

- **Strict Separation of Powers**:
  $$\text{OBSERVE} \neq \text{SELECT} \neq \text{CONSTRUCT} \neq \text{DO}$$
- Raw configuration, planner/model outputs, templates, and hooks possess **zero ambient execution authority**.
- Configuration becomes executable only after formal admission (`star-toml` / `scripts/admit-config.sh`) returns a verified witness (`q_config=1`).

## 3. Baseline Before Blame

A candidate failure does not prove the candidate caused it:
$$\text{candidate failure} \rightarrow \text{reproduce on authoritative baseline} \rightarrow \text{classify NEW\_REGRESSION or PRE\_EXISTING}$$

- Dirty worktree $\neq$ `BUILD_BROKEN`.
- Open PR $\neq$ unmerged semantics.
- File existence $\neq$ executed capability.
