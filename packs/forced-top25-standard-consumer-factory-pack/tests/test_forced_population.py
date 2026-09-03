import pathlib, re, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class ForcedPopulationCourt(unittest.TestCase):
 def test_exact_population_and_order(self):
  text=(ROOT/'forced-top25.ttl').read_text()
  expected=['ex4pm','gymact','autofde-lab','autofde','xaas','chatgpt-cloud-elixir','process-intelligence','ash_r2rml','wasm4pm','pm4wasm','mfact','mfact-command-center','mfw','SREGym','fdegym','revops','chatman-ecosystem','POWL','swarmsh-v2','cargo-cicd','clap-noun-verb','unrdf','dspygen','yawl','a2a-rs']
  found=re.findall(r'fta:repo "([^"]+)"', text)
  self.assertEqual(found, expected)
if __name__=='__main__': unittest.main()
