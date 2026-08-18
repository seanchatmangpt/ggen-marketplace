# soc2-readiness-pack

A SOC 2 readiness **binder**, not a single doc: 9 generated files under
`soc2/`, covering the full 28-criterion AICPA Trust Services taxonomy (all
5 categories, not just Security) and the full 10-phase engagement
lifecycle, combinatorially — every criterion and every phase gets a row
whether or not you've supplied evidence for it yet, so gaps are visible by
their presence in the table, not hidden by their absence from it.

**We cannot self-certify, but we can model the auditor's process and
results exactly.** This binder covers what a real SOC 2 Type II report's
Sections 3 and 4 would contain (system description; tests of controls and
results). Section 1 — the Independent Service Auditor's Report, the
auditor's actual professional opinion — is named, explained, and left
structurally blank everywhere it would otherwise appear.
`gates/010_no_compliance_verdict.rq` refuses any fact claiming compliance,
certification, attestation, or a rendered opinion, against every subject
type this binder uses (`prov:Entity`, `prov:Activity`, `org:Organization`,
`dcterms:Standard`) — verified against a real adversarial fact in a real
`ggen sync run`, not just written and trusted.

## The binder

| # | File | Consumer fact type |
|---|---|---|
| 00 | `00-README.md` | (computed index — no facts needed) |
| 01 | `01-SYSTEM-DESCRIPTION.md` | `org:Organization`, `prov:Entity` (`dcterms:type "SYSTEM-BOUNDARY"`) |
| 02 | `02-MANAGEMENT-ASSERTION.md` | `dcterms:Standard` |
| 03 | `03-CONTROL-MATRIX.md` | `prov:Entity` per criterion |
| 04 | `04-EVIDENCE-INVENTORY.md` | same `prov:Entity` facts as 03 |
| 05 | `05-AUDITOR-TEST-MATRIX.md` | `prov:Activity` per test, `prov:Activity` per phase |
| 06 | `06-ENGAGEMENT-TIMELINE.md` | `prov:Activity` (`skos:notation "PHASE-STATUS"`) |
| 07 | `07-EXCEPTION-LOG.md` | `prov:Entity` (`dcterms:type "EXCEPTION"`) |
| 08 | `08-SUBSERVICE-ORGANIZATIONS.md` | `org:Organization` (`dcterms:type "SUBSERVICE-ORG"`) |

## Full triple-shape reference

### Control status (drives 03, 04)

```turtle
[] a prov:Entity ;
    rdfs:label "Namespace-scoped RBAC for tenant provisioning" ;
    dcterms:subject "CC6" ;
    dcterms:type "TESTED" ;
    dcterms:contributor "platform-team" ;
    dcterms:source "platform-console/k8s/rbac.yaml" ;
    dcterms:description "ClusterRole grants get+create on namespaces only." .
```

`dcterms:subject` must be a real criterion notation: `CC1`..`CC8`,
`CC9-1`, `CC9-2`, `A1-1`..`A1-3`, `C1-1`, `C1-2`, `PI1-1`..`PI1-5`,
`P1`..`P8`. `dcterms:type` must be an `IMPL-STATUS` notation:
`NOT-STARTED`, `PLANNED`, `IN-PROGRESS`, `IMPLEMENTED`, `TESTED`,
`EXCEPTION`, `NOT-APPLICABLE`.

### Control test rehearsal (drives 05)

```turtle
[] a prov:Activity ;
    rdfs:label "Verify tenant namespace isolation" ;
    dcterms:subject "CC6" ;
    dcterms:description "Attempt cross-tenant namespace access; confirm RBAC denies it." ;
    skos:note "PASS -- 403 on cross-namespace GET" .
```

### Engagement phase status (drives 05, 06)

```turtle
[] a prov:Activity ;
    dcterms:subject "AUDIT-OE-TESTING" ;
    skos:notation "PHASE-STATUS" ;
    skos:prefLabel "in progress" ;
    prov:startedAtTime "2026-08-01"^^xsd:date ;
    dcterms:description "Operating-effectiveness testing underway for CC6, CC7." .
```

Phase notations: `AUDIT-SCOPING`, `AUDIT-READINESS`,
`AUDIT-CONTROL-DESIGN-DOC`, `AUDIT-DESIGN-EVAL`, `AUDIT-COLLECTION-INIT`,
`AUDIT-OE-TESTING`, `AUDIT-EXCEPTION-ID`, `AUDIT-REMEDIATION`,
`AUDIT-BUNDLE-ASSEMBLY`, `AUDIT-REPORT-HANDOFF`.

### Exception (drives 07)

```turtle
[] a prov:Entity ;
    rdfs:label "MFA not enforced for one break-glass admin account" ;
    dcterms:subject "CC6" ;
    dcterms:type "EXCEPTION" ;
    dcterms:relation "MEDIUM" ;
    dcterms:description "Break-glass account bypasses SSO/MFA by design." ;
    dcterms:isReplacedBy "Add hardware-key MFA gate to break-glass path" ;
    dcterms:hasVersion "in progress" .
```

`dcterms:relation` must be a `RISK-LEVELS` notation: `LOW`, `MEDIUM`,
`HIGH`, `CRITICAL`.

### System boundary / organization (drives 01)

```turtle
[] a org:Organization ;
    rdfs:label "Acme Platform, Inc." ;
    dcterms:description "SaaS platform providing tenant-isolated data pipelines." .

[] a prov:Entity ;
    rdfs:label "Production Kubernetes cluster (us-west-2)" ;
    dcterms:type "SYSTEM-BOUNDARY" ;
    dcterms:description "In scope: all workloads under namespace prefix tenant-*." .
```

### Management assertion draft (drives 02)

```turtle
[] a dcterms:Standard ;
    rdfs:label "Management asserts that the controls described in System Description (01) were suitably designed and, where TESTED in the Control Matrix (03), operated effectively." ;
    dcterms:creator "Jane Doe, VP Engineering" ;
    dcterms:date "2026-08-18"^^xsd:date .
```

### Subservice organization (drives 08)

```turtle
[] a org:Organization ;
    rdfs:label "AWS (us-west-2)" ;
    dcterms:type "SUBSERVICE-ORG" ;
    dcterms:coverage "Physical security, hypervisor isolation, network infrastructure" ;
    dcterms:accessRights "carve-out" ;
    dcterms:requires "Customer must enable and monitor CloudTrail." .
```

## Compose it

```toml
[packs]
"soc2-readiness-pack" = { path = "/Users/sac/ggen-marketplace/packs/soc2-readiness-pack" }
```

`ggen sync run` regenerates all 9 files under `soc2/` from whatever facts
your own ontology currently asserts. Criteria and phases with no fact
still render — as `NOT STARTED`, not as a missing row.
