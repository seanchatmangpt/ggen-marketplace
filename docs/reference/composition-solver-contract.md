# Reference: composition solver contract

Exact contract of `composition-solver-pack` (KernelPack, project profile). This page is a reference: it states what the pack sources declare and what was observed when the pack was manufactured, and it does not teach or justify. For the learning path see [Compose a capability cover](../tutorials/compose-a-capability-cover.md); for tasks see [Add a capability atom to the solver basis](../how-to/add-a-capability-atom.md); for rationale see [Why the solver is bounded and fenced](../explanation/why-the-composition-solver-is-bounded.md).

Nothing on this page copies a ggen release, commit, asset or digest. Where this page and a pack source differ, the source wins and this page is repaired.

## Scope and authority

- The pack SELECTs (queries, gates, inference CONSTRUCTs) and CONSTRUCTs candidate JSON. It declares no DO individual, class or property; gate `040_no_do_enabled.rq` refuses an enabled DO atom.
- Every generated row carries standing `UNKNOWN` and authority `NONE`. A `COVERED` row means a composition was found at one exact subject. It is not a manufactured, qualified or executed capability.
- It does not prove a generated consumer, an external system or any actuation boundary. Marketplace qualification proves its bounded boundary only.

## Vocabulary

Namespace `https://seanchatmangpt.github.io/packs/composition-solver-pack#` (`p:`). The seed basis uses `.../composition-solver-pack/basis#`.

| Term | Meaning |
|---|---|
| `p:Proposition` | A statement that is or becomes true, with `p:propId`. A given one carries `p:given true` and `p:admittedFrom`. |
| `p:CapabilityAtom` | A part with one `p:provides`, zero or more `p:requires`, `p:fromPack` and `p:authorityClass` (SELECT, CONSTRUCT or DO). |
| `p:Requirement` | Consumer input: `p:reqId` and one or more `p:needs`. |
| `p:derivable`, `p:enabled` | Materialized by inference stages. Never authored. |

## Manufacture

`ggen.toml` declares five `[[inference.rules]]`: stage 0 admits the given propositions, stages 1 to 4 are one identical CONSTRUCT unrolled four times. A non-DO atom is `p:enabled` when every requirement is `p:derivable`; it then makes its provided proposition derivable. Each CONSTRUCT carries `ORDER BY` because ggen's strict mode refuses an unordered inference CONSTRUCT (`E0011`).

Two rules write `generated/composition-solver/coverage.json` (per requirement and proposition: `COVERED`, `BLOCKED_AUTHORITY` or `UNCOVERED`) and `selected-atoms.json` (the backward closure of enabled atoms behind each needed proposition, by property path).

## Gates

| Gate | Refuses |
|---|---|
| `010_atom_identity` | an atom without atomId, fromPack, provides, or a lawful authorityClass |
| `020_stage_bound_converged` | a graph a further stage would still change (derivation depth over the bound) |
| `030_given_requires_admission` | a given proposition with no `p:admittedFrom` |
| `040_no_do_enabled` | an enabled DO atom |

Each gate has a pass and a fail witness with the exact same stem, and `ggen.toml` wires all four into `[validation].gates`, so a refusal stops `ggen sync run`.

## Observed behavior

Observed with ggen built from the pinned release commit; `tests/test_composition_solver_pack.py` pins each line and skips the ggen cases without a binary (`BLOCKED:ggen_binary_unavailable`).

| Observation | Result |
|---|---|
| Demo requirements | REQ-1 `COVERED` (depth-4 chain, four atoms), REQ-2 `BLOCKED_AUTHORITY`, REQ-3 `UNCOVERED` |
| Replay and fresh run | byte-identical output; second sync reports `unchanged: content identical` |
| Depth-5 chain | refused with `FM-LAW-018` naming the offending atom, not silently reported as a residual |
| Inference without `ORDER BY` | refused `E0011` |

## Known limits and sJira tickets

Each ticket states the proposition that must become true, so it can be projected as a candidate sJira work order (acceptance and falsifier included). All carry standing `UNKNOWN` and authority `NONE`. Deficit class names follow [Industry closure contract](industry-closure-contract.md).

### SJ-CSP-001 (L1): derivation depth is a static unrolling

