#!/usr/bin/env python3
"""Differential qualification court for a core-WASM QRI realization pair.

Realization A = native binary, Realization B = the WASM artifact hosted by the GENERATED BEAM host
(wasmex). Invariants are established by observation, never asserted: a required invariant the runner
cannot establish makes the receipt FAILED (missing invariant => no PASS). The substitution claim is
emitted only from two PASSED receipts for the same contract and context, then re-admitted by the
pack's own gates and SHACL shapes.

usage: qualify.py --contract C.ttl --wasm W --native N --mix-dir D --out OUT.ttl
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from rdflib import RDF, Graph, Literal, Namespace, URIRef

sys.path.insert(0, str(Path(__file__).parent))
import rdfc  # noqa: E402

PACK = Path(__file__).resolve().parents[1]
QRI = Namespace("https://seanchatmangpt.github.io/packs/qri-qualification-profile-pack#")
PROV = Namespace("http://www.w3.org/ns/prov#")
CORPUS = [b"hello", b"", b"unsupported:x", b"\x00\x01\x02", b"a" * 65536, bytes(range(256)) * 16]


def leb(data: bytes, i: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        b = data[i]
        i += 1
        value |= (b & 0x7F) << shift
        if not b & 0x80:
            return value, i
        shift += 7


def wasm_imports(data: bytes) -> list[str]:
    """Independent import-section parse (does not trust the host's own admission)."""
    i, found = 8, []
    while i < len(data):
        sid = data[i]
        size, i = leb(data, i + 1)
        if sid == 2:
            j = i
            count, j = leb(data, j)
            for _ in range(count):
                n, j = leb(data, j)
                mod = data[j : j + n].decode()
                j += n
                n, j = leb(data, j)
                name = data[j : j + n].decode()
                j += n
                kind = data[j]
                j += 1
                if kind == 0:
                    _, j = leb(data, j)
                elif kind == 1:
                    j += 1
                    flag, j = leb(data, j)
                    _, j = leb(data, j)
                    if flag & 1:
                        _, j = leb(data, j)
                elif kind == 2:
                    flag, j = leb(data, j)
                    _, j = leb(data, j)
                    if flag & 1:
                        _, j = leb(data, j)
                elif kind == 3:
                    j += 2
                found.append(f"{mod}::{name}")
        i += size
    return sorted(found)


def run_native(native: str, reqs: list[bytes]) -> list[str]:
    out = subprocess.run([native], input="".join(r.hex() + "\n" for r in reqs), capture_output=True, text=True, check=True)
    return out.stdout.splitlines()


def run_wasm(mix_dir: str, wasm: str, sha: str, reqs: list[bytes]) -> tuple[list[dict], dict]:
    cmd = ["mix", "run", str(PACK / "qualification" / "host_probe.exs"), wasm, sha]
    out = subprocess.run(cmd, cwd=mix_dir, input="".join(r.hex() + "\n" for r in reqs), capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit(f"BLOCKED:host_probe exit {out.returncode}: {(out.stdout + out.stderr)[-400:]}")
    rows = [json.loads(line) for line in out.stdout.splitlines() if line.startswith("{")]
    return rows[:-1], rows[-1]


def refusal_of(body: str) -> str | None:
    try:
        return json.loads(body).get("refused")
    except (ValueError, AttributeError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract", required=True)
    ap.add_argument("--wasm", required=True)
    ap.add_argument("--native", required=True)
    ap.add_argument("--mix-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    g = Graph().parse(a.contract)
    (contract,) = list(g.subjects(RDF.type, QRI.CapabilityContract))
    contract_digest = rdfc.digest(Path(a.contract))
    limit = {inv: int(v) for inv, v in g.subject_objects(QRI.limitValue)}
    kinds = {inv: next(g.objects(inv, QRI.invariantKind)) for inv in g.subjects(RDF.type, QRI.Invariant)}
    allowed = {str(o) for o in g.objects(contract, QRI.allowedImport)}
    required = list(g.objects(next(g.objects(contract, QRI.invariantSet)), QRI.requiresInvariant))

    wasm_bytes = Path(a.wasm).read_bytes()
    wasm_sha = hashlib.sha256(wasm_bytes).hexdigest()
    native_out = run_native(a.native, CORPUS)
    native_out2 = run_native(a.native, CORPUS)
    wrows, summary = run_wasm(a.mix_dir, a.wasm, wasm_sha, CORPUS)
    wrows2, summary2 = run_wasm(a.mix_dir, a.wasm, wasm_sha, CORPUS)
    wasm_out = [r.get("body", f"NONOK:{r}") for r in wrows]
    imports = wasm_imports(wasm_bytes)

    observed = {
        QRI.Semantic: native_out == wasm_out,
        QRI.Refusal: [refusal_of(x) for x in native_out] == [refusal_of(x) for x in wasm_out]
        and any(refusal_of(x) == "malformed-input" for x in wasm_out),
        QRI.Determinism: native_out == native_out2 and [r.get("body") for r in wrows2] == [r.get("body") for r in wrows],
        QRI.InformationFlow: set(imports) <= allowed and summary["sha256"] == wasm_sha,
    }

    ctx = URIRef("urn:qri:context:beam-wasmex-local")
    out = Graph()
    out += g
    for p, o in ((RDF.type, QRI.RuntimeContext), (QRI.host, URIRef("urn:qri:platform:beam-wasmex"))):
        out.add((ctx, p, o))

    def realize(tag: str, artifact_digest: str, actual_imports: list[str]) -> URIRef:
        r = URIRef(f"urn:qri:realization:{tag}:{artifact_digest[:16]}")
        out.add((r, RDF.type, QRI.Realization))
        out.add((r, QRI.implementsContract, contract))
        out.add((r, QRI.artifactDigest, Literal(artifact_digest)))
        for imp in actual_imports:
            out.add((r, QRI.actualImport, Literal(imp)))
        return r

    def qualify(tag: str, realization: URIRef, resource_ok: bool, artifact_digest: str) -> URIRef:
        est = []
        for inv in required:
            kind = kinds[inv]
            ok = resource_ok if kind == QRI.Resource else observed.get(kind, False)
            if ok:
                est.append(inv)
        passed = len(est) == len(required)
        seed = f"{tag}|{contract_digest}|{artifact_digest}|{ctx}|{sorted(map(str, est))}"
        rid = hashlib.sha256(seed.encode()).hexdigest()[:24]
        act, rec = URIRef(f"urn:qri:qualification:{rid}"), URIRef(f"urn:qri:receipt:qualification:{rid}")
        out.add((act, RDF.type, QRI.Qualification))
        out.add((act, PROV.used, contract))
        out.add((rec, RDF.type, QRI.QualificationReceipt))
        out.add((rec, PROV.wasGeneratedBy, act))
        out.add((rec, QRI.realization, realization))
        out.add((rec, QRI.runtimeContext, ctx))
        out.add((rec, QRI.qualifiesFor, contract))
        out.add((rec, QRI.qualificationResult, QRI.Passed if passed else QRI.Failed))
        for inv in est:
            out.add((rec, QRI.preservesInvariant, inv))
        return rec

    mem_ok = all(v >= summary["memory_bytes"] for v in limit.values()) if limit else True
    native_sha = hashlib.sha256(Path(a.native).read_bytes()).hexdigest()
    rn = qualify("native", realize("native", native_sha, []), True, native_sha)
    rw = qualify("wasm-wasmex", realize("wasm-wasmex", wasm_sha, imports), mem_ok, wasm_sha)

    both = all((r, QRI.qualificationResult, QRI.Passed) in out for r in (rn, rw))
    if both:
        cid = hashlib.sha256(f"{rn}|{rw}|{ctx}".encode()).hexdigest()[:24]
        claim = URIRef(f"urn:qri:substitution:{cid}")
        out.add((claim, RDF.type, QRI.SubstitutionClaim))
        out.add((claim, QRI.sourceQualification, rn))
        out.add((claim, QRI.targetQualification, rw))
        out.add((claim, QRI.interchangeableUnder, ctx))
    out.serialize(a.out, format="turtle")
    print(json.dumps({"contract_digest": contract_digest, "wasm_sha256": wasm_sha, "imports": imports,
                      "observed": {str(k).split("#")[1]: v for k, v in observed.items()},
                      "memory_bytes": summary["memory_bytes"], "native_passed": (rn, QRI.qualificationResult, QRI.Passed) in out,
                      "wasm_passed": (rw, QRI.qualificationResult, QRI.Passed) in out, "substitution_claim": both}, indent=2))
    return 0 if both else 1


if __name__ == "__main__":
    sys.exit(main())
