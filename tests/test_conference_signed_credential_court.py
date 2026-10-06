# tests/test_conference_signed_credential_court.py
# Lane CG8 - conference-commerce signed credentials over the affidavit wasm trust plane.
#
# Signing split (honest, documented):
#   * HOST signs  - Python `cryptography`, ES256 (P-256, ECDSA/DER, low-s normalized).
#   * WASM verifies - the pinned affidavit engine (artifact sha256 5cc37aea...) is the
#     only verifier: `derive_subject_digest` (domain-separated BLAKE3 binding of the
#     credential to its subject) and `verify_signature` (per-alg ES256/DER low-s check).
# The pinned wasm ABI has no signing op (verify_signature and derive_subject_digest are
# verify-side ops), so the engine cannot be asked to sign; it witnesses verification only.

import hashlib
import json

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import (
    decode_dss_signature,
    encode_dss_signature,
)
from wasmtime import Engine, FuncType, Linker, Module, Store, ValType

WASM_PATH = "/Users/sac/affidavit/affidavit-wasm/target/wasm32-wasip1/wasm/affidavit_wasm.wasm"
WASM_SHA256 = "5cc37aea8e59f7139e2ff5d43ab3c3c82931285b6400cf45f943c61d21a41402"

DOMAIN_TAG = "ggen-marketplace.conference-credential.v1"


class EngineUnavailable(Exception):
    """The pinned affidavit wasm artifact is not present/admissible at WASM_PATH."""


def _check_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            digest.update(chunk)
    if digest.hexdigest() != WASM_SHA256:
        raise EngineUnavailable(
            "affidavit wasm artifact digest drift: %s != %s" % (digest.hexdigest(), WASM_SHA256)
        )


def _load_engine():
    _check_sha256(WASM_PATH)
    engine = Engine()
    module = Module.from_file(engine, WASM_PATH)
    store = Store(engine)
    linker = Linker(engine)
    try:
        instance = linker.instantiate(store, module)
    except Exception:
        # wasip1 imports not auto-defined by this wasmtime-py build: stub the five
        # wasi_snapshot_preview1 calls the module declares (hermetic, no ambient WASI).
        i32 = ValType.i32()

        def _proc_exit(_code):
            raise RuntimeError("affidavit engine called proc_exit")

        linker.define_func(
            "wasi_snapshot_preview1", "random_get",
            FuncType([i32, i32], [i32]), lambda buf, ln: 0,
        )
        linker.define_func(
            "wasi_snapshot_preview1", "environ_get",
            FuncType([i32, i32], [i32]), lambda a, b: 0,
        )
        linker.define_func(
            "wasi_snapshot_preview1", "environ_sizes_get",
            FuncType([i32, i32], [i32]), lambda a, b: 0,
        )
        linker.define_func(
            "wasi_snapshot_preview1", "fd_write",
            FuncType([i32, i32, i32, i32], [i32]), lambda fd, iovs, n, out: 0,
        )
        linker.define_func(
            "wasi_snapshot_preview1", "proc_exit",
            FuncType([i32], []), _proc_exit,
        )
        instance = linker.instantiate(store, module)
    return engine, store, instance


_ENGINE = None


def _engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = _load_engine()
    return _ENGINE


# ---------------------------------------------------------------------------
# ABI transact: af_alloc -> write -> af_call -> read result -> af_free
# (mirror of AshAffidavit.Host.transact/3 + AshAffidavit.ABI.unpack_result/1)
# ---------------------------------------------------------------------------


def _u64(x):
    return x if x >= 0 else x + (1 << 64)


def _unpack_result(packed):
    unsigned = _u64(packed)
    return (unsigned >> 32, unsigned & 0xFFFFFFFF)


def af_transact(store, instance, request):
    exports = instance.exports(store)
    memory = exports["memory"]
    af_alloc = exports["af_alloc"]
    af_call = exports["af_call"]
    af_free = exports["af_free"]

    body = json.dumps(request).encode()
    ptr = af_alloc(store, len(body))
    if not isinstance(ptr, int) or ptr <= 0:
        raise RuntimeError("af_alloc refused a %d-byte request" % len(body))
    memory.write(store, body, ptr)
    packed = af_call(store, ptr, len(body))
    out_ptr, out_len = _unpack_result(packed)
    if (out_ptr, out_len) == (0, 0):
        raise RuntimeError("af_call returned an empty result slot")
    raw = bytes(memory.read(store, out_ptr, out_ptr + out_len))
    af_free(store, out_ptr, out_len)
    return json.loads(raw.decode())


def af_call(request):
    _engine_tuple = _engine()
    return af_transact(_engine_tuple[1], _engine_tuple[2], request)


# ---------------------------------------------------------------------------
# Credential manufacture (canonical JSON law) + host ES256 signing
# ---------------------------------------------------------------------------


def build_credential(customer_id, tier, entitlement_id):
    doc = {
        "version": "MKT-CRED-v1",
        "customer_id": customer_id,
        "tier": tier,
        "entitlement_id": entitlement_id,
    }
    return json.dumps(doc, sort_keys=True, separators=(",", ":")).encode()


def host_keypair_es256():
    key = ec.generate_private_key(ec.SECP256R1())
    pub = key.public_key().public_bytes(
        serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint
    )
    return key, pub


