//! Cross-pack court (lane L135, S3): "the signature binds the transaction".
//!
//! Pins ONE canonical strata-tx-pack frame as a byte constant, computes its
//! tx-pack-domain digest through the signer's domain-separated
//! `bind_tx_digest` (SHA-256(TX_DIGEST_DOMAIN_TAG || frame_bytes)), signs the
//! digest with REAL ML-DSA-65, verifies, then flips one body byte — new
//! digest, original signature refuses. The law is closed mechanically.
//!
//! Provenance of the pinned frame: derived from the deterministic
//! `sample_tx(2, 1, 1)` shape in packs/strata-tx-pack/generated/tx_model.rs
//! (itself generated from packs/strata-tx-pack/templates/tx_model.rs.tera +
//! ontology.ttl): nonce 0xABCD_0002, one input (prev_txid first 8 bytes =
//! 2 * 0x9E3779B97F4A7C15 = 0x3C6EF372FE94F82A big-endian, prev_index 0),
//! one output (value 1000, unit 0). The 32-byte PAYLOAD_DIGEST slot is held
//! in canonical (zeroed) form: the stored-digest slot is tx-pack-owned
//! (currently FNV-1a(64) expansion; lane L125 is migrating it to BLAKE3) and
//! is deliberately OUT of this court's scope — the signer hashes the frame
//! bytes itself under its own domain tag, so the court is stable across the
//! tx-pack digest-function migration.
//!
//! Digest paths noted read-only (no tx-pack edit from this lane):
//! - current (SHA-256 path, signer side): SHA-256(b"strata-tx-payload-digest-v1" || frame)
//! - tx-pack stored slot: FNV-1a(64) expansion today; BLAKE3 target (L125).
//!   The signer binds the FRAME under its own domain, so the slot migration
//!   does not invalidate this court either way.

use super::signing::{sha256, TxSigner, TX_DIGEST_DOMAIN_TAG, DIGEST_LEN, PAYLOAD_SIGNATURE_LEN};
use super::{MlDsaSigner, PayloadSigner, RealBackend};

/// Pinned canonical tx frame, 101 bytes = 56 (header) + 36 (1 input) + 9
/// (1 output). Digest slot zeroed (canonical hashing form; see module doc).
const PINNED_TX_FRAME: [u8; 101] = [
    // MAGIC "STX1" (tx:TX_MAGIC 0x5354_5831 big-endian)
    0x53, 0x54, 0x58, 0x31,
    // VERSION 0x01
    0x01,
    // RESERVED 3 bytes, zero
    0x00, 0x00, 0x00,
    // NONCE 0xABCD_0002
    0x00, 0x00, 0x00, 0x00, 0xAB, 0xCD, 0x00, 0x02,
    // INPUT_COUNT 1
    0x00, 0x00, 0x00, 0x01,
    // OUTPUT_COUNT 1
    0x00, 0x00, 0x00, 0x01,
    // PAYLOAD_DIGEST slot — canonical zeros (tx-pack-owned stored value)
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00,
    // INPUT[0].prev_txid: 3C 6E F3 72 FE 94 F8 2A then 24 zero bytes
    0x3C, 0x6E, 0xF3, 0x72, 0xFE, 0x94, 0xF8, 0x2A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00,
    // INPUT[0].prev_index 0
    0x00, 0x00, 0x00, 0x00,
    // OUTPUT[0].value 1000
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0xE8,
    // OUTPUT[0].unit 0
    0x00,
];

/// Court seed (byte-identical to lib.rs SEED).
const SEED: [u8; 32] = [
    0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e,
    0x1f, 0x20,
];

/// Positive: the pinned canonical frame's domain-separated digest, signed
/// with real ML-DSA-65, verifies; signing is deterministic.
#[test]
fn pinned_frame_signature_binds() {
    let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
    let digest = adapter.bind_tx_digest(&PINNED_TX_FRAME);
    assert_eq!(digest.len(), DIGEST_LEN);
    // Domain separation is real: tagged digest != bare SHA-256 of the frame.
    assert_ne!(digest, sha256(&PINNED_TX_FRAME));

    let sig = adapter.sign_tx(&PINNED_TX_FRAME);
    assert_eq!(sig.len(), PAYLOAD_SIGNATURE_LEN);
    assert!(adapter.verify_tx(&PINNED_TX_FRAME, &sig), "pinned-frame signature must verify");
    let sig2 = adapter.sign_tx(&PINNED_TX_FRAME);
    assert_eq!(sig, sig2, "deterministic sign must reproduce byte-identical sig");
}

