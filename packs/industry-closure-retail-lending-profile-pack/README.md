# industry-closure-retail-lending-profile-pack

ProfilePack for the industry closure calculus: one bounded real industry, consumer and mortgage
lending origination, expressed as ABox over `industry-closure-pack` vocabulary. Later industries are
sibling profile packs of the same shape, never new kernels.

## What it carries

- `lnd:RetailLending`, an `ic:IndustryClosure` bound to `ontologies/public/fibo/LOAN/`, with the empty
  epoch-0 snapshot `lnd:Snapshot0` (the closure starts empty).
- Four ADMITTED knowledge sources (FIBO LOAN Loans, LoanApplications, LoansRegulatory,
  MortgageOrigination), each pinned by the sha256 of the vendored file, with ontology IRI, version IRI
  and licence boundary read from the vendored file itself. One EXCLUDED source (MarineFinance) with a
  reason and one UNKNOWN source (StudentLoans) with a falsifier.
- Eight capability individuals grounded in those sources, and eleven paraphrased requirements: nine
  IN_SCOPE and mapped, one IN_SCOPE that needs consequential authority, one OUT_OF_SCOPE with its
  justification.
- `qualification/expected-residual.json`: the golden residual (`queries/10-residual.rq` of the kernel
  over kernel plus this ontology). Nine `DEFICIT_ABB` rows and one `DEFICIT_AUTHORITY` / `BLOCKED`
  row; the out-of-scope requirement is absent from the residual but keeps its justification.

## What it does not carry

No ABBs, SBBs, coverages, execution evidence or receipts, and no DO authority. A need for DO
authority is recorded as a need. The honest starting standing is `UNKNOWN` (and `BLOCKED` for the
authority row); nothing here is `ALIVE`. Manufacture with a real ggen runtime is
`BLOCKED:ggen_binary_unavailable` in an environment without that binary.

## Gate

`gates/010_profile_grounding.rq` refuses `REFUSED:LND_CAPABILITY_CONCEPT_NOT_PROVIDED`,
`REFUSED:LND_CAPABILITY_CONCEPT_MISSING`, `REFUSED:LND_REQUIREMENT_SOURCE_NOT_IN_CLOSURE` and
`REFUSED:LND_SOURCE_NOT_FIBO_LOAN`. Witnesses
under `witnesses/pass` and `witnesses/fail` share its exact stem; `tests/test_industry_closure_profile.py`
executes them with rdflib. The kernel gates 010, 020, 030, 060, 070, 080, 090 and 100 are executed
over kernel plus profile by the same test.

## Wiring into a consumer

The profile has no `ggen.toml` and no templates. A consumer copies this pack's `ontology.ttl` over the
kernel's `ontology/industry-input.ttl` (the single input its `ggen.toml` imports) and runs the kernel; the
commands and the checks to make afterwards are in `docs/how-to/add-an-industry-to-closure.md`, section 8.
`tests/test_industry_closure_profile.py` rehearses that wiring under rdflib. The golden residual is
therefore rdflib-only evidence: this profile has never been manufactured through ggen, and no
qualification overlay builds it.

## Evidence boundary

Marketplace admission, rdflib courts and (in CI, with a real ggen) qualification only. The vendored
FIBO files are not edited. Digests are not copied from documentation: the test recomputes them.
