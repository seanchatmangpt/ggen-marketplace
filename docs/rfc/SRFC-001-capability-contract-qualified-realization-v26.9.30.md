# SRFC-001 v26.9.30

## Capability Contract and Qualified Realization — From Public Meaning to Replayable Receipt

**Status:** Proposed Standard
**Version:** v26.9.30
**Category:** Architecture / Semantics
**Series:** SRFC (Semantic RFC). Technology-independent by construction. Sibling of,
not an extension of, RFC-GGEN-001 (pack core). RFC-GGEN-002 remains reserved for the
Qualification Court.
**Intended audience:** authors of capability contracts; authors of realizations and
generators; authors of consumer-side integration; auditors of receipts.

> This document uses RFC-style normative language but is not an IETF publication.

---

# 1. Abstract

A capability is a public meaning. A realization is some artifact that claims to
carry that meaning. A projection is consumer-side material generated from the
meaning plus one chosen realization. This document defines the chain that connects
them and the single rule that governs every link: each transition is admitted by a
check that can refuse, and each admitted transition leaves evidence that a third
party can replay.

```text
Public Meaning
  -> Capability Contract        (13 elements, section 6)
  -> Qualified Realization      (section 7)
  -> Generated Projection       (section 8)
  -> Admitted Runtime           (section 9)
  -> Evidence / Standing        (section 10)
  -> Receipt / Replay           (section 11)
```

This document names no programming language, runtime, template engine, graph store,
or binary format. Reference realization profiles that do are non-normative and live
in the documentation of the pack that implements this chain, never here.

# 2. Status of This Document

Proposed Standard within the ggen ecosystem document series. It has no relationship
to the IETF series beyond borrowing the normative-language convention. It is law, not
court: it states invariants and a falsifier for each, and does not itself build the
qualification corpus that executes those falsifiers.

# 3. Conventions Used in This Document

The capitalized key words of the specification convention (the strong-obligation word and
its negation) are normative in sections 5 through 13 only. Fixed vocabularies are rendered
as fenced text blocks.

Each numbered requirement in sections 5 through 13 is atomic. It consists of a heading, one
requirement sentence, one line beginning `Invariant:` and one line beginning `Falsifier:`, in
that order. The requirement sentence contains exactly one occurrence of the strong-obligation
word or of its negation, and nothing else in the requirement carries a modal of obligation,
recommendation or permission (a consequence that would be a second obligation is a separate
requirement). The falsifier names the stimulus, the boundary expected to decide it, the
forbidden outcome, and what would make a passing result invalid (a check that never exercised
the forbidden transition). A falsifier that cannot observe its own forbidden transition is
silence, not a verdict. The scripted check of section 15 enforces this paragraph.

# 4. Terms and Definitions

```text
Public Meaning        — a statement of what a capability is, expressed in public
                        vocabularies, independent of any implementation.
Capability Contract   — the 13-element record of section 6.
Realization           — an artifact claiming to implement a contract.
Qualified Realization — a realization with passing court evidence for one contract
                        version, bound to an exact artifact identity.
Realization Profile   — a named bundle of host assumptions under which a
                        realization is qualified. Profiles carry all host-specific
                        knobs; the contract and this document carry none.
Consumer Binding      — the single input that selects: one contract, one chosen
                        realization, one profile, one artifact pin, a ceiling.
Artifact Pin          — an exact identity (algorithm, digest, byte length) of one
                        realization artifact.
Projection            — consumer-side material derived deterministically from a
                        Consumer Binding.
Admission             — a check that may refuse. A check that never refuses is not
                        admission.
Refusal               — a typed, named, non-silent rejection carrying a code, a
                        class, and a broken term.
Authority Ceiling     — the maximum consequence any artifact in the chain may
                        cause. In this document it is NONE.
Standing              — a derived verdict about a subject, valid only for the
                        exact identity and scope it was derived against.
Receipt               — a record of identity, authority, consequence, replay, and
                        standing for one transition.
Alignment             — an explicit, machine-readable relation from a term to a published
                        term (subclass, subproperty, or a stated correspondence).
Delta Justification   — a written statement, bound to the nearest published term, of the
                        distinction that no published term carries.
Gate                  — one admission check over a graph that returns a violation row
                        for each defect it finds and no row otherwise.
Witness               — a small graph paired with a gate: a passing witness yields
                        zero rows from every gate, a failing witness yields rows from
                        exactly the named gate.
Court                 — the set of all gates with their witness pairs, run together;
                        it is the corpus that executes the falsifiers.
Broken term           — the name of the failure kind a refusal reports, one of:
                        mu_on_O (generation from an unadmitted input),
                        admission_vacuous (a check that never refuses),
                        R_missing_identity, R_missing_authority (a receipt field
                        absent). The set is closed for this document.
Partial standing      — standing derived from evidence that does not include an
                        observed run of the exact admitted subject (R33).
Positive standing     — standing derived from evidence that includes one (R33).
```

