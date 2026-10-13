//! Real ML-DSA-65 sign/verify courts for strata-signer-pack (S3 extension).
//!
//! The pack's generated `signing.rs` is a digest-binding TRAIT + adapter, not
//! a crypto implementation — the real ML-DSA-65 algorithm lives in
//! ~/strata/strata_protocol/src/signer.rs over the `ml-dsa` crate. This
//! harness ports that algorithm over the SAME crate version strata pins
//! (0.1.1), includes the generated file UNMODIFIED via `#[path]`, and runs
//! the positive/negative/key-length/sabotage courts against real crypto.

/// The pack's generated signing layer, compiled unmodified.
#[path = "../../generated/signing.rs"]
pub mod signing;

use ml_dsa::{Keypair, MlDsa65, Signature, SigningKey, VerifyingKey};
use signing::{PayloadSigner, PUBLIC_KEY_LEN, DIGEST_LEN, PAYLOAD_SIGNATURE_LEN};

/// Domain-separation context, byte-identical to the ground truth's
/// `SIGN_CONTEXT` in ~/strata/strata_protocol/src/signer.rs.
const SIGN_CONTEXT: &[u8] = b"strata-clap-attest-v1";

/// Ground-truth port: deterministic ML-DSA-65 signer derived from a 32-byte
/// seed (signer.rs `Signer::from_seed`), adapted to the pack's
/// `PayloadSigner` trait over a 32-byte tx digest.
pub struct MlDsaSigner {
    signing_key: SigningKey<MlDsa65>,
    verifying_key: VerifyingKey<MlDsa65>,
    public_key: Vec<u8>,
}

impl MlDsaSigner {
    /// Deterministic keypair from a 32-byte seed (xi).
    pub fn from_seed(seed: [u8; 32]) -> Self {
        let ml_seed = ml_dsa::Seed::from(seed);
        let signing_key = SigningKey::<MlDsa65>::from_seed(&ml_seed);
        let verifying_key = signing_key.verifying_key();
        let public_key = verifying_key.encode().to_vec();
        MlDsaSigner {
            signing_key,
            verifying_key,
            public_key,
        }
    }

    /// Encoded public key (1952 bytes).
    pub fn public_key(&self) -> &[u8] {
        &self.public_key
    }

    /// Deterministic detached signature (3309 bytes) under SIGN_CONTEXT.
    pub fn sign(&self, digest: &[u8; 32]) -> [u8; PAYLOAD_SIGNATURE_LEN] {
        let sig = self
            .signing_key
            .expanded_key()
            .sign_deterministic(digest, SIGN_CONTEXT)
            .expect("deterministic ML-DSA sign cannot fail for well-formed input");
        let mut out = [0u8; PAYLOAD_SIGNATURE_LEN];
        out.copy_from_slice(sig.encode().as_slice());
        out
    }

    /// Verify a detached signature over `digest` under SIGN_CONTEXT.
    /// Byte-port of signer.rs `Signer::verify`, fails closed.
    pub fn verify(public_key: &[u8], digest: &[u8; 32], signature: &[u8]) -> bool {
        let Ok(pk_enc) = ml_dsa::EncodedVerifyingKey::<MlDsa65>::try_from(public_key) else {
            return false;
        };
        let vk = VerifyingKey::<MlDsa65>::decode(&pk_enc);
        let Ok(sig_enc) = ml_dsa::EncodedSignature::<MlDsa65>::try_from(signature) else {
            return false;
        };
        let Some(sig) = Signature::<MlDsa65>::decode(&sig_enc) else {
            return false;
        };
        vk.verify_with_context(digest, SIGN_CONTEXT, &sig)
    }
}

/// Sabotage twin: a weakened verifier that SKIPS the domain-separation
/// prefix (verifies under the empty context instead of SIGN_CONTEXT). Under
/// real ML-DSA-65 this is a different domain — it must reject every valid
/// strata signature, which is exactly how the courts catch it.
struct SabotageTwin;

impl SabotageTwin {
    const WEAK_CONTEXT: &[u8] = b"";

    fn verify(public_key: &[u8], digest: &[u8; 32], signature: &[u8]) -> bool {
        let Ok(pk_enc) = ml_dsa::EncodedVerifyingKey::<MlDsa65>::try_from(public_key) else {
            return false;
        };
        let vk = VerifyingKey::<MlDsa65>::decode(&pk_enc);
        let Ok(sig_enc) = ml_dsa::EncodedSignature::<MlDsa65> ::try_from(signature) else {
            return false;
        };
        let Some(sig) = Signature::<MlDsa65>::decode(&sig_enc) else {
            return false;
        };
        vk.verify_with_context(digest, Self::WEAK_CONTEXT, &sig)
    }
}

/// Wire-size court: the ml-dsa crate's actual encoded sizes must equal the
/// FIPS 204 constants (port of signer.rs `assert_wire_sizes`).
fn assert_wire_sizes() {
    let sig_enc = ml_dsa::EncodedSignature::<MlDsa65>::default();
    let pk_enc = ml_dsa::EncodedVerifyingKey::<MlDsa65>::default();
    let sig_buf: &[u8] = sig_enc.as_ref();
    let pk_buf: &[u8] = pk_enc.as_ref();
    assert_eq!(sig_buf.len(), PAYLOAD_SIGNATURE_LEN);
    assert_eq!(pk_buf.len(), PUBLIC_KEY_LEN);
}

