"""Real-collaborator tests: real rdflib/pyshacl/pyld, real ggen, real cargo, real wasmex. No mocks."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF

PACK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACK / "qualification"))
import rdfc  # noqa: E402

QRI = Namespace("https://seanchatmangpt.github.io/packs/qri-qualification-profile-pack#")
CONTRACT = PACK / "ontology/examples/graphlaw-contract.ttl"


def gate_rows(gate: Path, data: Graph) -> int:
    return len(list(data.query(gate.read_text(encoding="utf-8"))))


def have(*tools: str) -> bool:
    return all(shutil.which(t) for t in tools)


class GateCourt(unittest.TestCase):
    def test_every_gate_has_both_witnesses_and_discriminates(self) -> None:
        gates = sorted((PACK / "gates").glob("*.rq"))
        self.assertGreaterEqual(len(gates), 6)
        for gate in gates:
            with self.subTest(gate=gate.stem):
                p = Graph().parse(PACK / "witnesses/pass" / f"{gate.stem}.ttl")
                f = Graph().parse(PACK / "witnesses/fail" / f"{gate.stem}.ttl")
                self.assertEqual(gate_rows(gate, p), 0, "pass witness must be admitted")
                self.assertGreater(gate_rows(gate, f), 0, "fail witness must be refused (non-vacuous)")

    def test_court_toml_entries_match_gates_and_discriminate(self) -> None:
        court = tomllib.loads((PACK / "gate-court.toml").read_text(encoding="utf-8"))
        self.assertEqual(court["court"]["schema"], "ggen.semantic-gate-witness-court/1")
        entries = court["gate"]
        stems = [e["stem"] for e in entries]
        self.assertEqual(len(stems), len(set(stems)), "duplicate [[gate]] stems")
        self.assertEqual(set(stems), {g.stem for g in (PACK / "gates").glob("*.rq")})
        for e in entries:
            with self.subTest(gate=e["stem"]):
                gate = PACK / court["court"]["gate_dir"] / f"{e['stem']}.rq"
                self.assertTrue(gate.is_file())
                self.assertTrue((PACK / e["pass"]).is_file())
                self.assertTrue((PACK / e["fail"]).is_file())
                self.assertEqual(gate_rows(gate, Graph().parse(PACK / e["pass"])), 0)
                self.assertGreater(gate_rows(gate, Graph().parse(PACK / e["fail"])), 0)

    def test_example_contract_is_admitted_by_every_gate(self) -> None:
        data = Graph().parse(CONTRACT)
        for gate in sorted((PACK / "gates").glob("*.rq")):
            with self.subTest(gate=gate.stem):
                self.assertEqual(gate_rows(gate, data), 0)


class Shapes(unittest.TestCase):
    def validate(self, data: Graph) -> tuple[bool, str]:
        import pyshacl

        data.parse(PACK / "ontology.ttl")
        conforms, _, text = pyshacl.validate(data, shacl_graph=str(PACK / "shapes/qri.shacl.ttl"), inference="none")
        return conforms, text

    def test_example_contract_conforms(self) -> None:
        conforms, text = self.validate(Graph().parse(CONTRACT))
        self.assertTrue(conforms, text)

    def test_ambiguous_field_type_is_refused(self) -> None:
        data = Graph().parse(CONTRACT)
        data.set((next(data.subjects(QRI.fieldName, Literal("request"))), QRI.fieldType, Literal("number")))
        conforms, _ = self.validate(data)
        self.assertFalse(conforms)

    def test_passed_receipt_missing_invariant_is_refused(self) -> None:
        data = Graph().parse(CONTRACT)
        ns = "urn:t:"
        from rdflib import URIRef

        c = next(data.subjects(RDF.type, QRI.CapabilityContract))
        rec, act, real, ctx = (URIRef(ns + x) for x in ("rec", "act", "real", "ctx"))
        for s, p, o in [
            (act, RDF.type, QRI.Qualification), (real, RDF.type, QRI.Realization), (ctx, RDF.type, QRI.RuntimeContext),
            (rec, RDF.type, QRI.QualificationReceipt), (rec, URIRef("http://www.w3.org/ns/prov#wasGeneratedBy"), act),
            (rec, QRI.realization, real), (rec, QRI.runtimeContext, ctx), (rec, QRI.qualifiesFor, c),
            (rec, QRI.qualificationResult, QRI.Passed),
        ]:
            data.add((s, p, o))
        conforms, text = self.validate(data)
        self.assertFalse(conforms)
        self.assertIn("required invariant", text)


class Identity(unittest.TestCase):
    def test_equivalent_serializations_share_a_digest_and_a_change_does_not(self) -> None:
        g = Graph().parse(CONTRACT)
        with tempfile.TemporaryDirectory() as t:
            nt = Path(t) / "c.nt"
            nt.write_text(g.serialize(format="nt"), encoding="utf-8")
            self.assertEqual(rdfc.digest(CONTRACT), rdfc.digest(nt))
        g.add((next(g.subjects(RDF.type, QRI.CapabilityContract)), QRI.contractVersion, Literal("9.9.9")))
        self.assertNotEqual(rdfc.digest(CONTRACT), rdfc.digest(g))

    def test_blank_node_relabeling_does_not_change_digest(self) -> None:
        a = Graph().parse(data='@prefix e: <urn:e:> . e:s e:p [ e:q "1" ] .', format="turtle")
        b = Graph().parse(data='@prefix e: <urn:e:> . e:s e:p _:zzz . _:zzz e:q "1" .', format="turtle")
        self.assertEqual(rdfc.digest(a), rdfc.digest(b))


@unittest.skipUnless(have("ggen"), "BLOCKED: ggen not installed")
class Generation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name) / "capsule"
        shutil.copytree(PACK, cls.root, ignore=shutil.ignore_patterns("generated", "__pycache__", "tests"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def sync(self) -> dict[str, bytes]:
        r = subprocess.run(["ggen", "sync", "run"], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-400:] + r.stderr[-400:])
        return {str(p.relative_to(self.root)): p.read_bytes() for p in sorted((self.root / "generated").rglob("*")) if p.is_file()}

    def test_projection_is_complete_and_deterministic(self) -> None:
        first = self.sync()
        second = self.sync()
        self.assertEqual(first, second)
        self.assertEqual(
            sorted(first),
            ["generated/abi.json", "generated/adapter/Cargo.toml", "generated/adapter/src/lib.rs",
             "generated/beam/qri_host.ex", "generated/wit/capability.wit", "generated/wit/refusal.wit"],
        )
        abi = json.loads(first["generated/abi.json"])
        self.assertEqual(abi["symbols"], {"alloc": "gl_alloc", "free": "gl_free", "call": "gl_call"})
        self.assertIn(b"call: func(request: list<u8>) -> result<list<u8>, code>;", first["generated/wit/capability.wit"])
        self.assertIn(b"semantic-refusal", first["generated/wit/refusal.wit"])
        self.assertIn(b"pub unsafe extern \"C\" fn gl_call", first["generated/adapter/src/lib.rs"])

    def test_graphlaw_output_same_six_files_and_ash_example_is_not_imported(self) -> None:
        first = self.sync()
        self.assertEqual(len(first), 6)
        self.assertNotIn("ash-graphlaw", (self.root / "ggen.toml").read_text(encoding="utf-8"))
        self.assertEqual(first, self.sync())


@unittest.skipUnless(have("ggen", "cargo", "mix"), "BLOCKED: ggen/cargo/mix missing")
class RealDifferentialCourt(unittest.TestCase):
    """generated adapter -> wasm32-wasip1 -> generated wasmex host; native vs wasm; receipts re-admitted."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        # cwd outside the repo: the repo's rust-toolchain.toml would select a toolchain without the target.
        targets = subprocess.run(["rustup", "target", "list", "--installed"], cwd=root, capture_output=True, text=True).stdout
        if "wasm32-wasip1" not in targets:
            raise unittest.SkipTest("BLOCKED: wasm32-wasip1 target not installed")
        cap = root / "capsule"
        shutil.copytree(PACK, cap, ignore=shutil.ignore_patterns("generated", "__pycache__", "tests"))
        subprocess.run(["ggen", "sync", "run"], cwd=cap, check=True, capture_output=True)
        crate = root / "ref"
        (crate / "src/bin").mkdir(parents=True)
        shutil.copy(cap / "generated/adapter/Cargo.toml", crate)
        shutil.copy(cap / "generated/adapter/src/lib.rs", crate / "src")
        shutil.copy(PACK / "qualification/reference/domain.rs", crate / "src/domain.rs")
        shutil.copy(PACK / "qualification/reference/native.rs", crate / "src/bin/qref-native.rs")
        for args in (["--release", "--target", "wasm32-wasip1", "--lib"], ["--release", "--bin", "qref-native"]):
            subprocess.run(["cargo", "build", *args], cwd=crate, check=True, capture_output=True)
        cls.wasm = crate / "target/wasm32-wasip1/release/qri_gl_adapter.wasm"
        cls.native = crate / "target/release/qref-native"
        mix = root / "mix"
        (mix / "lib").mkdir(parents=True)
        (mix / "mix.exs").write_text(
            'defmodule Q.MixProject do\n use Mix.Project\n def project, do: [app: :q, version: "0.1.0", elixir: "~> 1.15", deps: [{:wasmex, "~> 0.15.1"}]]\n'
            " def application, do: [extra_applications: [:logger, :crypto]]\nend\n", encoding="utf-8")
        shutil.copy(cap / "generated/beam/qri_host.ex", mix / "lib")
        r = subprocess.run(["mix", "deps.get"], cwd=mix, capture_output=True, text=True)
        if r.returncode != 0:
            raise unittest.SkipTest("BLOCKED: hex deps unavailable: " + r.stderr[-200:])
        r = subprocess.run(["mix", "compile"], cwd=mix, capture_output=True, text=True)
        if r.returncode != 0:
            raise AssertionError("generated host failed to compile: " + r.stdout[-600:] + r.stderr[-600:])
        cls.mix = mix
        cls.root = root

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_native_and_wasm_on_beam_are_substitutable_and_readmitted(self) -> None:
        out = self.root / "receipts.ttl"
        r = subprocess.run(
            [sys.executable, str(PACK / "qualification/qualify.py"), "--contract", str(PACK / "qualification/reference/contract.ttl"),
             "--wasm", str(self.wasm), "--native", str(self.native), "--mix-dir", str(self.mix), "--out", str(out)],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-600:] + r.stderr[-600:])
        report = json.loads(r.stdout)
        self.assertTrue(report["substitution_claim"])
        self.assertEqual(set(report["observed"].values()), {True})
        graph = Graph().parse(out)
        self.assertEqual(len(list(graph.subjects(RDF.type, QRI.SubstitutionClaim))), 1)
        self.assertEqual(len(list(graph.subjects(RDF.type, QRI.QualificationReceipt))), 2)
        for gate in sorted((PACK / "gates").glob("*.rq")):
            with self.subTest(gate=gate.stem):
                self.assertEqual(gate_rows(gate, graph), 0)
        import pyshacl

        graph.parse(PACK / "ontology.ttl")
        conforms, _, text = pyshacl.validate(graph, shacl_graph=str(PACK / "shapes/qri.shacl.ttl"), inference="none")
        self.assertTrue(conforms, text)

    def test_tampered_digest_is_refused_at_admission_not_trapped(self) -> None:
        r = subprocess.run(["mix", "run", str(PACK / "qualification/host_probe.exs"), str(self.wasm), "0" * 64],
                           cwd=self.mix, input="", capture_output=True, text=True)
        self.assertEqual(r.returncode, 3)
        row = json.loads(r.stdout.splitlines()[-1])
        self.assertEqual((row["kind"], row["code"]), ("admission_refused", "wasm_digest_mismatch"))

    def test_import_outside_contract_is_refused_by_host(self) -> None:
        # Hand-assembled module importing wasi sock_accept, outside the contract's allowed imports.
        def s(b: bytes) -> bytes:
            return bytes([len(b)]) + b

        def sec(i: int, payload: bytes) -> bytes:
            return bytes([i, len(payload)]) + payload

        types = bytes([4, 0x60, 3, 0x7F, 0x7F, 0x7F, 1, 0x7F, 0x60, 1, 0x7F, 1, 0x7F, 0x60, 2, 0x7F, 0x7F, 0, 0x60, 2, 0x7F, 0x7F, 1, 0x7E])
        imports = bytes([1]) + s(b"wasi_snapshot_preview1") + s(b"sock_accept") + bytes([0, 0])
        funcs = bytes([3, 1, 2, 3])
        exports = bytes([4]) + s(b"memory") + bytes([2, 0]) + s(b"gl_alloc") + bytes([0, 1]) + s(b"gl_free") + bytes([0, 2]) + s(b"gl_call") + bytes([0, 3])
        code = bytes([3, 4, 0, 0x41, 0, 0x0B, 2, 0, 0x0B, 4, 0, 0x42, 0, 0x0B])
        module = b"\0asm\1\0\0\0" + sec(1, types) + sec(2, imports) + sec(3, funcs) + sec(5, bytes([1, 0, 1])) + sec(7, exports) + sec(10, code)
        bad = self.root / "bad.wasm"
        bad.write_bytes(module)
        sha = __import__("hashlib").sha256(module).hexdigest()
        r = subprocess.run(["mix", "run", str(PACK / "qualification/host_probe.exs"), str(bad), sha], cwd=self.mix, input="", capture_output=True, text=True)
        row = json.loads(r.stdout.splitlines()[-1])
        self.assertEqual((row["kind"], row["code"]), ("admission_refused", "wasm_import_surface_mismatch"))


