# autofde-k8s-fault-taxonomy-pack

Packages the real AutoFDE Kubernetes fault-taxonomy vocabulary — a four-axis SKOS
enumeration (`afl:Component` x `afl:FailureMode` x `afl:AppTopology` x `afl:Severity`)
covering standard, publicly-documented K8s troubleshooting terms such as
`afl:Pod`/`afl:CrashLoopBackOff` and `afl:RBAC`/`afl:Forbidden` — as an admission gate
for a customer's own fault catalog.

## What this pack admits

A customer fault catalog is modeled as `afl:FaultCatalogEntry` individuals, each
carrying:

- `afl:catalogComponentRef` — must point at a real `afl:Component` individual in
  `afl:ComponentScheme`.
- `afl:catalogFailureModeRef` — must point at a real `afl:FailureMode` individual in
  `afl:FailureModeScheme`.

`qualification/consumer.ttl` is a real fixture of four valid entries built from the
enumerated ontology terms.

## What this pack refuses

`gates/010_known_fault_codes.rq` refuses any `afl:FaultCatalogEntry` whose
`afl:catalogComponentRef` or `afl:catalogFailureModeRef` does not resolve to a real,
enumerated `afl:Component`/`afl:FailureMode` individual — i.e. it refuses unknown or
misspelled fault codes before they reach downstream generation.

## What this pack does NOT do

This is a taxonomy admission gate only. No live cluster access, no incident
detection, no monitoring integration, and no claim of matching CKA/CKAD
certification curriculum text is included or implied. `ontology.ttl` is copied
verbatim from `ontologies/autofde/k8s-fault-taxonomy.ttl` with one addition
appended: the `afl:FaultCatalogEntry` class and its two object properties.
