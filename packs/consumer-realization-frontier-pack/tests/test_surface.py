import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SurfaceCourt(unittest.TestCase):
    def test_dependency_closed_surface_counts(self):
        self.assertEqual(25, len(list((ROOT / "queries").glob("*.rq"))))
        self.assertEqual(10, len(list((ROOT / "gates").glob("*.rq"))))
        self.assertEqual(5, len(list((ROOT / "templates").glob("*.tera"))))

if __name__ == "__main__": unittest.main()
