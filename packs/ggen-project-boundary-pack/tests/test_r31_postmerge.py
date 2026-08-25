import hashlib,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class T(unittest.TestCase):
 def test_receipt(self):
  r=json.loads((ROOT/'r31-postmerge-receipt.json').read_text()); raw=json.dumps(r['body'],sort_keys=True,separators=(',',':')); self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),r['sha256']); self.assertTrue(r['body']['contained']); self.assertFalse(r['body']['actuation_performed'])
 def test_ledger(self):
  rows=[json.loads(x) for x in (ROOT/'r31-postmerge-ledger.jsonl').read_text().splitlines()]; self.assertEqual(len(rows),2); self.assertEqual(rows[0]['merge'],'33b882b74e32a5e5db423d0ee3e64fbae40837dd')
 def test_queries(self):
  qs=sorted((ROOT/'queries').glob('r31-postmerge-*.rq')); self.assertEqual(len(qs),3); self.assertEqual(len({q.read_text() for q in qs}),3)
if __name__=='__main__': unittest.main()