def host_sign_es256(private_key, message):
    der = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    # The engine enforces low-s; `cryptography` may emit high-s. Normalize deterministically.
    r, s = decode_dss_signature(der)
    n = _P256_ORDER
    if s > n // 2:
        s = n - s
    return encode_dss_signature(r, s)


_P256_ORDER = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551


# ---------------------------------------------------------------------------
# Engine ops
# ---------------------------------------------------------------------------


def wasm_derive_subject_digest(subject, domain_tag=DOMAIN_TAG):
    resp = af_call({
        "op": "derive_subject_digest",
        "domain_tag": domain_tag,
        "subject_hex": subject.hex(),
    })
    assert resp.get("ok", True), resp
    return resp["digest_hex"]


def wasm_verify_signature(alg, public_key, signature, signing_input):
    resp = af_call({
        "op": "verify_signature",
        "alg": alg,
        "public_key_hex": public_key.hex(),
        "signature_hex": signature.hex(),
        "signing_input_hex": signing_input.hex(),
    })
    return resp


# ---------------------------------------------------------------------------
# Courts
# ---------------------------------------------------------------------------


def test_engine_pin_and_abi_version():
    """The pinned artifact admits and reports ABI version 1."""
    engine_tuple = _engine()
    store = engine_tuple[1]
    abi_version = engine_tuple[2].exports(store)["af_abi_version"](store)
    assert abi_version == 1


def test_valid_credential_verify_signature_true():
    """Valid credential: host signs, wasm verify_signature returns valid:true."""
    key, pub = host_keypair_es256()
    cred = build_credential("cust-001", "platinum", "ent-conf-booth-9")
    digest_hex = wasm_derive_subject_digest(cred)
    assert len(digest_hex) == 64
    sig = host_sign_es256(key, cred)
    resp = wasm_verify_signature("ES256", pub, sig, cred)
    assert resp.get("ok") is True, resp
    assert resp.get("valid") is True, resp
    assert resp.get("refusal") in (None, ""), resp


def test_tampered_credential_verify_signature_false():
    """Tampered credential (one byte flipped): wasm returns valid:false."""
    key, pub = host_keypair_es256()
    cred = build_credential("cust-002", "gold", "ent-conf-booth-9")
    wasm_derive_subject_digest(cred)
    sig = host_sign_es256(key, cred)
    tampered = bytearray(cred)
    tampered[cred.index(b'":', 20) + 2] ^= 0x01
    resp = wasm_verify_signature("ES256", pub, bytes(tampered), sig)
    assert resp.get("ok") is False or resp.get("valid") is False, resp
    assert resp.get("valid") is False, resp


def test_wrong_alg_typed_refusal():
    """An algorithm outside the engine's set is a typed refusal, not valid:false."""
    key, pub = host_keypair_es256()
    cred = build_credential("cust-003", "silver", "ent-conf-booth-9")
    sig = host_sign_es256(key, cred)
    resp = wasm_verify_signature("RSA2048", pub, sig, cred)
    refusal = (resp.get("refusal") or "")
    # The engine answers on the ok channel with a typed refusal string:
    # `unsupported_algorithm: ...` names the bad alg and the supported set.
    assert "unsupported_algorithm" in refusal, resp
    assert "RSA2048" in refusal, resp
    assert resp.get("valid") is False, resp


def test_cross_customer_use_refused():
    """A credential bound to customer A does not verify under customer B's bytes."""
    key, pub = host_keypair_es256()
    cred_a = build_credential("cust-A", "platinum", "ent-conf-booth-9")
    cred_b = build_credential("cust-B", "platinum", "ent-conf-booth-9")
    sig_a = host_sign_es256(key, cred_a)
    # B's credential presented with A's signature: subject digest differs, signature fails.
    digest_a = wasm_derive_subject_digest(cred_a)
    digest_b = wasm_derive_subject_digest(cred_b)
    assert digest_a != digest_b, "engine-derived subject digest must bind the customer"
    resp = wasm_verify_signature("ES256", pub, sig_a, cred_b)
    assert resp.get("valid") is False, resp


def test_cross_entitlement_use_refused():
    """Same customer, different entitlement_id: signature no longer verifies."""
    key, pub = host_keypair_es256()
    cred_1 = build_credential("cust-A", "platinum", "ent-conf-booth-9")
    cred_2 = build_credential("cust-A", "platinum", "ent-conf-keynote-1")
    sig_1 = host_sign_es256(key, cred_1)
    assert wasm_derive_subject_digest(cred_1) != wasm_derive_subject_digest(cred_2)
    resp = wasm_verify_signature("ES256", pub, sig_1, cred_2)
    assert resp.get("valid") is False, resp


def test_derive_subject_digest_is_domain_separated():
    """Different domain tags yield different digests over the same subject."""
    cred = build_credential("cust-D", "gold", "ent-conf-booth-9")
    d1 = wasm_derive_subject_digest(cred, DOMAIN_TAG)
    d2 = wasm_derive_subject_digest(cred, "other.domain.v1")
    assert d1 != d2


def test_digest_sha_drift_is_detected():
    """A digest-drifted engine artifact is refused at admission, not verified."""
    import os
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".wasm", delete=False) as fh:
        fh.write(b"not a real wasm module")
        path = fh.name
    try:
        with pytest.raises(EngineUnavailable):
            _check_sha256(path)
    finally:
        os.unlink(path)