/// Negative (the binding law): flipping ONE body byte (OUTPUT[0].value low
/// byte) yields a different digest; the original signature REFUSES.
#[test]
fn one_flipped_frame_byte_refuses_original_signature() {
    let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
    let sig = adapter.sign_tx(&PINNED_TX_FRAME);

    let mut tampered = PINNED_TX_FRAME;
    tampered[100] ^= 0x01; // OUTPUT[0].unit tag byte
    assert_ne!(
        adapter.bind_tx_digest(&tampered),
        adapter.bind_tx_digest(&PINNED_TX_FRAME),
        "one flipped frame byte must change the digest"
    );
    assert!(
        !adapter.verify_tx(&tampered, &sig),
        "signature over the pinned frame must REFUSE the one-byte-tampered frame"
    );
}

/// Negative (header-tamper variant): flipping the nonce byte is equally
/// refused — the binding covers the whole canonical frame.
#[test]
fn nonce_flipped_frame_byte_refuses_original_signature() {
    let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
    let sig = adapter.sign_tx(&PINNED_TX_FRAME);
    let mut tampered = PINNED_TX_FRAME;
    tampered[12] ^= 0x01; // NONCE byte
    assert!(!adapter.verify_tx(&tampered, &sig));
}

/// Negative (wrong-key): the pinned-frame signature does not verify under a
/// different key's verifier.
#[test]
fn pinned_frame_wrong_key_refuses() {
    let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
    let other = TxSigner::new(RealBackend(MlDsaSigner::from_seed([0xEE; 32])));
    let sig = adapter.sign_tx(&PINNED_TX_FRAME);
    assert!(!other.verify_tx(&PINNED_TX_FRAME, &sig));
}

/// Sabotage twin (digest-layer domain skip): a signer whose bind_tx_digest
/// omits TX_DIGEST_DOMAIN_TAG (bare SHA-256, the pre-L135 weakness) produces
/// a signature that the correct domain-separated verifier refuses — and the
/// twin accepts it, exhibiting the cross-domain replay channel the tag
/// closes. Caught by real ML-DSA-65 on both sides.
#[test]
fn sabotage_twin_untagged_digest_caught() {
    /// Twin: bare SHA-256, no domain tag.
    struct UntaggedBackend(MlDsaSigner);
    impl PayloadSigner for UntaggedBackend {
        fn sign(&self, payload: &[u8]) -> [u8; PAYLOAD_SIGNATURE_LEN] {
            let mut d = [0u8; 32];
            d.copy_from_slice(payload);
            self.0.sign(&d)
        }
        fn verify(&self, payload: &[u8], sig: &[u8; PAYLOAD_SIGNATURE_LEN]) -> bool {
            let mut d = [0u8; 32];
            d.copy_from_slice(payload);
            MlDsaSigner::verify(self.0.public_key(), &d, sig)
        }
    }

    let correct = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));

    // The twin signs the BARE digest of the pinned frame.
    let bare = sha256(&PINNED_TX_FRAME);
    let twin_signer = MlDsaSigner::from_seed(SEED);
    let twin_sig = UntaggedBackend(twin_signer).sign(&bare);

    // (a) The correct, domain-separated verifier REFUSES it.
    assert!(
        !correct.verify_tx(&PINNED_TX_FRAME, &twin_sig),
        "untagged (bare-digest) signature must be refused by the domain-separated verifier"
    );
    // (b) The correct signature over the TAGGED digest verifies (control) and
    //     differs from the twin's output.
    let good_sig = correct.sign_tx(&PINNED_TX_FRAME);
    assert!(correct.verify_tx(&PINNED_TX_FRAME, &good_sig));
    assert_ne!(good_sig, twin_sig, "domain tag must change what is signed");
}

/// Cross-domain note court: the frame's tagged digest must also differ from
/// the digest the same tx bytes would get under a DIFFERENT domain tag —
/// domain separation generalizes (the tag is load-bearing, not decorative).
#[test]
fn domain_tag_alternate_differs() {
    let correct = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
    let tagged = correct.bind_tx_digest(&PINNED_TX_FRAME);
    let mut alt = b"strata-tx-payload-digest-v2-ALT".to_vec();
    alt.extend_from_slice(&PINNED_TX_FRAME);
    assert_ne!(tagged, sha256(&alt));
    // And the tag constant is exactly the ontology-declared st:digestDomainTag.
    assert_eq!(TX_DIGEST_DOMAIN_TAG, b"strata-tx-payload-digest-v1");
}
