"""Real collaborators: real rdflib gates, real ggen sync in a scratch copy, real affi binary
(skipped with a stated reason when the affi binary is absent)."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AFFI = Path(os.environ.get("AFFI_BIN", Path.home() / "affidavit/target/debug/affi"))

def run(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)

class ConsumerPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.pack = Path(cls._tmp.name) / "p"
        shutil.copytree(ROOT, cls.pack, ignore=shutil.ignore_patterns("generated", ".ggen*", "__pycache__"))
        r = run("ggen", "sync", "run", cwd=cls.pack)
        assert r.returncode == 0, r.stderr[-400:]

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_gate_court_every_leg(self):
        for g in sorted((ROOT / "gates").glob("*.rq")):
            for exp in ("pass", "fail"):
                r = run(sys.executable, str(ROOT / "runners/semantic_runner.py"), "--gate", str(g),
                        "--witness", str(ROOT / f"witnesses/{exp}/{g.stem}.ttl"), "--expectation", exp)
                self.assertEqual(r.returncode, 0, f"{g.stem} {exp}: {r.stderr}")

    def test_render_is_idempotent_and_typed(self):
        if True:
            pack = self.pack
            ts = (pack / "generated/affidavit_events.ts").read_text()
            self.assertIn('["audit-log", "build", "deploy", "test"]', ts)
            before = {p.name: p.read_bytes() for p in (pack / "generated").iterdir()}
            r2 = run("ggen", "sync", "run", cwd=pack)
            self.assertEqual(r2.returncode, 0, r2.stderr[-400:])
            after = {p.name: p.read_bytes() for p in (pack / "generated").iterdir()}
            self.assertEqual(before, after)

    @unittest.skipUnless(AFFI.is_file(), f"affi binary not built at {AFFI}")
    def test_generated_gate_accepts_honest_and_rejects_tampered(self):
        import yaml
        action = yaml.safe_load((self.pack / "generated/action.yml").read_text())
        script = action["runs"]["steps"][0]["run"].replace("${{ inputs.receipt }}", "receipt.json")
        with tempfile.TemporaryDirectory() as d:
            w = Path(d)
            (w / "pa").write_text("a"); (w / "pb").write_text("b")
            (w / "bin").mkdir(); (w / "bin/affi").symlink_to(AFFI)
            env = {**os.environ, "PATH": f"{w/'bin'}:{os.environ['PATH']}"}
            for args in (["emit", "--type", "build", "--object", "repo:repo:main", "--payload", "pa"],
                         ["emit", "--type", "test", "--object", "suite:suite:unit", "--payload", "pb"],
                         ["assemble", "--out", "receipt.json"]):
                self.assertEqual(run(str(AFFI), "receipt", *args, cwd=w).returncode, 0)
            ok = run("bash", "-c", script, cwd=w, env=env)
            self.assertEqual(ok.returncode, 0, ok.stdout[-300:])
            text = (w / "receipt.json").read_text().replace('"test"', '"tampered"')
            (w / "receipt.json").write_text(text)
            bad = run("bash", "-c", script, cwd=w, env=env)
            self.assertEqual(bad.returncode, 2)

if __name__ == "__main__":
    unittest.main()
