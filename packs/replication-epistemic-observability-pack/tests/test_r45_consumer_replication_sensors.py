from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUERIES = ROOT / "queries"


def test_r45_sensor_family_is_complete_and_nonvacuous():
    sensors = [QUERIES / f"{n:03d}_{name}.rq" for n, name in []]
    actual = sorted(p for p in QUERIES.glob("*.rq") if 86 <= int(p.name.split("_")[0]) <= 135)
    assert len(actual) == 50
    for path in actual:
        text = path.read_text()
        assert "SELECT" in text
        assert "https://ggen.dev/ontology/replication-epistemic#" in text
        assert len(text.strip()) > 100


def test_r45_sensor_family_has_no_ambient_actuation():
    for path in QUERIES.glob("*.rq"):
        prefix = int(path.name.split("_")[0])
        if 86 <= prefix <= 135:
            text = path.read_text().lower()
            assert "insert " not in text
            assert "delete " not in text
            assert "load " not in text
            assert "clear " not in text
