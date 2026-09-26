# premature-actuation-survival-pack

Reusable semantic source for long-horizon autonomic survival experiments.

The pack takes the time-to-failure evaluation pattern from
**arXiv:2609.29508** and specializes the event of interest to the first invalid
consequential `DO`. It does not make an LLM the owner of generation,
analysis, or execution.

## Ownership

- **ggen-marketplace** owns the semantic vocabulary, refusal gates, catalog
  queries, generator templates, and anti-vacuity witness court.
- **GymAct** owns bounded scenario/policy/factor manufacture, deterministic
  fault campaigns, manifests, replay, and powerless synthetic evidence.
- **autofde-lab** owns first-failure/recurrent survival analysis, competing
  risks, uncertainty, log-rank comparison, OCEL projection, stratification,
  and configured SPC drift courts.
- **BRCE** remains the only consequential DO boundary.

No artifact in this pack grants DO authority.

## Canonical machinery

The ontology declares five policy machinery strata:

1. `llm-native`
2. `llm-tools`
3. `selective-llm`
4. `planner-llm-residue`
5. `formal-generated`

It also declares the canonical 4×3 reversible campaign factor grid:

- authority: `full | filtered | expired`
- transport: `stable | lossy | reordered`
- evidence: `complete | delayed | missing`
- terminal signal: `exact | stale | false_positive`

and all eight deterministic observational fault identities used by GymAct.

## Analysis prior art

The ontology names the analysis machinery rather than collapsing it into a
single benchmark score:

- Kaplan-Meier first-failure survival
- restricted mean survival time (RMST)
- Greenwood + log-log survival confidence intervals
- Wilson interval for observed failure probability
- two-sample log-rank comparison
- configured two-sided CUSUM for explicitly bound release series

The first five require the same exact subject/workload/horizon. CUSUM is the
intentional exception: exact subjects may change across a named series, while
workload, policy, and horizon stay fixed.

## Generated catalogs

`ggen.toml` projects the ontology into four replaceable machine catalogs:

- `generated/survival/policies.json`
- `generated/survival/factors.json`
- `generated/survival/faults.json`
- `generated/survival/analysis-methods.json`

The generated files are projections. The ontology remains the source.

## Qualification

`gate-court.toml` pairs every semantic gate with one passing and one failing
witness. The semantic runner executes **all** gates for every witness and
requires a failing witness to fire only its corresponding gate.

`qualification/verify_catalog.py` independently checks:

- SHACL conformance,
- zero refusal rows on the canonical ontology,
- exactly 5 policies,
- exactly 12 factor levels,
- exactly 8 fault kinds,
- exactly 6 analysis methods,
- contract ownership/authority/receipt/replay bindings.

A clean catalog is structural evidence only. It is not runtime or production
standing.
