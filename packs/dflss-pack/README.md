# dflss-pack

`dflss-pack` is a Design for Lean Six Sigma (DMADV) domain ontology and template set. It
lets a consumer project generate a project charter, a DFMEA worksheet, and a control plan
document directly from its own DFLSS project facts, via a plain `ggen sync` run — no
separate rendering tool, no intermediate representation.

## Phase naming: DMADV, not DMEDI

Every existing DFLSS artifact in this ecosystem's prior art
(`cns/dflss_comprehensive_ontology.json`, `cns/semantic_ontology_framework.py`,
`open-ontologies/portfolio-os.ttl`'s `port:tickPhase` comment) uses DMADV
(Define-Measure-Analyze-Design-Verify). This pack matches that, not the DMEDI
(Define-Measure-Explore-Develop-Implement) naming from the original Black Belt course
curriculum, which has no existing source material to ground it in this ecosystem.

## CTQ admission is composed, not redefined

`dflss:CTQ` is `rdfs:subClassOf req:AdmittedCtq` — the requirements-andon pack's own
5-field-gated CTQ class (source, measure, verification, negative case, control plan). A
DFLSSProject may only cite a CTQ that has already cleared that admission gate. This pack
does not reimplement CTQ admission.

## Admission laws

The native SPARQL gates refuse:

1. a `DFLSSProject` missing a label or with no bound phase activity;
2. a `PhaseActivity` whose `dflss:hasPhase` does not resolve to a member of the closed
   `dflss:DMADVPhaseScheme`;
3. a `DFLSSProject` citing a CTQ that is not already `req:AdmittedCtq`;
4. a `DFMEARisk` missing severity/occurrence/detection (each must be 1-10) or a bound
   control plan;
5. a `DOEExperiment` with no declared factor or no declared response.

## Consuming this pack

```toml
# consumer project's ggen.toml
[packs]
dflss = { path = "../ggen-marketplace/packs/dflss-pack" }
# or, pinned:
# dflss = { git = "https://github.com/<org>/ggen-marketplace", version = "v26.9.x", subdir = "packs/dflss-pack" }
```

Then supply your own project facts (see `qualification/consumer.ttl` for a minimal worked
example satisfying every gate) and run `ggen sync run`. Output:

- `docs/DFLSS_PROJECT_CHARTER.md`
- `docs/DFLSS_DFMEA_WORKSHEET.md`
- `docs/DFLSS_CONTROL_PLAN.md`

## Scope

v1 renders documents only. Rust/Python code scaffolds for CTQ tracking and DOE factor
tables are a deliberate v2 addition once the document path is proven in production use.
