import pathlib
import unittest

from rdflib import Graph


PACK = pathlib.Path(__file__).resolve().parents[1]


class HumanValueCourtTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse(PACK / "ontology.ttl", format="turtle")
        cls.graph.parse(PACK / "fixtures/law.ttl", format="turtle")

    def test_all_ask_courts_admit(self):
        courts = sorted((PACK / "courts").glob("*.rq"))
        self.assertGreaterEqual(len(courts), 20)
        failures = []

        for court in courts:
            result = self.graph.query(court.read_text(encoding="utf-8"))
            if not bool(result.askAnswer):
                failures.append(court.name)

        self.assertEqual([], failures, f"refused courts: {failures}")

    def test_static_fixture_never_claims_value_alive(self):
        standing = "https://ggen.dev/ontology/human-value-runtime#standing"
        for _, _, value in self.graph.triples((None, self.graph.namespace_manager.compute_qname(standing) if False else None, None)):
            self.assertNotEqual("VALUE_ALIVE", str(value))

        self.assertFalse(
            any(str(obj) == "VALUE_ALIVE" for _, pred, obj in self.graph if str(pred) == standing),
            "VALUE_ALIVE may only be emitted by the runtime Playwright receipt",
        )


if __name__ == "__main__":
    unittest.main()
