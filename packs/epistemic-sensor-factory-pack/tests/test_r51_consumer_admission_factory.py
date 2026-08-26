#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "queries" / "r51-consumer-admission.manifest"


def r51_queries():
    names = [line.strip() for line in MANIFEST.read_text().splitlines() if line.strip()]
    assert len(names) == 50, len(names)
    assert len(set(names)) == 50, "duplicate semantic query identity"
    queries = [ROOT / "queries" / name for name in names]
    assert all(path.is_file() for path in queries)
    return queries


def check_exactly_fifty_admission_sensors():
    matched = r51_queries()
    assert len(matched) == 50, len(matched)
    assert [int(p.name[:3]) for p in matched] == list(range(401, 451))


def check_select_only_authority():
    for path in r51_queries():
        text = path.read_text().upper()
        assert "SELECT" in text, path
        assert not re.search(r"\b(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD)\b", text), path


def check_public_semantic_admission_model():
    ontology = (ROOT / "ontology.ttl").read_text()
    for term in ["ConsumerAdmissionCandidate", "ConsumerAdmissionDecision", "ConsumerAdapterPlan", "ConsumerAdmissionCompiler"]:
        assert term in ontology
    for prefix in ["http://www.w3.org/ns/prov#", "http://www.w3.org/ns/dqv#", "http://www.w3.org/ns/dcat#", "http://www.w3.org/ns/odrl/2/"]:
        assert prefix in ontology


def check_grounded_frontier_preserves_standing():
    fixture = (ROOT / "fixtures" / "r51-consumer-admission-frontier.ttl").read_text()
    for sha in [
        "3604bd0bb0834477fca02453ad787009bffb06dd",
        "a2795bcb1f0c49cbaaac91749edf7ef7c68d3a23",
        "5371a28719881c2466927874958e4e1ef3f8ed59",
    ]:
        assert sha in fixture
    assert 'admissionStanding "ADMITTED"' in fixture
    assert 'admissionStanding "PARTIAL_ALIVE"' in fixture
    assert "noAmbientDo false" not in fixture


def main():
    checks = [
        check_exactly_fifty_admission_sensors,
        check_select_only_authority,
        check_public_semantic_admission_model,
        check_grounded_frontier_preserves_standing,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"R51_CONTRACT_PASS={len(checks)}")


if __name__ == "__main__":
    main()
