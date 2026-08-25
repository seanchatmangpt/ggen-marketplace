# Tutorial: calibrate option capital from realized evidence

Start with a reversible `rch:CompositionEdge` that records expected capability-space delta, expected reuse, and observed success/failure counts. Bind an exact current `rch:Realization` to that edge with PROV-O provenance, standing, exact subject, and a 64-character receipt digest.

Run the pack gates before generation. The evidence gate refuses current realizations without exact subject/receipt standing; the authority gate refuses ambient DO authority or performed actuation; the reversibility gate refuses incomplete composition edges.

Generate the portfolio and qualification court through `ggen.toml`. The frontier intentionally retains conservative, optimistic, reuse-adjusted, failed-edge, and Pareto views. A failed edge remains graph information rather than becoming a global rejection.
