import pathlib, tomllib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ForcedTop25FactoryCourt(unittest.TestCase):
 def test_pack_manifest_is_ggen_schema_minimal(self):
  manifest=tomllib.loads((ROOT/'pack.toml').read_text())
  self.assertEqual(set(manifest), {'pack'})
  self.assertEqual(manifest['pack']['name'], 'forced-top25-pack')
 def test_projection_is_non_actuating(self):
  text=(ROOT/'templates'/'ftfac_consumer-subject.json.tmpl').read_text()
  self.assertIn('"consequential_do":false', text)
  self.assertIn('"authority":"VERIFY|CONSTRUCT"', text)
 def test_ready_set_legality_precedes_rank(self):
  q=(ROOT/'queries'/'ftfac_10-ready-set.rq').read_text()
  self.assertIn('COMPATIBLE_READY', q)
  self.assertIn('FILTER NOT EXISTS', q)
  self.assertIn('ORDER BY ?rank', q)
  self.assertIn('?producer_head', q)
  self.assertIn('?compatibility_state', q)
 def test_gap_projection_preserves_unknown_targets(self):
  q=(ROOT/'queries'/'ftfac_20-admissibility-gaps.rq').read_text()
  self.assertIn('FILTER NOT EXISTS', q)
 def test_generation_contract_connects_ready_set_to_consumer_subjects(self):
  text=(ROOT/'ggen.toml').read_text()
  self.assertIn('queries/ftfac_10-ready-set.rq', text)
  self.assertIn('templates/ftfac_consumer-subject.json.tmpl', text)