# 5. No Private Semantics

Normative alignment sources. These are published standards, not technology products; the
section 15 neutrality scan exempts exactly these names:

```text
PROV-O     — provenance (Entity, Activity, derivation, generation, use)
DCAT       — distributions, byte size, media type, download location
SPDX       — checksums (algorithm, value), files, packages
ODRL       — permission and policy (the separate permission plane)
SKOS       — concept schemes, notations, correspondence and scope notes
SHACL      — shape constraints over graphs
OWL-Time   — temporal terms, only if a temporal term is introduced
```

Informative counterparts (not normative sources): the qri contract vocabulary of the pack
core, and W3C SOSA/SSN for capability.

## R1 — Public Vocabulary First

Every term used to express a contract, binding, pin, projection, or receipt MUST be a published term where one exists, so that a new term appears only as the smallest delta that carries a distinction no published term carries.

Invariant: a term that duplicates a published term does not exist in the vocabulary.

Falsifier: add a term that duplicates a published term and observe the vocabulary gate admit it. The boundary is the vocabulary gate. A pass is invalid if the gate never compared the term against the published set.

## R2 — Alignment Is Explicit

The vocabulary MUST state the alignment of each new term as an explicit machine-readable relation to a published term from the normative alignment sources or to the pack-core contract vocabulary, name similarity never being treated as alignment.

Invariant: every new term has at least one stated relation to a published term.

Falsifier: remove the stated relation of one new term, leaving a similar name, and observe the alignment gate. The boundary is the alignment gate. A pass is invalid if the gate compared names instead of relations.

## R3 — New Terms Carry Subsumption Or Delta

Each new term MUST be a subclass or subproperty of a published term, or carry a Delta Justification bound to the published term it nearest matches.

Invariant: each new term has a subsumption link to a published term, or a justification and a nearest-match link.

Falsifier: add a new term with neither a subsumption link nor a justification and observe the alignment gate; then add a justification with no nearest-match link. Both cases are refused. The boundary is the alignment gate. A pass is invalid if the gate accepted the justification text without checking the nearest-match link.

## R4 — Meaning Is Not Realization

A contract MUST be expressible and checkable without reference to any realization, host, language, or format.

Invariant: the contract record contains no element whose value names a realization technology; profile identifiers (element 6) are opaque tokens the contract never interprets and are the only values exempt from this scan.

Falsifier: inject a technology-specific value into a contract element and observe the contract check admit it. The boundary is the contract check. A pass is invalid if the check inspected only element presence and never element values.

# 6. Capability Contract

A capability contract has exactly thirteen elements.

```text
 1  Semantic identity       — contract identifier, version, content digest
 2  Input/output contract   — logical operations and their field names
 3  Invariants              — named properties every realization preserves
 4  Refusal                 — the typed refusal vocabulary (section 12)
 5  Authority ceiling       — NONE
 6  Runtime assumptions     — the profile identifiers under which qualification
                              was observed; values live in the profile
 7  Provenance              — derivation of the contract and its realizations
 8  Evidence                — the receipts that qualify a realization
 9  Replay                  — what is needed to recompute each receipt
10  Qualification courts    — identity of the courts that produced the evidence
11  Artifact digests        — pins for each realization artifact
12  Realization and
    projection identity     — identifiers of realizations and projections
13  Substitution claim      — a claim that two realizations are interchangeable
                              for this contract, with the evidence for it
```

## R5 — Thirteen Elements Present

A contract admitted for binding MUST carry all thirteen elements, each non-empty.

Invariant: element count is 13 and none is empty.

Falsifier: delete each element in turn; each deletion produces a typed refusal naming the missing element. The boundary is contract admission. A pass is invalid if two deletions produce the same undifferentiated refusal.

## R6 — Digest Is Recomputed

A stored contract digest MUST be admitted only after the checker compares it to a digest it recomputes from a canonical form of the contract.

