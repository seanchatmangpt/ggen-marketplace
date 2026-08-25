# Reference

Accepted envelope fields are `repository`, `head_sha`, `kind`, and `payload`. `repository` must contain owner/name, `head_sha` must be exactly 40 lowercase hexadecimal characters, `kind` must be one of `run`, `job`, `pull_request`, or `commit_status`, and `payload` must be a JSON object.

The normalizer emits `exact_subject`, `evidence_kind`, `payload`, `raw_digest`, `receipt_digest`, `authority`, and `actuation_performed`. Digests are SHA-256 over canonical JSON with sorted keys and compact separators. Authority is fixed to `OBSERVE|VERIFY|CONSTRUCT`; actuation is always false. Unsupported evidence kinds, invalid repositories, inexact SHAs, or non-object payloads are typed refusals.

HANDWRITTEN_IRREDUCIBLE_REASON: canonical JSON normalization, cryptographic digest computation, stdin/stdout framing, and grouping algorithms are runtime substrate not expressible as static ontology projection alone. Reusable structure, contracts, fixtures, queries, and documentation remain pack-owned deterministic source.
