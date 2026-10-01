#!/usr/bin/env python3
"""Consume a ConsumerBinding: gates -> contract digest -> ggen sync (x2) -> receipt -> outputs.

UNSUPPORTED(generator-capability): the orchestration (admission before generation, a scratch capsule,
the two-pass receipt) is a fixed runner; ggen has no capability for pre-sync typed refusal JSON or for
rendering a receipt of its own outputs. Everything emitted is rendered by ggen from RDF; this script
writes no output file itself except by copying ggen's generated/ tree.

    consume.py --binding <binding.ttl> --out <dir> [--pack-dir <pack>] [--ggen <ggen>]

Exit codes: 0 projection written; 2 typed REFUSED (JSON key "refused" on stdout, ZERO files written, --out
untouched); 7 typed UNSUPPORTED (JSON key "unsupported", zero files; UNSUPPORTED is not REFUSED);
3 structural error (unparseable binding, pyshacl missing: SHACL fails closed); 4 ggen failed (nothing
written); 5 SHACL non-conformance after generation (typed SHAPE_NONCONFORMANT JSON on stdout, nothing
written); 6 replay mismatch between the two ggen passes (nothing written).
Binding SHACL non-conformance before generation is a typed REFUSED:SHAPE_NONCONFORMANT (exit 2).
Standing is never printed: it is derived from receipts elsewhere, never stored here.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import receipt  # noqa: E402
import semantic_runner  # noqa: E402

QCB, QRI = receipt.QCB, receipt.QRI
CAPSULE_SKIP = {"generated", ".ggen-v2", ".ggen", "__pycache__", "fixtures", "tests", "docs"}


def refusal_record(pack: Path, code: str, gate: str | None) -> dict:
    ontology = Graph().parse(pack / "ontology.ttl")
    for concept in ontology.subjects(SKOS.notation, Literal(code)):
        def one(prop):
            return next((str(o) for o in ontology.objects(concept, URIRef(QCB + prop))), None)
        return {"broken_term": one("brokenTerm"), "class": one("refusalClass"), "code": code,
                "gate": gate or one("refusedByGate"), "standing_literal": one("standingLiteral")}
    return {"broken_term": None, "class": None, "code": code, "gate": gate, "standing_literal": None}


def refuse(record: dict, also=()) -> int:
    unsupported = record.get("class") == "unsupported"
    print(json.dumps({"also": sorted(also), "unsupported" if unsupported else "refused": record}, sort_keys=True))
    return 7 if unsupported else 2


# Composed gates (qri) select ?subject only; the typed code they emit is fixed here.
COMPOSED_GATE_CODES = {"030_authority_not_from_capability": "AUTHORITY_GRANTED"}


def shacl_violations(data: Graph, pack: Path):
    """Run the pack's SHACL shapes. Fails closed: a missing pyshacl raises ImportError to the caller."""
    import pyshacl
    from rdflib.namespace import Namespace
    SH = Namespace("http://www.w3.org/ns/shacl#")
    conforms, results, text = pyshacl.validate(
        data, shacl_graph=Graph().parse(pack / "shapes" / "qcb.shacl.ttl"), inference="none")
    if conforms:
        return []
    found = []
    for result in results.subjects(RDF.type, SH.ValidationResult):
        one = lambda prop: next((str(o) for o in results.objects(result, prop)), None)
        found.append({"component": one(SH.sourceConstraintComponent), "focus": one(SH.focusNode),
                      "path": one(SH.resultPath)})
    return sorted(found, key=lambda v: json.dumps(v, sort_keys=True)) or [{"component": None, "focus": None, "path": None}]


def gate_files(pack: Path):
    """The pack's own gates plus the gates composed from sibling packs (profiles.toml [compose])."""
    own = sorted((pack / "gates").glob("*.rq"))
    composed = []
    profiles = tomllib.loads((pack / "profiles.toml").read_text(encoding="utf-8"))
    for sibling, spec in sorted(profiles.get("compose", {}).items()):
        composed += [(pack.parent / sibling / rel).resolve() for rel in spec["gates"]]
    return own + composed


def run_gates(pack: Path, graph: Graph):
    fired = []
    for gate in gate_files(pack):
        for row in semantic_runner.gate_rows(gate, graph):
            code = str(row[1]) if len(row) > 1 else COMPOSED_GATE_CODES[gate.stem]
            fired.append((gate.stem, code))
    return sorted(fired)


def ggen_version(ggen: str) -> str:
    out = subprocess.run([ggen, "--version"], capture_output=True, text=True, check=True).stdout
    return out.split()[1] if out.startswith("ggen ") else out.strip().splitlines()[0]


def build_capsule(pack: Path, capsule: Path, target: dict, composes) -> Path:
    consumer = capsule / pack.name
    shutil.copytree(pack, consumer, ignore=lambda d, names: [n for n in names if n in CAPSULE_SKIP and Path(d) == pack])
    for name in composes:
        shutil.copytree(pack.parent / name, capsule / name, ignore=shutil.ignore_patterns(".ggen-v2", "__pycache__"))
    if target["manifest"] != "ggen.toml":
        shutil.copyfile(consumer / target["manifest"], consumer / "ggen.toml")
    return consumer


