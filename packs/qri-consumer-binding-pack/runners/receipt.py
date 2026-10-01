#!/usr/bin/env python3
"""Identity and receipt facts for qri-consumer-binding-pack projections.

UNSUPPORTED(generator-capability): no ggen capability computes content digests of its own
inputs or outputs; this module computes them and emits the ProjectionReceipt FACTS (Turtle).
The receipt JSON itself is rendered by ggen from those facts (templates/projection-receipt.json.tmpl).

Digests (all sha256 lowercase hex):
  contract_digest   RDFC-1.0 (URDNA2015) of the closure of the bound contract, excluding the
                    qri:contractDigest triple itself (runners are reused from qri qualification/rdfc.py)
  binding_digest    RDFC-1.0 of the whole binding graph
  pack_content      sorted (path, sha256) listing of the pack sources that determine output
  output_digest     sorted (path, sha256) listing of emitted files (paths relative to generated/)
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF

PACK_ROOT = Path(__file__).resolve().parents[1]
QRI_QUAL = PACK_ROOT.parent / "qri-qualification-profile-pack" / "qualification"
if str(QRI_QUAL) not in sys.path:
    sys.path.insert(0, str(QRI_QUAL))
import rdfc  # noqa: E402  (reused from qri-qualification-profile-pack; never copied)

QRI = "https://seanchatmangpt.github.io/packs/qri-qualification-profile-pack#"
QCB = "https://seanchatmangpt.github.io/packs/qri-consumer-binding-pack#"
CONTRACT_DIGEST = URIRef(QRI + "contractDigest")

SOURCE_ROOTS = ("pack.toml", "ggen.toml", "ggen-node-wasi.toml", "targets.toml", "profiles.toml", "ontology.ttl",
                "ontology", "shapes", "gates", "templates")
DEPENDENCY_ROOTS = ("pack.toml", "ontology.ttl", "gates", "templates")


def contract_closure(graph: Graph, contract: URIRef) -> Graph:
    closure, seen, todo = Graph(), set(), [contract]
    while todo:
        node = todo.pop()
        if node in seen:
            continue
        seen.add(node)
        for s, p, o in graph.triples((node, None, None)):
            if p == CONTRACT_DIGEST:
                continue
            closure.add((s, p, o))
            if not isinstance(o, Literal):
                todo.append(o)
    return closure


def contract_digest(graph: Graph, contract: URIRef) -> str:
    return rdfc.digest(contract_closure(graph, contract))


def binding_digest(graph: Graph) -> str:
    return rdfc.digest(graph)


def listing_digest(records) -> str:
    h = hashlib.sha256()
    for path, digest in sorted(records):
        h.update(path.encode())
        h.update(b"\0")
        h.update(digest.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def tree_records(root: Path, relative_to: Path | None = None, prefix: str = ""):
    base = relative_to or root
    out = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if "__pycache__" in path.parts or path.name == ".DS_Store":
            continue
        out.append((prefix + path.relative_to(base).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
    return out


def _roots_records(pack: Path, roots, prefix: str):
    records = []
    for name in roots:
        target = pack / name
        if target.is_file():
            records.append((prefix + name, hashlib.sha256(target.read_bytes()).hexdigest()))
        elif target.is_dir():
            records.extend(tree_records(target, pack, prefix))
    return records


def pack_content_digest(pack: Path, composed: tuple[str, ...] = ()) -> str:
    records = _roots_records(pack, SOURCE_ROOTS, "")
    records += [(f"runners/{p.name}", hashlib.sha256(p.read_bytes()).hexdigest())
                for p in sorted((pack / "runners").glob("*.py"))]
    for name in composed:
        records += _roots_records(pack.parent / name, DEPENDENCY_ROOTS, f"../{name}/")
    return listing_digest(records)


def receipt_turtle(*, binding: URIRef, binding_dig: str, pack_version: str,
                   generator_version: str, pack_dig: str, output_dig: str, files) -> str:
    """ProjectionReceipt + GeneratedProjection + prov:Activity facts (authority ceiling NONE)."""
    rid, pid, aid = (f"urn:qcb:{kind}:{binding_dig}" for kind in ("receipt", "projection", "activity"))
    lines = [
        f"@prefix qcb: <{QCB}> .",
        "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "@prefix spdx: <http://spdx.org/rdf/terms#> .",
        "",
        f"<{aid}> a prov:Activity ; prov:used <{binding}> .",
        f"<{pid}> a qcb:GeneratedProjection ; qcb:projectionOf <{binding}> ; prov:wasGeneratedBy <{aid}> ;",
        f'    qcb:outputDigest "{output_dig}" ; qcb:authorityCeiling "NONE" ;',
        "    prov:hadMember " + " , ".join(f"<urn:qcb:file:{hashlib.sha256(p.encode()).hexdigest()}>" for p, _ in files) + " .",
        f"<{rid}> a qcb:ProjectionReceipt ; qcb:projection <{pid}> ;",
        f'    qcb:packVersion "{pack_version}" ; qcb:generatorVersion "{generator_version}" ;',
        f'    qcb:packContentDigest "{pack_dig}" ; qcb:bindingDigest "{binding_dig}" ;',
        f'    qcb:outputDigest "{output_dig}" ;',
        '    qcb:authorityCeiling "NONE" .',
    ]
    for path, sha in files:
        fid = hashlib.sha256(path.encode()).hexdigest()
        lines += [
            f'<urn:qcb:file:{fid}> a spdx:File ; spdx:fileName "{path}" ; spdx:checksum <urn:qcb:checksum:{fid}> .',
            f"<urn:qcb:checksum:{fid}> a spdx:Checksum ; spdx:algorithm spdx:checksumAlgorithm_sha256 ;",
            f'    spdx:checksumValue "{sha}" .',
        ]
    return "\n".join(lines) + "\n"


def binding_node(graph: Graph) -> URIRef:
    nodes = sorted(graph.subjects(RDF.type, URIRef(QCB + "ConsumerBinding")))
    if len(nodes) != 1:
        raise ValueError(f"expected exactly one qcb:ConsumerBinding, found {len(nodes)}")
    return nodes[0]


if __name__ == "__main__":
    graph = Graph().parse(sys.argv[1])
    node = binding_node(graph)
    contract = next(graph.objects(node, URIRef(QCB + "contract")))
    print(contract_digest(graph, contract))
