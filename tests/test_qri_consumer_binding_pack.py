# SPDX-License-Identifier: MIT
"""Courts for qri-consumer-binding-pack (lane E1): C1, C3, C5, C6, C7, C8, C10 plus mutation checks.

Chicago style: real ggen (via runners/consume.py), real pyshacl, real rdflib gates, real wasm,
real files in tmp dirs, real subprocesses. Nothing is doubled. Standing is never asserted here;
these courts observe admission, refusal, replay and byte identity only.
"""
from __future__ import annotations

import filecmp
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from rdflib import Graph

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "qri-consumer-binding-pack"
RUNNERS = PACK / "runners"
CONSUME = RUNNERS / "consume.py"
RUNNER = RUNNERS / "semantic_runner.py"
BINDING = PACK / "qualification" / "consumer.ttl"
BINDING_NODE = PACK / "qualification" / "consumer-node-wasi.ttl"
ASH = Path("/Users/sac/ash_affidavit")
WASM = ASH / "priv" / "affidavit" / "affidavit.wasm"
EXAMPLES = ASH / "priv" / "affidavit" / "op-examples.json"
GGEN = shutil.which("ggen")
PY = sys.executable

needs_ggen = pytest.mark.skipif(GGEN is None, reason="ggen binary not on PATH")

REFUSALS = {
    "090_pin_present": ("PIN_MISSING", "refused_identity", "R_missing_identity"),
    "092_pin_exactly_one": ("PIN_AMBIGUOUS", "refused_identity", "admission_vacuous"),
    "095_pin_digest_wellformed": ("PIN_DIGEST_MALFORMED", "refused_identity", "R_missing_identity"),
    "100_realization_unambiguous": ("AMBIGUOUS_REALIZATION", "refused_structure", "admission_vacuous"),
    "105_realization_implements_contract": ("REALIZATION_CONTRACT_MISMATCH", "refused_structure", "mu_on_O"),
    "110_authority_ceiling_none": ("CEILING_NOT_NONE", "refused_authority", "R_missing_authority"),
    "120_pin_registry_match": ("PIN_REGISTRY_MISMATCH", "refused_identity", "mu_on_O"),
    "130_contract_digest_present": ("CONTRACT_DIGEST_MISSING", "refused_identity", "R_missing_identity"),
    "140_profile_supported": ("PROFILE_UNSUPPORTED", "unsupported", "mu_on_O"),
    "150_projection_type_supported": ("PROJECTION_TYPE_UNSUPPORTED", "unsupported", "mu_on_O"),
    "160_no_authority_grant": ("AUTHORITY_GRANTED", "refused_authority", "R_missing_authority"),
}


def run(*args, cwd=None):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, cwd=cwd)


def consume(binding: Path, out: Path, pack: Path = PACK):
    return run(PY, CONSUME, "--binding", binding, "--out", out, "--pack-dir", pack)


