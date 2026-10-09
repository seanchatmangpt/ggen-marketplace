#!/usr/bin/env python3
"""Fleet generator-of-record for v1.0 A2A member-contract agent cards.

One generator identity for the fleet: parses each owning repo's real public
surface (never hand-transcribed) and emits its card(s) deterministically
(double run byte-identical, sorted keys, no timestamps). Generated cards are
never hand-edited; violations are fixed in this generator and cards are
regenerated.

Currently serves (validator registry: scripts/validate_agent_cards.py):

    wasm4pm — SA2A actuator card, emitted to <repo>/.well-known/agent-card.json

Fail-closed: refuses if a published skill loses its lib.rs export, or if the
emitted card would violate the member contract enforced by
scripts/validate_agent_cards.py.

Usage:

    python3 scripts/gen_agent_cards.py            # emit all served cards
    python3 scripts/gen_agent_cards.py --check    # exit 1 on drift, no write
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

WASM4PM = Path("/Users/sac/wasm4pm")

LIB_RS = WASM4PM / "crates/wasm4pm-sa2a-actuator/src/lib.rs"
WORKSPACE_CARGO = WASM4PM / "Cargo.toml"
OUT = WASM4PM / ".well-known/agent-card.json"

NAME = "wasm4pm SA2A Actuator"

DESCRIPTION = (
    "Independent SA2A actuator. Authority is external: no effect is executed "
    "without an ActuationCertificate carrying an external authority signature "
    "quorum across independent trust domains, verified by the SecurityVerifier "
    "before the Effector runs. Resource allocation is powerless input admitted "
    "before the durable actuator claim; allocation identity is bound into the "
    "same durable record as the effect claim."
)

# Each published skill, keyed to the lib.rs re-exports (and the wire.rs types
# re-exported there) it must keep to stay publishable.
SKILLS = [
    {
        "id": "wasm4pm.actuator.execute",
        "name": "Execute an admitted effect",
        "description": (
            "Actuator::execute — executes a PreparedEffect against an Effector "
            "only after SecurityVerifier::verify accepts an ActuationCertificate "
            "(external authority signature quorum, independent trust domains) "
            "and the EffectLedger records the claim. Refuses with typed "
            "ActuatorRefusal otherwise."
        ),
        "tags": ["actuator", "execute", "authority", "certificate"],
        "requires": ["Actuator", "ActuationReceipt", "ActuatorContext"],
    },
    {
        "id": "wasm4pm.actuator.effect.digest",
        "name": "Digest a prepared effect",
        "description": (
            "PreparedEffect::digest — canonical-JSON sha256 digest of a "
            "version-1 PreparedEffect (principal, capability, subject, payload). "
            "Refuses invalid effects via ActuatorRefusal::InvalidEffect."
        ),
        "tags": ["effect", "digest", "canonicalization"],
        "requires": ["PreparedEffect"],
    },
    {
        "id": "wasm4pm.actuator.certificate.signing_message",
        "name": "Certificate signing message",
        "description": (
            "ActuationCertificate::signing_message — constructs the canonical "
            "'SA2A-C2-ACTUATION-CERTIFICATE-V1' signing message for an "
            "ActuationCertificate (effect digest, principal, policy/revocation "
            "epochs, generation, nonce, validity window, audience, threshold). "
            "Refuses invalid certificates via ActuatorRefusal::InvalidCertificate."
        ),
        "tags": ["certificate", "signing", "quorum"],
        "requires": ["ActuationCertificate", "CertificateSignature"],
    },
    {
        "id": "wasm4pm.actuator.verify",
        "name": "Verify an actuation certificate",
        "description": (
            "SecurityVerifier::verify — verifies an ActuationCertificate's "
            "signature quorum against the KeyRegistry (SignatureAlgorithm, "
            "KeyState including revocation epochs)."
        ),
        "tags": ["verify", "signatures", "key-registry"],
        "requires": ["SecurityVerifier", "KeyRegistry", "SignatureAlgorithm", "KeyState"],
    },
    {
        "id": "wasm4pm.actuator.resource.admit",
        "name": "Admit a resource allocation",
        "description": (
            "ResourceAdmission::admit / admit_children — admits a powerless "
            "ResourceBudget/ResourceEnvelope allocation before any effect, "
            "producing a ResourceReceipt and ResourceOcelEvent bound into the "
            "same durable record as the effect claim; supports ResourceRecovery."
        ),
        "tags": ["resource", "admission", "receipt"],
        "requires": [
            "ResourceAdmission",
            "ResourceBudget",
            "ResourceEnvelope",
            "ResourceReceipt",
            "ResourceOcelEvent",
            "ResourceRecovery",
        ],
    },
    {
        "id": "wasm4pm.actuator.ledger",
        "name": "Durable effect ledger",
        "description": (
            "EffectLedger / FileEffectLedger — durable EffectClaimRecord storage "
            "binding allocation identity and effect claims (LedgerState "
            "transitions)."
        ),
        "tags": ["ledger", "durable", "claims"],
        "requires": ["EffectLedger", "FileEffectLedger", "EffectClaimRecord", "LedgerState"],
    },
]

AUTHORITY_LAW = (
    "external authority signature quorum across independent trust domains "
    "required before any effect"
)


def parse_exports() -> set[str]:
    """Collect re-exported names from lib.rs pub use statements (incl. the
    wire.rs types re-exported there). Fail-closed surface = lib.rs exports."""
    text = LIB_RS.read_text(encoding="utf-8")
    names = set()
    for m in re.finditer(r"pub use\s+([\w:]+)::\{([^}]*)\}", text):
        for item in m.group(2).split(","):
            item = item.strip()
            if not item:
                continue
            name = item.split(" as ")[-1].strip()
            if name:
                names.add(name)
    for m in re.finditer(r"^pub use\s+[\w:]+::(\w+)\s*;", text, re.MULTILINE):
        names.add(m.group(1))
    return names


def parse_version() -> str:
    text = WORKSPACE_CARGO.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    if not m:
        sys.exit("refusing: no workspace version in Cargo.toml")
    return m.group(1)


def format_card(card):
    """Deterministic emitter: 2-space indent, short scalar arrays inline."""
    def enc(value, indent):
        pad = " " * indent
        if isinstance(value, dict):
            if not value:
                return "{}"
            items = [
                "{p}  {k}: {v}".format(
                    p=pad,
                    k=json.dumps(k, ensure_ascii=False),
                    v=enc(v, indent + 2),
                )
                for k, v in value.items()
            ]
            return "{\n" + ",\n".join(items) + "\n" + pad + "}"
        if isinstance(value, list):
            if not value:
                return "[]"
            if all(isinstance(v, (str, int, float, bool)) for v in value):
                flat = [json.dumps(v, ensure_ascii=False) for v in value]
                return "[" + ", ".join(flat) + "]"
            items = ["{p}  {v}".format(p=pad, v=enc(v, indent + 2)) for v in value]
            return "[\n" + ",\n".join(items) + "\n" + pad + "]"
        return json.dumps(value, ensure_ascii=False)

    return enc(card, 0)


def check_contract(card) -> list:
    """Mirror the member-contract checks from validate_agent_cards.py so a
    violating card is refused at generation time, not just at validation."""
    errs = []
    if not card.get("name"):
        errs.append("missing name")
    if not card.get("description"):
        errs.append("missing description")
    if not card.get("version"):
        errs.append("missing version")
    ifaces = card.get("supportedInterfaces") or []
    if not ifaces or not (ifaces[0] or {}).get("protocolVersion"):
        errs.append("missing supportedInterfaces[0].protocolVersion")
    if "url" in card:
        errs.append("forbidden top-level field: url")
    if "preferredTransport" in card:
        errs.append("forbidden top-level field: preferredTransport")
    if not card.get("skills"):
        errs.append("missing/empty skills")
    for s in card.get("skills", []):
        sid = s.get("id", "")
        segs = sid.split(".")
        if len(segs) < 2 or any(not seg for seg in segs):
            errs.append("skill id '%s' not <tool>.<cluster>.<verb>-ish" % sid)
    if "authorit" not in card.get("description", "").lower():
        errs.append("authority statement missing from description")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="exit 1 on drift, no write")
    args = ap.parse_args()

    exports = parse_exports()
    version = parse_version()

    missing = []
    for skill in SKILLS:
        for req in skill["requires"]:
            if req not in exports:
                missing.append((skill["id"], req))
    if missing:
        for skill_id, req in missing:
            print("REFUSED: skill %s lost lib.rs export: %s" % (skill_id, req),
                  file=sys.stderr)
        return 1

    skills_out = [
        {k: s[k] for k in ("id", "name", "description", "tags")}
        for s in SKILLS
    ]
    card = {
        "protocolVersion": "1.0",
        "name": NAME,
        "description": DESCRIPTION,
        "supportedInterfaces": [
            {"protocolVersion": "1.0", "protocolBinding": "SA2A"}
        ],
        "version": version,
        "capabilities": {"streaming": False},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": skills_out,
    }

    errs = check_contract(card)
    if errs:
        for e in errs:
            print("REFUSED: %s" % e, file=sys.stderr)
        return 1

    rendered = format_card(card) + "\n"

    if args.check:
        if OUT.exists() and OUT.read_text(encoding="utf-8") == rendered:
            print("OK: %s up to date (v%s)" % (OUT, version))
            return 0
        print("DRIFT: %s differs from generator output (v%s)" % (OUT, version))
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    print("wrote %s (v%s, %d skills)" % (OUT, version, len(skills_out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
