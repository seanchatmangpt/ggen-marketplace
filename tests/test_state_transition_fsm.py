"""Chicago-style tests for state-transition-pack FSM codegen.

Real ggen binary, real generated code executed under python3/bun/rustc/elixir
(skipped by name when a toolchain is absent), real SPARQL gate evaluation via
ggen sync on deliberately illegal consumer graphs. No mocks or patches.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import marketplace  # noqa: E402
import qualify_packs as q  # noqa: E402

PACK_NAME = "state-transition-pack"
PACK_DIR = ROOT / "packs" / PACK_NAME
GGEN = shutil.which("ggen")
OUT = "src/st_fsm"


def pack():
    return next(p for p in marketplace.require_admitted() if p.name == PACK_NAME)


def generate(consumer_ttl: str | None = None):
    """Run the qualifier's capsule (optionally with a replaced consumer.ttl) and return (rc, dir)."""
    tmp = Path(tempfile.mkdtemp(prefix="st-fsm-test-"))
    p = pack()
    consumer = q.prepare_consumer(p, tmp)
    if consumer_ttl is not None:
        onto = consumer / "ontology.ttl"
        text = onto.read_text(encoding="utf-8")
        onto.write_text(consumer_ttl_rewrite(text, consumer_ttl), encoding="utf-8")
    r = q.run_bounded([GGEN, "sync", "run"], consumer, 5.0)
    return r, consumer


def consumer_ttl_rewrite(text: str, replacement: str) -> str:
    # Replace the whole qualification consumer graph with `replacement`, keeping
    # the marketplace probe subject appended by the qualifier.
    head = text.split("# ===== QUALIFICATION SOURCE", 1)[0]
    tail = "@prefix mq: <https://ggen.dev/marketplace/qualification#> ." + text.split("@prefix mq: <https://ggen.dev/marketplace/qualification#> .", 1)[1]
    return head + replacement + "\n" + tail


def consumer_text() -> str:
    return (PACK_DIR / "qualification" / "consumer.ttl").read_text(encoding="utf-8")


