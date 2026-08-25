import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class PortfolioEpistemicObservabilityContract(unittest.TestCase):
    def test_sensor_count(self):
        self.assertGreaterEqual(len(list((ROOT / 'queries').glob('*.rq'))), 22)

    def test_public_ontology_reuse(self):
        text = (ROOT / 'ontology.ttl').read_text()
        for iri in ('www.w3.org/ns/prov', 'www.w3.org/ns/dcat', 'www.w3.org/ns/dqv', 'www.w3.org/ns/odrl'):
            self.assertIn(iri, text)

    def test_generated_consequences_are_non_actuating(self):
        court = (ROOT / 'templates/court.py.tera').read_text()
        self.assertIn('CONSEQUENTIAL_DO = False', court)
        self.assertIn('assert CONSEQUENTIAL_DO is False', court)
        self.assertNotIn('CONSEQUENTIAl_DO', court)

    def test_marketplace_first_contract(self):
        pack = (ROOT / 'pack.toml').read_text()
        self.assertIn('generated_outputs_are_consequences = true', pack)
        self.assertIn('BRCE_ONLY', pack)

if __name__ == '__main__':
    unittest.main()
