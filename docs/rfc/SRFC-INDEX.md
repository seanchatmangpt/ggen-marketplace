# SRFC Index

Semantic RFC series: technology-independent specifications. Numbers are reserved here
so that no two documents share one (a sibling series has duplicate numbers).

| Number | Title | Version | Status |
|---|---|---|---|
| SRFC-001 | Capability Contract and Qualified Realization | v26.9.30 | Proposed Standard (46 atomic requirements, R1-R46) |
| SRFC-002 | (reserved) | — | Reserved |
| SRFC-003 | (reserved) | — | Reserved |

Related and not part of this series: RFC-GGEN-001 (pack core), RFC-GGEN-002 (reserved,
Qualification Court).

## Rules

- A number is never reused or reassigned.
- Normative sections name no language, runtime, template engine, graph store, or
  binary format. Such material lives in pack documentation as non-normative profiles.
  The check is executable: SRFC-001 section 15, run by
  `tests/test_qri_consumer_binding_pack.py` (`test_srfc_*`).
- Normative alignment sources are published standards only (PROV-O, DCAT, SPDX, ODRL, SKOS,
  SHACL, OWL-Time); every new term is aligned to one or carries a stated delta justification.

## See Also

- [SRFC-001](SRFC-001-capability-contract-qualified-realization-v26.9.30.md)
- [RFC-GGEN-001](RFC-GGEN-001-semantic-pack-core.md)