Invariant: `stored_digest == recompute(contract)`.

Falsifier: change one contract value without changing the stored digest and observe admission. The boundary is contract admission. A pass is invalid if the checker only tested that a digest was present.

## R7 — Logical Operations Are Names Until Typed

Where a contract records operation fields by name only, a projection MUST NOT claim typed request or response fields.

Invariant: projected material asserts no field type the contract lacks.

Falsifier: inspect a projection from a names-only contract for any typed field claim. The boundary is the projection check. A pass is invalid if the inspected contract in fact carried types.

## R8 — Typing Gap Is Recorded

Where a contract records operation fields by name only, the typing gap MUST be recorded as unsupported.

Invariant: a names-only contract yields an unsupported marker for typed projection, never silence.

Falsifier: request a typed projection from a names-only contract and read the class. The boundary is the checker. A pass is invalid if the contract carried field types.

## R9 — Substitution Needs Joint Evidence

A substitution claim MUST be admitted only when both realizations carry passing evidence for the same contract version in the same profile context.

Invariant: claim implies two passing receipts with equal contract digest and equal profile.

Falsifier: present a claim with one passing and one failing or missing receipt, or with receipts from different profiles, and observe admission. The boundary is substitution admission. A pass is invalid if both receipts were passing.

# 7. Qualified Realization

## R10 — Realization Names Its Contract

A realization MUST state which contract and contract version it implements.

Invariant: `implements(R) = (contract id, version, digest)` is present.

Falsifier: omit the statement from a realization and observe qualification. The boundary is qualification. A pass is invalid if the realization carried a statement under another name.

## R11 — Implementation Statement Is Digest-Checked

Qualification MUST compare the contract digest stated by a realization with the digest of the contract it names.

Invariant: the stated digest equals the contract digest, else qualification refuses.

Falsifier: point a realization at a contract version whose digest differs and observe qualification. The boundary is qualification. A pass is invalid if the digest was never compared.

## R12 — Qualification Is Evidence, Not Authority

A realization with passing qualification MUST NOT be treated as holding any authority.

Invariant: no qualification record carries a consequence above the ceiling; qualification evidence bounds identity and behavior only.

Falsifier: attach a permission or grant to a qualification record and observe the authority gate. The boundary is the authority gate. A pass is invalid if the attached statement was never looked at.

## R13 — Qualification Standing Names Its Tuple

Qualification standing MUST name the exact artifact identity, contract version, profile, and court identity it was derived against.

Invariant: standing carries its derivation tuple.

Falsifier: read standing with one tuple member removed and observe the standing reader. The boundary is the standing reader. A pass is invalid if the removed member was never part of the derivation.

## R14 — Standing Is Unknown Outside Its Tuple

Qualification standing MUST be treated as unknown for any tuple other than the one it names.

Invariant: standing for a different tuple is UNKNOWN.

Falsifier: reuse standing derived for one artifact identity on a different identity and observe whether a consumer accepts it. The boundary is consumer admission. A pass is invalid if the two identities were equal.

# 8. Generated Projection

## R15 — Single Selection Input

Projection MUST be derived from exactly one Consumer Binding naming exactly one contract, one chosen realization, one profile, one artifact pin, and an authority ceiling.

Invariant: cardinality of each selection field is exactly one.

Falsifier: supply a binding with two candidate realizations and no selection, then one with zero profiles; each ends in refusal with zero material emitted. The boundary is binding admission. A pass is invalid if the refusal came from a syntax error unrelated to cardinality.

## R16 — Ambiguity Refuses

When a binding does not determine the projection uniquely, generation MUST end in a refusal.

Invariant: `ambiguous(binding) => refused`.

Falsifier: run generation on an ambiguous binding and read the outcome. The boundary is the generator. A pass is invalid if the binding was in fact unambiguous.

## R17 — No Handwritten Fallback

A hand-authored fallback MUST NOT be substituted for a projection that generation refused.

Invariant: a refused generation leaves no hand-authored substitute in the output location.

Falsifier: refuse a generation and list the output location. The boundary is the generator. A pass is invalid if the output location was never inspected, or held files from an earlier run.

## R18 — Projection Is Deterministic

Two generation runs with equal binding, equal generator identity, and equal realization-description content MUST yield byte-identical projections.

Invariant: `output = f(binding, generator identity, description content)`.

