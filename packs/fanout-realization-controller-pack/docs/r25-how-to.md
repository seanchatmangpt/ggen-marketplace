# How to qualify fanout-control realization

Use the canonical `fanout-realization-controller-pack` only.

- Bind each decision to an exact `owner/repo@40hex` subject, current generation, policy digest, receipt, and selected edge.
- Bind selected outcomes to realized qualified actions, dependency relief, cost, latency, standing, evidence root, receipt, and `actuationPerformed=false`.
- Add alternatives only when independently observed; `r25-13-observed-only-regret.rq` will not manufacture counterfactual evidence.
- Run all `queries/r25-*.rq`, the `03-control-realization-r25.rq` gate, and `tests/test_control_realization_r25.py`.
- Treat duplicate evidence roots, stale/split-current policies, missing receipts, authority drift, and a red worst stratum as falsifiers.
- Run ggen only from canonical source. Never hand-edit `generated/fanout-realization/*`.