ASH = PACK / "ontology/examples/ash-graphlaw-contract.ttl"
EXAMPLES = [ASH, PACK / "ontology/examples/beam4pm-pg-contract.ttl", PACK / "ontology/examples/autofde-cmca-contract.ttl"]
HOST_GATES = ("070_typed_import_matches_allowed", "080_abi_family_closed",
              "090_zero_ok_declares_meaning", "100_recycle_rule_names_declared_code")


def select(query: Path, data: Graph) -> list[tuple]:
    return [tuple(str(v) if v is not None else None for v in row) for row in data.query(query.read_text(encoding="utf-8"))]


class HostProfileGates(unittest.TestCase):
    def test_new_gates_have_witnesses_and_fail_witnesses_are_refused(self) -> None:
        for stem in HOST_GATES:
            with self.subTest(gate=stem):
                gate = PACK / "gates" / f"{stem}.rq"
                self.assertTrue(gate.exists())
                p = Graph().parse(PACK / "witnesses/pass" / f"{stem}.ttl")
                f = Graph().parse(PACK / "witnesses/fail" / f"{stem}.ttl")
                self.assertEqual(gate_rows(gate, p), 0)
                self.assertGreater(gate_rows(gate, f), 0)
        court = (PACK / "gate-court.toml").read_text(encoding="utf-8")
        for stem in HOST_GATES:
            self.assertIn(stem, court)

    def test_unsupported_family_row_is_marked_unsupported(self) -> None:
        rows = select(PACK / "gates/080_abi_family_closed.rq", Graph().parse(PACK / "witnesses/fail/080_abi_family_closed.ttl"))
        self.assertEqual([r[1:] for r in rows], [("outMode", "scatter_gather", "UNSUPPORTED")])

    def test_every_host_example_is_admitted_by_every_gate(self) -> None:
        for ex in EXAMPLES:
            data = Graph().parse(ex)
            for gate in sorted((PACK / "gates").glob("*.rq")):
                with self.subTest(example=ex.stem, gate=gate.stem):
                    self.assertEqual(gate_rows(gate, data), 0)

    def test_mutated_host_example_is_refused_by_new_gates(self) -> None:
        data = Graph().parse(ASH)
        data.set((next(data.subjects(RDF.type, QRI.HostProfile)), QRI.outMode, Literal("scatter_gather")))
        self.assertGreater(gate_rows(PACK / "gates/080_abi_family_closed.rq", data), 0)
        data = Graph().parse(ASH)
        data.remove((None, QRI.allowedImport, Literal("wasi_snapshot_preview1::random_get")))
        self.assertGreater(gate_rows(PACK / "gates/070_typed_import_matches_allowed.rq", data), 0)


