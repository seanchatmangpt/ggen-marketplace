from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SurfaceCourt(unittest.TestCase):
    def test_dependency_closed_surface(self):
        self.assertEqual(len(list((ROOT / 'queries').glob('*.rq'))), 23)
        self.assertEqual(len(list((ROOT / 'gates').glob('*.rq'))), 4)
        self.assertEqual(len(list((ROOT / 'templates').glob('*.tera'))), 7)
        cfg = (ROOT / 'ggen.toml').read_text()
        for name in (
            '10-ash-surface-frontier.rq','20-dual-revops-frontier.rq','30-ocel-value-evidence.rq',
            '90-ash-resources.rq','110-ash-policies.rq','140-reactor-steps.rq','150-liveview-surfaces.rq'
        ):
            self.assertIn(name, cfg)

if __name__ == '__main__': unittest.main()
