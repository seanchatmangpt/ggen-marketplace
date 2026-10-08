# v26.9.21 Acceptance Courts — WD Semantic Failure Analysis

All statuses below are **PLANNED** until the named commands or equivalent repository-native courts are observed against exact heads.

## Gate 0 — Marketplace baseline

Required before attributing any later failure to this milestone:

```bash
python3.11 scripts/marketplace.py validate
python3.11 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3.11 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3.11 scripts/marketplace.py fingerprint
python3.11 -m pytest tests/ scripts/
```

Acceptance:
- marketplace remains valid;
- catalog projection is deterministic;
- corpus fingerprint is emitted;
- repository tests pass.

## Gate 1 — Prior-art composition before invention

For each proposed WD capability, evidence must record one of:

- `REUSE`
- `COMPOSE`
- `EXTEND`
- `INVENT`

A new pack is refused if an existing marketplace pack covers the same semantics and the equivalence boundary has not been falsified.

Required reuse:
- canonical active platform packs;
- `shacl-projection-pack`;
- `shacl-to-pydantic-pack`;
- `process-intelligence-pack`;
- `protocol-integration-pack`;
- `evidence-standing-pack`;
- `decision-optionality-pack`;
- `planning-policy-pack`;
- `experience-projection-pack`;
- `receipt-provenance-unification-pack`;
- `semantic-gate-witness-court-pack`.

## Gate 2 — Canonical semantic source

The WD domain graph must be sovereign; generated Python/JavaScript/OpenAPI files must be projections.

Required assertions:
- no generated artifact is also a canonical semantic source;
- every projection records lineage to the source graph/shape;
- generated outputs are not hand-edited as independent schemas.

## Gate 3 — SHACL → Python / web contract parity

One admitted SHACL shape must drive:

1. Pydantic models;
2. FastAPI request/response contracts;
3. Zod runtime schemas;
4. JSDoc typedefs for the Next.js JavaScript consumer.

Falsifier:
- any independently hand-maintained field set diverges from the canonical shape.

## Gate 4 — OCEL 2.0 HDD world

The first synthetic world must include multiple object types and events that relate to more than one object.

Minimum object types:
- Drive
- FailureCase
- Lot
- Component
- Supplier
- BOMRevision
- FirmwareRevision
- ProductionLine
- TestStation
- TestRun
- Rework
- EvidenceArtifact
- FailureMode
- DiagnosticAction
- Disposition

Acceptance:
- write/read round trip preserves exact object/event identities;
- provenance survives projection;
- process analysis consumes the reconstructed log rather than a hand-authored parallel fixture.

## Gate 5 — Known / partial / unknown court

Required fixtures:

1. **Known A** — admits the correct known failure.
2. **Known B with misleading similarity** — similarity points toward A; applicability/falsifiers select B.
3. **Incomplete evidence** — returns `PARTIAL_ALIVE`, never `KNOWN`.
4. **Novel X** — refuses every admitted known mode and returns `UNKNOWN`.
5. **Tampered evidence** — digest/identity mismatch is refused.
6. **Self-certification** — TPOT, planner, SA2A producer, or UI cannot promote its own candidate to standing.

Primary falsifier:

```text
Novel X → confidently KNOWN
```

If observed, the case-study architecture fails its central safety/trust requirement.

## Gate 6 — Planner and model authority ceiling

Invariant:

```text
TPOT result ≠ diagnosis
POWL plan ≠ execution
AutoFDE selection ≠ DO
SA2A result ≠ admission
Jira/Next.js status ≠ standing
```

Any candidate surface asserting ambient consequential authority must fail closed.

## Gate 7 — Receipts and independent verification

A verified disposition must bind:

- exact subject identity;
- exact evidence identities/digests;
- producer/model/planner identity where applicable;
- selected diagnostic action;
- authority context;
- observed consequence;
- independent verifier identity;
- final standing.

NoReceipt ⇒ NoStanding.

## Gate 8 — Replay / MachineExperience

Episode N:

```text
UNKNOWN
→ investigation
→ verified disposition
→ receipt
→ MachineExperience
```

Episode N+1, for an equivalent subject:

```text
admitted prior experience
→ applicability/falsifier check
→ KNOWN
→ deterministic/reduced-reasoning replay
```

Acceptance is not merely model retraining. The repeated case must require less exploratory intelligence.

## Gate 9 — API and UI projection

The browser may request commands and render evidence, but it must not implement semantic standing rules.

Required boundary:

```text
Next.js → FastAPI → application service → sJira admission
```

No React/Next.js component may contain a rule equivalent to:

```text
confidence > threshold ⇒ KNOWN
```

## Gate 10 — SA2A projection

The Python SA2A adapter must reuse `protocol-integration-pack` capability semantics rather than minting a second capability definition.

Every consequential capability must default to requiring authority.

Phase one remains candidate/evidence exchange only; production DO is outside the evidence ceiling.

## Gate 11 — End-to-end demonstration

One command in the downstream consumer should eventually execute the four-case synthetic court and emit an evidence bundle containing:

- OCEL subject/event identities;
- PM4Py/POWL analysis identity;
- TPOT candidate identity;
- AutoFDE selection identity;
- sJira WorkOrder identity;
- verification result;
- receipt/replay identity;
- final scoped standing.

Until this command has executed successfully against an exact head, end-to-end standing remains `UNKNOWN` or `PARTIAL_ALIVE`.
