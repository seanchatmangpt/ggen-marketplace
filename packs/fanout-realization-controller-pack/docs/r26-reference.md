# R26 selection-calibration reference

R26 consumes observed `ControlOutcome` evidence and exposes executable selection calibration without manufacturing counterfactual outcomes.

## Metrics

- confusion matrix, precision, observed-alternative recall, and F1;
- realized dependency-relief ROI and latency-normalized relief;
- independent evidence-root diversity and duplicate-root pressure;
- policy-generation realized value and churn without improvement;
- orphan current decisions without selected realized outcomes;
- qualified-action capital yield and root-discounted yield.

## Admission

`04-selection-calibration-r26.rq` admits only current, receipted, exact-subject, non-actuating evidence. `SELECT` remains distinct from `VERIFY`; neither implies `DO`.

## Frontier

`r26-35-clean-capital-frontier.rq` preserves positive, current, independently rooted selected outcomes while refusing negative-value selected evidence. Observed alternatives remain evidence, never ambient execution authority.
