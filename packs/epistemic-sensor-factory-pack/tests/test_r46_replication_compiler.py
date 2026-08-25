from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def check_r46_has_exactly_fifty_new_sensors():
    files = list((ROOT / "queries").glob("*.rq"))
    matched = [p for p in files if p.name[:3].isdigit() and 186 <= int(p.name[:3]) <= 235]
    assert len(matched) == 50, len(matched)
    assert len({p.name[:3] for p in matched}) == 50


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
    for p in (ROOT / "queries").glob("*.rq"):
        if p.name[:3].isdigit() and 186 <= int(p.name[:3]) <= 235:
            text = p.read_text().upper()
            assert "SELECT" in text, p
            assert not re.search(r"\b(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|MOVE|COPY|ADD)\b", text), p


def main():
    checks = [
        check_r46_has_exactly_fifty_new_sensors,
        check_replication_compiler_is_deterministic_and_non_actuating,
        check_live_fixture_binds_three_exact_heads,
        check_sensor_queries_preserve_select_only_authority,
    ]
    for check in checks:
        check()
        print(f"PASS {check.__name__}")
    print(f"R46_CONTRACT_PASS={len(checks)}")


if __name__ == "__main__":
    main()
