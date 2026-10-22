# RECEIPT — industry-pharma-21cfr pillar-gate extension (IND-3)

Date: 2026-10-22
Subject: /Users/sac/ggen-marketplace/packs/industry-pharma-21cfr/ @ working tree
(main, uncommitted per dispatch; sibling in-flight lane on
packs/industry-semantic-cad-bim untouched, disclosed: its gate/witness mismatch
currently trips scripts/check_gate_witness_courts.py repo-wide — pre-existing,
not session-introduced)

Standing: ALIVE (all commands below executed on this subject, outputs quoted)

## What landed

- `ontology.ttl`: pillar vocabulary — P1 `IsolatedStorageScope` /
  `hasJournalScope` / `journalPath`; P2 `attestationFingerprint`; P3
  `QualityAnnotation` / `aiDerived` / `proposesMutationOf` / `adjudicatedBy` /
  `JudgeActivity` / `verdict`; P5 `MerkleSeal` / `hasMerkleSeal` / `sealedRoot`
  / `receiptDigest` / `completionStatus`; compliant individuals extended
  (esig-001 attested, batch-101 scoped + completed + sealed; judge-001/annot-001
  proposer-judge chain; journal-scope-001; merkle-seal-001).
- Four new gates, witnessed pass AND fail, exactly-one-law:
  - `gates/050_journal_scope_missing.rq` (P1 per-batch journal path law)
  - `gates/060_esig_attestation_missing.rq` (P2 SKR measurement fingerprint)
  - `gates/070_ai_annotation_unadjudicated.rq` (P3 proposer-judge)
  - `gates/080_merkle_seal_missing.rq` (P5 sealed root + 320-byte receipt digest)
- Existing witnesses (010/020 pass+fail) made pillar-complete so every fail
  witness flips exactly one law.
- `qualification/verify.py`: exactly-one-law court (fail witness flips its own
  gate, zero rows on all others; pass witness zero rows on all 8).
- `runners/semantic_runner.py` (new): dflss-exemplar runner contract
  (`--gate/--witness/--expectation`, exit 0/2/3, REFUSED_* vocabulary); wired
  into `gate-court.toml`:
  `runner = "python3 runners/semantic_runner.py --gate {gate} --witness {witness} --expectation {expectation}"`.
  Documented divergence from dflss exemplar: no SHACL leg (pack carries no
  ontology/shapes.ttl; pass contract is zero gate rows, pack graph cleanliness
  proven separately by verify.py).
- Consumer: `/Users/sac/ggen/examples/industry/pharma-21cfr/pack-vocabulary.ttl`
  refreshed to the extended pack pin; `PILLARS.md` pillar-to-gate mapping added.

## Verification receipts (real output)

```
$ python3 qualification/verify.py
... 8 gates x (ontology + pass + fail) legs ...
PASS court 080_merkle_seal_missing: fail witness flips ONLY its gate (1 row(s))
OK: 8 gates, 16 witness legs, zero-rows/flips-as-contracted, exactly-one-law enforced
$ echo $?
0
```

```
$ for g in gates/*.rq; do for pol in pass fail; do
    python3 runners/semantic_runner.py --gate "$g" \
      --witness "witnesses/$pol/$(basename "${g%.rq}").ttl" \
      --expectation "$pol"; done; done
16/16 legs rc=0 (observed:"pass" rows:0 x8; observed:"fail" rows:1 x7, rows:3 x020)
```

Non-vacuity probes (a court that cannot refuse is the failure):

```
$ python3 runners/semantic_runner.py --gate gates/050_journal_scope_missing.rq \
    --witness witnesses/fail/050_journal_scope_missing.ttl --expectation pass
{"refusal": "REFUSED_GATE_ROWS_ON_PASS", ...}   rc=2
$ ... --gate gates/050_journal_scope_missing.rq --witness witnesses/fail/030_capa_missing.ttl --expectation fail
{"refusal": "REFUSED_EXPECTED_GATE_DID_NOT_FIRE", ...}  rc=2
$ ... --gate gates/050.rq --witness witnesses/pass/050_journal_scope_missing.ttl --expectation pass
{"refusal": "REFUSED_STRUCTURAL", "error": "gate not found: gates/050.rq"}  rc=3
```

```
$ cd /Users/sac/ggen-marketplace && python3 scripts/marketplace.py validate
validated packs=339 manifests=339 ontologies=557 templates=1925 native_gates=1962 verifier_gates=21 ...
$ echo $?
0
```

```
$ cd /Users/sac/ggen/examples/industry/pharma-21cfr
$ cp <pack>/ontology.ttl pack-vocabulary.ttl && ggen sync run   # twice
$ diff -q run1 run2 -> byte-identical (DETERMINISTIC); generated SHACL 126 triples
```

## Falsifiers (how this receipt is wrong)

- Any fail witness flipping a second gate → verify.py exits 1 (NOT
  exactly-one-law).
- Deleting a pillar face from any compliant individual → its gate returns rows
  over ontology.ttl → exit 1.
- Swapped expectation or cross-stem pairing accepted → runner exit 0 → vacuous
  court.
- Consumer sync drift between consecutive runs → not deterministic.

None fired on this subject (receipts above).
