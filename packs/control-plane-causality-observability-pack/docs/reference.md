# Reference

## Public semantic surface

The pack uses PROV-O for causal lineage, DQV for observations and yield measurements, and DCTERMS for identity/documentation. Its local `cpc:` vocabulary names control-plane-specific predicates while preserving public provenance semantics.

Core control-plane classes: `cpc:Request`, `cpc:WorkflowRun`, `cpc:Receipt`, `cpc:MemoryRecord`, `cpc:Observation`.

R70 manufacturing-capital classes: `cpc:ManufacturingInvestment`, `cpc:ReusablePrimitive`, `cpc:Consumer`, `cpc:QualifiedManufacturingAction`, `cpc:DependencyUnlock`, `cpc:Composition`, `cpc:YieldObservation`.

Identity and correspondence: `cpc:requestId`, `cpc:headSha`, `prov:used`, `prov:wasGeneratedBy`, `cpc:causedBy`, `cpc:exactSubjectPresent`, `cpc:provenancePresent`.

Currentness and standing: `cpc:current`, `cpc:currentEvidence`, `cpc:terminal`, `cpc:standing`, `cpc:downstreamStanding`, `cpc:archived`, `cpc:contradicted`.

Qualification evidence: `cpc:qualificationReceiptPresent`, `cpc:replayVerified`, `cpc:falsifierPassed`, `cpc:independent`, `cpc:sameEvidenceRoot`, `cpc:actuationPerformed`.

Capital metrics: `cpc:investmentUnits`, `cpc:qualifiedActionsUnlocked`, `cpc:marginalYield`, `cpc:memoryRecordsConsumed`, `cpc:memoryUnlocks`, `cpc:memoryMultiplier`, `cpc:reuseFactor`, `cpc:consumerFactor`, `cpc:compositionFactor`, `cpc:causalLagSeconds`, `cpc:optionPreserved`.

## Court families

001–012: request/receipt symmetry, latency, stale state, exact identity, provenance, fanout, authority.
013–024: duplicate/currentness/provenance correspondence and exact-head integrity.
025–043: terminal standing, ALIVE validity, metric validity, required identifiers, currentness.
044–049: fanout/receipt density and request↔receipt currentness disagreement.
050: clean request→workflow→receipt causal crown.
051–056: investment, action, unlock, primitive, consumer and composition census.
057–069: causal provenance, receipt/replay/falsifier/currentness, standing, temporal and shared-root falsifiers.
070–080: independent consumer yield, marginal Y, memory M, and observed leverage-factor measurement.
081–083: explicit sub-1000X evidence, false-claim guard and 10××10××10× admission crown.
084–090: option preservation, primitive provenance, independent composition and unlock correspondence.
091–100: clean yield frontiers, unrelated/ambiguous attribution, exact-subject qualification, causal Y/M and evidence-bounded phase-change crown.

## Capital equations

`Y = qualified manufacturing actions causally unlocked / manufacturing investment`.

`M = qualified opportunities or dependency unlocks caused by remembered state / memory records consumed`.

The 1000X crown requires independently evidenced `reuseFactor >= 10`, `consumerFactor >= 10`, and `compositionFactor >= 10` on current, replayed, falsifier-backed, receipted evidence. A positive factor product is an observation, not admission.

Authority is `OBSERVE|VERIFY|SELECT|CONSTRUCT`; consequential DO is excluded from this pack and remains BRCE-only.
