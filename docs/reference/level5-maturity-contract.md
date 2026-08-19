# Reference: Level-5 maturity contract

Level 5 is a scoped standing claim over an exact admitted subject. It is not inferred from pack age, file count, README quality, or the existence of CI.

The marketplace uses a **5 × 7 maturity matrix**. Five levels describe progression on each of seven independent dimensions.

## The seven dimensions

| Dimension | Question |
|---|---|
| Semantic source | What source has authority to state the subsystem's meaning? |
| Admission | How are invalid observations/facts refused before manufacture? |
| Manufacture | How are consequences deterministically projected from admitted source? |
| Execution | What real boundary has been exercised against the exact subject? |
| Receipt/replay | Can the consequence be identity-bound, verified, and replayed? |
| Authority fence | Are SELECT, CONSTRUCT, and DO separated with zero ambient actuation authority? |
| Composition | Can the capability compose without duplicating semantic authority or hiding conflicts? |

## The five levels

| Level | Semantic source | Admission | Manufacture | Execution | Receipt/replay | Authority fence | Composition |
|---|---|---|---|---|---|---|---|
| L1 — specimen | prose/ad hoc | none | copied/manual | none | none | implicit | standalone |
| L2 — structured | identifiable source | structural/schema checks | templates/scripts | smoke/example | metadata | stated | manually reusable |
| L3 — admitted | RDF/canonical model | deterministic gates | ggen projection | bounded qualification | provenance | typed boundary | explicit dependencies |
| L4 — executable | source correspondence | fail-closed admission | fixed-point manufacture | real consumer/runtime | verified receipt/replay | SELECT/CONSTRUCT/DO explicit | dependency-closed |
| L5 — class-closed | authoritative class semantics | formal/complete admission for claimed domain | generic deterministic manufacture | exact-subject courts for claimed boundary | replay-equivalent receipt DAG | zero ambient DO; consequential actuation receipted | parameterized family/umbrella with conflict law |

A pack is not globally L5 merely because one dimension reaches L5. Claims must state the dimensions and boundary they close.

## Level-5 documentation closure

A Level-5 capability requires all four Diátaxis quadrants:

```text
Tutorial ∧ How-to ∧ Reference ∧ Explanation
```

The quadrants have different proof obligations:

- **Tutorial** — the documented learning path is executable against a real bounded subject and includes verification plus replay/receipt where applicable.
- **How-to** — the operational recipe names admitted inputs, expected consequence, authority ceiling, falsifiers, and rollback.
- **Reference** — exact ontology, configuration, commands, generated surfaces, gates/refusals, receipts, dependencies, compatibility, and maturity facts are specified without hand-maintained duplication of canonical data.
- **Explanation** — the rationale preserves the system's fences: Preserve → Fence → Calculus → Exclusions → Falsifiers → Extensions → Operationalization.

Documentation existence is insufficient. Level-5 documentation must correspond to the same source and execution semantics as the implementation.

## Generic mechanical infrastructure

`pack-maturity-pack` is reusable across consumers because it does not pretend to know their domain semantics. It supplies:

- deterministic regeneration / fixed-point convergence support;
- receipt verification support;
- generated Level-5 Tutorial, How-to, Reference, and Explanation surfaces;
- a generated structural court for the Level-5 documentation contract.

It currently makes honest generic claims about the mechanical promotion capabilities it can actually prove. A composing pack remains responsible for domain-specific authority, complete generation surface, positive and negative behavioral witnesses, domain verification, domain provenance, release semantics, and external/runtime courts.

## Typed documentation refusals

The Level-5 Diátaxis court uses the `L5-DOC-*` namespace. The intended refusal classes are:

- `L5-DOC-001` — a Diátaxis quadrant is missing;
- `L5-DOC-002` — reference has no semantic-authority statement;
- `L5-DOC-003` — tutorial lacks an executable path or verification boundary;
- `L5-DOC-004` — generated surfaces are undocumented;
- `L5-DOC-005` — admission gates/refusals are undocumented;
- `L5-DOC-006` — a consequential how-to lacks an authority ceiling;
- `L5-DOC-007` — replay/receipt obligations are absent where claimed;
- `L5-DOC-008` — documentation treats a projection/duplicate as canonical source;
- `L5-DOC-009` — composition/dependency semantics are undocumented;
- `L5-DOC-010` — explanation omits exclusions, falsifiers, or extension law.

A refusal blocks the documentation promotion claim; it does not imply that unrelated runtime behavior failed.

## Promotion equation

For a bounded subject `s`, a defensible Level-5 claim has the shape:

```text
O_s → admit → O*_s
O*_s → manufacture → A_s
A_s → execute/verify → E_s
E_s → receipt/replay → R_s
```

with documentation correspondence:

```text
D_s = Tutorial_s ∧ HowTo_s ∧ Reference_s ∧ Explanation_s
```

and standing:

```text
L5(s) only if the claimed seven-dimensional closure and D_s
are observed against the exact admitted subject and authority boundary.
```

`UNKNOWN` is not promoted to admitted. `UNSUPPORTED` is not equivalent to `REFUSED`. A checkpoint on one dimension is not a crown over the others.

## Required receipt fields for a Level-5 promotion

A promotion receipt should bind at least:

- repository and exact base/head SHA;
- admitted semantic source identity;
- pack/version/profile and dependencies;
- commands and exit statuses actually executed;
- generated-output status and fixed-point result;
- domain positive and negative witnesses;
- receipt/replay result;
- authority ceiling and any blocked/unsupported actuation boundary;
- Diátaxis correspondence result;
- falsifiers and rollback;
- scoped standing.

See [Standing](standing.md), [ggen qualification contract](ggen-qualification-contract.md), and [Why Level 5 requires Diátaxis](../explanation/level5-diataxis.md).