def ggen_sync(ggen: str, consumer: Path):
    return subprocess.run([ggen, "sync", "run"], cwd=consumer, capture_output=True, text=True)


def snapshot(generated: Path):
    return receipt.tree_records(generated, generated)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--binding", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--pack-dir", type=Path, default=HERE.parent)
    parser.add_argument("--ggen", default=shutil.which("ggen") or "ggen")
    args = parser.parse_args()
    pack = args.pack_dir.resolve()

    try:
        graph = Graph().parse(args.binding.resolve())
        node = receipt.binding_node(graph)
    except Exception as error:  # unparseable binding or not exactly one ConsumerBinding
        print(json.dumps({"error": f"{type(error).__name__}: {error}"}), file=sys.stderr)
        return 3

    # 1. admission gates (same files ggen enforces through [law].gates)
    fired = run_gates(pack, graph)
    if fired:
        gate, code = fired[0]
        return refuse(refusal_record(pack, code, gate), also=[f"{g}:{c}" for g, c in fired[1:]])

    # 1b. SHACL over the binding, before any generation; typed refusal, never an untyped report
    try:
        violations = shacl_violations(graph, pack)
    except ImportError:
        print(json.dumps({"error": "pyshacl unavailable: SHACL fails closed"}), file=sys.stderr)
        return 3
    if violations:
        record = refusal_record(pack, "SHAPE_NONCONFORMANT", None)
        record["violations"] = violations
        return refuse(record)

    # 2. contract identity: the declared qri:contractDigest must equal the RDFC-1.0 digest of the closure
    contract = next(graph.objects(node, URIRef(QCB + "contract")))
    declared = str(next(graph.objects(contract, URIRef(QRI + "contractDigest"))))
    computed = receipt.contract_digest(graph, contract)
    if declared != computed:
        # RDFC-1.0 cannot be computed in SPARQL: the check is runner-side, the code is in qcb:generation-refusals
        record = refusal_record(pack, "CONTRACT_DIGEST_MISMATCH", None)
        record.update({"declared": declared, "computed": computed})
        return refuse(record)

    # 3. target by profile
    profile = str(next(graph.objects(next(graph.objects(node, URIRef(QCB + "realizationProfile"))),
                                     URIRef(QCB + "profileId"))))
    targets = tomllib.loads((pack / "profiles.toml").read_text(encoding="utf-8"))["target"]
    target = targets[profile]
    composes = tuple(target["composes"])
    pack_version = tomllib.loads((pack / "pack.toml").read_text(encoding="utf-8"))["pack"]["version"]

    with tempfile.TemporaryDirectory(prefix="qcb-consume-") as raw:
        capsule = Path(raw)
        consumer = build_capsule(pack, capsule, target, composes)
        shutil.copyfile(args.binding.resolve(), consumer / "qualification" / "consumer.ttl")
        generated = consumer / "generated"

        # 4. pass 1
        first = ggen_sync(args.ggen, consumer)
        if first.returncode != 0:
            print(first.stderr[-2000:], file=sys.stderr)
            return 4
        files1 = snapshot(generated)
        output_dig = receipt.listing_digest(files1)

        # 5. receipt facts from pass-1 outputs, SHACL over binding + receipt, pass 2 renders the receipt JSON
        gver = ggen_version(args.ggen)
        facts = receipt.receipt_turtle(
            binding=node, binding_dig=receipt.binding_digest(graph),
            pack_version=pack_version, generator_version=gver,
            pack_dig=receipt.pack_content_digest(pack, composes), output_dig=output_dig, files=files1)
        combined = (args.binding.resolve().read_text(encoding="utf-8") + "\n" + facts)
        (consumer / "qualification" / "consumer.ttl").write_text(combined, encoding="utf-8")
        try:
            post = shacl_violations(Graph().parse(data=combined, format="turtle"), pack)
        except ImportError:
            print(json.dumps({"error": "pyshacl unavailable: SHACL fails closed"}), file=sys.stderr)
            return 3
        if post:
            record = refusal_record(pack, "SHAPE_NONCONFORMANT", None)
            record["violations"] = post
            print(json.dumps({"also": [], "refused": record}, sort_keys=True))
            return 5
        second = ggen_sync(args.ggen, consumer)
        if second.returncode != 0:
            print(second.stderr[-2000:], file=sys.stderr)
            return 4
        files2 = snapshot(generated)
        carried = {p: d for p, d in files2 if p != "projection-receipt.json"}
        if sorted(carried.items()) != sorted(files1) or "projection-receipt.json" not in dict(files2):
            print(json.dumps({"error": "replay mismatch between ggen passes"}), file=sys.stderr)
            return 6

        # 6. write outputs (ggen's own generated/ tree, relative to generated/)
        args.out.mkdir(parents=True, exist_ok=True)
        for path, _ in files2:
            dest = args.out / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(generated / path, dest)

    print(json.dumps({
        "authority_ceiling": "NONE",
        "binding_digest": receipt.binding_digest(graph),
        "contract_digest": computed,
        "final_listing_digest": receipt.listing_digest(files2),
        "files": dict(files2),
        "generator_version": gver,
        "output_digest": output_dig,
        "profile": profile,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
