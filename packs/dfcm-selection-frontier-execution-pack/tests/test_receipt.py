import importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
receipt=load('receipt'); replay=load('replay')
class Court(unittest.TestCase):
    def test_replay(self):
        r=receipt.canonical_receipt('o/r@'+'a'*40,['x'],['y'],'b'*40)
        self.assertEqual(replay.replay(r),'REPLAY_MATCH')
        r['selected']=['tampered']
        with self.assertRaisesRegex(ValueError,'TAMPER'): replay.replay(r)
if __name__=='__main__': unittest.main()
