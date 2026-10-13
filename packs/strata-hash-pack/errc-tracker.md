# errc-tracker.md — strata-hash-pack S1 construction lane

ERRC pass over the S1 construction. Claims verified against the working
tree at edit time (2026-10-13 session).

## Eliminate

- **No BLAKE3 implementation in the generated module.** BLAKE3 requires
  external crates to implement properly; the module is zero-crate by
  contract, so only the BLAKE3 *constants* are projected and the
  digest-closure gate (020) refuses any third algorithm. Documented, not
  hidden.

## Reduce

- **One query, two rules**: `queries/hash_algos.rq` is shared by both
  generation rules (constants and Merkle); no duplicate query text.
- **Zero-dep test entropy**: property tests use an in-file splitmix64
  instead of a test-only RNG crate — keeps `rustc --test` viable.

## Raise

- **Typed-malformed closed both ways** in `gates/010_digest_length.rq`:
  explicit `datatype()` arm AND malformed-lexical REGEX arm (the
  pn64/temprun fail-open pattern).
- **FIPS ground-truth vectors** pin the from-scratch SHA-256: empty
  string, "abc", and the 56-byte two-block NIST vector (message corrected
  this session via real hashlib/shasum cross-check — an earlier draft
  vector string was wrong and the test caught it).
- **REFUSED guard pattern** in both templates ({% if results | length == 0 %}).

## Create

- Pack per the strata house pattern (modeled on packs/strata-pn64-pack):
  pack.toml with FM-PACK-018 relationship note, ontology.ttl on the family
  kernel namespace, two validation gates, two generation rules, committed
  generated/ output.

## Incidents

- Mid-wave, the whole pack directory disappeared from the shared checkout
  (observed ~2026-10-13 05:26 UTC: `ls packs/ | grep hash` empty) and
  reappeared with identical content (sha256 match against session-known
  values) minutes later. Cause external to this lane (likely another
  process or lane); no edits lost. Coordinator should check for a
  concurrent actor touching packs/strata-hash-pack.
