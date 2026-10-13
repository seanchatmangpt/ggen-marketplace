# errc-tracker.md — strata-signer-pack hardening wave 2026-10-13

ERRC pass; citations re-verified at write time — no paraphrase for a
citation.

## Eliminate

Legacy `templates/signer.rs.tmpl` deleted (superseded by
`templates/signer.rs.tera` + `ggen.toml` `signer-keys` rule). `pack.toml`
`[dependencies]` removed (FM-PACK-014).

## Reduce

Dead-vocabulary debt: `st:signatureLen 3309` / `st:publicKeyLen 1952`
were declared but never projected; now REQUIRED query bindings
(`queries/keys.rq`) projected as `SIGNATURE_LEN`/`PUBLIC_KEY_LEN` consts.

## Raise

ML-DSA-65 constants court-gated (`gates/010_mldsa65_lengths.rq`);
ground truth cross-verified against the real sources 2026-10-12:
`~/strata/strata_protocol/src/signer.rs` (AttestedPayload sign/verify)
and affidavit-trust-plane-pack `ontology.ttl:399` `ctp:alg-ML-DSA-65`.
Negative witness: algorithm→ed25519 refused FM-LAW-018.

S3 (2026-10-13): digest-binding layer raised from constants-only —
`st:DigestBinding` class + `st:TxDigestBinding` individual
(SHA-256/32 → ML-DSA-65/3309), `queries/digest_bindings.rq`,
`templates/signing.rs.tera` → `generated/signing.rs`
(`PayloadSigner` trait + `TxSigner::bind_tx_digest`), second gate
`gates/020_digest_binding.rq` (presence+value arms, fail-closed, V7
pattern). Receipts: ggen sync ×2 byte-identical
(graph_hash `1134b20c…`), rustc --test 7/7 pass, `verify.py` exit 0
(gate set witnessed in `witness.ttl`), `qualify_packs.py --pack
strata-signer-pack` ALIVE.

## Create

`ggen.toml`, `queries/keys.rq`, `templates/signer.rs.tera`,
`generated/signer.rs` (sha256 5875b83a… at write time; superseded by 2a0fd535… after banner regen), gate — new this wave.