Falsifier: run twice and compare bytes; then perturb one input and observe the output change. The boundary is projection replay. A pass is invalid if the perturbation changed nothing, since then the comparison proved nothing.

## R19 — Generated Material Is Not Edited

Generated material MUST NOT be edited by hand.

Invariant: regeneration from current sources reproduces the committed material with zero difference.

Falsifier: hand-edit one generated file and regenerate; the difference is reported. The boundary is the drift check. A pass is invalid if regeneration was skipped.

## R20 — Defects Are Repaired At The Source

A defect in generated material MUST be repaired at the contract, binding, profile, or generator, and the material regenerated.

Invariant: every repair is a change to a source followed by regeneration.

Falsifier: repair a defect by editing generated output only and observe the drift check. The boundary is the drift check. A pass is invalid if the defect was repaired at a source as well.

## R21 — Residue Is Listed With A Reason

Any material that cannot be generated MUST be listed as handwritten residue with a reason.

Invariant: every non-generated file in the projection root appears in the residue list with a reason.

Falsifier: add an unlisted file to the projection root and observe the residue check. The boundary is the residue check. A pass is invalid if the check enumerated only generated files.

## R22 — Residue Carries An Unsupported Marker

Each entry of handwritten residue MUST carry a typed unsupported marker naming the missing generator capability.

Invariant: every residue entry has an unsupported marker.

Falsifier: list a residue entry without the marker and observe the residue check. The boundary is the residue check. A pass is invalid if the check read only the file names.

# 9. Admitted Runtime

## R23 — Pin Verified Before Use

A runtime MUST verify the realization artifact against its pin before first use.

Invariant: `digest(artifact) == pin.digest` and `length(artifact) == pin.length` precede use.

Falsifier: alter one byte of the artifact and start the runtime. The boundary is runtime start. A pass is invalid if the altered byte was in a region the loader never read and the digest was computed over a different region.

## R24 — Pin Mismatch Refuses Typed

A runtime MUST end in a typed digest-mismatch refusal on any pin mismatch.

Invariant: mismatch yields a code from the refusal vocabulary and no use.

Falsifier: present an artifact whose digest differs and read the outcome. The boundary is runtime start. A pass is invalid if the artifact matched the pin.

## R25 — Pin Mismatch Caches Nothing

A runtime MUST NOT retain any state derived from an artifact that failed its pin.

Invariant: after a mismatch the cache is empty.

Falsifier: start the runtime on a mismatching artifact and list the cache. The boundary is runtime start. A pass is invalid if the cache was empty before the start.

## R26 — Pin Is Identity, Not Authorization

A pin MUST be treated as identity only, so that matching a pin grants no consequence.

Invariant: pin match changes no authority value.

Falsifier: present a matching pin together with a request for a consequence above the ceiling and observe refusal. The boundary is the authority gate. A pass is invalid if the request was below the ceiling.

## R27 — Runtime Assumptions Are Compared

A runtime MUST compare the host assumptions of the chosen profile against the capabilities it actually offers.

Invariant: the comparison happens before use.

Falsifier: remove one assumed host capability and start the runtime. The boundary is runtime start. A pass is invalid if the removed capability was unused.

## R28 — Assumption Gap Is Unsupported

A runtime MUST refuse as unsupported on any gap between assumed and offered capabilities.

Invariant: unmet assumption yields an unsupported marker, never silent degradation.

Falsifier: create a gap and read the class. The boundary is runtime start. A pass is invalid if the gap was in a capability the profile never assumed.

# 10. Evidence and Standing

## R29 — Standing Is Computed At Read Time

Standing MUST be computed from receipts at read time.

Invariant: deleting all receipts for a subject removes its standing.

Falsifier: delete the receipts and read standing; a stored value would survive. The boundary is the standing reader. A pass is invalid if the receipts deleted were not the ones the reader consults.

## R30 — Standing Is Not Stored

Standing MUST NOT be held as a stored field of the subject it describes.

Invariant: no record of a subject carries a standing field.

Falsifier: scan every record type of the chain for a standing field. The boundary is the record schema. A pass is invalid if the scan skipped a record type.

## R31 — No Receipt, No Standing

A subject without at least one receipt MUST have standing UNKNOWN, never a positive value.

Invariant: `receipts(S) = {} => standing(S) = UNKNOWN`.

Falsifier: query a subject with no receipt. The boundary is the standing reader. A pass is invalid if the subject had a receipt under another name.

## R32 — Evidence Does Not Imply Authority

