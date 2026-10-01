"""Real collaborators: real rdflib gates, real ggen sync in a scratch copy, real affi binary
(skipped with a stated reason when the affi binary is absent)."""
import os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AFFI = Path(os.environ.get("AFFI_BIN", Path.home() / "affidavit/target/debug/affi"))

def run(*a, **k):
    return subprocess.run(list(a), capture_output=True, text=True, **k)

class Rendered(unittest.TestCase):
    __test__ = False

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


class ConsumerPack(Rendered):
    __test__ = True

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
            before = {p.name: p.read_bytes() for p in (pack / "generated").iterdir() if p.is_file()}
            r2 = run("ggen", "sync", "run", cwd=pack)
            self.assertEqual(r2.returncode, 0, r2.stderr[-400:])
            after = {p.name: p.read_bytes() for p in (pack / "generated").iterdir() if p.is_file()}
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

WASM = Path.home() / "ash_affidavit/priv/affidavit"

class Hosts(Rendered):
    __test__ = True

    """Generated TS and Python hosts drive the real affidavit.wasm through every op example."""

    @unittest.skipUnless((WASM / "affidavit.wasm").is_file(), "ash_affidavit vendored wasm absent")
    def test_python_host_runs_every_op_example(self):
        try:
            import wasmtime  # noqa: F401
        except ImportError:
            self.skipTest("wasmtime not installed (pip install wasmtime)")
        import hashlib, importlib.util
        spec = importlib.util.spec_from_file_location("h", self.pack / "generated/affidavit_host.py")
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        wasm = WASM / "affidavit.wasm"
        pin = hashlib.sha256(wasm.read_bytes()).hexdigest()
        host = m.AffidavitHost(str(wasm), pin)
        import json
        examples = json.loads((WASM / "op-examples.json").read_text())["examples"]
        self.assertEqual({e["op"] for e in examples}, set(m.OPS))
        for e in examples:
            req = dict(e["request"]); op = req.pop("op")
            self.assertTrue(host.call(op, **req)["ok"], op)
        with self.assertRaises(m.AffidavitRefusal) as c:
            host.call("nope")
        self.assertEqual(c.exception.code, "unknown_op")
        with self.assertRaises(m.AffidavitRefusal) as c:
            m.AffidavitHost(str(wasm), "00")
        self.assertEqual(c.exception.code, "wasm_digest_mismatch")

    @unittest.skipUnless((WASM / "affidavit.wasm").is_file(), "ash_affidavit vendored wasm absent")
    def test_ts_host_runs_every_op_example(self):
        import hashlib, shutil as sh
        if sh.which("node") is None:
            self.skipTest("node absent")
        wasm = WASM / "affidavit.wasm"
        pin = hashlib.sha256(wasm.read_bytes()).hexdigest()
        d = self.pack / "tsrun"; d.mkdir()
        sh.copy(self.pack / "generated/affidavit_host.ts", d / "host.ts")
        (d / "run.ts").write_text(f"""
import {{ AffidavitHost }} from "./host.ts";
import {{ readFileSync }} from "node:fs";
const ex = JSON.parse(readFileSync({str(WASM / 'op-examples.json')!r}, "utf8")).examples;
const h = await AffidavitHost.load({str(wasm)!r}, {pin!r});
for (const e of ex) {{ const {{op, ...rest}} = e.request; console.log(op, h.call(op, rest).ok); }}
try {{ h.call("nope" as any); }} catch (x) {{ console.log("refused", (x as any).code); }}
""")
        r = run("node", "--experimental-strip-types", "--no-warnings", "run.ts", cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        lines = r.stdout.split("\n")
        self.assertEqual(sum(1 for l in lines if l.endswith(" true")), 9, r.stdout)
        self.assertIn("refused unknown_op", r.stdout)

if __name__ == "__main__":
    unittest.main()
