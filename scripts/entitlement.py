#!/usr/bin/env python3
"""Entitlement seam: typed decide() over the GCP Marketplace commerce sim.

`decide(entitlement_id, config)` returns a typed standing record — never raises
for expected conditions. Standing vocabulary:
  ALIVE  (entitlement active, sim backend, backend_standing=SIMULATED,
          jwt_verified=true — the record's RS256 JWT is cryptographically
          verified against the sim/real x509 metadata endpoint)
  BLOCKED with a typed `refusal` otherwise.

Exit codes (CLI): 0=ALIVE, 3=unreachable/endpoint-not-loopback, 4=NOT_ACTIVE,
5=invalid refusal, 6=registry invalid. Refusal codes are typed strings, never
bare exceptions.
"""

import argparse
import base64
import binascii
import hashlib
import ipaddress
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from re import fullmatch

DEFAULT_ENDPOINT = "http://localhost:8443"
DEFAULT_TIMEOUT_SECS = 5

METADATA_PATH = "/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com"
CANONICAL_ISSUER = "https://www.googleapis.com" + METADATA_PATH

ENTITLEMENT_ID_PATTERN = r"^[A-Za-z0-9._-]{1,128}$"

REFUSED_UNREACHABLE = "REFUSED_ENTITLEMENT_UNREACHABLE"
REFUSED_NOT_FOUND = "REFUSED_ENTITLEMENT_NOT_FOUND"
REFUSED_NOT_ACTIVE = "REFUSED_ENTITLEMENT_NOT_ACTIVE"
REFUSED_REAL_NOT_PERMITTED = "REFUSED_ENTITLEMENT_REAL_NOT_PERMITTED"
REFUSED_PROVIDER_UNREACHABLE = "REFUSED_ENTITLEMENT_PROVIDER_UNREACHABLE"
REFUSED_CARDINALITY = "REFUSED_BILLING_AUTHORITY_CARDINALITY"
REFUSED_BACKEND_UNKNOWN = "REFUSED_BACKEND_UNKNOWN"
REFUSED_REGISTRY_INVALID = "REFUSED_REGISTRY_INVALID"
REFUSED_ID_INVALID = "REFUSED_ENTITLEMENT_ID_INVALID"
REFUSED_ENDPOINT_NOT_LOOPBACK = "REFUSED_ENTITLEMENT_ENDPOINT_NOT_LOOPBACK"
REFUSED_JWT_INVALID = "REFUSED_ENTITLEMENT_JWT_INVALID"
REFUSED_CRYPTO_UNAVAILABLE = "REFUSED_ENTITLEMENT_CRYPTO_UNAVAILABLE"

EXIT_OK = 0
EXIT_UNREACHABLE = 3
EXIT_NOT_ACTIVE = 4
EXIT_INVALID = 5
EXIT_REGISTRY_INVALID = 6


def _base_url() -> str:
    return os.environ.get("AAIF_ENTITLEMENT_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")


def _refused(refusal: str) -> dict:
    return {"standing": "BLOCKED", "refusal": refusal}


def _is_loopback(url: str) -> bool:
    try:
        parsed = urllib.parse.urlparse(url)
        host = parsed.hostname
        if not host:
            return False
        if host == "localhost":
            return True
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def _validate_endpoint() -> str | None:
    """AAIF_ENTITLEMENT_ENDPOINT overrides must stay on loopback unless
    AAIF_ENTITLEMENT_ALLOW_REMOTE=1 is set."""
    override = os.environ.get("AAIF_ENTITLEMENT_ENDPOINT")
    if not override:
        return None
    if os.environ.get("AAIF_ENTITLEMENT_ALLOW_REMOTE") == "1":
        return None
    if _is_loopback(override):
        return None
    return REFUSED_ENDPOINT_NOT_LOOPBACK


def _validate_registry(config: dict) -> str | None:
    """Return a refusal code when the monetization registry is unusable."""
    if "backend" not in config:
        return REFUSED_REGISTRY_INVALID
    auths = config.get("billing_authorities")
    if not isinstance(auths, list) or len(auths) != 1:
        return REFUSED_CARDINALITY
    return None


def _validate_entitlement_id(entitlement_id: str) -> str | None:
    """entitlement_id is interpolated into URLs; refuse everything outside the
    safe charset/length before it touches a request path."""
    if not isinstance(entitlement_id, str) or not fullmatch(ENTITLEMENT_ID_PATTERN, entitlement_id):
        return REFUSED_ID_INVALID
    return None


