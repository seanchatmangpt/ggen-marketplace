# Reference: semantic Diátaxis contract

Namespace `https://ggen.dev/ontology/sa2a-semantic-diataxis#` (`sd:`).

| Field | Rule |
|---|---|
| `sd:quadrant` | single-valued: `tutorial`, `how-to`, `reference`, `explanation` |
| `sd:outputId` | unique across documents |
| `sd:subjectRevision` | `^[0-9a-f]{40}$` |
| `sd:authority` | `NONE` |
| `sd:standing` | `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE` (needs `sd:evidence`), `BLOCKED`, `BUILD_BROKEN`, `UNSUPPORTED`, `REFUSED:*` |
| `sd:linkType` | `requires`, `explains`, `procedureFor`, `specifiedBy` |
| contract | `semanticEquivalence` = `UNCLAIMED`; consequence `EVIDENCE_ONLY` |

Gates `010`–`090` in `packs/sa2a-semantic-diataxis-pack/gates/` return one row per violation. Unknown `sd:extension` semantics may only be `UNSUPPORTED`.
