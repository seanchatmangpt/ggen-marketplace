# SWE-Prometheus Governance Pack

Ontology-first source for repository-governance retrofit benchmarks based on
SWE-Prometheus (arXiv:2609.29465) and the stricter autofde-lab Verified
Governance Gain (VGG) court.

## What this pack owns

The pack owns **declarative contracts**, not execution:

```text
RetrofitCase
  ├─ exact repository + base commit + patch digest
  ├─ D1..D6 governance observations
  ├─ evidence receipts
  ├─ ProbeSpec[]
  ├─ VerifierSpec
  └─ MutationSpec[]
```

PROV-O, EARL, and Dublin Core are reused where their semantics fit. The `spg:`
terms cover only the failed edges: the six-dimension benchmark ontology,
fixed-base patch identity, paired score observations, gate-strength semantics,
ordered argv generation, and reversible mutation plans.

## Generated artifacts

Run a normal ggen pack sync against a consumer graph. The pack projects three
artifacts:

```text
generated/swe-prometheus-probe-manifest.json
generated/swe-prometheus-mutation-manifest.json
generated/swe-prometheus-case.json
```

Their target runtime schemas are:

```text
autofde-lab.swe-prometheus-probe-manifest/1
autofde-lab.swe-prometheus-mutation-manifest/1
autofde-lab.swe-prometheus-case/1
```

The first two describe execution. The third describes scored paired evidence.
They are projections; edit RDF and regenerate rather than modifying generated
JSON.

## Runtime round trip

With autofde-lab:

```text
RDF
  -> ggen sync
  -> probe manifest + mutation manifest
  -> exact git reconstruction
       base worktree
       treated worktree
       replay worktree
  -> raw probe receipts
  -> reversible mutation court
  -> semantic replay receipt
  -> pair_id
  -> scorecard(pair_id)
  -> VGG court
  -> OCEL 2.0 projection
  -> common-subject benchmark league
```

The scorecard is intentionally after reconstruction. Raw probe execution never
manufactures a 1..5 governance score.

## Gates

All gates are violation-row SELECT queries: zero rows means the graph passed that
guard; one or more rows is a refusal witness.

| Gate | Law |
|---|---|
| 010 | one exact repository/base/patch subject |
| 020 | exactly one observation for every D1..D6 dimension |
| 030 | `detected` requires a PASS mutation receipt and receipt id |
| 040 | PASS evidence requires paired scores in [1,5] |
| 050 | protocol enums are closed |
| 060 | clean/replay receipts are present, typed, and unique |
| 070 | scores are unique and absent when evidence is non-PASS |
| 080 | Probe/Verifier/Mutation plan identities are complete |
| 090 | mutation preimage/path/operator payload is reversible and bounded |
| 100 | argv/cwd/timeout remains inside the shell-free runtime boundary |

## Qualification

Run:

```bash
python3 qualification/verify.py
python3 qualification/receipt.py
```

The first is the semantic falsifier court. The second is only a content-addressed
source receipt.

The marketplace court is also registered in `gate-court.toml` so repository
automation can exercise the same runner.

## Execution boundary

A probe command is an **argv array**, not a shell string. CWDs and mutation paths
must remain relative to the reconstructed subject root. Timeouts are bounded to
the runtime's supported range. Mutation operators are closed to:

```text
replace_once
delete_once
append_text
write_text
```

Every mutation is guarded by the SHA-256 of the exact preimage file. If the
preimage moved, the runtime refuses rather than mutating an adjacent subject.

## Standing boundary

This pack can prove that a graph conforms to the source contract. It cannot prove
that:

- the target repository reconstructed successfully;
- a probe executed;
- a behavior gate detected a mutation;
- treated execution replayed;
- a score is correct;
- VGG is positive;
- a repository is production-ready.

Those require their respective runtime observations and courts.
