from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RegenerationCourt(unittest.TestCase):
    def test_learning_regeneration_chain_is_explicit(self):
        ontology = (ROOT / 'ontology.ttl').read_text()
        for token in ('ar:AgentRefinement','ar:GeneralizableKnowledge','ar:Regeneration','ar:Qualification'):
            self.assertIn(token, ontology)
        gate = (ROOT / 'gates' / '03-qualified-regeneration.rq').read_text()
        self.assertIn('ar:hasQualification', gate)

if __name__ == '__main__': unittest.main()
