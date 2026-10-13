# How to share a cross-repo fixture court

When two repositories must agree on one byte-exact surface — a golden fixture, a known-answer
test (KAT) head, a set of ABI constants — a comment that says "matches repo X" is not a pin; it
is a promise with no court behind it. This pattern, proven across five seams on 2026-10-13,
makes the agreement mechanical: one committed fixture, a sha256 provenance header, a drift
meta-test on both sides, and lanes that never commit.

Exemplars (read these before writing your own):

- Canonical fixture: `graphlaw tests/fixtures/fm_chain_009.json`
  (sha256 `b5eccba4…`), with the byte-identical copy at
  `affidavit affidavit-core/tests/fixtures/fm_chain_009.json`.
- Pin + drift meta-test: `affidavit affidavit-core/tests/bcinr_fm_chain_009.rs`
  (`PIN_SHA256` constant and `fixture_pin_detects_cross_repo_drift`).
- Refusal-receipt seam (sealed an all-zero placeholder): `strata-valve-pack`
  real refusal-receipt derivation, `docs/sjira/v26.10.8/RECEIPT-INDEX.md`.

## 1. When to use

Use this pattern when a test in repo A would pass against a stale or hand-tuned copy of a
surface owned by repo B. Signals:

- a fixture or constant table is duplicated in two repos with no digest binding them;
- a spec-bearing repo publishes a surface that consumers cite in comments but do not verify
  (the meta-pattern in `docs/sjira/v26.10.8/INNOVATION-LEDGER.md` #28/#34–#39);
- a KAT head, golden receipt chain, or ABI constant set is the actual interface between two
  runtimes.

Do not use it for surfaces that change intentionally and often — pin the generator instead.

## 2. The sha256 provenance-header convention

Commit the fixture once, in the owning repo, and copy it byte-identically into consumers.
Bind it with two pin layers:

1. **Header comments.** The first lines of the fixture file name the canonical source, the
   pin rule, and the drift consequence:

   ```text
   // Canonical: graphlaw tests/fixtures/fm_chain_009.json
   // Pin: both copies must stay byte-identical; a one-sided edit fails the drift meta-test.
   // Re-pin procedure: edit both, recompute the sha256, update PIN_SHA256 in both repos in
   // the same dependency-closed commit.
   ```

2. **`FIXTURE_SHA256`/`PIN_SHA256` constants.** The consuming test declares the expected
   digest as a constant and fails loudly with a repair instruction:

   ```rust
   /// Any one-sided edit of the fixture fails `fixture_pin_detects_cross_repo_drift`.
   const PIN_SHA256: &str = "4f3c42aa0c561bc143af61e3715aec2f73ed1a1249e45e6113a9880e368a4875";
   const FIXTURE_PATH: &str = "tests/fixtures/fm_chain_009.json";
   ```

The digest covers the JSON body (or the whole file when the header is part of the pin); pick
one rule and state it in the header. A header without a digest is a comment; a digest without
a header is a mystery.

## 3. The drift meta-test pattern

Both repos get a test whose only job is to detect a one-sided edit — the class of defect where
repo A's copy moves and repo B's silently diverges. The test hashes the local fixture copy and
asserts the digest equals `PIN_SHA256`; on mismatch it must name the other repo's fixture path
in the failure message so the repair path is one hop:

```rust
assert_eq!(
    hex::encode(Sha256::digest(&bytes)),
    PIN_SHA256,
    "fixture drift: {FIXTURE_PATH} changed; if intentional, re-pin PIN_SHA256 AND keep \
     graphlaw's tests/fixtures/fm_chain_009.json byte-identical in its JSON body"
);
```

Run the tamper case too: flip a byte in an in-memory copy, assert the chain head (or the
surface under test) changes. A pin that cannot detect an injected tamper is decoration. On the
FM-CHAIN-009 seam this ran as graphlaw 5 passed / affidavit 6 passed (ledger #28 close-out).

## 4. Coordinator-owned git

Lanes write files; the coordinator owns every git transition. Concretely:

- lanes never run `git commit`, `git stash`, or any state command;
- each lane owns a disjoint file set; shared files (a fixture two lanes both re-pin) are
  resolved by the coordinator at integration;
- the coordinator commits per lane, so each seam's receipt names one exact diff.

This is what makes the receipt chain replayable: one commit per seam, one digest per fixture.

## 5. Failure modes seen on 2026-10-13

- **Hand-copied fixture goes stale.** Ledger #37 superseded #28 because T10 ported the rule
  but the fixture hex stayed hand-copied on both sides with no shared artifact. The fix was
  not more care — it was the committed fixture + hash meta-tests.
- **Pinning a placeholder instead of a real value.** The strata-valve-pack refusal-receipt
  derivation initially had to seal out an all-zero receipt placeholder: a pin constant filled
  with `0000…` passes any structural check and proves nothing. Assert the digest is a real
  observed value (and non-trivial) before admitting it as a pin.
- **Concurrent writers to one file.** Two lanes wrote `mfact procint/ProcInt/Petri/
  PN64Conservation.lean` in the same wave and clobbered each other; the seam had to be
  re-serialized through the coordinator. If two lanes need the same file, the second waits or
  takes a different file — never "both, last write wins".

## See Also

- [Add or migrate a CI court](add-a-ci-court.md)
- [Pin and verify packs](pin-and-verify-packs.md)
- [Qualify a realization](qualify-a-realization.md)
- [Innovation ledger, seams 28/29](../sjira/v26.10.8/INNOVATION-LEDGER.md)
