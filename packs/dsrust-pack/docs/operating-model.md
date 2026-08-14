# DsRust Enterprise Operating Model

## RACI

| Activity | Marketplace | DsRust source owner | Enterprise architecture | Consumer engineering | Security/SRE |
|---|---|---|---|---|---|
| Define semantic projection | **A/R** | C | C | C | I |
| Export/API compatibility | C | **A/R** | I | C | I |
| Source repin decision | R | C | **A** | C | I |
| Deterministic generation qualification | **A/R** | I | I | I | I |
| Rust compile/test qualification | I | C | I | **A/R** | C |
| Provider/tool authorization | I | I | C | R | **A** |
| Data classification/residency | I | I | C | R | **A** |
| Runtime SLO/DR | I | I | C | R | **A** |
| Production promotion | I | I | **A** | R | C |
| Rollback | I | I | C | **R** | **A** |

## Change classes

- **patch** — documentation, non-semantic gate diagnostics, or generated text changes with no admitted
  API/ontology contract change.
- **minor** — additive admitted vocabulary/templates/enterprise controls compatible with existing consumers.
- **major** — breaking ontology, generated Rust interface, or authority-boundary change.
- **source-repin** — any change to the admitted DsRust repository commit or crate version. Treat as an
  architecture review event even when pack semver impact would otherwise be minor.

## Release evidence bundle

A release candidate should retain:

1. marketplace base and exact candidate SHA;
2. pack version and archive SHA-256;
3. exact DsRust repository commit and crate version;
4. coverage ledger result;
5. gate/refusal results;
6. real-ggen deterministic replay receipt;
7. generated consequence SHA-256;
8. consumer compiler/test/security evidence before runtime promotion;
9. enterprise asset/release identity;
10. rollback pin.

## Incident / rollback posture

The pack itself has no live service to fail over. Incidents caused by generated code are handled by
the consuming application's runbook. The marketplace response is to freeze promotion, preserve the
failing ontology/source/receipt tuple, reproduce the generation deterministically, and either repair
the projection or roll the consumer back to the previous admitted tuple.

## Architecture review triggers

Re-enter architecture review when any of these changes:

- DsRust source commit or crate version;
- admitted module/optimizer set;
- generated public Rust construction surface;
- tool/reward/metric authority boundary;
- provider/model configuration semantics;
- enterprise binding contract;
- direct-actuation policy;
- deterministic replay behavior.
