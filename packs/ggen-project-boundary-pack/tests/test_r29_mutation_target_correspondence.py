import hashlib
import json
import pathlib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
FIXTURE=ROOT/'fixtures'/'r29-mutation-target-correspondence.ttl'
QUERIES=ROOT/'queries'/'r29-mutation-target'
GATE=ROOT/'gates'/'r29-mutation-target-admission.rq'
RECEIPT=ROOT/'receipts'/'r29-mutation-target-correspondence-receipt.json'
LEDGER=ROOT/'innovation-capital-r29-mutation-ledger.jsonl'

class MutationTargetCorrespondence(unittest.TestCase):
 def test_incident_preserves_wrong_and_correct_targets(self):
  text=FIXTURE.read_text()
  self.assertIn('r29m:prNumber 223',text)
  self.assertIn('r29m:prNumber 224',text)
  self.assertIn('18fcc286c3d2fa8082e9e8a6c073fcb64e45e8b0',text)
  self.assertIn('16a8e4b9932033d0ab5a03ef24145197ce23abc9',text)
  self.assertIn('REFUSED[TARGET_CORRESPONDENCE_FAILURE]',text)
  self.assertIn('r29m:wrongTargetMerge false',text)
 def test_sensor_surface_is_noncollapsed(self):
  qs=sorted(QUERIES.glob('*.rq')); self.assertEqual(len(qs),8)
  bodies=[q.read_text() for q in qs]; self.assertEqual(len(set(bodies)),8)
  self.assertTrue(all('SELECT' in b and 'ORDER BY' in b for b in bodies))
 def test_gate_requires_full_identity_tuple(self):
  gate=GATE.read_text()
  for token in ('r29m:repository','r29m:prNumber','r29m:headRef','r29m:headSha','r29m:baseSha'):
   self.assertIn(token,gate)
  self.assertIn('dcterms:status "MATCH"',gate)
 def test_receipt_replays_and_refuses_do(self):
  r=json.loads(RECEIPT.read_text()); body=r['body']
  raw=json.dumps(body,sort_keys=True,separators=(',',':'))
  self.assertEqual(hashlib.sha256(raw.encode()).hexdigest(),r['sha256'])
  self.assertTrue(body['mismatch_detected']); self.assertFalse(body['merge_performed_on_wrong_target'])
  self.assertEqual(body['authority'],'OBSERVE|VERIFY'); self.assertFalse(body['actuation_performed'])
 def test_ledger_turns_incident_into_portfolio_opportunities(self):
  rows=[json.loads(x) for x in LEDGER.read_text().splitlines() if x.strip()]
  self.assertEqual(sum(r.get('kind')=='opportunity' for r in rows),3)
  self.assertTrue(any(r.get('id')=='pr-number-reassignment-detection' for r in rows))

if __name__=='__main__': unittest.main()
