# environment-evolution-pack

Reusable semantic contract for evolving **bounded GymAct environments** while keeping the task request fixed and correctness mechanically re-derived.

The pack extracts the useful mechanism from *Breaking the Environment Wall: Evolving LLM Agent Environments for Recursive Self-Improvement* (arXiv:2609.29773) and removes the assumption that a privileged learned "evolver" owns the loop.

## Ecosystem ownership

- **ggen-marketplace** owns this semantic contract and its SHACL admission surface.
- **AutoFDE Lab** may SELECT an evolution direction from planner/search/optimization machinery.
- **sJira** carries the exact work identity, parent subject, acceptance predicates, falsifiers, and evidence ceiling.
- **SA2A** carries powerless evolution candidates and failure-feedback observations.
- **GymAct** owns bounded environment materialization, observation, verification, checkpoint/restore, and replay.
- **OCEL / PROV** carry causal event history.
- **BRCE** remains the only consequential DO boundary. This pack grants no DO authority.

## Evolution law

For a fixed request digest `q`, an admitted variant changes environment state only together with its reference/evaluator assets:

```text
(E_t, y_t, V_t, H_t, D_t, z_t)
  -> candidate
  -> structural admission
  -> bounded GymAct materialization
  -> reference execution
  -> evaluator execution
  -> seed/variant comparison
  -> receipt + replay
  -> failure feedback D_(t+1)
```

An admitted candidate must bind:

1. the exact parent environment digest;
2. the byte-identical task-request digest;
3. at least three counter-default decision points;
4. each decision point's plausible wrong choice, uniquely resolving evidence, and rejecting check;
5. causal event-history identity;
6. the updated reference outcome and evaluator identities;
7. independent observations that the new reference passes and the previous reference fails.

The four canonical counter-default kinds are `temporal`, `exclusion`, `exception_rule`, and `numerical`.

## What is deliberately not canonical

The generator is **not** canonical. It may be an LLM, HDDL/FOND planner, constraint solver, search procedure, mutation system, procedural graph, hand-authored seed, or composition of those. Generator output is a candidate until the same semantic court admits it.

The objective is recursive **environment improvement with declining exceptional intelligence**, not recursive dependence on a particular model.
