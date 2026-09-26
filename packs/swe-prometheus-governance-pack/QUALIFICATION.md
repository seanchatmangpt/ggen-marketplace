# Qualification — swe-prometheus-governance-pack v0.2.0

## Subject

v0.2 is authored from `ggen-marketplace@ba3641dee8ea95828a3aaa4358bac8b4a091136f`.

The pack projects the SWE-Prometheus paired-governance evidence model into the
runtime schemas consumed by autofde-lab's VGG, paired-probe, mutation, and exact
git-reconstruction courts.

## Court topology

`gate-court.toml` registers the canonical marketplace semantic witness:

```text
ontology.ttl
  + pos_clean.ttl
  + each negative fixture
  + gates/*.rq
      |
      v
qualification/verify.py
```

The positive graph must return zero rows from every gate. Each negative fixture
pins an exact target row count for the gate family it exists to falsify; other
guards may also fire because failure surfaces intentionally overlap.

| fixture | target gate | expected target rows |
|---|---|---:|
| `neg_all.ttl` | 010 exact identity | 2 |
| `neg_all.ttl` | 020 dimension universe | 6 |
| `neg_all.ttl` | 030 detected mutation receipt | 1 |
| `neg_all.ttl` | 040 paired score shape | 3 |
| `neg_enums.ttl` | 050 closed enums | 9 |
| `neg_receipts.ttl` | 060 receipt binding | 6 |
| `neg_scores.ttl` | 070 score cardinality | 6 |
| `neg_plans.ttl` | 080 executable plan shape | 13 |
| `neg_mutation_payload.ttl` | 090 mutation payload | 7 |
| `neg_command_boundary.ttl` | 100 command boundary | 6 |

The original v0.1 rdflib court observed `0/0/0/0` on the clean fixture and
`2/6/1/3` on the original negative fixture for gates 010–040. Those observations
remain historical evidence for that exact source version; they are not silently
promoted to the v0.2 head.

## Positive execution-plan witness

`pos_clean.ttl` now contains:

- exact repository/base/patch identity;
- six governance dimension observations;
- PASS mutation/clean/replay receipt resources;
- one governance ProbeSpec;
- one behavior ProbeSpec;
- one VerifierSpec;
- one exact-preimage replace-once MutationSpec.

That prevents the v0.2 plan gates from passing vacuously.

## Generated runtime contracts

A conforming consumer graph manufactures:

- `generated/swe-prometheus-probe-manifest.json`
  → `autofde-lab.swe-prometheus-probe-manifest/1`
- `generated/swe-prometheus-mutation-manifest.json`
  → `autofde-lab.swe-prometheus-mutation-manifest/1`
- `generated/swe-prometheus-case.json`
  → `autofde-lab.swe-prometheus-case/1`

The first two are pre-execution plans. The case document is a downstream scored
artifact and does not itself prove probe execution, reconstruction, mutation
detection, replay, or production standing.

## Content-addressed source receipt

`qualification/receipt.py` hashes the pack metadata, ontology, court config,
all gates, templates, and fixtures and emits:

```text
ggen.swe-prometheus-governance-qualification/1
```

The receipt identifies source bytes only. It is not a semantic-court PASS.

## Evidence ceiling

Current-chat local execution cannot reach GitHub from the container, so no local
claim is made for dual-engine marketplace execution or real ggen sync at this
v0.2 head. Exact-head repository workflows are the next independent verifier
source after the PR opens. CI remains verifier evidence and never implies deployed
production standing.

## Authority boundary

The pack does not:

- run repository commands;
- clone or mutate target repositories;
- apply mutation operators;
- assign 1..5 governance scores;
- compute NGI/VGG;
- admit ALIVE;
- grant DO authority.

Those remain external runtime courts. RDF is the source contract; generated JSON
is projection; execution receipts are observations; VGG admission is a separate
court.
