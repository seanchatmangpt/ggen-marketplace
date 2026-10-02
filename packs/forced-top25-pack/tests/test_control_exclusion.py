import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ControlExclusionCourt(unittest.TestCase):
 def test_control_repo_is_explicitly_fenced(self):
  text=(ROOT/'fixtures'/'ftscf-forced-top25-copy.ttl').read_text()
  line=next(x for x in text.splitlines() if 'fta:repo "chatgpt-cloud-elixir"' in x)
  self.assertIn('fts:controlOnly true', line)
 def test_control_fence_conserved_in_merged_population(self):
  text=(ROOT/'targets'/'population.ttl').read_text()
  line=next(x for x in text.splitlines() if 'fta:repo "seanchatmangpt/chatgpt-cloud-elixir"' in x)
  self.assertIn('fts:controlOnly true', line)
if __name__=='__main__': unittest.main()
