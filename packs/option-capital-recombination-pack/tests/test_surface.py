import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SurfaceTest(unittest.TestCase):
    def test_option_machinery_surface_is_broad(self):
        self.assertGreaterEqual(len(list((ROOT / "queries").glob("*.rq"))), 25)
        self.assertGreaterEqual(len(list((ROOT / "gates").glob("*.rq"))), 10)
        self.assertGreaterEqual(len(list((ROOT / "templates").glob("*.tera"))), 4)

if __name__ == "__main__": unittest.main()
