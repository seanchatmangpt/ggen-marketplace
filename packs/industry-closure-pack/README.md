# industry-closure-pack

KernelPack for the industry closure calculus. Public knowledge enters through
admission (pinned, licensed, vendored, inside scope; `EXCLUDED` with a reason;
`UNKNOWN` with a falsifier). Requirements have identity, a safe key, an explicit
scope disposition and an admitted origin. The residual is computed, never stored
as a second source of truth:

```text
Chain(c) := grounded(c) ∧ ABB ∧ approved contract ∧ QUALIFIED pinned SBB ∧ independent VERIFIED evidence at the current subject
Δ        := { (r, c) | r IN_SCOPE, ¬Chain(c) ∨ needsDoAuthority(r) }
```

Each residual has exactly one of seven deficit classes (first failing link), and the
class carries its own upstream target, delta code, acceptance text and falsifier text
as data. A monotone ledger of snapshots, coverages and receipted retirements records
growth; a regression marks a coverage `STALE` and keeps it.

## Identity

- Semantic source: `ontology.ttl` (namespace `https://seanchatmangpt.github.io/packs/industry-closure-pack#`).
  Vocabulary plus `DeficitClass` and `FeedbackTarget` individuals only; no specimen ABox.
- Input contract: `ontology/industry-input.ttl` ships empty. A ProfilePack or the
  consumer supplies the industry at that path.
- Terms of `enterprise-architecture-pack` (`ea:`) are consumed by IRI only; nothing is
  imported or re-typed, and no existing pack is edited.

## Gates and witnesses

`gates/010` to `gates/100` are SPARQL `SELECT ?subject ?reason`: zero rows pass, any row is a
typed `REFUSED:IC_*` refusal. `witnesses/pass/<stem>.ttl` returns zero rows and
`witnesses/fail/<stem>.ttl` triggers every `REFUSED:` literal its gate declares. The
repository test `tests/test_industry_closure_pack.py` executes all of them with rdflib;
`gate-court.toml` and `scripts/check_gate_witness_courts.py` prove stem correspondence only.

## Manufacture

`ggen.toml` is pass 2 of a two-pass pipeline (pass 1 is `enterprise-operating-model-pack`).
It renders, under `generated/industry-closure/`, a candidate residual ledger, candidate
sJira work orders, a candidate next snapshot and an upstream feedback packet. All are
candidates: they carry `authorityClaim "NONE"` and standing `UNKNOWN` or `BLOCKED`.

## Documentation

- Tutorial: `docs/tutorials/generate-an-industry-closure.md`
- How-to: `docs/how-to/add-an-industry-to-closure.md`, `docs/how-to/triage-an-industry-closure-residual.md`
- Reference: `docs/reference/industry-closure-contract.md`
- Explanation: `docs/explanation/industry-closure-as-architecture-strategy.md`

## Evidence boundary

This pack proves the bounded marketplace qualification boundary only, and the gates are
proven under rdflib. It selects and constructs; it carries no ambient DO authority.
`ea:QUALIFIED` is not ALIVE. The only input a real ggen would consume from this repository is the
synthetic qualification overlay; the residual of a real profile such as the retail-lending one is
rdflib-only evidence until a consumer wires the profile's `ontology.ttl` to `ontology/industry-input.ttl`
(see `docs/how-to/add-an-industry-to-closure.md`, section 8) and runs ggen on the exact subject. The
classifier uses EXISTS inside BIND, whose native-engine behaviour is unproven. Without a ggen binary, manufacture, execution and replay stay
`BLOCKED:ggen_binary_unavailable`; nothing here is ALIVE and no Level-5 claim is made.
