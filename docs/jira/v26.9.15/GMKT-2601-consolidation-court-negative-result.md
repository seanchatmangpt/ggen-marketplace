# GMKT-2601: Consolidation refusal + headless-Service extension — recorded, no action

- **Status**: Closed (no action)
- **Severity**: Info
- **Found by**: 14-hour cross-repo code review, window 2026-09-14 9:40 PM → 2026-09-15 11:40 AM PDT (inspection, not execution)

## Evidence

**Consolidation court.** Apparently shared ontology semantics were contaminated first by generic RDF/RDFS/OWL/XSD vocabulary and then by the marketplace's own `ggen-create` scaffolding. After removing both false signals:

- **0 ADMITTED**
- **6 PARTIAL**
- **3 REFUTED**

instead of manufacturing an unjustified common kernel. The court also found there is currently no exercised cross-pack ontology-import primitive; the existing composition mechanism is whole-pack dependency.

**Kubernetes.** The later change adds optional `k8s:serviceClusterIP` and conditionally renders `spec.clusterIP`, enabling the `"None"` headless-Service case required for Kubernetes-DNS Erlang clustering. Existing graphs leave it unbound, preserving previous generated Services.

## Impact

The failed equivalence proof correctly preserves the separate topology (the Chesterton/DfCM outcome — refusing false consolidation is a result, not a failure). No new blocker found. Standing: PARTIAL_ALIVE by its own evidence.

## Fix

None required. The absent cross-pack ontology-import primitive is a recorded capability fact to remember when a cross-pack fact is next needed — not a defect to fix preemptively.
