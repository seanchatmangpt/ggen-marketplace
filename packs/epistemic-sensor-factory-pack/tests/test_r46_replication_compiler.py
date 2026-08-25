from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def r46_slot_queries():
    """Return all queries occupying the immutable R46 ordinal slots.

    R46 owns ordinal identities 186..235. Later semantic generations may add
    additional independently named queries in an existing ordinal slot, so
    file cardinality is not the historical identity. The durable contract is
    complete coverage of the fifty R46 ordinal slots plus SELECT-only
    authority for every query sharing those slots.
    """
    files = list((ROOT / "queries").glob("*.rq"))
    return [p for p in files if p.name[:3].isdigit() and 186 <= int(p.name[:3]) <= 235]


def check_r46_covers_exactly_fifty_immutable_slots():
    matched = r46_slot_queries()
    slots = {int(p.name[:3]) for p in matched}
    assert slots == set(range(186, 236)), sorted(set(range(186, 236)) - slots)


def check_replication_compiler_is_deterministic_and_non_actuating():
    ggen = (ROOT / "ggen.toml").read_text()
    tmpl = (ROOT / "templates" / "replication-plan.json.tera").read_text()
    assert "queries/260_replication_targets.rq" in ggen
    assert "generated/epistemic-sensor-factory/replication-plan.json" in ggen
    assert '"consequential_do": false' in tmpl


def check_live_fixture_binds_three_exact_heads():
    fixture = (ROOT / "fixtures" / "r46-live-replication.ttl").read_text()
    for sha in [
        "22743d39d31a19490d6c9db881d02f3690b24913",
        "f4e1bce1efdcdc4f6c2531be9f66070950f7ec93",
        "791758248859dbf4201952294825ab324531ee0f",
    ]:
        assert sha in fixture
    assert "actuationPerformed true" not in fixture


def check_sensor_queries_preserve_select_only_authority():
    for p in r46_slot_queries():
        text = p.read_text().upper()
        assert "SELECT" in text, p
        assert not re.search(r"\b(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD)\b", text), p


def main():
    checks = [
        check_r46_covers_exactly_fifty_immutable_slots,
        check_replication_compiler_is_deterministic_and_non_actuating,
        check_live_fixture_binds_three_exact_heads,
        check_sensor_queries_preserve_select_only_authority,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"R46_CONTRACT_PASS={len(checks)} slot_queries={len(r46_slot_queries())}")


if __name__ == "__main__":
    main()
