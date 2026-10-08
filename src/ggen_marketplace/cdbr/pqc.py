"""Post-Quantum Cryptographic (PQC) Protocol Profile Models (NIST FIPS 203/204/205)."""
from __future__ import annotations

import base64
from enum import Enum
from typing import Any, Dict


class PQCSuite(str, Enum):
    ML_DSA_65 = "ML_DSA_65"  # FIPS 204: 1952 byte pk, 3309 byte sig
    ML_DSA_87 = "ML_DSA_87"  # FIPS 204: 2592 byte pk, 4627 byte sig
    ML_KEM_768 = "ML_KEM_768"  # FIPS 203: 1184 byte pk, 1088 byte ct


PQC_BUFFER_CONSTRAINTS = {
    PQCSuite.ML_DSA_65: {"public_key_bytes": 1952, "signature_bytes": 3309},
    PQCSuite.ML_DSA_87: {"public_key_bytes": 2592, "signature_bytes": 4627},
    PQCSuite.ML_KEM_768: {"public_key_bytes": 1184, "ciphertext_bytes": 1088},
}


class PqcValidationError(Exception):
    """Raised when an unapproved cryptographic algorithm or buffer mismatch is detected."""
    pass


class PQCVerifier:
    """Validates PQC cryptographic envelopes and rejects classical downgrade attempts."""

    @classmethod
    def validate_key_descriptor(cls, alg_name: str, public_key_b64: str) -> Dict[str, Any]:
        # 1. Closed-enum validation: Classical algorithms do not exist in the algebraic type
        try:
            suite = PQCSuite(alg_name)
        except ValueError as exc:
            raise PqcValidationError(
                f"ERR_UNINHABITED_CIPHER_SUITE: Algorithm '{alg_name}' is not an admitted post-quantum suite. "
                f"Classical ciphers (RSA, ECDSA, Ed25519) are structurally refused."
            ) from exc

        # 2. Strict unpadded Base64URL check
        if "=" in public_key_b64:
            raise PqcValidationError("ERR_PQC_ENCODING: Padding character '=' is forbidden in unpadded Base64URL")

        try:
            # Add back required padding for decoding check
            pad_len = (4 - len(public_key_b64) % 4) % 4
            raw_pk = base64.urlsafe_b64decode(public_key_b64 + "=" * pad_len)
        except Exception as exc:
            raise PqcValidationError(f"ERR_PQC_DECODE_FAILED: {exc}") from exc

        # 3. Fixed-width buffer constraint
        expected_len = PQC_BUFFER_CONSTRAINTS[suite]["public_key_bytes"]
        if len(raw_pk) != expected_len:
            raise PqcValidationError(
                f"ERR_PQC_BUFFER_MISMATCH: Public key for {suite.value} must be exactly {expected_len} bytes, got {len(raw_pk)}"
            )

        return {"suite": suite, "raw_bytes_len": len(raw_pk)}
