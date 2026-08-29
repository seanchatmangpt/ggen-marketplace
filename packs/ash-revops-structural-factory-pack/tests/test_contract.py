from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ContractCourt(unittest.TestCase):
    def test_public_semantics_and_dual_revenue(self):
        text = (ROOT / 'ontology.ttl').read_text()
        for token in ('http://www.w3.org/ns/prov#','http://www.w3.org/2004/02/skos/core#','http://www.w3.org/ns/dqv#'):
            self.assertIn(token, text)
        self.assertIn('ar:RevenueFromCustomer', text)
        self.assertIn('ar:RevenueForCustomer', text)
        self.assertNotEqual(text.find('ar:RevenueFromCustomer'), text.find('ar:RevenueForCustomer'))

if __name__ == '__main__': unittest.main()
