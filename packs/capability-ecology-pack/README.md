# capability-ecology-pack

Qualified capability contracts for the runtime families a capability-resolution
engine (consumer: ash_pplan v26.9.30) resolves against. **One pack, one version,
one admission unit, ten family modules** — consolidated (2026-10-01) from the
v26.9.30 wave's ten per-family packs, which were a lane-partition artifact of the
10-agent fan-out, not a durable topology. The consolidation applies the drift law
("N implementations of one calculus → O(N²) drift; converge on one kernel with N
bindings"): `qce:` (packs/qualified-capability-ecology-pack) remains the pure
lifecycle kernel; this pack is the single N-family binding.

## Layout

| path | content |
|---|---|
| `ontology/<family>.ttl` | one module per family, disjoint namespaces (`fscap:` … `ecap:`), verbatim from the qualified wave packs |
| `gates/<famprefix>_<stem>.rq` | 59 violation-row SELECTs (family-prefixed exact stems) |
| `witnesses/{pass,fail}/<gate-stem>.ttl` | exact-stem witnesses — pass must be silent, fail must fire |
| `qualification/fixtures/` | per-family positive + negative fixtures (court data; prefix-named) |
| `qualification/verify.py` | the ONE uniform court (exact-stem, exit 0 = ADMITTED) |
| `families/<family>.md` | each wave pack's README, preserved verbatim as family notes |

## Families

filesystem `fscap:` · network `ncap:` · process `pcap:` · scheduling `scap:` ·
event-state `escap:` · observation `ocap:` · durability `dcap:` · a2a `aacap:` ·
authority `authcap:` · evidence `ecap:` — pinned capability IDs, failed edges,
realization provider metadata and per-family gate rationale live in
`families/<family>.md`; the cross-family pins live in
`docs/jira/v26.9.30/RESOLUTIONS.md`.

## Consumer join doctrine

Capabilities are referenced by pinned dotted-ID literals (`File.Write`,
`A2A.Invoke`, …) carried as `rdfs:label` + `dcterms:identifier`. The join happens
in the consumer resolver, never as a cross-pack import.

## Invariants (encoded as gates)

Capability ≠ Implementation · Plan ≠ Execution · Policy ≠ Authority ·
ProviderAvailable ≠ Authorized · Projection ≠ Source · Generated ≠ Admitted ·
COMPENSATABLE ≠ REVERSIBLE.

## Evidence boundary

Marketplace admission + real-ggen qualification + the exact-stem witness court
only. No execution authority; BRCE remains the sole actuation boundary.

## Supersession

Replaces `filesystem-`, `network-`, `process-`, `scheduling-`, `event-state-`,
`observation-`, `durability-`, `a2a-`, `authority-`, `evidence-capability-pack`
(v0.1.0 each; a2a 26.9.0) — content moved byte-equivalent modulo prefix renames;
per-pack verify.py variants replaced by the single uniform court.