class HostProfileShapes(unittest.TestCase):
    validate = Shapes.validate

    def test_all_host_examples_conform(self) -> None:
        for ex in EXAMPLES:
            with self.subTest(example=ex.stem):
                conforms, text = self.validate(Graph().parse(ex))
                self.assertTrue(conforms, text)

    def test_ash_graphlaw_example_conforms_to_shacl(self) -> None:
        conforms, text = self.validate(Graph().parse(ASH))
        self.assertTrue(conforms, text)

    def test_bad_out_mode_and_bad_limit_are_refused(self) -> None:
        data = Graph().parse(ASH)
        data.set((next(data.subjects(RDF.type, QRI.HostProfile)), QRI.outMode, Literal("scatter_gather")))
        self.assertFalse(self.validate(data)[0])
        data = Graph().parse(ASH)
        data.set((next(data.subjects(QRI.limitName, Literal("max_queue"))), QRI.limitDefault, Literal("many")))
        self.assertFalse(self.validate(data)[0])


class HostProfileQueries(unittest.TestCase):
    def test_ash_profile_row_carries_real_values(self) -> None:
        data = Graph().parse(ASH)
        q = lambda n: next(d for d in sorted((PACK / "queries").glob(n + "-*.rq")))
        res = list(data.query(q("50").read_text(encoding="utf-8")))
        self.assertEqual(len(res), 1)
        row = {str(k): str(v) for k, v in res[0].asdict().items()}
        self.assertEqual(row["prefix"], "gl")
        self.assertEqual(row["free_symbol"], "gl_free")
        self.assertEqual(row["len_type"], "u32")
        self.assertEqual(row["out_mode"], "packed_u64")
        self.assertEqual(row["req_consumed"], "true")
        self.assertEqual(row["request_cap"], "16777216")
        self.assertEqual(row["path_env"], "GRAPHLAW_WASM_PATH")
        self.assertEqual((row["root"], row["task_root"], row["app"]), ("AshGraphLaw", "AshGraphlaw", "ash_graphlaw"))
        self.assertEqual((row["pool_strategy"], row["pool_size_source"]), ("rest_for_one", "schedulers_online"))  # pool.ex:110
        self.assertEqual((row["taxonomy_ns"], row["telemetry_root"], row["pin_format"]), ("chatman", "ash_graphlaw", "sha256-hex"))
        self.assertEqual((row["engine_id"], row["probe_op"], row["probe_expect"]), ("GraphLaw", "capabilities", "abi"))
        self.assertEqual(data.value(next(data.subjects(RDF.type, QRI.HostProfile)), QRI.freeArity).toPython(), 2)  # gl_free(ptr, len)
        self.assertEqual(len(select(q("51"), data)), 18)
        self.assertIn(("gl", "fuel_per_ms", "1000000", "1", "false", ""), select(q("51"), data))
        zero_ok = {r[1] for r in select(q("51"), data) if r[4] == "true"}
        self.assertEqual(zero_ok, {"table_elements", "instances", "tables", "memories"})
        imps = select(q("52"), data)
        self.assertEqual(len(imps), 7)
        self.assertIn(("gl", "clock_time_get", "i32,i64,i32", "i32"), imps)
        self.assertIn(("gl", "proc_exit", "i32", ""), imps)
        self.assertIn(("gl", "sched_yield", "", "i32"), imps)
        ex = {(r[1], r[2]) for r in select(q("53"), data)}
        self.assertEqual(ex, {("gl_alloc", "required"), ("gl_call", "required"), ("gl_free", "required"),
                              ("memory", "required"), ("_initialize", "optional")})
        self.assertEqual([r[1] for r in select(q("54"), data)],
                         ["abi_failure", "call_exited", "call_trapped", "call_timeout", "fuel_exhausted"])  # recycleRule order, not alphabetical
        self.assertEqual(row["doc_example_op"], "law")

    def test_defaults_apply_for_other_families(self) -> None:
        q50 = next((PACK / "queries").glob("50-*.rq"))
        pg = list(Graph().parse(EXAMPLES[1]).query(q50.read_text(encoding="utf-8")))[0].asdict()
        self.assertEqual((str(pg["free_symbol"]), str(pg["len_type"])), ("pg_dealloc", "usize"))
        cm = list(Graph().parse(EXAMPLES[2]).query(q50.read_text(encoding="utf-8")))[0].asdict()
        self.assertEqual((str(cm["out_mode"]), str(cm["req_consumed"])), ("len_prefix", "false"))

    def test_legacy_queries_are_unchanged_for_graphlaw_and_skip_host_profile_contracts(self) -> None:
        data = Graph().parse(CONTRACT)
        data.parse(PACK / "ontology.ttl")  # kind labels (rdfs:label) live in the core ontology
        for n in ("10-operations", "20-abi", "30-invariants", "40-refusals"):
            q = PACK / "queries" / f"{n}.rq"
            text = q.read_text(encoding="utf-8")
            self.assertIn("FILTER NOT EXISTS { ?c qri:hostProfile", text)
            stripped = text.replace("  FILTER NOT EXISTS { ?c qri:hostProfile ?hpx }\n", "")
            self.assertNotEqual(stripped, text)
            with self.subTest(q=n):
                before = [tuple(map(str, r)) for r in data.query(stripped)]
                self.assertGreater(len(before), 0)
                self.assertEqual(before, [tuple(map(str, r)) for r in data.query(text)])
                self.assertEqual(select(q, Graph().parse(ASH).parse(PACK / "ontology.ttl")), [])
        for n in ("50", "51", "52", "53", "54"):
            self.assertEqual(select(next((PACK / "queries").glob(f"{n}-*.rq")), data), [])


