# NIST Zero-Trust Agentic Data Pack

Semantic crosswalk for applying NIST zero-trust source law to agentic data-engineering and OLAP workflows.

## Source boundary

This pack keeps two provenance classes separate:

- **NIST-derived**: resource-centric protection, explicit authentication/authorization, policy decision/enforcement, and service/workload identity. Source anchors are NIST SP 800-207 and SP 800-207A. OSCAL and SP 800-53 Rev. 5 are referenced as machine-readable/control-catalog integration surfaces.
- **Paper-derived extensions**: evidence-gated graph progression, bounded recovery, trusted-delivery evidence, evidence-gated production promotion, same-snapshot exact result equivalence, and independent terminal verification. Source: arXiv:2609.29668v1.

The paper is not treated as NIST authority, and the pack does not restate paper extensions as NIST requirements.

## Reuse boundary

This pack is semantic and deliberately does not duplicate execution machinery:

- `governed-runtime-adapter-pack` owns runtime identity, budgets, execution modes, authority fencing, and receipts.
- `supply-chain-evidence-pack` owns executable supply-chain evidence courts.
- `receipt-provenance-unification-pack` owns unified receipt/provenance validation.

Consumers bind those existing packs to this vocabulary rather than creating a second implementation.

## Admission gates

The pack refuses facts that claim:

1. verified completion without independently verified repository, deployment, runtime, and policy evidence;
2. a recovery loop without explicit attempt, time, token, tool-call, cost, privilege, and blast-radius bounds;
3. consequential execution without subject/resource/action/context policy decision and a policy-enforcement point;
4. production promotion without immutable-source, independent validation, approval binding, and least-privilege writer evidence;
5. a verified analytical answer without same-snapshot execution, exact result equivalence, grounding, and independent verification;
6. a trusted build without immutable source revision, independent rebuild, SBOM, provenance, security validation, and IaC validation evidence;
7. paper-derived control patterns whose provenance boundary has been erased.

Gate result rows are refusals; an empty result set is admission at that gate only. It does not establish deployment, production, or external standing.

## Sources

- NIST SP 800-207 — Zero Trust Architecture
- NIST SP 800-207A — Zero Trust Architecture Model for cloud-native/multi-cloud access control
- NIST SP 800-53 Rev. 5 — Security and Privacy Controls
- NIST SP 800-218 — Secure Software Development Framework
- NIST OSCAL — machine-readable security-control representation
- arXiv:2609.29668v1 — Graph, Loop, and Harness Engineering for Zero-Trust Agentic Data Engineering and Analytical Processing