/// Bridge so the generated `TxSigner` adapter runs over REAL crypto.
struct RealBackend(MlDsaSigner);

impl PayloadSigner for RealBackend {
    fn sign(&self, payload: &[u8]) -> [u8; PAYLOAD_SIGNATURE_LEN] {
        let mut digest = [0u8; 32];
        digest.copy_from_slice(payload);
        self.0.sign(&digest)
    }
    fn verify(&self, payload: &[u8], sig: &[u8; PAYLOAD_SIGNATURE_LEN]) -> bool {
        let mut digest = [0u8; 32];
        digest.copy_from_slice(payload);
        MlDsaSigner::verify(self.0.public_key(), &digest, sig)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use signing::TxSigner;

    const SEED: [u8; 32] = [
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e,
        0x1f, 0x20,
    ];

    #[test]
    fn wire_sizes_match_crate() {
        assert_wire_sizes();
    }

    /// S3 court (positive): real ML-DSA-65 sign of a deterministic 32-byte
    /// tx digest — exactly 3309 bytes, verifies, and deterministic.
    #[test]
    fn real_positive_sign_verify_tx_digest() {
        let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
        let digest = adapter.bind_tx_digest(b"tx-digest-court-001");
        assert_eq!(digest.len(), 32);
        let sig = adapter.sign_tx(b"tx-digest-court-001");
        assert_eq!(sig.len(), 3309);
        assert!(adapter.verify_tx(b"tx-digest-court-001", &sig));
        let sig2 = adapter.sign_tx(b"tx-digest-court-001");
        assert_eq!(sig, sig2, "deterministic sign must reproduce byte-identical sig");
    }

    /// S3 court (negative): flipping one bit of a REAL ML-DSA-65 signature
    /// must refuse.
    #[test]
    fn real_flipped_signature_bit_refused() {
        let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
        let sig = adapter.sign_tx(b"tx-digest-court-002");
        let mut bad = sig;
        bad[17] ^= 0x01;
        assert!(!adapter.verify_tx(b"tx-digest-court-002", &bad));
    }

    /// S3 court (negative): a real signature over one digest must not verify
    /// over a different digest.
    #[test]
    fn real_different_digest_refuses_original_signature() {
        let adapter = TxSigner::new(RealBackend(MlDsaSigner::from_seed(SEED)));
        let sig = adapter.sign_tx(b"tx-digest-court-003");
        assert!(!adapter.verify_tx(b"a-different-tx", &sig));
    }

    /// S3 court (key lengths): encoded public key is exactly 1952 bytes and
    /// the signature exactly 3309 — the ontology-declared st:publicKeyLen /
    /// st:signatureLen.
    #[test]
    fn real_key_lengths_match_ontology() {
        let signer = MlDsaSigner::from_seed(SEED);
        assert_eq!(signer.public_key().len(), 1952);
        assert_eq!(signer.public_key().len(), PUBLIC_KEY_LEN);
        let sig = signer.sign(&signing::sha256(b"len-court"));
        assert_eq!(sig.len(), 3309);
        assert_eq!(sig.len(), PAYLOAD_SIGNATURE_LEN);
    }

    /// S3 court (sabotage twin): a verifier that skips the domain-separation
    /// prefix (empty context) must be CAUGHT — it rejects the valid strata
    /// signature (positive court fails under the twin) and cannot pass a
    /// cross-context signature off as valid.
    #[test]
    fn sabotage_twin_caught_by_courts() {
        let signer = MlDsaSigner::from_seed(SEED);
        let digest = signing::sha256(b"tx-digest-court-sabotage");
        let good_sig = signer.sign(&digest);

        // (a) The twin refuses the valid strata signature → the positive
        //     court catches the weakened verifier.
        assert!(
            !SabotageTwin::verify(signer.public_key(), &digest, &good_sig),
            "sabotage twin must NOT accept a SIGN_CONTEXT signature"
        );
        // (b) The correct verifier accepts it (control).
        assert!(MlDsaSigner::verify(signer.public_key(), &digest, &good_sig));

        // (c) Cross-context: a twin-signed (empty-context) signature is also
        //     refused by the correct verifier — domain separation holds both
        //     directions.
        let weak_sig = signer
            .signing_key
            .expanded_key()
            .sign_deterministic(&digest, SabotageTwin::WEAK_CONTEXT)
            .expect("empty context is a legal ML-DSA context");
        let mut weak_bytes = [0u8; PAYLOAD_SIGNATURE_LEN];
        weak_bytes.copy_from_slice(weak_sig.encode().as_slice());
        assert_ne!(weak_bytes, good_sig, "different context must change the signature");
        assert!(
            !MlDsaSigner::verify(signer.public_key(), &digest, &weak_bytes),
            "empty-context signature must not verify under the strata context"
        );
    }
}
