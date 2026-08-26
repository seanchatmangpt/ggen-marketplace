import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TemplateSurfaceCourt(unittest.TestCase):
 def test_projection_families_exist(self): self.assertGreaterEqual(len(list((ROOT/'templates').glob('*.tera'))),7)
if __name__=='__main__': unittest.main()