Evidence, standing, signature, and qualification MUST NOT imply or raise authority.

Invariant: authority is independent of every evidence value.

Falsifier: maximize every evidence value for a subject and read its authority; it remains NONE. The boundary is the authority gate. A pass is invalid if the gate read standing as an input.

## R33 — Positive Standing Needs An Observed Run

Positive standing MUST require an observed execution of the exact admitted subject, not source inspection or generation alone.

Invariant: generation without execution yields at most partial standing.

Falsifier: generate a projection, run nothing, and read standing. The boundary is the standing reader. A pass is invalid if an execution receipt existed.

# 11. Receipt and Replay

## R34 — Receipt Carries Five Fields

A projection receipt MUST carry identity, authority, consequence, replay, and standing information.

Invariant: all five fields present and non-empty.

Falsifier: inspect a receipt for each of the five fields. The boundary is receipt construction. A pass is invalid if a field was present only under another name.

## R35 — Incomplete Receipt Is Refused

Receipt admission MUST refuse a record missing any of the five fields, with a distinct typed reason per field.

Invariant: a record missing a field is not accepted as a receipt.

Falsifier: remove each field in turn and offer the record as a receipt; each removal refuses with a distinct typed reason. The boundary is receipt admission. A pass is invalid if the record was refused for parse failure.

## R36 — Receipt Replay Is Recomputable

A receipt MUST carry enough identities (binding digest, contract digest, generator identity, description-content digest, output digest) that a third party can recompute the output and compare.

Invariant: `recompute(receipt inputs) = receipt output digest`.

Falsifier: replay from the receipt in a clean location and compare the output digest. The boundary is replay. A pass is invalid if the replay reused cached output.

## R37 — Receipts Do Not Contain Their Own Subject Identity

Where a receipt describes a source revision, it MUST record that revision from outside the revision it names.

Invariant: no self-reference between a revision and its identity.

Falsifier: require the source revision identity inside the artifact and observe that the requirement cannot be satisfied. The boundary is receipt construction. A pass is invalid if the identity recorded was of a parent revision.

# 12. Typed Refusal

A refusal has a code, a class, and a broken term.

```text
classes:
  refused_identity     refused_structure     refused_authority
  refused_admission    blocked_resource      unsupported

codes (minimum set):
  AMBIGUOUS_REALIZATION        refused_structure   admission_vacuous
  PIN_MISSING                  refused_identity    R_missing_identity
  PIN_DIGEST_MALFORMED         refused_identity    R_missing_identity
  PIN_AMBIGUOUS                refused_identity    admission_vacuous
  PIN_REGISTRY_MISMATCH        refused_identity    mu_on_O
  CONTRACT_DIGEST_MISSING      refused_identity    R_missing_identity
  CONTRACT_DIGEST_MISMATCH     refused_identity    R_missing_identity
  REALIZATION_CONTRACT_MISMATCH refused_structure  mu_on_O
  CEILING_NOT_NONE             refused_authority   R_missing_authority
  AUTHORITY_GRANTED            refused_authority   R_missing_authority
  SHAPE_NONCONFORMANT          refused_structure   mu_on_O
  PROFILE_UNSUPPORTED          unsupported         mu_on_O
  PROJECTION_TYPE_UNSUPPORTED  unsupported         mu_on_O

standing string forms (colon form, derived, never stored):
  REFUSED:<CODE>       for every code whose class is a refused or blocked class
  UNSUPPORTED:<CODE>   for every code whose class is unsupported
```

## R38 — Refusals Are Typed And Total

Every rejection in the chain MUST return a code from the refusal vocabulary with its class and broken term.

Invariant: the rejection set is a subset of the vocabulary; an untyped failure is a defect of the checker.

Falsifier: inject one fault per code and collect the rejection; each carries its own code, class, and broken term. The boundary is the checker. A pass is invalid if two faults produced one code.

## R39 — Unsupported Is Marked

A capability the chain cannot express MUST be marked unsupported.

Invariant: an inexpressible request yields the unsupported class.

Falsifier: request an inexpressible projection and read the class. The boundary is the checker. A pass is invalid if the request was in fact expressible.

## R40 — Unsupported Is Not Refused

An unsupported marking MUST NOT be reported as refused or as passing.

Invariant: the unsupported class is disjoint from the refused classes.

