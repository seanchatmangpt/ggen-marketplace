#!/usr/bin/env python3
"""Deterministic contract court for gym-named ggen Marketplace packs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import tomllib

SCHEMA = "ggen.marketplace.gym-pack-contract/v1"
VERSION = "26.9.1"
EXPECTED = {
    "autofde-gymact-certification-pack": (
        "pack.toml",
        "ontology.ttl",
        "gates/010_evidence_integrity.rq",
        "qualification/consumer.ttl",
    ),
    "chatgptgym-gymact-bridge-pack": (
        "pack.toml",
        "ontology.ttl",
        "gates/010_execution_boundary.rq",
    ),
    "lifegym-world-pack": (
        "pack.toml",
        "ontology.ttl",
        "gates/010_execution_boundary.rq",
    ),
    "ww3gym-planning-pack": (
        "pack.toml",
        "gates/010_safe_scope.rq",
    ),
}
PACK_VERSIONS = {
    "autofde-gymact-certification-pack": "1.0.0",
    "chatgptgym-gymact-bridge-pack": VERSION,
    "lifegym-world-pack": VERSION,
    "ww3gym-planning-pack": VERSION,
}


class Refusal(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def refuse(condition: bool, code: str, detail: str) -> None:
    if condition:
        raise Refusal(code, detail)


def read(path: Path) -> str:
    refuse(not path.is_file(), "MISSING_SOURCE", str(path))
    return path.read_text(encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def pack_meta(path: Path) -> dict:
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    refuse("pack" not in data, "PACK_TABLE_MISSING", str(path))
    return data["pack"]


def require_gate_contract(text: str, pack: str) -> None:
    refuse(not text.startswith("# MESSAGE:"), "GATE_MESSAGE_MISSING", pack)
    refuse("SELECT ?subject ?problem WHERE" not in text, "GATE_SELECT_MISSING", pack)
    refuse("ORDER BY ?subject ?problem" not in text, "GATE_ORDER_MISSING", pack)


def validate(root: Path) -> tuple[list[dict], list[str]]:
    packs_root = root / "packs"
    refuse(not packs_root.is_dir(), "PACK_ROOT_MISSING", str(packs_root))

    discovered = sorted(p.name for p in packs_root.iterdir() if p.is_dir() and "gym" in p.name.lower())
    expected = sorted(EXPECTED)
    refuse(discovered != expected, "GYM_PACK_SET_DRIFT", f"expected={expected} observed={discovered}")

    checks: list[str] = []
    pack_receipts: list[dict] = []

    for name in expected:
        base = packs_root / name
        meta = pack_meta(base / "pack.toml")
        expected_version = PACK_VERSIONS[name]
        refuse(meta.get("name") != name, "PACK_IDENTITY_DRIFT", name)
        refuse(meta.get("version") != expected_version, "PACK_VERSION_DRIFT", f"{name}:{meta.get('version')} expected={expected_version}")
        refuse((base / "generated").exists(), "GENERATED_SOURCE_REFUSED", name)
        checks.extend([f"{name}:identity", f"{name}:version", f"{name}:no-generated-source"])

        files = []
        for relative in EXPECTED[name]:
            path = base / relative
            read(path)
            files.append({"path": str(path.relative_to(root)), "sha256": digest(path)})
        pack_receipts.append({"name": name, "version": expected_version, "files": files})

    autofde = packs_root / "autofde-gymact-certification-pack"
    autofde_ontology = read(autofde / "ontology.ttl")
    autofde_gate = read(autofde / "gates/010_evidence_integrity.rq")
    autofde_fixture = read(autofde / "qualification/consumer.ttl")
    refuse(not autofde_gate.startswith("# MESSAGE:"), "AUTOFDE_CERT_GATE_MESSAGE_MISSING", autofde.name)
    refuse("SELECT ?subject ?violation WHERE" not in autofde_gate, "AUTOFDE_CERT_GATE_SELECT_MISSING", autofde.name)
    refuse("ORDER BY ?subject ?violation" not in autofde_gate, "AUTOFDE_CERT_GATE_ORDER_MISSING", autofde.name)
    for term in (
        "afl:CheckSeverity",
        "afl:CertificationCheck",
        "afl:CertificationCheckResult",
        "afl:CertificationManifest",
        "afl:EvaluateArgShape",
        "afl:OracleContractFinding",
    ):
        refuse(term not in autofde_ontology, "AUTOFDE_CERT_ONTOLOGY_TERM_MISSING", term)
    for concept in ("afl:STRUCTURAL", "afl:BEHAVIORAL", "afl:EVIDENCE", "afl:STRUCTURAL_ONLY", "afl:SMOKE_TESTED"):
        refuse(concept not in autofde_ontology, "AUTOFDE_CERT_CONCEPT_MISSING", concept)
    for token in (
        "EVIDENCE-severity resultPassed=true with no resultEvidenceRef",
        "resultCheckRef does not match any admitted CertificationCheck",
    ):
        refuse(token not in autofde_gate, "AUTOFDE_CERT_REFUSAL_MISSING", token)
    for fixture_token in (
        'afl:checkSeverityRef afl:STRUCTURAL',
        'afl:checkSeverityRef afl:BEHAVIORAL',
        'afl:checkSeverityRef afl:EVIDENCE',
        'afl:manifestConformanceLevelRef afl:SMOKE_TESTED',
        'afl:resultEvidenceRef "blake3:',
    ):
        refuse(fixture_token not in autofde_fixture, "AUTOFDE_CERT_FIXTURE_MISSING", fixture_token)
    checks.extend([
        "autofde-cert:typed-contract",
        "autofde-cert:severity-concepts",
        "autofde-cert:evidence-refusal",
        "autofde-cert:admitted-check-refusal",
        "autofde-cert:qualification-fixture",
    ])

    chat = packs_root / "chatgptgym-gymact-bridge-pack"
    chat_ontology = read(chat / "ontology.ttl")
    chat_gate = read(chat / "gates/010_execution_boundary.rq")
    require_gate_contract(chat_gate, chat.name)
    refuse(chat_ontology.count("a sosa:Procedure") != 4, "CHATGPTGYM_PROCEDURE_DRIFT", "expected=4")
    refuse(chat_ontology.count("<urn:gymact:consequence:read>") != 2, "CHATGPTGYM_READ_DRIFT", "expected=2")
    refuse(chat_ontology.count("<urn:gymact:consequence:do>") != 2, "CHATGPTGYM_DO_DRIFT", "expected=2")
    for title in ("simulate-capability", "reset-simulation"):
        refuse(f'dct:title "{title}"' not in chat_ontology, "CHATGPTGYM_SIMULATION_INTENT_MISSING", title)
    for token in ("ambient-do-authority-refused", "non-observational-read-refused"):
        refuse(token not in chat_gate, "CHATGPTGYM_REFUSAL_MISSING", token)
    checks.extend(["chatgptgym:4-procedures", "chatgptgym:2-read", "chatgptgym:2-bounded-do", "chatgptgym:ambient-do-refusal"])

    life = packs_root / "lifegym-world-pack"
    life_ontology = read(life / "ontology.ttl")
    life_gate = read(life / "gates/010_execution_boundary.rq")
    require_gate_contract(life_gate, life.name)
    refuse('dct:identifier "lifegym-v26.9.1"' not in life_ontology, "LIFEGYM_PROFILE_ID_DRIFT", VERSION)
    refuse(life_ontology.count("urn:lifegym:domain:") != 10, "LIFEGYM_DOMAIN_DRIFT", "expected=10")
    refuse(life_ontology.count("urn:lifegym:service:") != 22, "LIFEGYM_SERVICE_DRIFT", "expected=22")
    refuse("Consequential DO requires external GymAct authority" not in life_ontology, "LIFEGYM_AUTHORITY_POLICY_MISSING", "ontology")
    for evidence in ("tasks", "procedures", "events", "checks"):
        refuse(f'dct:identifier "{evidence}"' not in life_ontology, "LIFEGYM_EVIDENCE_MISSING", evidence)
    for token in ("missing-external-gymact-authority-policy", "service-must-not-carry-authority-policy"):
        refuse(token not in life_gate, "LIFEGYM_REFUSAL_MISSING", token)
    checks.extend(["lifegym:profile-version", "lifegym:10-domains", "lifegym:22-services", "lifegym:external-authority", "lifegym:benchmark-evidence"])

    ww3 = packs_root / "ww3gym-planning-pack"
    ww3_gate = read(ww3 / "gates/010_safe_scope.rq")
    require_gate_contract(ww3_gate, ww3.name)
    for token in (
        "simulation/evaluation-only",
        "operational-or-live-actuation-semantics-refused",
        "runtime-actuation-relation-refused",
        "production.?deployment",
        "real.?world.?actuation",
        "profile-missing-public-source",
    ):
        refuse(token not in ww3_gate, "WW3GYM_SAFETY_FENCE_MISSING", token)
    ww3_description = str(pack_meta(ww3 / "pack.toml").get("description", ""))
    refuse("simulation/evaluation-only" not in ww3_description, "WW3GYM_SCOPE_DESCRIPTION_DRIFT", ww3.name)
    checks.extend(["ww3gym:simulation-only", "ww3gym:operational-refusal", "ww3gym:runtime-actuation-refusal", "ww3gym:public-source"])

    return pack_receipts, sorted(checks)


def manufacture_receipt(root: Path, subject_sha: str) -> dict:
    packs, checks = validate(root)
    standing = "ALIVE" if re.fullmatch(r"[0-9a-f]{40}", subject_sha) else "PARTIAL_ALIVE"
    body = {
        "schema": SCHEMA,
        "subject": {"repository": "seanchatmangpt/ggen-marketplace", "sha": subject_sha},
        "scope": "gym-pack-source-contract",
        "standing": standing,
        "authority": "NO_RUNTIME_ACTUATION_AUTHORITY",
        "packs": packs,
        "checks": checks,
    }
    body["receipt_sha256"] = hashlib.sha256(canonical(body)).hexdigest()
    return body


def verify_receipt_digest(receipt: dict) -> None:
    supplied = receipt.get("receipt_sha256")
    core = dict(receipt)
    core.pop("receipt_sha256", None)
    expected = hashlib.sha256(canonical(core)).hexdigest()
    refuse(supplied != expected, "RECEIPT_DIGEST_MISMATCH", f"expected={expected} observed={supplied}")


def self_test(root: Path, subject_sha: str) -> None:
    mutations = (
        (
            "packs/autofde-gymact-certification-pack/gates/010_evidence_integrity.rq",
            "EVIDENCE-severity resultPassed=true with no resultEvidenceRef",
            "evidence-integrity-check-removed",
        ),
        ("packs/chatgptgym-gymact-bridge-pack/gates/010_execution_boundary.rq", "ambient-do-authority-refused", "ambient-do-authority-removed"),
        ("packs/lifegym-world-pack/ontology.ttl", "lifegym-v26.9.1", "lifegym-v26.8.12"),
        ("packs/ww3gym-planning-pack/gates/010_safe_scope.rq", "production.?deployment", "production-deployment-check-removed"),
    )
    survived = []
    with tempfile.TemporaryDirectory(prefix="gym-pack-falsifier-") as temp:
        trial = Path(temp)
        shutil.copytree(root / "packs", trial / "packs")
        for relative, needle, replacement in mutations:
            path = trial / relative
            original = path.read_text(encoding="utf-8")
            refuse(needle not in original, "SELF_TEST_FIXTURE_MISSING", relative)
            path.write_text(original.replace(needle, replacement, 1), encoding="utf-8")
            try:
                manufacture_receipt(trial, subject_sha)
            except Refusal:
                pass
            else:
                survived.append(relative)
            path.write_text(original, encoding="utf-8")
    refuse(bool(survived), "MUTATION_SURVIVED", ",".join(survived))
    print(f"ALIVE:MUTATION_FALSIFIERS {len(mutations)}/{len(mutations)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--replay", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--subject-sha", default=os.environ.get("GITHUB_SHA", "UNBOUND"))
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        receipt = manufacture_receipt(root, args.subject_sha)
        if args.replay:
            observed = json.loads(args.replay.read_text(encoding="utf-8"))
            verify_receipt_digest(observed)
            refuse(observed != receipt, "REPLAY_DRIFT", str(args.replay))
            print("ALIVE:REPLAY")
        if args.receipt:
            args.receipt.parent.mkdir(parents=True, exist_ok=True)
            args.receipt.write_bytes(canonical(receipt))
        if args.self_test:
            self_test(root, args.subject_sha)
        print(f"ALIVE:GYM_PACK_CONTRACT packs={len(EXPECTED)} checks={len(receipt['checks'])} standing={receipt['standing']}")
        return 0
    except (OSError, tomllib.TOMLDecodeError, json.JSONDecodeError) as exc:
        print(f"REFUSED:SOURCE_PARSE:{exc}", file=sys.stderr)
        return 3
    except Refusal as exc:
        print(f"REFUSED:{exc.code}:{exc.detail}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
