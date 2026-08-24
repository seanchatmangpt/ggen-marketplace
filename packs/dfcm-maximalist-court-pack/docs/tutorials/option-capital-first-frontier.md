# Build a first option-capital frontier

Model two actionable opportunities as `dmc:Opportunity`, connect them through a `dmc:Composition`, and emit multiple `dmc:ExecutableCandidate` nodes rather than selecting immediately. Mark independently verified candidates with `dmc:executable true`, attach reuse, reversibility, and capability-space-delta observations, then run the R12 frontier courts. The tutorial fixture at `fixtures/r12-option-capital.ttl` is intentionally small enough to replay while still containing pairwise, higher-order, zero-yield, dominated, and non-dominated cases.

The important invariant is that EXPLORE manufactures alternatives but does not actuate them: candidate authority is `CONSTRUCT|VERIFY` and `dmc:actuationPerformed` remains false. Use `r12-option-32-clean-executable-frontier.rq` only after receipts and standing exist.
