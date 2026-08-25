from pathlib import Path
import unittest

ROOT = Path(__file__).parents[1]

class ContractTest(unittest.TestCase):
    def test_authority_is_select_only(self):
        ontology = (ROOT / 'ontology.ttl').read_text()
        gate = (ROOT / 'gates/20-authority.rq').read_text()
        self.assertIn('cloc:SELECT', ontology)
        self.assertIn('cloc:authority "DO"', gate)
        self.assertIn('cloc:actuationPerformed true', gate)

    def test_failed_or_missing_edges_remain_queryable(self):
        q = (ROOT / 'queries/46-missing-primitive.rq').read_text()
        self.assertIn('cloc:missingPrimitive', q)
        self.assertNotIn('DELETE', q.upper())

if __name__ == '__main__':
    unittest.main()
