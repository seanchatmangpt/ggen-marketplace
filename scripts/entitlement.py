#!/usr/bin/env python3
"""Entitlement seam: typed decide() over the GCP Marketplace commerce sim.

`decide(entitlement_id, config)` returns a typed standing record — never raises
for expected conditions. Standing vocabulary:
  ALIVE  (entitlement active, sim backend, backend_standing=SIMULATED)
  BLOCKED with a typed `refusal` otherwise.

Exit codes (CLI): 0=ALIVE, 3=unreachable, 4=NOT_ACTIVE, 5=invalid refusal,
6=registry invalid. Refusal codes are typed strings, never bare exceptions.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_ENDPOINT = "http://localhost:8443"
DEFAULT_TIMEOUT_SECS = 5

REFUSED_UNREACHABLE = "REFUSED_ENTITLEMENT_UNREACHABLE"
REFUSED_NOT_FOUND = "REFUSED_ENTITLEMENT_NOT_FOUND"
REFUSED_NOT_ACTIVE = "REFUSED_ENTITLEMENT_NOT_ACTIVE"
REFUSED_REAL_NOT_PERMITTED = "REFUSED_ENTITLEMENT_REAL_NOT_PERMITTED"
REFUSED_PROVIDER_UNREACHABLE = "REFUSED_ENTITLEMENT_PROVIDER_UNREACHABLE"
REFUSED_CARDINALITY = "REFUSED_BILLING_AUTHORITY_CARDINALITY"
REFUSED_BACKEND_UNKNOWN = "REFUSED_BACKEND_UNKNOWN"
REFUSED_REGISTRY_INVALID = "REFUSED_REGISTRY_INVALID"

EXIT_OK = 0
EXIT_UNREACHABLE = 3
EXIT_NOT_ACTIVE = 4
EXIT_INVALID = 5
EXIT_REGISTRY_INVALID = 6


def _base_url() -> str:
    return os.environ.get("AAIF_ENTITLEMENT_ENDPOINT", DEFAULT_ENDPOINT).rstrip("/")


def _refused(refusal: str) -> dict:
    return {"standing": "BLOCKED", "refusal": refusal}


def _validate_registry(config: dict) -> str | None:
    """Return a refusal code when the monetization registry is unusable."""
    if "backend" not in config:
        return REFUSED_REGISTRY_INVALID
    auths = config.get("billing_authorities")
    if not isinstance(auths, list) or len(auths) != 1:
        return REFUSED_CARDINALITY
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


def decide(entitlement_id: str, config: dict) -> dict:
    registry_problem = _validate_registry(config)
    if registry_problem:
        return _refused(registry_problem)

    backend = config.get("backend")
    if backend == "real":
        if os.environ.get("AAIF_ENTITLEMENT_REAL_PERMIT") != "1":
            return _refused(REFUSED_REAL_NOT_PERMITTED)
        # Real cloudcommerceprocurement rail: no vendor id / ADC material is
        # configured in this environment, so an attempt is honestly BLOCKED.
        url = "{}/v1/providers/{}/entitlements/{}".format(
            _base_url(),
            os.environ.get("GCP_PROVIDER_ID", "UNSET_PROVIDER"),
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
    return {
        "standing": "ALIVE",
        "backend_standing": "SIMULATED",
        "entitlement": record,
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
    if refusal in (REFUSED_UNREACHABLE, REFUSED_PROVIDER_UNREACHABLE):
        return EXIT_UNREACHABLE
    if refusal == REFUSED_REGISTRY_INVALID:
        return EXIT_REGISTRY_INVALID
    return EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())