def _fetch(url: str) -> tuple[int, dict | None]:
    """GET url. Returns (status, parsed-json-or-None); never raises on transport error."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT_SECS) as resp:
            body = resp.read()
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
        body = b""
    except Exception:
        return 0, None
    try:
        return status, json.loads(body.decode("utf-8"))
    except Exception:
        return status, None


def _b64url_decode(segment: str) -> bytes:
    padded = segment + "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def _verify_jwt(jwt_token: str, base_url: str, provider_id: str) -> tuple[bool, str]:
    """Verify the record's RS256 JWT against the x509 metadata map served at
    {base_url}{METADATA_PATH}. Returns (ok, kid)."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography import x509 as _x509
    except Exception:
        return False, REFUSED_CRYPTO_UNAVAILABLE

    parts = jwt_token.split(".") if isinstance(jwt_token, str) else []
    if len(parts) != 3:
        return False, ""
    try:
        header = json.loads(_b64url_decode(parts[0]))
        claims = json.loads(_b64url_decode(parts[1]))
        signature = _b64url_decode(parts[2])
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return False, ""

    if not isinstance(header, dict) or header.get("alg") != "RS256":
        return False, str(header.get("kid", "")) if isinstance(header, dict) else ""
    kid = header.get("kid")
    if not isinstance(kid, str) or not kid:
        return False, ""

    metadata_url = base_url + METADATA_PATH
    status, keys = _fetch(metadata_url)
    if status != 200 or not isinstance(keys, dict):
        return False, kid
    pem = keys.get(kid)
    if not isinstance(pem, str):
        return False, kid
    try:
        # Google's x509 metadata map is kid -> PEM certificate; the signing key
        # is the certificate's public key.
        public_key = _x509.load_pem_x509_certificate(pem.encode("utf-8")).public_key()
        public_key.verify(signature, f"{parts[0]}.{parts[1]}".encode("utf-8"),
                          padding.PKCS1v15(), hashes.SHA256())
    except Exception:
        return False, kid

    if not isinstance(claims, dict):
        return False, kid
    # The issuer is the canonical Google robot metadata URL; when the keys are
    # served by a sim/override endpoint the fetch URL differs from the iss the
    # (real or sim) signer embeds, so both are accepted.
    if claims.get("iss") not in (CANONICAL_ISSUER, metadata_url):
        return False, kid
    if claims.get("aud") != provider_id:
        return False, kid
    exp = claims.get("exp")
    now = int(time.time())
    if not isinstance(exp, int) or exp <= 0 or exp <= now:
        return False, kid
    return True, kid


def decide(entitlement_id: str, config: dict) -> dict:
    registry_problem = _validate_registry(config)
    if registry_problem:
        return _refused(registry_problem)

    endpoint_problem = _validate_endpoint()
    if endpoint_problem:
        return _refused(endpoint_problem)

    id_problem = _validate_entitlement_id(entitlement_id)
    if id_problem:
        return _refused(id_problem)

    backend = config.get("backend")
    if backend == "real":
        if os.environ.get("AAIF_ENTITLEMENT_REAL_PERMIT") != "1":
            return _refused(REFUSED_REAL_NOT_PERMITTED)
        # Real cloudcommerceprocurement rail: no vendor id / ADC material is
        # configured in this environment, so an attempt is honestly BLOCKED.
        url = "{}/v1/providers/{}/entitlements/{}".format(
            _base_url(),
            config.get("provider_id") or os.environ.get("GCP_PROVIDER_ID", "UNSET_PROVIDER"),
            entitlement_id,
        )
        status, _ = _fetch(url)
        if status == 200:
            return {"standing": "BLOCKED", "refusal": REFUSED_REAL_NOT_PERMITTED}
        return _refused(REFUSED_PROVIDER_UNREACHABLE)

    if backend != "sim":
        return _refused(REFUSED_BACKEND_UNKNOWN)

    status, record = _fetch("{}/entitlements/{}".format(_base_url(), entitlement_id))
    if status == 0:
        return _refused(REFUSED_UNREACHABLE)
    if status == 404:
        return _refused(REFUSED_NOT_FOUND)
    if not isinstance(record, dict) or record.get("state") != "ENTITLEMENT_ACTIVE":
        return _refused(REFUSED_NOT_ACTIVE)

    provider_id = config.get("provider_id")
    if not isinstance(provider_id, str) or not provider_id:
        return _refused(REFUSED_REGISTRY_INVALID)
    jwt_token = record.get("jwt")
    ok, kid = _verify_jwt(jwt_token, _base_url(), provider_id)
    if not ok:
        if kid == REFUSED_CRYPTO_UNAVAILABLE:
            return _refused(REFUSED_CRYPTO_UNAVAILABLE)
        return _refused(REFUSED_JWT_INVALID)

    return {
        "standing": "ALIVE",
        "backend_standing": "SIMULATED",
        "entitlement": record,
        "jwt_verified": True,
        "jwt_kid": kid,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AAIF entitlement seam")
    parser.add_argument("command", choices=["decide"])
    parser.add_argument("entitlement_id")
    parser.add_argument("--config", default="monetization.toml")
    args = parser.parse_args(argv)

    config: dict = {}
    registry_invalid = False
    try:
        import tomllib

        with open(args.config, "rb") as f:
            config = tomllib.load(f)
    except FileNotFoundError:
        registry_invalid = True
    except Exception:
        registry_invalid = True

    if registry_invalid:
        result = _refused(REFUSED_REGISTRY_INVALID)
        print(json.dumps(result, indent=2))
        return EXIT_REGISTRY_INVALID

    result = decide(args.entitlement_id, config)
    print(json.dumps(result, indent=2))
    if result.get("standing") == "ALIVE":
        return EXIT_OK
    refusal = result.get("refusal")
    if refusal == REFUSED_NOT_ACTIVE:
        return EXIT_NOT_ACTIVE
    if refusal in (REFUSED_UNREACHABLE, REFUSED_PROVIDER_UNREACHABLE,
                   REFUSED_ENDPOINT_NOT_LOOPBACK):
        return EXIT_UNREACHABLE
    if refusal == REFUSED_REGISTRY_INVALID:
        return EXIT_REGISTRY_INVALID
    return EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())
