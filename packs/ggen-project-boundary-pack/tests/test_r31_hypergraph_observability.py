import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class R31Court(unittest.TestCase):
 def test_surface(self):
  qs=sorted((ROOT/'queries').glob('r31-*.rq')); self.assertGreaterEqual(len(qs),36); self.assertEqual(len({p.read_text() for p in qs}),len(qs))
 def test_public_semantics(self):
  t=(ROOT/'r31-hypergraph-observability-realization.ttl').read_text()
  for iri in ('prov#','dqv#','dc/terms','skos/core#'): self.assertIn(iri,t)
 def test_fixture_pressure(self):
  f=(ROOT/'fixtures/r31-hypergraph-observability-realization.ttl').read_text(); self.assertIn('candidate-stale',f); self.assertIn('current false',f); self.assertIn('overlapRate 0.80',f)
 def test_receipt(self):
  r=json.loads((ROOT/'r31-hypergraph-observability-realization-receipt.json').read_text()); raw=json.dumps(r['body'],sort_keys=True,separators=(',',':')); self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),r['sha256']); self.assertFalse(r['body']['actuation_performed'])
 def test_ledger(self):
  rows=[json.loads(x) for x in (ROOT/'r31-hypergraph-observability-ledger.jsonl').read_text().splitlines()]; self.assertGreaterEqual(len(rows),4)
if __name__=='__main__': unittest.main()
