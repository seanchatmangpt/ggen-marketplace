import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SurfaceCourt(unittest.TestCase):
    def test_surface_counts(self):
        self.assertEqual(len(list((ROOT / "queries").glob("*.rq"))), 12)
        self.assertEqual(len(list((ROOT / "gates").glob("*.rq"))), 6)
        self.assertEqual(len(list((ROOT / "templates").glob("*.tera"))), 2)

if __name__ == "__main__": unittest.main()