Falsifier: read the transport form of an unsupported marking and of a refusal; the two differ in a top-level key and in exit status. The boundary is the checker. A pass is invalid if the two outcomes shared a key.

## R41 — Refusal Emits Nothing

A refusal at any generation step MUST leave zero projected files in the output location.

Invariant: `refused => emitted = 0`.

Falsifier: trigger each generation-time code and list the output location. The boundary is the generator. A pass is invalid if the location was pre-empty only because the run never started.

# 13. Authority Ceiling NONE

## R42 — Ceiling Is Present And NONE

The binding, the projection, and the receipt MUST each carry an authority ceiling whose value is exactly NONE.

Invariant: `ceiling = NONE` on all three records, cardinality exactly one.

Falsifier: read the ceiling of each record. The boundary is the authority gate. A pass is invalid if the gate also passes when it is deleted from the court set (vacuous gate).

## R43 — Wrong Ceiling Is Refused

A missing ceiling value or any value other than NONE MUST be refused as CEILING_NOT_NONE.

Invariant: every non-NONE or absent ceiling ends in that code.

Falsifier: set the ceiling to a nonzero level, then remove it, on each record; all six cases refuse. The boundary is the authority gate. A pass is invalid if the gate also passes when it is deleted from the court set (vacuous gate).

## R44 — Projected Material Cannot Escalate

Projected material MUST NOT emit any response carrying authority other than NONE.

Invariant: every response field for authority equals NONE.

Falsifier: drive the projected material through every operation of the contract and collect authority fields. The boundary is projected-material tests. A pass is invalid if an operation was skipped.

## R45 — Projected Material Claims No Standing

Projected material MUST NOT report positive standing on its own output.

Invariant: no response of projected material carries a standing value.

Falsifier: drive the projected material through every operation and collect standing fields. The boundary is projected-material tests. A pass is invalid if an operation was skipped.

## R46 — Courts Are Not Vacuous

Every gate in the chain MUST have a witness that passes it and a witness that fails it, so that removing the gate or mutating its subject flips the verdict of the pair.

Invariant: each gate is paired with a passing and a failing witness.

Falsifier: delete one gate at a time and rerun; the corresponding fail witness stops refusing. The boundary is the gate corpus. A pass is invalid if deleting the gate left every verdict unchanged for an unrelated reason.

# 14. Relationship To Other Documents (Non-Normative)

This document is the technology-independent layer. Reference realization profiles,
host assumptions, binary formats, build toolchains, and runtime-specific tests are
specified in the documentation of the pack that implements this chain. Nothing in
those profiles can add a requirement to this document; a profile that conflicts with
a requirement here is a defect of the profile.

RFC-GGEN-001 defines what a pack is and is the container in which an implementation
of this chain is shipped. RFC-GGEN-002 is reserved for the Qualification Court that
executes the falsifiers stated here.

# 15. Falsifier For This Document

If a normative section above names a technology, this document has failed its own R4. The
check is executable (it lives in the test suite of the pack that implements this chain) and
has three parts, each of which must hold.

Neutrality scan. A case-insensitive, whole-word scan of sections 5 through 13 for each name
in this enumerated list returns zero matches:

```text
rust, python, elixir, erlang, beam, node, javascript, typescript, java, go, wasm, wasi, wasmex, wit, tera, jinja, oxigraph, sparql, rdf, json, xml, yaml, toml, git, github, crates, hex, npm, oci, docker, ggen, cargo, mix, http, sha256, blake3
```

Whole-word means a maximal run of letters, digits and underscore bounded by anything else.
The names of the published vocabularies listed in section 5 (PROV-O, DCAT, SPDX, ODRL, SKOS,
SHACL, OWL-Time) and the word digest are not technologies and are exempt; the exempt names
and the forbidden list are disjoint. Protocol, format and hashing names are listed because
they would fix a realization choice.

Atomicity count. Over sections 5 through 13, for each requirement block (from its `## R`
heading to the next heading), the number of occurrences of the strong-obligation word (its
negation counting once) is exactly one, the number of lines beginning `Invariant:` is exactly
one, the number of lines beginning `Falsifier:` is exactly one, and no lowercase modal of
obligation, recommendation or permission (must, shall, should, may, required, recommended)
occurs. The requirement headings are numbered consecutively from R1 and their number is 46.

Defined terms. Each term of section 4 is defined there, and every normative use of gate,
court, witness, broken term, partial standing and positive standing in sections 5 through 13
is a use of the section 4 definition.
