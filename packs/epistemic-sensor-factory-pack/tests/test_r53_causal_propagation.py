from pathlib import Path
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]


def load_graph():
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    graph.parse(ROOT / "fixtures" / "r53-causal-propagation.ttl", format="turtle")
    return graph


def test_all_r53_sensors_parse_and_execute():
    graph = load_graph()
    sensors = sorted((ROOT / "queries" / "r53").glob("*.rq"))
    assert len(sensors) == 50
    for sensor in sensors:
        list(graph.query(sensor.read_text()))


def test_fixture_exercises_positive_and_negative_causal_surfaces():
    graph = load_graph()
    missing_witness = list(graph.query((ROOT / "queries" / "r53" / "556_missing_causal_witness.rq").read_text()))
    clean_frontier = list(graph.query((ROOT / "queries" / "r53" / "589_clean_causal_frontier.rq").read_text()))
    standing_violations = list(graph.query((ROOT / "queries" / "r53" / "558_standing_transfer_violation.rq").read_text()))
    authority_violations = list(graph.query((ROOT / "queries" / "r53" / "559_authority_transfer_violation.rq").read_text()))
    assert missing_witness
    assert clean_frontier
    assert not standing_violations
    assert not authority_violations


def main():
    test_all_r53_sensors_parse_and_execute()
    test_fixture_exercises_positive_and_negative_causal_surfaces()
    print("R53 causal propagation court: PASS (50/50 sensors)")


if __name__ == "__main__":
    main()
