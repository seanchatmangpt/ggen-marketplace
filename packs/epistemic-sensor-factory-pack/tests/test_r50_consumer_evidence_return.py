#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


# R48 consumer-court queries share the 350-359 prefix band (added by the
# qualify(r48) series). They are not R50 sensors; the R50 matcher excludes
# exactly this closed set and refuses if any member disappears or a new
# unlisted collision appears (the 50-count and 350..399 order assertions).
R48_PREFIX_COLLISIONS = frozenset(
    {
        "350_tensorflow_consumer_identity.rq",
        "351_stale_consumer_falsifier.rq",
        "352_writable_consumer_frontier.rq",
        "353_readonly_consumer_falsifier.rq",
        "354_consumer_default_branch.rq",
        "355_consumer_exact_head.rq",
        "356_consumer_age_falsifier.rq",
        "357_consumer_pack_compatibility.rq",
        "358_missing_pack_compatibility_falsifier.rq",
        "359_replication_authority_fence.rq",
    }
)


def r50_queries():
    present = {p.name for p in (ROOT / "queries").glob("*.rq")}
    missing = sorted(R48_PREFIX_COLLISIONS - present)
    assert not missing, f"REFUSED:R48_COLLISION_SET_DRIFT missing={missing}"
    matched = []
    for p in (ROOT / "queries").glob("*.rq"):
        prefix = p.name[:3]
        if p.name in R48_PREFIX_COLLISIONS:
            continue
        if prefix.isdigit() and 350 <= int(prefix) <= 399:
            matched.append(p)
    return sorted(matched)


def check_exactly_fifty_return_sensors():
    matched = r50_queries()
    assert len(matched) == 50, len(matched)
    assert [int(p.name[:3]) for p in matched] == list(range(350, 400))


def check_select_only_query_authority():
    for p in r50_queries():
        text = p.read_text().upper()
        assert "SELECT" in text, p
        assert not re.search(
            r"\b(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD)\b", text
        ), p


def check_fixture_preserves_independent_standing():
    fixture = (ROOT / "fixtures" / "r50-consumer-evidence-return.ttl").read_text()
    assert "a5be7f0c88c411cb023eb7960a4cb1b3e521f474" in fixture
    assert 'consumerStandingValue "ALIVE"' in fixture
    assert 'consumerStandingValue "PARTIAL_ALIVE"' in fixture
    assert "4715c562c3dd2c073c0ca119edbc013647978cae" in fixture
    assert "actuationPerformed true" not in fixture


def check_ggen_projection_is_canonical():
    ggen = (ROOT / "ggen.toml").read_text()
    template = (ROOT / "templates" / "evidence-return-protocol.json.tera").read_text()
    assert "queries/400_evidence_return_protocol.rq" in ggen
    assert "templates/evidence-return-protocol.json.tera" in ggen
    assert "generated/epistemic-sensor-factory/evidence-return-protocol.json" in ggen
    assert '"consequential_do": false' in template
    assert "never transfers consumer execution authority" in template


def check_public_semantic_correspondence():
    ontology = (ROOT / "ontology.ttl").read_text()
    for prefix in [
        "http://www.w3.org/ns/prov#",
        "http://www.w3.org/ns/dqv#",
        "http://www.w3.org/ns/dcat#",
        "http://purl.org/dc/terms/",
        "http://www.w3.org/ns/odrl/2/",
    ]:
        assert prefix in ontology
    for term in [
        "ConsumerReceiptAssertion",
        "EvidenceReturn",
        "ProducerAssimilation",
        "ReturnedConsumerStanding",
    ]:
        assert term in ontology


def main():
    checks = [
        check_exactly_fifty_return_sensors,
        check_select_only_query_authority,
        check_fixture_preserves_independent_standing,
        check_ggen_projection_is_canonical,
        check_public_semantic_correspondence,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"R50_CONTRACT_PASS={len(checks)}")


if __name__ == "__main__":
    main()
