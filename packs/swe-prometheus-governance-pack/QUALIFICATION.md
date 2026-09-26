# Qualification — swe-prometheus-governance-pack

## Subject

Pack authored against `ggen-marketplace@d9dcc9e52b65361f2b6e8131b9ee993c315dd017`.

The pack encodes the paired evidence interface from SWE-Prometheus
(arXiv:2609.29465) and projects a one-case graph into the executable
`autofde-lab.swe-prometheus-case/1` input consumed by the VGG court.

## Local falsifier court

A local rdflib court parsed `ontology.ttl`, joined each qualification fixture,
and executed all four violation-row gates.

| fixture | 010 identity | 020 dimensions | 030 mutation gate | 040 scores |
|---|---:|---:|---:|---:|
| `pos_clean.ttl` | 0 | 0 | 0 | 0 |
| `neg_all.ttl` | 2 | 6 | 1 | 3 |

The negative rows are not generic syntax failures:

- 010: duplicate `baseCommit` + missing `patchDigest`;
- 020: duplicate D1 + missing D2..D6;
- 030: `gateStrength="detected"` without mutation receipt;
- 040: out-of-range base score, missing treated score, invalid evidence status.

This is **VERIFIER_ALIVE for the local rdflib court**, not a claim that every
marketplace engine or ggen binary executed here.

## Evidence ceiling

Dual-engine marketplace admission (locked SPARQL + Oxigraph) and real `ggen
sync` are **UNSUPPORTED in the current execution environment** and are not
silently promoted to PASS. The PR's repository CI may add independent evidence,
but CI is not production standing.

## Authority boundary

The pack provides vocabulary, structural gates, fixtures, and a deterministic
projection template. It does not:

- execute install/test/quality/security probes;
- compute NGI;
- decide `ALIVE` or `PARTIAL_ALIVE`;
- mutate the target repository;
- manufacture authority from an intent hook.

Those remain external: paired probes produce evidence; autofde-lab recomputes
NGI and applies the evidence ceiling.
