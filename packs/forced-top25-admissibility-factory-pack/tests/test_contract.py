import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ForcedTop25FactoryCourt(unittest.TestCase):
 def test_projection_is_non_actuating(self):
  text=(ROOT/'templates'/'consumer-subject.json.tera').read_text()
  self.assertIn('"consequential_do":false', text)
  self.assertIn('"authority":"VERIFY|CONSTRUCT"', text)
 def test_ready_set_legality_precedes_rank(self):
  q=(ROOT/'queries'/'10-ready-set.rq').read_text()
  self.assertIn('COMPATIBLE_READY', q)
  self.assertIn('FILTER NOT EXISTS', q)
  self.assertIn('ORDER BY ?rank', q)
  self.assertIn('?producer_head', q)
  self.assertIn('?compatibility_state', q)
 def test_gap_projection_preserves_unknown_targets(self):
  q=(ROOT/'queries'/'20-admissibility-gaps.rq').read_text()
  self.assertIn('FILTER NOT EXISTS', q)
 def test_generation_contract_connects_ready_set_to_consumer_subjects(self):
  text=(ROOT/'ggen.toml').read_text()
  self.assertIn('queries/10-ready-set.rq', text)
  self.assertIn('templates/consumer-subject.json.tera', text)
  self.assertIn('generated/forced-top25/{{ rank }}.json', text)
  self.assertIn('skip_empty = true', text)
 def test_generated_subject_requires_exact_producer_identity(self):
  ontology=(ROOT/'ontology.ttl').read_text()
  template=(ROOT/'templates'/'consumer-subject.json.tera').read_text()
  self.assertIn('fta:producerHead', ontology)
  self.assertIn('"producer_head":"{{ producer_head }}"', template)
if __name__=='__main__': unittest.main()