ASH_SRC = Path("/Users/sac/ash_graphlaw")
BEAM_HOST = ("abi.ex", "wasm_config.ex", "engine_load.ex", "host.ex", "pool.ex", "vendor_task.ex", "verify_task.ex")
BEAM_TARGET = {"abi.ex": "lib/ash_graphlaw/abi.ex", "wasm_config.ex": "lib/ash_graphlaw/wasm_config.ex",
               "engine_load.ex": "lib/ash_graphlaw/engine_load.ex", "host.ex": "lib/ash_graphlaw/host.ex",
               "pool.ex": "lib/ash_graphlaw/pool.ex", "vendor_task.ex": "lib/mix/tasks/ash_graphlaw.vendor.ex",
               "verify_task.ex": "lib/mix/tasks/ash_graphlaw.verify.ex"}


def render_beam_host(dest: Path, contract_text: str | None = None) -> dict[str, bytes]:
    """Copy the pack inputs, install ggen-beam-host.toml as ggen.toml, run the real ggen, return the files."""
    (dest / "ontology/examples").mkdir(parents=True)
    shutil.copy(PACK / "ontology.ttl", dest / "ontology.ttl")
    (dest / "ontology/examples/ash-graphlaw-contract.ttl").write_text(
        contract_text if contract_text is not None else ASH.read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copytree(PACK / "templates/beam-host", dest / "templates/beam-host")
    shutil.copy(PACK / "ggen-beam-host.toml", dest / "ggen.toml")
    r = subprocess.run(["ggen", "sync", "run"], cwd=dest, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(r.stdout[-600:] + r.stderr[-600:])
    return {p.name: p.read_bytes() for p in sorted((dest / "generated/beam-host").glob("*")) if p.is_file()}


@unittest.skipUnless(have("ggen"), "BLOCKED: ggen not installed")
class BeamHostProjection(unittest.TestCase):
    def render(self, contract_text: str | None = None) -> dict[str, bytes]:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return render_beam_host(Path(tmp.name) / "capsule", contract_text)

    def test_beam_host_set_is_seven_files_and_deterministic(self) -> None:
        first, second = self.render(), self.render()
        self.assertEqual(sorted(first), sorted(BEAM_HOST))
        self.assertEqual(first, second)

    def test_templates_embed_exactly_queries_50_to_54(self) -> None:
        import re
        names = {"profile": "50-profile.rq", "limits": "51-limits.rq", "imports": "52-imports.rq",
                 "exports": "53-exports.rq", "recycle": "54-recycle.rq"}
        seen = set()
        for tmpl in sorted((PACK / "templates/beam-host").glob("*.tmpl")):
            head = tmpl.read_text(encoding="utf-8").split("\n---\n", 1)[0]
            blocks, cur = [], None
            for line in head.split("sparql:\n", 1)[1].split("\n"):
                m = re.match(r"^  (\w+): \|$", line)
                if m:
                    cur = (m.group(1), [])
                    blocks.append(cur)
                elif cur is not None and (line.startswith("    ") or not line):
                    cur[1].append(line[4:])
            blocks = [(n, "\n".join(ls).rstrip("\n")) for n, ls in blocks]
            self.assertTrue(blocks, tmpl.name)
            for name, body in blocks:
                self.assertIn(name, names, f"{tmpl.name}: query outside 50-54")
                self.assertEqual(body, (PACK / "queries" / names[name]).read_text(encoding="utf-8").rstrip("\n"), f"{tmpl.name}:{name} drifted")
                seen.add(name)
        self.assertEqual(seen, {"profile", "limits", "exports", "recycle"})  # 52 (imports) is carried by the manifest at runtime

    def test_no_contract_literal_is_hardwired_in_the_templates(self) -> None:
        """Rename every GraphLaw/ash_graphlaw/gl literal in the contract; no trace may survive in any output."""
        text = ASH.read_text(encoding="utf-8")
        for a, b in [("AshGraphLaw", "Zork"), ("AshGraphlaw", "Zork"), ("ash_graphlaw", "zork"), ("GRAPHLAW", "ZORK"),
                     ("graphlaw", "zork"), ("GraphLaw", "Zork"), ('"gl"', '"zz"'), ("gl_", "zz_")]:
            text = text.replace(a, b)
        base = self.render()
        out = self.render(text)
        import re
        for name, blob in out.items():
            self.assertIsNone(re.search(r"(?i)graphlaw|\bgl_", blob.decode()), name)
        self.assertIn(b"defmodule Zork.Host do", out["host.ex"])
        self.assertIn(b'"zz_alloc"', out["host.ex"])
        self.assertIn(b"Mix.Tasks.Zork.Vendor", out["vendor_task.ex"])
        self.assertIn(b'@env "ZORK_WASM_PATH"', out["wasm_config.ex"])
        self.assertNotEqual(base["host.ex"], out["host.ex"])

    def test_limits_request_cap_recycle_codes_and_pool_come_from_the_graph(self) -> None:
        text = ASH.read_text(encoding="utf-8")
        text = text.replace('qri:limitName "abi_timeout" ; qri:limitDefault 1000', 'qri:limitName "abi_timeout" ; qri:limitDefault 7777')
        text = text.replace('qri:limitName "max_response_bytes" ; qri:limitDefault 33554432', 'qri:limitName "max_response_bytes" ; qri:limitDefault 1234567')
        text = text.replace("qri:requestCap 16777216", "qri:requestCap 33554432")
        text = text.replace('"fuel_exhausted" ;', '"fuel_exhausted" , "saturated" ;')
        text = text.replace('qri:poolStrategy "rest_for_one"', 'qri:poolStrategy "one_for_one"')
        out = self.render(text)
        base = self.render()
        self.assertIn(b"@abi_timeout 7_777", out["host.ex"])
        self.assertIn(b"@abi_timeout 1_000", base["host.ex"])
        self.assertIn(b"max_response_bytes: 1_234_567", out["wasm_config.ex"])
        self.assertIn(b"@max_request_bytes 32 * 1_048_576", out["abi.ex"])
        self.assertIn(b"@max_request_bytes 16 * 1_048_576", base["abi.ex"])
        self.assertIn(b":saturated", out["host.ex"].split(b"@recycle_codes")[1].split(b"\n")[0])
        self.assertIn(b"strategy: :one_for_one", out["pool.ex"])
        self.assertIn(b"strategy: :rest_for_one", base["pool.ex"])

    def test_zero_ok_limits_recycle_order_and_doc_example_come_from_the_graph(self) -> None:
        base, text = self.render(), ASH.read_text(encoding="utf-8")
        cfg = base["wasm_config.ex"]
        self.assertIn(b"@zero_ok [:table_elements, :instances, :tables, :memories]", cfg)
        self.assertIn(b"&1 >= min_limit(key)", cfg)
        self.assertIn(b"defp min_limit(key) when key in @zero_ok, do: 0", cfg)
        self.assertIn(b":call_trapped, :call_timeout", base["host.ex"])
        self.assertIn(b'`%{"op" => "law", ...}`', base["host.ex"])
        # dropping the flag from one limit removes it from @zero_ok; dropping all removes the clause
        one = self.render(text.replace(' ; qri:limitZeroOk true ; qri:limitZeroMeaning "\\"none allowed\\", refused at instantiation" .', ' .', 1))
        self.assertNotIn(b":table_elements, :instances", one["wasm_config.ex"])
        self.assertIn(b"@zero_ok [:instances, :tables, :memories]", one["wasm_config.ex"])
        swapped = text.replace('qri:recycleOrder 3', 'qri:recycleOrder 9').replace('qri:recycleOrder 4', 'qri:recycleOrder 3')
        line = self.render(swapped)["host.ex"].split(b"@recycle_codes [")[1].split(b"]")[0]
        self.assertEqual(line, b":abi_failure, :call_exited, :call_timeout, :fuel_exhausted, :call_trapped")
        bare = text.replace('qri:docExampleOp "law" ;', '')
        self.assertIn(b'`%{"op" => ...}`', self.render(bare)["host.ex"])

    def test_unsupported_host_shape_fails_loudly_instead_of_emitting_a_wrong_host(self) -> None:
        text = ASH.read_text(encoding="utf-8").replace('qri:outMode "packed_u64"', 'qri:outMode "out_param"')
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with self.assertRaises(AssertionError) as cm:
            render_beam_host(Path(tmp.name) / "capsule", text)
        self.assertIn("UNSUPPORTED_host_profile", str(cm.exception))

    @unittest.skipUnless(have("elixir"), "BLOCKED: elixir not installed")
    def test_generated_files_parse_and_are_format_clean(self) -> None:
        out = self.render()
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        paths = []
        for name, blob in out.items():
            f = Path(tmp.name) / name
            f.write_bytes(blob)
            paths.append(str(f))
        code = ('for f <- System.argv() do src = File.read!(f); Code.string_to_quoted!(src, file: f); '
                'fmt = src |> Code.format_string!(line_length: 120, trailing_comma: true, local_pipe_with_parens: true, single_clause_on_do: true) '
                '|> IO.iodata_to_binary(); if fmt <> "\\n" != src, do: raise("not format-clean: " <> f) end; IO.puts("ok")')
        r = subprocess.run(["elixir", "-e", code, *paths], capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout.strip()), (0, "ok"), r.stderr[-600:])

    @unittest.skipUnless(ASH_SRC.exists(), "BLOCKED: /Users/sac/ash_graphlaw not present")
    def test_ash_example_values_match_the_hand_written_source(self) -> None:
        import re
        lib = ASH_SRC / "lib"
        rd = lambda rel: (lib / rel).read_text(encoding="utf-8")
        host, pool, cfg, eng = rd("ash_graphlaw/host.ex"), rd("ash_graphlaw/pool.ex"), rd("ash_graphlaw/wasm_config.ex"), rd("ash_graphlaw/engine_load.ex")
        g = Graph().parse(ASH)
        q = lambda n: next(d for d in sorted((PACK / "queries").glob(n + "-*.rq")))
        row = {str(k): str(v) for k, v in list(g.query(q("50").read_text(encoding="utf-8")))[0].asdict().items()}
        self.assertIn(f"strategy: :{row['pool_strategy']}", pool)
        self.assertEqual(row["pool_strategy"], "rest_for_one")
        self.assertEqual(row["pool_size_source"], "schedulers_online")
        self.assertIn("System.schedulers_online()", pool)
        self.assertEqual(row["telemetry_root"], "ash_graphlaw")
        self.assertIn(f"[:{row['telemetry_root']}, :engine, :admit]", eng)
        self.assertIn(f"[:{row['telemetry_root']}, :host, :recycle]", host)
        self.assertIn(f'@env "{row["path_env"]}"', cfg)
        self.assertIn(f'@manifest_rel "{row["manifest_rel"]}"', cfg)
        self.assertIn(f'@wasm_rel "{row["wasm_rel"]}"', cfg)
        self.assertIn(f'"{row["manifest_schema"]}"', rd("../lib/mix/tasks/ash_graphlaw.vendor.ex"))
        self.assertEqual(row["taxonomy_ns"], "chatman")  # refusal.ex: "Chatman failure-taxonomy `broken_term`"
        self.assertIn("Chatman failure-taxonomy", rd("ash_graphlaw/refusal.ex"))
        self.assertIn(f'"{row["prefix"]}_alloc"', host)
        self.assertIn(f'call_raw(state, "{row["free_symbol"]}", [out_ptr, out_len]', host)  # free takes (ptr, len): arity 2
        self.assertIn((g.value(next(g.subjects(RDF.type, QRI.HostProfile)), QRI.freeArity).toPython()), {2})
        self.assertIn(f"@required_exports [{', '.join(chr(34) + r[1] + chr(34) for r in select(q('53'), g) if r[2] == 'required')}]", eng)
        self.assertIn("@recycle_codes [" + ", ".join(":" + r[1] for r in
                      select(q("54"), g)) + "]", host)
        zero = re.search(r"@zero_ok \[([^\]]*)\]", cfg).group(1)
        self.assertEqual({z.strip().lstrip(":") for z in zero.split(",")}, {r[1] for r in select(q("51"), g) if r[4] == "true"})
        self.assertIn('Runs one GraphLaw request (a string-keyed map such as `%{"' + row["op_key"] + '" => "' + row["doc_example_op"] + '", ...}`)', host)
        defaults = dict(re.findall(r"^\s+(\w+): ([\d_]+),?$", cfg.split("@defaults %{", 1)[1].split("}", 1)[0], re.M))
        attrs = dict(re.findall(r"@(abi_timeout|margin|retry_base_ms|retry_max_ms) ([\d_]+)", host))
        lims = {r[1]: r[2] for r in select(q("51"), g)}
        for name, val in {**defaults, **attrs}.items():
            self.assertEqual(int(val.replace("_", "")), int(lims[name]), name)
        self.assertEqual(int(re.search(r"@max_request_bytes (\d+) \* 1_048_576", rd("ash_graphlaw/abi.ex")).group(1)) * 1048576, int(row["request_cap"]))
        self.assertEqual(int(re.search(r"@max_redirects (\d+)", rd("mix/tasks/ash_graphlaw.vendor.ex")).group(1)), int(lims["max_redirects"]))
        self.assertIn(f"@abi_timeout * {lims['initialize_timeout_mult']}", host)
        self.assertIn(f"min(retries, {lims['backoff_exp_cap']})", host)

    @unittest.skipUnless(have("mix", "elixir") and ASH_SRC.exists() and __import__("os").environ.get("QRI_BEAM_SUBSTITUTE") == "1",
                         "BLOCKED: opt-in (QRI_BEAM_SUBSTITUTE=1, ~5 min): needs /Users/sac/ash_graphlaw, mix, vendored engine")
    def test_substituted_ash_graphlaw_behaves_like_the_hand_written_one(self) -> None:
        import os
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = self.render()
        base, sub = Path(tmp.name) / "base", Path(tmp.name) / "sub"
        shutil.copytree(ASH_SRC, base, ignore=shutil.ignore_patterns(".git", "_build"))
        # test/support files that need the (unrelated, ungenerated here) capability DSL do not compile in this tree
        for f in ("lifecycle_domain.ex", "capability_case.ex"):
            (base / "test/support" / f).unlink(missing_ok=True)
        shutil.copytree(base, sub)
        for name, rel in BEAM_TARGET.items():
            (sub / rel).write_bytes(out[name])
        env = {**os.environ, "MIX_ENV": "test", "ASH_GRAPHLAW_REQUIRE_ENGINE": "1"}
        tests = ["test/unit/wasm_config_test.exs", "test/unit/engine_load_test.exs", "test/unit/abi_test.exs",
                 "test/integration/host_test.exs", "test/integration/pinned_engine_test.exs",
                 "test/integration/fuel_and_response_cap_test.exs", "test/integration/store_limits_test.exs"]
        import re
        results = {}
        for label, d in (("base", base), ("sub", sub)):
            r = subprocess.run(["mix", "test", *tests, "--include", "slow"], cwd=d, env=env, capture_output=True, text=True)
            results[label] = (set(re.findall(r"^\s+\d+\) test (.*)$", r.stdout, re.M)), re.findall(r"(\d+) tests?, (\d+) failures?", r.stdout))
            self.assertTrue(results[label][1], r.stdout[-800:] + r.stderr[-800:])
        self.assertEqual(results["base"][1], results["sub"][1])
        self.assertEqual(results["base"][0], results["sub"][0])  # same (pre-existing) failures, no new ones


if __name__ == "__main__":
    unittest.main()
