# Tutorial: explore a reversible composition frontier

Start from an admitted capability set and encode each capability as an `oc:Capability`. Add pairwise or third-order `oc:Composition` entities, then represent each executable alternative as an `oc:Candidate`. Keep `oc:actuationPerformed false`: this pack manufactures option capital, not consequential execution.

Run the repository admission and validation ladder, then run ggen with this pack. Inspect `generated/option-capital/ledger.json` before `frontier.json`; the ledger preserves all admitted edges, while the frontier projects only candidates explicitly marked executable and non-dominated.

A failed candidate should be marked non-executable or dominated in ontology source and regenerated. Do not delete adjacent candidates merely because one edge fails qualification.