def tree(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def mutate(text: str, old: str, new: str) -> str:
    assert text.count(old) == 1, f"mutation anchor not unique: {old!r}"
    return text.replace(old, new)


# The binding lives inside ontology.ttl's marked swap region (single-source law for frozen ggen
# v26.8.11): direct `ggen sync run` courts inject a mutated binding through the same region consume.py
# swaps. Mirrors runners/consume.py swap_binding.
REGION_BEGIN = "# ==== BINDING-SWAP-REGION BEGIN ===="
REGION_END = "# ==== BINDING-SWAP-REGION END ===="


def swap_binding_region(ontology: Path, binding_text: str) -> None:
    text = ontology.read_text(encoding="utf-8")
    begin = text.index(REGION_BEGIN)
    head = text.index("\n", begin) + 1
    tail = text.index(REGION_END, head)
    ontology.write_text(text[:head] + binding_text.rstrip("\n") + "\n\n" + text[tail:], encoding="utf-8")


@pytest.fixture(scope="module")
def projection(tmp_path_factory):
    """One real consume run on the beam-wasmex binding, shared by read-only courts."""
    out = tmp_path_factory.mktemp("qcb-beam") / "out"
    proc = consume(BINDING, out)
    assert proc.returncode == 0, proc.stderr
    return out, json.loads(proc.stdout)


# ---------------------------------------------------------------- C1 semantic admission

def test_c1_gate_court_all_alive():
    proc = run(PY, ROOT / "scripts" / "check_gate_witness_courts.py", cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "qri-consumer-binding-pack" in proc.stdout


@pytest.mark.parametrize("gate", sorted(REFUSALS))
def test_c1_exact_stem_pairs_judged_by_runner(gate):
    for expectation in ("pass", "fail"):
        proc = run(PY, RUNNER, "--gate", PACK / "gates" / f"{gate}.rq",
                   "--witness", PACK / "witnesses" / expectation / f"{gate}.ttl",
                   "--expectation", expectation)
        assert proc.returncode == 0, (gate, expectation, proc.stdout, proc.stderr)


def test_c1_extra_witnesses_fire_only_their_gate():
    proc = run(PY, RUNNER, "--extras")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert json.loads(proc.stdout)["failures"] == []


@pytest.mark.parametrize("binding", [BINDING, BINDING_NODE])
def test_c1_shacl_conforms_on_real_bindings(binding):
    import pyshacl
    conforms, _, text = pyshacl.validate(Graph().parse(binding),
                                         shacl_graph=Graph().parse(PACK / "shapes" / "qcb.shacl.ttl"),
                                         inference="none")
    assert conforms, text


def test_c1_shacl_rejects_non_none_ceiling_in_witness():
    import pyshacl
    conforms, _, _ = pyshacl.validate(
        Graph().parse(PACK / "witnesses" / "fail" / "110_authority_ceiling_none.ttl"),
        shacl_graph=Graph().parse(PACK / "shapes" / "qcb.shacl.ttl"), inference="none")
    assert not conforms


@needs_ggen
def test_c1_marketplace_check_real_ggen_double_pass():
    proc = run(PY, ROOT / "scripts" / "marketplace.py", "check", "qri-consumer-binding-pack", cwd=ROOT)
    assert proc.returncode == 0, proc.stdout + proc.stderr


# ---------------------------------------------------------------- C3 typed refusal, zero files

@needs_ggen
@pytest.mark.parametrize("gate", sorted(REFUSALS))
def test_c3_each_fail_witness_refuses_typed_with_zero_files(gate, tmp_path):
    code, klass, broken = REFUSALS[gate]
    out = tmp_path / "out"
    proc = consume(PACK / "witnesses" / "fail" / f"{gate}.ttl", out)
    # UNSUPPORTED is not REFUSED: distinct exit code and distinct top-level key
    assert proc.returncode == (7 if klass == "unsupported" else 2), proc.stdout + proc.stderr
    refused = json.loads(proc.stdout)["unsupported" if klass == "unsupported" else "refused"]
    assert (refused["code"], refused["class"], refused["broken_term"]) == (code, klass, broken)
    assert refused["gate"] in (gate, "030_authority_not_from_capability")  # qri 030 is composed and sorts first
    expected_prefix = "UNSUPPORTED" if klass == "unsupported" else "REFUSED"
    assert refused["standing_literal"] == f"{expected_prefix}:{code}"
    assert not out.exists()


@needs_ggen
def test_c3_ggen_itself_refuses_ambiguous_binding_with_empty_generated(tmp_path):
    """Bypass consume.py: ggen sync's own [law].gates is the transport, no file emitted."""
    capsule = tmp_path / "cap"
    shutil.copytree(PACK, capsule / PACK.name, ignore=shutil.ignore_patterns("generated", ".ggen-v2", "__pycache__", "tests"))
    shutil.copytree(PACK.parent / "qri-qualification-profile-pack", capsule / "qri-qualification-profile-pack",
                    ignore=shutil.ignore_patterns(".ggen-v2", "__pycache__"))
    consumer = capsule / PACK.name
    text = BINDING.read_text(encoding="utf-8")
    text = mutate(text, "qcb:chosenRealization ab:realization ;",
                  "qcb:candidateRealization ab:realization, ab:realizationB ;")
    text += "\nab:realizationB a qri:Realization .\n"
    swap_binding_region(consumer / "ontology.ttl", text)
    proc = run(GGEN, "sync", "run", cwd=consumer)
    assert proc.returncode != 0
    assert "AMBIGUOUS_REALIZATION" in proc.stdout + proc.stderr
    assert not (consumer / "generated").exists() or not any((consumer / "generated").rglob("*.*"))


@needs_ggen
def test_c3_declared_contract_digest_mismatch_refuses(tmp_path):
    text = mutate(BINDING.read_text(encoding="utf-8"),
                  'qri:contractDigest "f156c190c6c6', 'qri:contractDigest "a156c190c6c6')
    binding = tmp_path / "b.ttl"
    binding.write_text(text, encoding="utf-8")
    out = tmp_path / "out"
    proc = consume(binding, out)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    refused = json.loads(proc.stdout)["refused"]
    assert refused["code"] == "CONTRACT_DIGEST_MISMATCH"
    assert refused["declared"] != refused["computed"]
    assert not out.exists()


# ---------------------------------------------------------------- C5 authority non-escalation

@needs_ggen
@pytest.mark.parametrize("variant", ["OBSERVE", "missing"])
def test_c5_ceiling_mutations_refuse(variant, tmp_path):
    text = BINDING.read_text(encoding="utf-8")
    new = 'qcb:authorityCeiling "OBSERVE" ;' if variant == "OBSERVE" else ""
    binding = tmp_path / "b.ttl"
    binding.write_text(mutate(text, 'qcb:authorityCeiling "NONE" ;', new), encoding="utf-8")
    out = tmp_path / "out"
    proc = consume(binding, out)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert json.loads(proc.stdout)["refused"]["code"] == "CEILING_NOT_NONE"
    assert not out.exists()


def test_c5_generated_files_carry_only_ceiling_none(projection):
    out, summary = projection
    assert summary["authority_ceiling"] == "NONE"
    receipt = json.loads((out / "projection-receipt.json").read_text(encoding="utf-8"))
    assert receipt["authority_ceiling"] == "NONE"
    blob = "\n".join(p.read_text(encoding="utf-8") for p in out.rglob("*") if p.is_file())
    assert "ALIVE" not in json.dumps(receipt)
    for forbidden in ('authority_ceiling": "OBSERVE', "authority = OBSERVE", "grantsAuthority"):
        assert forbidden not in blob


@pytest.mark.skipif(shutil.which("node") is None or not WASM.exists() or not EXAMPLES.exists(),
                    reason="node or the real wasm/op-examples unavailable")
def test_c5_generated_node_authority_test_passes_on_real_module(tmp_path):
    out = tmp_path / "out"
    assert consume(BINDING_NODE, out).returncode == 0
    env = {"AUTHORITY_WASM": str(WASM), "AUTHORITY_EXAMPLES": str(EXAMPLES), "PATH": __import__("os").environ["PATH"]}
    proc = subprocess.run(["node", "--test", str(out / "node-wasi" / "authority-boundary.test.mjs")],
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 0, proc.stdout + proc.stderr


# ---------------------------------------------------------------- mutation checks (anti-vacuity)

def test_mutation_vacuous_gate_110_makes_court_fail(tmp_path):
    """Replace gate 110 with a gate that never fires: the exact-stem fail leg must now fail."""
    pack = tmp_path / "pack"
    shutil.copytree(PACK, pack, ignore=shutil.ignore_patterns("generated", ".ggen-v2", "__pycache__"))
    gate = pack / "gates" / "110_authority_ceiling_none.rq"
    gate.write_text("SELECT ?subject ?code WHERE { ?subject <urn:never> ?code . } ORDER BY ?subject\n",
                    encoding="utf-8")
    runner = pack / "runners" / "semantic_runner.py"
    fail = run(PY, runner, "--gate", gate, "--witness", pack / "witnesses" / "fail" / "110_authority_ceiling_none.ttl",
               "--expectation", "fail")
    assert fail.returncode == 2, fail.stdout + fail.stderr
    # control: the unmutated gate satisfies the same leg
    ok = run(PY, RUNNER, "--gate", PACK / "gates" / "110_authority_ceiling_none.rq",
             "--witness", PACK / "witnesses" / "fail" / "110_authority_ceiling_none.ttl", "--expectation", "fail")
    assert ok.returncode == 0


@needs_ggen
def test_mutation_deleted_gate_110_with_observe_is_not_admitted_silently(tmp_path):
    """Remove gate 110 from a pack copy and inject ceiling OBSERVE: the court for that copy fails
    (its fail witness can no longer be judged) and the binding must not yield a projection."""
    pack = tmp_path / "pack"
    shutil.copytree(PACK, pack, ignore=shutil.ignore_patterns("generated", ".ggen-v2", "__pycache__"))
    shutil.copytree(PACK.parent / "qri-qualification-profile-pack", tmp_path / "qri-qualification-profile-pack",
                    ignore=shutil.ignore_patterns(".ggen-v2", "__pycache__"))
    (pack / "gates" / "110_authority_ceiling_none.rq").unlink()
    court = run(PY, pack / "runners" / "semantic_runner.py", "--gate", pack / "gates" / "110_authority_ceiling_none.rq",
                "--witness", pack / "witnesses" / "fail" / "110_authority_ceiling_none.ttl", "--expectation", "fail")
    assert court.returncode == 3, court.stdout + court.stderr  # structural: gate absent, court cannot pass
    binding = tmp_path / "b.ttl"
    binding.write_text(mutate(BINDING.read_text(encoding="utf-8"),
                              'qcb:authorityCeiling "NONE" ;', 'qcb:authorityCeiling "OBSERVE" ;'), encoding="utf-8")
    out = tmp_path / "out"
    proc = consume(binding, out, pack=pack)
    assert proc.returncode != 0, "OBSERVE ceiling produced a projection with gate 110 removed"
    assert not out.exists()


@needs_ggen
def test_mutation_two_realizations_no_selection_refuses_ambiguous_with_empty_output(tmp_path):
    text = mutate(BINDING.read_text(encoding="utf-8"), "qcb:chosenRealization ab:realization ;",
                  "qcb:candidateRealization ab:realization, ab:realizationB ;")
    binding = tmp_path / "b.ttl"
    binding.write_text(text + "\nab:realizationB a qri:Realization .\n", encoding="utf-8")
    out = tmp_path / "out"
    proc = consume(binding, out)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    refused = json.loads(proc.stdout)["refused"]
    assert refused["code"] == "AMBIGUOUS_REALIZATION"
    assert refused["standing_literal"] == "REFUSED:AMBIGUOUS_REALIZATION"
    assert not out.exists() or list(out.rglob("*")) == []


# ---------------------------------------------------------------- C6 pin identity

def test_c6_pin_in_generated_equals_real_wasm(projection):
    if not WASM.exists():
        pytest.skip("real wasm unavailable")
    import hashlib
    out, _ = projection
    pin = json.loads((out / "artifact-pin.json").read_text(encoding="utf-8"))
    data = WASM.read_bytes()
    assert pin["sha256"] == hashlib.sha256(data).hexdigest()
    assert pin["bytes"] == len(data)


@pytest.mark.skipif(shutil.which("node") is None or not WASM.exists(), reason="node or real wasm unavailable")
def test_c6_node_host_check_ok_and_tamper_refused(tmp_path):
    out = tmp_path / "out"
    assert consume(BINDING_NODE, out).returncode == 0
    host = out / "node-wasi" / "host.mjs"
    ok = run("node", host, "--check", WASM)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    tampered = tmp_path / "tampered.wasm"
    data = bytearray(WASM.read_bytes())
    data[-1] ^= 0x01
    tampered.write_bytes(bytes(data))
    bad = run("node", host, "--check", tampered)
    assert bad.returncode == 3, bad.stdout + bad.stderr
    body = json.loads(bad.stdout)
    assert body["code"] == "wasm_digest_mismatch" and body["ok"] is False


# ---------------------------------------------------------------- C7 replay

@needs_ggen
def test_c7_two_runs_byte_identical_outputs_and_summary(tmp_path):
    runs = []
    for name in ("r1", "r2"):
        out = tmp_path / name
        proc = consume(BINDING, out)
        assert proc.returncode == 0, proc.stderr
        runs.append((tree(out), proc.stdout))
    assert runs[0][0] == runs[1][0]
    assert runs[0][1] == runs[1][1]
    assert "projection-receipt.json" in runs[0][0]


def test_c7_receipt_digests_bind_to_outputs(projection):
    out, summary = projection
    receipt = json.loads((out / "projection-receipt.json").read_text(encoding="utf-8"))
    assert receipt["binding_digest"] == summary["binding_digest"]
    assert receipt["contract_digest"] == summary["contract_digest"]
    assert receipt["output_digest"] == summary["output_digest"]


@needs_ggen
def test_c7_receipt_changes_when_pack_content_changes(tmp_path):
    """Replay identity is real: a one-byte pack change moves pack_content_digest in the receipt."""
    pack = tmp_path / "pack"
    shutil.copytree(PACK, pack, ignore=shutil.ignore_patterns("generated", ".ggen-v2", "__pycache__"))
    shutil.copytree(PACK.parent / "qri-qualification-profile-pack", tmp_path / "qri-qualification-profile-pack",
                    ignore=shutil.ignore_patterns(".ggen-v2", "__pycache__"))
    gate = pack / "gates" / "150_projection_type_supported.rq"
    gate.write_text(gate.read_text(encoding="utf-8") + "\n# replay-identity mutation\n", encoding="utf-8")
    a, b = tmp_path / "a", tmp_path / "b"
    assert consume(BINDING, a).returncode == 0
    assert consume(BINDING, b, pack=pack).returncode == 0, "mutated pack copy failed to consume"
    ra = json.loads((a / "projection-receipt.json").read_text(encoding="utf-8"))
    rb = json.loads((b / "projection-receipt.json").read_text(encoding="utf-8"))
    assert ra["pack_content_digest"] != rb["pack_content_digest"]
    assert ra["binding_digest"] == rb["binding_digest"]


# ---------------------------------------------------------------- C8 regeneration equals committed

def test_c8_generated_tree_in_pack_equals_fresh_consume(projection):
    out, _ = projection
    committed = {k: v for k, v in tree(PACK / "generated").items() if not k.startswith("profiles/")}
    assert tree(out) == committed


def test_c8_node_wasi_generated_tree_equals_fresh_consume(tmp_path):
    out = tmp_path / "out"
    assert consume(BINDING_NODE, out).returncode == 0
    committed_root = PACK / "generated" / "profiles" / "node-wasi"
    assert tree(out) == tree(committed_root)


BEAM = ["abi", "wasm_config", "engine_load", "host", "pool"]


@pytest.mark.skipif(not (ASH / "lib" / "ash_affidavit").is_dir(), reason="ash_affidavit checkout unavailable")
def test_c8_beam_host_and_manifest_byte_identical_to_ash_affidavit(projection):
    out, _ = projection
    for name in BEAM:
        assert filecmp.cmp(out / "beam-host" / f"{name}.ex", ASH / "lib" / "ash_affidavit" / f"{name}.ex", shallow=False), name
    for task in ("vendor", "verify"):
        assert filecmp.cmp(out / "beam-host" / f"{task}_task.ex", ASH / "lib" / "mix" / "tasks" / f"ash_affidavit.{task}.ex",
                           shallow=False), task
    assert filecmp.cmp(out / "MANIFEST.json", ASH / "priv" / "affidavit" / "MANIFEST.json", shallow=False)


# ---------------------------------------------------------------- no private semantics / hygiene

def test_no_dependency_on_unlanded_packs():
    for path in PACK.rglob("*"):
        if path.is_file() and path.suffix in {".toml", ".ttl", ".rq", ".py", ".md", ".tmpl", ".json"} \
                and "tests" not in path.parts and "generated" not in path.parts:
            body = path.read_text(encoding="utf-8", errors="ignore")
            assert "wasi-json-abi-pack" not in body and "graphlaw-ash-capability-pack" not in body, path


# ---------------------------------------------------------------- repair courts (audit defects)

NODE_TEXT = BINDING_NODE.read_text(encoding="utf-8")
PIN2 = ('\nab:pin2 a qcb:ArtifactPin ; qcb:checksum ab:checksum ; dcat:byteSize "1"^^xsd:nonNegativeInteger ;'
        ' qcb:registrySha256 "ebac457843cd2322af575f02583a4a2a2a11a2488de6ee0eabef468861ebe61b" .'
        '\nab:binding qcb:artifactPin ab:pin2 .\n')
ODRL = "\n@prefix odrl: <http://www.w3.org/ns/odrl/2/> .\n"

AUTHORITY_MUTATIONS = {
    "odrl-permission-on-realization": lambda s: s + ODRL + "ab:realization odrl:permission ab:x .\n",
    "grants-on-realization": lambda s: s + '\nab:realization qri:grantsAuthority "DO" .\n',
    "grants-on-binding": lambda s: mutate(s, 'qcb:authorityCeiling "NONE" ;', 'qcb:authorityCeiling "NONE" ; qri:grantsAuthority "DO" ;'),
    "grants-on-pin": lambda s: s + '\nab:pin qri:grantsAuthority "DO" .\n',
}


@needs_ggen
@pytest.mark.parametrize("name", sorted(AUTHORITY_MUTATIONS))
def test_authority_grants_refuse_typed_with_zero_files(name, tmp_path):
    binding = tmp_path / "b.ttl"
    binding.write_text(AUTHORITY_MUTATIONS[name](NODE_TEXT), encoding="utf-8")
    out = tmp_path / "out"
    proc = consume(binding, out)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    refused = json.loads(proc.stdout)["refused"]
    assert (refused["code"], refused["class"], refused["broken_term"]) == ("AUTHORITY_GRANTED", "refused_authority", "R_missing_authority")
    assert not out.exists()


def direct_ggen_capsule(tmp_path, manifest, text):
    capsule = tmp_path / "cap"
    shutil.copytree(PACK, capsule / PACK.name, ignore=shutil.ignore_patterns("generated", ".ggen-v2", "__pycache__", "tests"))
    shutil.copytree(PACK.parent / "qri-qualification-profile-pack", capsule / "qri-qualification-profile-pack",
                    ignore=shutil.ignore_patterns(".ggen-v2", "__pycache__"))
    consumer = capsule / PACK.name
    if manifest != "ggen.toml":
        shutil.copyfile(consumer / manifest, consumer / "ggen.toml")
    swap_binding_region(consumer / "ontology.ttl", text)
    return consumer


@needs_ggen
@pytest.mark.parametrize("name,mutator,code", [
    ("grants", AUTHORITY_MUTATIONS["grants-on-realization"], "AUTHORITY_GRANTED"),
    ("two-pins", lambda s: s + PIN2, "PIN_AMBIGUOUS"),
    ("ceiling-langtag", lambda s: mutate(s, 'qcb:authorityCeiling "NONE" ;', 'qcb:authorityCeiling "NONE"@en ;'), "CEILING_NOT_NONE"),
    ("other-contract", lambda s: mutate(s, "qri:implementsContract ab:contract", "qri:implementsContract ab:other"), "REALIZATION_CONTRACT_MISMATCH"),
])
def test_ggen_sync_itself_refuses_node_binding_defects(name, mutator, code, tmp_path):
    """Transport is direct `ggen sync run` (no consume.py): the [law].gates alone must refuse, zero files."""
    consumer = direct_ggen_capsule(tmp_path, "ggen-node-wasi.toml", mutator(NODE_TEXT))
    proc = run(GGEN, "sync", "run", cwd=consumer)
    assert proc.returncode != 0
    assert code in proc.stdout + proc.stderr
    generated = consumer / "generated"
    assert not generated.exists() or not any(generated.rglob("*.*"))


@needs_ggen
@pytest.mark.parametrize("name,mutator", [
    ("bytes-zero", lambda s: mutate(s, 'dcat:byteSize "660847"', 'dcat:byteSize "0"')),
    ("ceiling-token-datatype", lambda s: mutate(s, 'qcb:authorityCeiling "NONE" ;', 'qcb:authorityCeiling "NONE"^^xsd:token ;')),
])
def test_shacl_only_defects_are_typed_refusals_not_untyped_reports(name, mutator, tmp_path):
    binding = tmp_path / "b.ttl"
    binding.write_text(mutator(NODE_TEXT), encoding="utf-8")
    out = tmp_path / "out"
    proc = consume(binding, out)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    refused = json.loads(proc.stdout)["refused"]
    assert refused["code"] in ("SHAPE_NONCONFORMANT", "CEILING_NOT_NONE")
    assert refused["standing_literal"] == f"REFUSED:{refused['code']}"
    assert refused["broken_term"] and refused["class"]
    assert not out.exists()


@needs_ggen
def test_chosen_realization_outside_candidates_or_for_another_contract_is_refused(tmp_path):
    for name, text in {
        "no-implements": mutate(NODE_TEXT, "qri:implementsContract ab:contract", "a qri:Realization"),
        "not-candidate": mutate(NODE_TEXT, "qcb:chosenRealization ab:realization ;",
                                "qcb:chosenRealization ab:realization ; qcb:candidateRealization ab:candA ;")
        + "\nab:candA a qri:Realization ; qri:implementsContract ab:contract .\n",
    }.items():
        binding = tmp_path / f"{name}.ttl"
        binding.write_text(text, encoding="utf-8")
        out = tmp_path / name
        proc = consume(binding, out)
        assert proc.returncode == 2, (name, proc.stdout + proc.stderr)
        assert json.loads(proc.stdout)["refused"]["code"] == "REALIZATION_CONTRACT_MISMATCH"
        assert not out.exists()


def test_shacl_fails_closed_when_pyshacl_is_unavailable(tmp_path):
    """A real directory holding a pyshacl.py that cannot import stands in for the absent library on PYTHONPATH."""
    block = tmp_path / "block"
    block.mkdir()
    (block / "pyshacl.py").write_text('raise ImportError("pyshacl blocked for this run")\n', encoding="utf-8")
    out = tmp_path / "out"
    env = {"PATH": __import__("os").environ["PATH"], "PYTHONPATH": str(block)}
    proc = subprocess.run([PY, str(CONSUME), "--binding", str(BINDING_NODE), "--out", str(out)],
                          capture_output=True, text=True, env=env)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert "fails closed" in proc.stderr
    assert not out.exists()


def test_committed_generated_trees_exist_for_both_profiles():
    assert (PACK / "generated" / "beam-host" / "host.ex").is_file()
    assert (PACK / "generated" / "profiles" / "node-wasi" / "node-wasi" / "host.mjs").is_file()
    assert (PACK / "generated" / "profiles" / "node-wasi" / "projection-receipt.json").is_file()


# ---------------------------------------------------------------- G1 courts: SRFC executable checks, alignment, naming

import re  # noqa: E402

from rdflib import RDF, RDFS, SKOS, Namespace, URIRef  # noqa: E402
from rdflib.namespace import OWL  # noqa: E402

SRFC = next((ROOT / "docs" / "rfc").glob("SRFC-001-*.md"))
QCB_NS = "https://seanchatmangpt.github.io/packs/qri-consumer-binding-pack#"
EXEMPT_VOCABULARIES = {"prov-o", "dcat", "spdx", "odrl", "skos", "shacl", "owl-time", "digest"}


def srfc_text() -> str:
    return SRFC.read_text(encoding="utf-8")


def srfc_normative(text: str) -> str:
    return text[text.index("# 5. "):text.index("# 14. ")]


def srfc_forbidden(text: str) -> list[str]:
    """The enumerated forbidden-name list of SRFC section 15 (the fenced block after the neutrality scan)."""
    section = text[text.index("# 15. "):]
    block = re.search(r"Neutrality scan\..*?```text\n(.*?)```", section, re.S).group(1)
    return [name.strip().lower() for name in block.replace("\n", " ").split(",") if name.strip()]


def srfc_requirements(text: str):
    body = srfc_normative(text)
    parts = re.split(r"^## (R\d+) — ", body, flags=re.M)
    blocks = []
    for index in range(1, len(parts), 2):
        # a requirement block ends at the next top-level heading
        blocks.append((parts[index], re.split(r"^# ", parts[index + 1], maxsplit=1, flags=re.M)[0]))
    return blocks


def neutrality_hits(normative: str, forbidden: list[str]) -> list[str]:
    words = re.findall(r"[A-Za-z0-9_]+", normative)
    return sorted({w.lower() for w in words if w.lower() in set(forbidden)})


def test_srfc_neutrality_scan_zero_matches_and_scan_is_not_vacuous():
    text = srfc_text()
    forbidden = srfc_forbidden(text)
    assert len(forbidden) >= 30 and "ggen" in forbidden and "wasm" in forbidden and "json" in forbidden
    assert not set(forbidden) & EXEMPT_VOCABULARIES
    normative = srfc_normative(text)
    assert neutrality_hits(normative, forbidden) == []
    # the scan observes its own forbidden transition: a leaked technology name is found
    assert neutrality_hits(normative + "\nThe runtime is Elixir over WASM.\n", forbidden) == ["elixir", "wasm"]


def test_srfc_atomicity_one_obligation_one_invariant_one_falsifier():
    text = srfc_text()
    blocks = srfc_requirements(text)
    ids = [name for name, _ in blocks]
    assert ids == [f"R{n}" for n in range(1, len(blocks) + 1)]
    assert f"requirement headings are numbered consecutively from R1 and their number is {len(blocks)}." in text
    modal = re.compile(r"\b(must|shall|should|may|required|recommended)\b", re.I)
    for name, block in blocks:
        assert len(re.findall(r"\bMUST\b", block)) == 1, name
        assert len(re.findall(r"^Invariant:", block, re.M)) == 1, name
        assert len(re.findall(r"^Falsifier:", block, re.M)) == 1, name
        hits = [m.group(0) for m in modal.finditer(block)]
        assert hits == ["MUST"], (name, hits)
    # totals over sections 5-13 equal the heading count (the section 15 statement)
    normative = srfc_normative(text)
    assert len(re.findall(r"\bMUST\b", normative)) == len(blocks)
    assert len(re.findall(r"^Falsifier:", normative, re.M)) == len(blocks)


def test_srfc_names_normative_alignment_sources_and_alignment_requirements():
    text = srfc_text()
    section5 = text[text.index("# 5. "):text.index("# 6. ")]
    for source in ("PROV-O", "DCAT", "SPDX", "ODRL", "SKOS", "SHACL", "OWL-Time"):
        assert re.search(rf"^{re.escape(source)}\s+—", section5, re.M), source
    titles = {name: block.splitlines()[0] for name, block in srfc_requirements(text)}
    assert "Alignment Is Explicit" in titles["R2"] and "Subsumption Or Delta" in titles["R3"]
    assert "delta justification" in text.lower()


def test_srfc_refusal_table_equals_ontology_scheme():
    text = srfc_text()
    table = text[text.index("codes (minimum set):"):text.index("standing string forms")]
    rows = {m[0]: (m[1], m[2]) for m in re.findall(r"^  ([A-Z_]+)\s+(\w+)\s+(\w+)$", table, re.M)}
    onto = Graph().parse(PACK / "ontology.ttl")
    scheme = {}
    for concept in onto.subjects(SKOS.inScheme, URIRef(QCB_NS + "generation-refusals")):
        one = lambda prop: str(next(onto.objects(concept, URIRef(QCB_NS + prop))))
        scheme[str(next(onto.objects(concept, SKOS.notation)))] = (one("refusalClass"), one("brokenTerm"))
    assert rows == scheme


# ---- alignment: every qcb term is subsumed by, or justified against, a published term

QCB_TERM_TYPES = (RDFS.Class, RDF.Property, SKOS.ConceptScheme)
RELATIONS = (SKOS.relatedMatch, SKOS.closeMatch, SKOS.exactMatch, RDFS.seeAlso)


def qcb_terms(onto: Graph) -> set:
    return {s for t in QCB_TERM_TYPES for s in onto.subjects(RDF.type, t) if str(s).startswith(QCB_NS)}


def unaligned_terms(graph: Graph) -> list[str]:
    """Terms with neither an entailing link to a non-qcb term nor (a scopeNote and a non-qcb correspondence)."""
    bad = []
    for term in sorted(qcb_terms(graph)):
        parents = [o for p in (RDFS.subClassOf, RDFS.subPropertyOf) for o in graph.objects(term, p)
                   if isinstance(o, URIRef) and not str(o).startswith(QCB_NS)]
        matches = [o for p in RELATIONS for o in graph.objects(term, p)
                   if isinstance(o, URIRef) and not str(o).startswith(QCB_NS)]
        noted = any(graph.objects(term, SKOS.scopeNote))
        if not parents and not (noted and matches):
            bad.append(str(term))
    return bad


def alignment_graph() -> Graph:
    return Graph().parse(PACK / "ontology.ttl") + Graph().parse(PACK / "ontology" / "alignments.ttl")


def test_every_qcb_term_is_subsumed_or_justified_against_a_public_term():
    graph = alignment_graph()
    assert len(qcb_terms(graph)) >= 25
    assert unaligned_terms(graph) == []
    # the check observes its own forbidden transition: drop one justification, then one correspondence
    victim = URIRef(QCB_NS + "outputDigest")
    no_note = Graph()
    for triple in graph:
        if not (triple[0] == victim and triple[1] == SKOS.scopeNote):
            no_note.add(triple)
    assert unaligned_terms(no_note) == [str(victim)]
    no_match = Graph()
    for triple in graph:
        if not (triple[0] == victim and triple[1] in RELATIONS):
            no_match.add(triple)
    assert unaligned_terms(no_match) == [str(victim)]


def test_refusal_codes_are_instances_of_the_qri_refusal_class():
    onto = Graph().parse(PACK / "ontology.ttl")
    qri_code = URIRef("https://seanchatmangpt.github.io/packs/qri-qualification-profile-pack#RefusalCode")
    codes = set(onto.subjects(SKOS.inScheme, URIRef(QCB_NS + "generation-refusals")))
    assert len(codes) == 13 and all((c, RDF.type, qri_code) in onto for c in codes)


def test_published_terms_are_reused_not_duplicated():
    onto = Graph().parse(PACK / "ontology.ttl")
    assert (URIRef(QCB_NS + "contractDigest"), RDF.type, RDF.Property) not in onto
    assert not [p for p in PACK.rglob("*.ttl") if "qcb:contractDigest" in p.read_text(encoding="utf-8")]
    assert (URIRef(QCB_NS + "profileId"), RDFS.subPropertyOf, URIRef("http://purl.org/dc/terms/identifier")) in onto
    # the receipt's contract digest is the contract's own qri:contractDigest, reached through the binding
    receipt = json.loads((PACK / "generated" / "projection-receipt.json").read_text(encoding="utf-8"))
    declared = re.search(r'qri:contractDigest "([0-9a-f]{64})"', BINDING.read_text(encoding="utf-8")).group(1)
    assert receipt["contract_digest"] == declared


def test_no_generator_product_name_in_qcb_vocabulary_or_receipts():
    for path in [PACK / "ontology.ttl", PACK / "ontology" / "alignments.ttl", PACK / "shapes" / "qcb.shacl.ttl",
                 PACK / "templates" / "projection-receipt.json.tmpl", RUNNERS / "receipt.py"]:
        body = path.read_text(encoding="utf-8")
        assert "ggenVersion" not in body and "ggen_version" not in body, path
    onto = Graph().parse(PACK / "ontology.ttl")
    assert (URIRef(QCB_NS + "generatorVersion"), RDF.type, RDF.Property) in onto
    for receipt_path in (PACK / "generated" / "projection-receipt.json",
                         PACK / "generated" / "profiles" / "node-wasi" / "projection-receipt.json"):
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        assert "generator_version" in receipt and "ggen_version" not in receipt
    for witness in (PACK / "witnesses").rglob("*.ttl"):
        assert "ggenVersion" not in witness.read_text(encoding="utf-8"), witness


# ---- typed refusal transport

BASE_REFUSAL_KEYS = {"broken_term", "class", "code", "gate", "standing_literal"}


@pytest.mark.parametrize("gate", sorted(REFUSALS))
def test_refusal_detail_shape_is_identical_for_refused_and_unsupported(gate, tmp_path):
    """Transport contract: top-level key and exit code separate REFUSED from UNSUPPORTED; the detail record
    has the same keys for both (extras only for the runner-side digest/shape codes)."""
    code, klass, _ = REFUSALS[gate]
    proc = consume(PACK / "witnesses" / "fail" / f"{gate}.ttl", tmp_path / "out")
    payload = json.loads(proc.stdout)
    key = "unsupported" if klass == "unsupported" else "refused"
    assert set(payload) == {"also", key}
    assert proc.returncode == (7 if key == "unsupported" else 2)
    assert set(payload[key]) == BASE_REFUSAL_KEYS


def test_runner_side_codes_are_scheme_concepts_and_use_the_shared_shape(tmp_path):
    onto = Graph().parse(PACK / "ontology.ttl")
    notations = {str(o) for o in onto.objects(None, SKOS.notation)}
    assert {"CONTRACT_DIGEST_MISMATCH", "SHAPE_NONCONFORMANT"} <= notations
    source = CONSUME.read_text(encoding="utf-8")
    used = set(re.findall(r'refusal_record\(pack, "([A-Z_]+)"', source)) | set(re.findall(r'"([A-Z_]+)"\)\n', source))
    assert {"CONTRACT_DIGEST_MISMATCH", "SHAPE_NONCONFORMANT"} <= used
    assert used <= notations
    # SHACL-only defect (byte size 0): typed REFUSED with the shared keys plus violations
    text = BINDING_NODE.read_text(encoding="utf-8")
    bad = tmp_path / "b.ttl"
    bad.write_text(re.sub(r'dcat:byteSize "\d+"\^\^xsd:nonNegativeInteger', 'dcat:byteSize "0"^^xsd:nonNegativeInteger', text, count=1),
                   encoding="utf-8")
    proc = consume(bad, tmp_path / "out")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    record = json.loads(proc.stdout)["refused"]
    assert BASE_REFUSAL_KEYS <= set(record) and record["code"] == "SHAPE_NONCONFORMANT" and record["violations"]
    assert not (tmp_path / "out").exists()


# ---- pin schema identities

def test_producer_and_consumer_pin_records_have_distinct_schema_ids():
    consumer_pin = json.loads((PACK / "generated" / "artifact-pin.json").read_text(encoding="utf-8"))
    assert consumer_pin["schema"] == "qcb.artifact-pin/1"
    producer = Path("/Users/sac/affidavit/affidavit-wasm/registry/artifact-pin.json")
    if not producer.is_file():
        pytest.skip("affidavit checkout unavailable")
    producer_pin = json.loads(producer.read_text(encoding="utf-8"))
    assert producer_pin["schema"] == "affidavit.wasm-pin/1"
    assert producer_pin["schema"] != consumer_pin["schema"]
    # the mapping documented for the ConsumerBinding pin: identity fields agree
    assert (producer_pin["sha256"], producer_pin["bytes"], producer_pin["registry_sha256"], producer_pin["abi_version"]) == \
           (consumer_pin["sha256"], consumer_pin["bytes"], consumer_pin["registry_sha256"], consumer_pin["abi_version"])


# ---------------------------------------------------------------- C10 host parity with affidavit-consumer-pack

AFC = ROOT / "packs" / "affidavit-consumer-pack"
PARITY_DRIVER = PACK / "fixtures" / "node-wasi" / "parity-affidavit-consumer.mjs"
QCB_DRIVER = PACK / "fixtures" / "node-wasi" / "drive.mjs"


def test_c10_afc_templates_have_no_frontmatter_so_path_dependency_cannot_compose_them():
    """Falsifier F1 of the composition probe: the reason the node-wasi host template is kept."""
    templates = sorted((AFC / "templates").glob("affidavit_host.*.tmpl"))
    assert len(templates) == 2, "positive control: both afc host templates exist"
    for template in templates:
        assert not template.read_text(encoding="utf-8").lstrip().startswith("---"), template.name
    assert (PACK / "templates" / "node-wasi" / "host.mjs.tmpl").read_text(encoding="utf-8").startswith("---\n")


@needs_ggen
@pytest.mark.skipif(shutil.which("node") is None or not WASM.exists() or not EXAMPLES.exists(),
                    reason="node or the real wasm/op-examples unavailable")
def test_c10_qcb_node_host_and_afc_ts_host_agree_per_op_and_on_pin_refusal(tmp_path):
    afc = tmp_path / "afc"
    shutil.copytree(AFC, afc, ignore=shutil.ignore_patterns("generated", ".ggen", ".ggen-v2", "__pycache__"))
    sync = subprocess.run([GGEN, "sync", "run"], cwd=afc, capture_output=True, text=True)
    assert sync.returncode == 0, sync.stderr[-400:]
    afc_host = afc / "generated" / "affidavit_host.ts"
    out = tmp_path / "out"
    assert consume(BINDING_NODE, out).returncode == 0
    qcb_host = out / "node-wasi" / "host.mjs"

    qcb = run("node", QCB_DRIVER, qcb_host, WASM, EXAMPLES)
    assert qcb.returncode == 0, qcb.stderr
    theirs = run("node", "--experimental-strip-types", "--no-warnings", PARITY_DRIVER, afc_host, WASM, EXAMPLES)
    assert theirs.returncode == 0, theirs.stderr
    qcb_responses, afc_responses = json.loads(qcb.stdout), json.loads(theirs.stdout)
    assert len(qcb_responses) == 14, "positive control: all fourteen op examples"
    assert qcb_responses == afc_responses

    tampered = tmp_path / "tampered.wasm"
    data = bytearray(WASM.read_bytes())
    data[-1] ^= 0x01
    tampered.write_bytes(bytes(data))
    afc_refusal = json.loads(run("node", "--experimental-strip-types", "--no-warnings", PARITY_DRIVER,
                                 afc_host, WASM, EXAMPLES, tampered).stdout)
    qcb_refusal = json.loads(run("node", qcb_host, "--check", tampered).stdout)
    assert afc_refusal == {"code": "wasm_digest_mismatch", "refused": True}
    assert qcb_refusal["code"] == afc_refusal["code"] and qcb_refusal["authority"] == "NONE"
