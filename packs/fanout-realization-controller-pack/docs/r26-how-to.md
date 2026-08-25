# How to qualify R26 selection calibration

1. Bind each current `ControlDecision` to exact subject, generation, policy digest, receipt, SELECT authority, and `actuationPerformed=false`.
2. Bind selected outcomes to realized qualified actions, dependency relief, cost, latency, evidence root, receipt, currentness, VERIFY authority, and no actuation.
3. Add alternatives only when independently observed. Never synthesize an unexecuted alternative to improve recall or regret.
4. Execute every `queries/r26-*.rq` surface and `gates/04-selection-calibration-r26.rq`.
5. Treat costly zero-relief selections, missed observed beneficial alternatives, duplicate evidence roots, policy churn without realized improvement, and orphan current decisions as falsifiers.
6. Use the clean capital frontier only for SELECT. Consequential execution remains BRCE-only.