@unittest.skipUnless(GGEN, "ggen binary required")
class GeneratedFsm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        r, cls.dir = generate()
        assert r.returncode == 0, r.stderr[-800:]
        cls.out = cls.dir / OUT

    def test_qualifier_consumes_toy_consumer_and_emits_four_languages(self):
        for ext in ("ts", "py", "rs", "ex"):
            text = (self.out / f"fsm.{ext}").read_text(encoding="utf-8")
            self.assertIn("Shipped" if ext != "ex" else "shipped", text)
            self.assertIn("Observed" if ext != "ex" else "observed", text)  # loop model from pack ontology

    def test_python_replay_detects_illegal_and_skipped(self):
        code = (
            "import sys; sys.path.insert(0, %r)\nimport fsm, hashlib\nS=fsm.OrderState\n"
            "print(fsm.replay_order([('pay',S.New,S.Paid),('ship',S.Paid,S.Shipped)]))\n"
            "print([v[1] for v in fsm.replay_order([('ship',S.Paid,S.Shipped)])])\n"
            "print([v[1] for v in fsm.replay_order([('pay',S.New,S.Shipped)])])\n"
            "print(fsm.chain_digest('abc')==hashlib.sha256(b'abc').hexdigest())\n"
        ) % str(self.out)
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True).stdout.split("\n")
        self.assertEqual(out[:4], ["[]", "['skipped']", "['illegal']", "True"])

    @unittest.skipUnless(shutil.which("bun"), "bun required")
    def test_typescript_replay_and_sha256(self):
        (self.out / "t.ts").write_text(
            'import * as f from "./fsm.ts"; const S=f.OrderState;\n'
            'console.log(JSON.stringify([f.replayOrder([{name:"pay",from:S.New,to:S.Paid}]).length,'
            'f.replayOrder([{name:"ship",from:S.Paid,to:S.Shipped}])[0].kind,'
            'f.replayOrder([{name:"pay",from:S.New,to:S.Shipped}])[0].kind, f.chainDigest("abc")]));\n')
        out = subprocess.run(["bun", "t.ts"], cwd=self.out, capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(out), [0, "skipped", "illegal", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"])

    @unittest.skipUnless(shutil.which("rustc"), "rustc required")
    def test_rust_replay_and_hand_rolled_sha256(self):
        (self.out / "t.rs").write_text(
            'include!("fsm.rs");\nfn main(){ use OrderState::*;\n'
            'println!("{}", replay_order(&[("pay",New,Paid)]).len());\n'
            'println!("{:?}", replay_order(&[("ship",Paid,Shipped)])[0].kind);\n'
            'println!("{:?}", replay_order(&[("pay",New,Shipped)])[0].kind);\n'
            'println!("{}", chain_digest("abc")); }\n')
        subprocess.run(["rustc", "-o", "t_rs", "t.rs"], cwd=self.out, capture_output=True, check=True)
        out = subprocess.run(["./t_rs"], cwd=self.out, capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(out, ["0", "Skipped", "Illegal", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"])

    @unittest.skipUnless(shutil.which("elixir"), "elixir required")
    def test_elixir_replay_and_sha256(self):
        (self.out / "t.exs").write_text(
            'Code.require_file("fsm.ex")\n'
            'IO.puts(length(StFsm.Order.replay([{"pay",:new,:paid}])))\n'
            'IO.puts(elem(hd(StFsm.Order.replay([{"ship",:paid,:shipped}])),1))\n'
            'IO.puts(elem(hd(StFsm.Order.replay([{"pay",:new,:shipped}])),1))\n'
            'IO.puts(StFsm.Chain.digest("abc"))\n')
        out = subprocess.run(["elixir", "t.exs"], cwd=self.out, capture_output=True, text=True, check=True).stdout.split()
        self.assertEqual(out, ["0", "skipped", "illegal", "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"])

    def test_mutation_rename_individual_changes_output_accordingly(self):
        base = consumer_text()
        mutated = base.replace('st:stateName "Shipped"', 'st:stateName "Delivered"')
        self.assertNotEqual(base, mutated)
        r, m_dir = generate(mutated)
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        for ext in ("ts", "py", "rs", "ex"):
            before = (self.out / f"fsm.{ext}").read_text(encoding="utf-8")
            after = (m_dir / OUT / f"fsm.{ext}").read_text(encoding="utf-8")
            expected = before.replace("Shipped", "Delivered").replace("shipped", "delivered")
            self.assertNotEqual(before, after)
            self.assertEqual(after, expected, f"{ext}: rename must change only the renamed state")


@unittest.skipUnless(GGEN, "ggen binary required")
class Gates(unittest.TestCase):
    def refused(self, ttl_edit) -> str:
        r, _ = generate(ttl_edit(consumer_text()))
        self.assertNotEqual(r.returncode, 0)
        return r.stdout + r.stderr

    def test_skipped_advance_transition_refused_by_gate_020(self):
        out = self.refused(lambda t: t.replace("st:from st:OrderPaid ; st:to st:OrderShipped", "st:from st:OrderNew ; st:to st:OrderShipped"))
        self.assertIn("No skipped transitions", out)

    def test_unreachable_state_refused_by_gate_030(self):
        out = self.refused(lambda t: t + '\nst:OrderOrphan a st:State ; st:inMachine st:OrderMachine ; st:stateName "Orphan" ; st:seq 9 .\n')
        self.assertIn("reachable", out)

    def test_unsupported_hash_for_language_refused_by_gate_040(self):
        out = self.refused(lambda t: t + '\nst:B2 a st:ChainPolicy ; st:chosenAlgo "blake2b256" ; st:policyPrecedence 5 ; st:policyLanguage "ts", "py" .\n')
        self.assertIn("Chain policy refused", out)

    def test_blake2b256_policy_for_python_only_is_lawful(self):
        r, d = generate(consumer_text() + '\nst:B2 a st:ChainPolicy ; st:chosenAlgo "blake2b256" ; st:policyPrecedence 5 ; st:policyLanguage "py" .\n')
        self.assertEqual(r.returncode, 0, r.stderr[-800:])
        py = (d / OUT / "fsm.py").read_text(encoding="utf-8")
        self.assertIn("blake2b", py)
        self.assertIn('CHAIN_ALGO = "blake2b256"', py)


class LiteralScanGate(unittest.TestCase):
    gate = PACK_DIR / "gates" / "050_template_literal_scan.py"

    def test_shipped_templates_are_clean(self):
        r = subprocess.run([sys.executable, str(self.gate)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_banned_literal_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "x.tmpl").write_text("// wired to zcode runtime\n", encoding="utf-8")
            r = subprocess.run([sys.executable, str(self.gate), tmp], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn('"literal": "zcode"', r.stdout)


if __name__ == "__main__":
    unittest.main()
