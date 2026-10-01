"""Real-collaborator tests: real rdflib graphs, the real index, real subprocess for the CLI."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import solve  # noqa: E402

PY = sys.executable

class Solver(unittest.TestCase):
    def test_fully_provided_requirement_has_empty_residual(self):
        out = solve.solve(ROOT / "fixtures" / "req-fully-provided.ttl")
        self.assertEqual(out["residual"], [])
        self.assertEqual({r["id"] for r in out["reuse"]},
                         {"wasm-host:elixir-wasmex", "ci:github-composite-action"})

    def test_affidavit_consumer_requirement_is_fully_closed(self):
        out = solve.solve(ROOT / "fixtures" / "req-affidavit-consumer.ttl")
        self.assertEqual(out["residual"], [])
        self.assertEqual(out["coverage"]["needs"], 7)
        self.assertIn("wasm-host:typescript", {r["id"] for r in out["reuse"]})

    def test_a_stale_provider_is_residual_not_reuse(self):
        out = solve.solve(ROOT / "fixtures" / "req-stale-only.ttl")
        self.assertEqual([(r["id"], r["reason"], r["disposition"]) for r in out["residual"]],
                         [("affidavit:rust-catalog-fork", "only_stale_provider", "EXTEND")])
        self.assertEqual(out["reuse"], [])

    def test_closure_follows_requires_edges(self):
        out = solve.solve(ROOT / "fixtures" / "req-fully-provided.ttl")
        # elixir host requires the capability registry, so it is in the closure
        self.assertIn("wasm-abi:capability-registry", out["closure"])

    def test_gate_violation_refuses_instead_of_solving(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.ttl"
            bad.write_text(
                '@prefix cc: <https://ggen.dev/ontology/capability-closure#> .\n'
                '<urn:r> a cc:Requirement ; cc:need <urn:n> .\n<urn:n> cc:id "x:y" .\n')
            out = solve.solve(bad)
        self.assertEqual(out["refusal"], "REFUSED_GATE_ROWS")
        self.assertEqual(out["violations"][0]["gate"], "060_need_shape")

    def test_cli_exit_codes(self):
        ok = subprocess.run([PY, str(ROOT / "scripts/solve.py"), str(ROOT / "fixtures/req-fully-provided.ttl")],
                            capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0)
        self.assertEqual(json.loads(ok.stdout)["residual"], [])

    def test_every_evidence_path_exists(self):
        r = subprocess.run([PY, str(ROOT / "scripts/verify_evidence.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_gate_court_witnesses_all_hold(self):
        gates = sorted((ROOT / "gates").glob("*.rq"))
        self.assertGreaterEqual(len(gates), 6)
        for g in gates:
            for exp in ("pass", "fail"):
                r = subprocess.run([PY, str(ROOT / "runners/semantic_runner.py"), "--gate", str(g),
                                    "--witness", str(ROOT / f"witnesses/{exp}/{g.stem}.ttl"),
                                    "--expectation", exp], capture_output=True, text=True)
                self.assertEqual(r.returncode, 0, f"{g.stem} {exp}: {r.stderr}")

if __name__ == "__main__":
    unittest.main()
