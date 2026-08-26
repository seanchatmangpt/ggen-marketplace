from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SurfaceCourt(unittest.TestCase):
    def test_dependency_closed_surface(self):
        self.assertEqual(len(list((ROOT / 'queries').glob('*.rq'))), 8)
        self.assertEqual(len(list((ROOT / 'gates').glob('*.rq'))), 4)
        self.assertEqual(len(list((ROOT / 'templates').glob('*.tera'))), 3)
        cfg = (ROOT / 'ggen.toml').read_text()
        for name in ('10-ash-surface-frontier.rq','20-dual-revops-frontier.rq','30-ocel-value-evidence.rq'):
            self.assertIn(name, cfg)

if __name__ == '__main__': unittest.main()