- Evidence: inference rules run once each in order with no iteration, so depth equals the stage count (4). A depth-5 chain is refused (`FM-LAW-018`). A separate probe showed N3 `[law].rules` reaching a true recursive fixpoint (a depth-6 chain, past the SPARQL bound) for single-body Horn rules. Universal quantification ("every requirement derivable") in N3 was probed once with `log:notIncludes`; that probe was malformed and proved nothing, so N3 negation support is UNVERIFIED.
- Deficit class: SBB (marketplace, ggen capability).
- Must become true: the cover reaches a fixpoint for any acyclic basis without a hand-unrolled bound.
- Acceptance: either ggen gains an iterate-until-stable inference mode with a declared cap and a refusal on cap overrun, or an N3 encoding of "all requirements derivable" is shown to materialize correctly on a depth greater than 4 basis with a mixed single-/multi-requirement atom.
- Falsifier: a basis of depth 8 whose multi-requirement atom gets a wrong cover (enabled with an unmet requirement, or never enabled).

### SJ-CSP-002 (L2): authority class is self-declared

- Evidence: relabeling the DO atom `CONSTRUCT` made REQ-2 `COVERED` with exit 0; no gate detects it.
- Deficit class: authority.
- Must become true: an atom's authority class is bound to an admitted source, not to the basis author's assertion.
- Acceptance: a gate refuses an atom whose owning pack's admitted capability record (see `scripts/pack_capabilities.py`) disagrees with the declared class, with a fail witness for the mislabel above. Whether `scripts/pack_capabilities.py` records can express authority classes was not checked and is part of the ticket.
- Falsifier: a pack whose admitted capabilities include DO-like actuation yet which has an atom classed SELECT or CONSTRUCT passes.

### SJ-CSP-003 (L3): reachability, not selection

- Evidence: with an alternative provider added, both providers appear in `selected-atoms.json` for the same requirement. Nothing ranks, minimizes or applies cost, runtime, provenance or invariant-preservation constraints.
- Deficit class: SBB.
- Must become true: given alternatives, the solver names one composition under declared constraints, or states the constraint that left more than one.
- Acceptance: a ranked or constraint-filtered selection with the same gate refusals; if the engine cannot do it in SPARQL, a separate verifier lane with receipts.
- Falsifier: two providers differing in a declared constraint yield the same selection.

### SJ-CSP-004 (L4): atoms are authored in the solver basis

- Evidence: the seed atoms cite real packs but those packs declare no `provides`/`requires`; a search of `packs/`, `docs/` and `scripts/` finds no reference to this pack outside it. The solver's reading of a pack contract is therefore not authoritative.
- Deficit class: ontology.
- Must become true: a pack declares its own atoms, and the basis is a derived join of them.
- Acceptance: at least two packs declare their own atoms; a gate refuses a basis atom whose owning pack declares none.
- Falsifier: a pack changes its contract and the basis still reports it covered.

### SJ-CSP-005 (L5): Vision 2030 capabilities carry no dependency data

- Evidence: the Vision 2030 generator declares 50 capabilities and none has a `requires`, `provides` or `dependsOn` edge, so there is nothing to compose over. Asserting edges here would invent semantics.
- Deficit class: ontology.
- Must become true: each v30 capability is grounded to a provided proposition and its requirements from an admitted source.
- Acceptance: edges for a stated subset with provenance, and the solver cover over that subset.
- Falsifier: an edge cannot be tied to a source other than the author's judgment.

### SJ-CSP-006: Vision 2040 capability families are not manufactured

- Evidence: this change ships the composition solver only. The closure frontier ledger, generalization court and public-ontology admission families named in the Vision 2040 framing have no source.
- Deficit class: ontology and SBB. Depends on SJ-CSP-004 and SJ-CSP-005.
- Must become true: each family has admitted semantic source, a gate with witnesses, and a primary falsifier.
- Falsifier: closure ratio stays flat across epochs.

### SJ-CSP-007: pinned ggen release asset is not downloadable here

- Evidence: `scripts/install-ggen.sh` received HTTP 403 from the session egress proxy for the pinned release asset, so ggen was built from the pinned release commit instead. This is a network policy denial and was not retried.
- Deficit class: qualification.
- Must become true: the pinned, digest-verified asset is reachable, or the build-from-source path is an admitted alternative.
- Falsifier: a source build whose digest differs from the pinned asset's is accepted as equivalent.

Evidence on this page was observed at one exact subject. A source build is not the digest-pinned release asset, so it is not equivalent evidence for qualification, and marketplace CI remains the separate court.
