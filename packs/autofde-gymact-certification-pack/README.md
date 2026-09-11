# autofde-gymact-certification-pack

Real, ggen-projected typed containers for autofde-lab's GymAct Certified conformance
vocabulary: `afl:CheckSeverity` (STRUCTURAL/BEHAVIORAL/EVIDENCE), `afl:ConformanceLevel`,
`afl:CertificationCheck`, `afl:CertificationCheckResult`, `afl:CertificationManifest`, and
the statically-scanned `afl:OracleContractFinding`/`afl:EvaluateArgShape` taxonomy.

## What this pack does

Admits and refuses **already-produced** certification check results for evidence
integrity. `gates/010_evidence_integrity.rq` refuses:

1. Any `afl:CertificationCheckResult` where `afl:resultPassed` is `true`, the referenced
   `afl:CertificationCheck` (via `afl:resultCheckRef` matching `afl:checkName`) carries
   `afl:checkSeverityRef afl:EVIDENCE`, and `afl:resultEvidenceRef` is absent -- a claimed
   EVIDENCE-level pass with no independently verifiable receipt.
2. Any `afl:CertificationCheckResult` whose `afl:resultCheckRef` does not match any
   admitted `afl:CertificationCheck`'s `afl:checkName` -- a result for a check that does
   not exist in this manifest's own universe.

## What this pack does NOT do

It does not run any certification check itself. It does not decide whether a check
passed. It does not compute a conformance level. All of that logic lives in
autofde-lab's `src/autofde_lab/reasoning/gymact_certification_checker.py`, hand-written
and out of scope for this pack. A `afl:CertificationManifest` admitted here is never a
pre-issued badge -- constructing the RDF does not itself certify anything; it only lets
already-decided, already-executed check results be represented and, via the gate,
refused when they claim more integrity than they can back up.

## Files

- `ontology.ttl` -- verbatim copy of `ontologies/autofde/gymact-certification.ttl`.
- `gates/010_evidence_integrity.rq` -- the SPARQL SELECT gate described above; any row is
  a refusal.
- `qualification/consumer.ttl` -- a real fixture: three `afl:CertificationCheck`
  individuals (one per severity) with matching, all-valid `afl:CertificationCheckResult`
  individuals and one `afl:CertificationManifest` tying them together. Verified against
  the gate with `rdflib` (zero rows); a temporary violating fixture (an EVIDENCE-severity
  pass with no receipt, and a result referencing an unknown check) was constructed
  in-memory to confirm the gate returns rows, then removed.
