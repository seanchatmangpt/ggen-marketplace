#!/usr/bin/env python3
"""Qualify evidence-standing-pack's hash-chained receipt projection for real.

Checks (each prints ALIVE / UNVERIFIED / REFUSED; exit 0 only when nothing failed):
  consumer   qualification/consumer.ttl chain hashes equal the recomputed
             CanonLinesV1 digests (--regen rewrites them; default only checks)
  literal    gates/050_literal_scan.py accepts templates/ and refuses an injected literal
  gates      lawful consumer syncs through real `ggen sync run`; seal-twice, dangling
             parent and out-of-supported-set overlays are each refused by their gate
  golden     the same events yield identical per-entry digests across ts/py/rs/ex
             (and equal an independent reference + the frozen golden.expected);
             a toolchain that is not installed is reported UNVERIFIED, never skipped
  blake2b    a ChainPolicy individual selecting blake2b256 changes the generated py
             digest to blake2b(digest_size=32) and only py
  mutation   renaming one ontology individual's name changes generated output
             at exactly that token and nowhere else, in every language
  affidavit  diff of chain semantics vs the affidavit-pack (BLAKE3 rolling chain) rule
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PACK = REPO / "packs" / "evidence-standing-pack"
NS = "https://ggen.dev/ontology/evidence-standing#"
QUAL = PACK / "qualification"
VEC = QUAL / "vectors" / "golden.vec"
EXPECTED = QUAL / "vectors" / "golden.expected"
LANGS = ("ts", "py", "rs", "ex")
OUTPUT = {l: f"src/es/chain.{l}" for l in LANGS}
OUTPUT["ex"] = "lib/es/chain.ex"  # ggen relocates .ex output under lib/
GENESIS = "0" * 64

sys.path.insert(0, str(REPO / "scripts"))
import qualify_packs as q  # noqa: E402

_spec = importlib.util.spec_from_file_location("literal_scan", PACK / "gates" / "050_literal_scan.py")
literal_scan = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(literal_scan)


def sh(cmd, cwd, timeout=120):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------- reference (independent of templates)
def digest(alg: str, text: str) -> str:
    data = text.encode("utf-8")
    if alg == "blake2b256":
        return hashlib.blake2b(data, digest_size=32).hexdigest()
    return hashlib.new(alg, data).hexdigest()


def canon(e: dict, fields=("entry_id", "parent_hash", "phase", "standing", "subject", "action")) -> str:
    return "\n".join(f"{f}={e[f]}" for f in fields)


STANDINGS = {"unknown", "partial_alive", "alive", "blocked", "build_broken", "unsupported"}


def reference_run(vec_text: str, alg: str = "sha256") -> list[str]:
    """Spec-level model of append/seal/verify, written from the rules, not from a template."""
    out: list[str] = []
    chain: list[dict] = []

    def mk(i, ph, st, su, ac, seal):
        e = {"entry_id": i, "parent_hash": chain[-1]["hash"] if chain else GENESIS,
             "phase": ph, "standing": st, "subject": su, "action": ac, "seal": seal}
        e["hash"] = digest(alg, canon(e))
        return e

    def ok_verify():
        prev, seals = GENESIS, 0
        for e in chain:
            if e["parent_hash"] != prev or e["hash"] != digest(alg, canon(e)):
                return False
            seals += e["seal"]
            prev = e["hash"]
        return seals <= 1 and (seals == 0 or chain[-1]["seal"])

    for raw in vec_text.split("\n"):
        if not raw or raw.startswith("#"):
            continue
        p = raw.split("|")
        if raw.startswith("case "):
            chain = []
            out.append("case " + raw[5:])
        elif p[0] == "append":
            _, i, ph, st, su, ac = p
            sealed = any(e["seal"] for e in chain)
            bad = ph not in ("pending", "outcome") or st not in STANDINGS
            no_pending = ph == "outcome" and not any(e["phase"] == "pending" and e["action"] == ac for e in chain)
            if sealed or bad or no_pending:
                out.append("err")
            else:
                chain.append(mk(i, ph, st, su, ac, False))
                out.append("ok " + chain[-1]["hash"])
        elif p[0] == "seal":
            _, i, st, su = p
            if any(e["seal"] for e in chain) or st not in STANDINGS:
                out.append("err")
            else:
                chain.append(mk(i, "outcome", st, su, "seal", True))
                out.append("ok " + chain[-1]["hash"])
        elif p[0] == "verify":
            out.append("verify " + ("true" if ok_verify() else "false"))
        elif p[0] == "tamper":
            chain[0]["subject"] = "tampered"
            out.append("tampered")
    return out


# ---------------------------------------------------------------- rendering through real ggen
def render(pack_dir: Path, consumer_ttl: str, workdir: Path) -> tuple[int, str, Path]:
    consumer = workdir / "consumer"
    (consumer / "templates").mkdir(parents=True)
    pack_path = pack_dir.resolve().as_posix()
    (consumer / "ggen.toml").write_text(
        f'[project]\nname = "es-chain-qualification"\n\n[ontology]\nsource = "ontology.ttl"\n\n'
        f'[packs]\n"evidence-standing-pack" = {{ path = "{pack_path}" }}\n\n[templates]\ndir = "templates"\n',
        encoding="utf-8")
    (consumer / "ontology.ttl").write_text(consumer_ttl, encoding="utf-8")
    (consumer / "templates" / "marketplace-probe.txt.tmpl").write_text(q.FRONTMATTER_PROBE_TEMPLATE, encoding="utf-8")
    r = sh(["ggen", "sync", "run"], consumer)
    return r.returncode, (r.stdout + r.stderr), consumer


def consumer_text() -> str:
    return (QUAL / "consumer.ttl").read_text(encoding="utf-8")


def read_outputs(consumer: Path) -> dict[str, str]:
    return {l: (consumer / OUTPUT[l]).read_text(encoding="utf-8") for l in LANGS if (consumer / OUTPUT[l]).is_file()}


# ---------------------------------------------------------------- consumer hash derivation
def derive_entries():
    import rdflib
    from rdflib import Namespace
    es = Namespace(NS)
    g = rdflib.Graph()
    g.parse(PACK / "ontology.ttl")
    g.parse(QUAL / "consumer.ttl")
    fields = sorted(((int(g.value(f, es.fieldOrder)), str(g.value(f, es.fieldName)))
                     for f in g.objects(es.CanonLinesV1, es.canonField)))
    fields = [n for _, n in fields]
    genesis = str(g.value(es.DefaultChainPolicy, es.genesisHash))
    alg = str(g.value(g.value(es.DefaultChainPolicy, es.hashAlgorithm), es.algorithmName))
    entries = {}
    for s in g.subjects(rdflib.RDF.type, es.ChainEntry):
        entries[s] = {
            "name": str(s).split("#")[1],
            "entry_id": str(g.value(s, es.entryId)),
            "phase": str(g.value(g.value(s, es.entryPhase), es.phaseName)),
            "standing": str(g.value(g.value(s, es.entryStanding), es.standingName)),
            "subject": str(g.value(s, es.entrySubject)),
            "action": str(g.value(s, es.entryAction)),
            "parent": g.value(s, es.parentEntry),
            "chain": str(g.value(s, es.chainId)),
            "cur_hash": str(g.value(s, es.entryHash)),
            "cur_parent_hash": str(g.value(s, es.parentHash)),
        }
    for s, e in entries.items():  # topological: parent before child
        pass
    done: dict = {}

    def solve(s):
        if s in done:
            return done[s]
        e = entries[s]
        e["parent_hash"] = solve(e["parent"])["hash"] if e["parent"] else genesis
        e["hash"] = digest(alg, canon(e, fields))
        done[s] = e
        return e

    for s in entries:
        solve(s)
    return entries


def regen_consumer(write: bool) -> bool:
    text = consumer_text()
    new = text
    for e in derive_entries().values():
        m = re.search(rf"es:{e['name']} a es:ChainEntry.*?\" \.\n", new, re.S)
        block = m.group(0)
        nb = re.sub(r'es:parentHash "[0-9a-f]+"', f'es:parentHash "{e["parent_hash"]}"', block)
        nb = re.sub(r'es:entryHash "[0-9a-f]+"', f'es:entryHash "{e["hash"]}"', nb)
        new = new.replace(block, nb)
    if new != text and write:
        (QUAL / "consumer.ttl").write_text(new, encoding="utf-8")
    return new == text


# ---------------------------------------------------------------- checks
class Report:
    def __init__(self):
        self.failed = False

    def line(self, status, name, detail=""):
        if status in ("REFUSED", "FAILED"):
            self.failed = True
        print(f"{status:10} {name}" + (f": {detail}" if detail else ""))


def check_consumer(rep, regen):
    fresh = regen_consumer(write=regen)
    if regen:
        print("regenerated consumer.ttl chain hashes" if not fresh else "consumer.ttl already current")
        fresh = regen_consumer(write=False)
    rep.line("ALIVE" if fresh else "REFUSED", "consumer", "hashes match CanonLinesV1 recomputation" if fresh else "stale hashes; run --regen")


def check_literal(rep):
    clean = literal_scan.scan(PACK)
    with tempfile.TemporaryDirectory() as t:
        shutil.copytree(PACK / "templates", Path(t) / "templates")
        f = next((Path(t) / "templates").glob("chain.py.tmpl"))
        f.write_text(f.read_text() + "\n# uses zcode runtime\n")
        dirty = literal_scan.scan(Path(t))
    ok = not clean and any("zcode" in h for h in dirty)
    rep.line("ALIVE" if ok else "REFUSED", "literal", f"clean={clean} injected_refused={dirty}")


def check_gates(rep):
    base = consumer_text()
    cases = {
        "lawful": ("", True, ""),
        "seal-twice": ('es:ToyChainX a es:ChainEntry ; es:chainId "toy-1" ; es:chainPolicy es:DefaultChainPolicy ; es:isSeal true ; '
                       'es:parentHash "0000000000000000000000000000000000000000000000000000000000000000" .\n', False, "sealed at most once"),
        "dangling-parent": ('es:ToyChainY a es:ChainEntry ; es:chainId "toy-2" ; es:chainPolicy es:DefaultChainPolicy ; '
                            'es:parentHash "ffff" .\n', False, "parent-hash closure"),
        "unsupported-language": ('es:BadPolicy a es:ChainPolicy ; es:hashAlgorithm es:Blake2b256 ; es:targetLanguage es:LangRs ; '
                                 'es:policyPrecedence 5 ; es:genesisHash "0" ; es:canonicalization es:CanonLinesV1 .\n', False, "supported-set"),
    }
    for name, (extra, should_pass, needle) in cases.items():
        with tempfile.TemporaryDirectory() as t:
            rc, out, _ = render(PACK, base + "\n" + extra, Path(t))
        ok = (rc == 0) if should_pass else (rc != 0 and needle in out)
        rep.line("ALIVE" if ok else "REFUSED", f"gate:{name}", f"rc={rc}" + ("" if ok else " " + out[-300:]))


def drivers(consumer: Path, vec: Path) -> dict[str, list[str] | str]:
    res: dict[str, list[str] | str] = {}
    d = QUAL / "drivers"
    shutil.copy(d / "driver.py", consumer / "driver.py")
    shutil.copy(d / "driver.ts", consumer / "driver.ts")
    shutil.copy(d / "driver.exs", consumer / "driver.exs")
    shutil.copy(vec, consumer / "golden.vec")

    def run(lang, cmd, cwd=consumer, tool=None):
        if tool and not shutil.which(tool):
            res[lang] = f"UNVERIFIED: {tool} not installed"
            return
        r = sh(cmd, cwd, timeout=300)
        res[lang] = r.stdout.strip().split("\n") if r.returncode == 0 else f"FAILED rc={r.returncode}: {(r.stderr or r.stdout)[-400:]}"

    run("py", ["python3", "driver.py", "golden.vec"], tool="python3")
    run("ts", ["bun", "driver.ts", "golden.vec"], tool="bun")
    run("ex", ["elixir", "-r", "lib/es/chain.ex", "driver.exs", "golden.vec"], tool="elixir")
    if shutil.which("cargo"):
        rs = consumer / "rsdrv"
        (rs / "src" / "es").mkdir(parents=True)
        (rs / "Cargo.toml").write_text('[package]\nname = "esdrv"\nversion = "0.0.0"\nedition = "2021"\n\n[dependencies]\nsha2 = "0.10"\n')
        shutil.copy(d / "rs" / "main.rs", rs / "src" / "main.rs")
        shutil.copy(consumer / OUTPUT["rs"], rs / "src" / "es" / "chain.rs")
        run("rs", ["cargo", "run", "--offline", "--quiet", "--", str(consumer / "golden.vec")], cwd=rs)
    else:
        res["rs"] = "UNVERIFIED: cargo not installed"
    return res


def check_golden(rep, freeze):
    vec_text = VEC.read_text(encoding="utf-8")
    ref = reference_run(vec_text)
    with tempfile.TemporaryDirectory() as t:
        rc, out, consumer = render(PACK, consumer_text(), Path(t))
        if rc != 0:
            rep.line("REFUSED", "golden", "render failed: " + out[-300:])
            return
        res = drivers(consumer, VEC)
    if freeze:
        EXPECTED.write_text("\n".join(ref) + "\n", encoding="utf-8")
    frozen = EXPECTED.read_text(encoding="utf-8").strip().split("\n") if EXPECTED.is_file() else None
    rep.line("ALIVE" if frozen == ref else "REFUSED", "golden:reference-vs-frozen", f"{len(ref)} lines")
    verified = []
    for lang in LANGS:
        r = res[lang]
        if isinstance(r, str):
            rep.line("UNVERIFIED" if r.startswith("UNVERIFIED") else "REFUSED", f"golden:{lang}", r)
        elif r == ref:
            verified.append(lang)
            rep.line("ALIVE", f"golden:{lang}", "identical to reference on every op")
        else:
            diff = [(i, a, b) for i, (a, b) in enumerate(zip(r, ref)) if a != b][:3]
            rep.line("REFUSED", f"golden:{lang}", f"diverges {diff} len {len(r)} vs {len(ref)}")
    digests = {json.dumps(res[l]) for l in verified}
    rep.line("ALIVE" if len(digests) <= 1 and verified else "REFUSED", "golden:cross-language",
             f"identical chain digests across {verified}")


def check_blake(rep):
    base = consumer_text()
    over = ('es:Blake2bPolicy a es:ChainPolicy ; es:hashAlgorithm es:Blake2b256 ; es:targetLanguage es:LangPy ; '
            'es:policyPrecedence 10 ; es:genesisHash "0000000000000000000000000000000000000000000000000000000000000000" ; '
            'es:canonicalization es:CanonLinesV1 .\n')
    with tempfile.TemporaryDirectory() as t:
        rc, out, consumer = render(PACK, base + "\n" + over, Path(t))
        if rc != 0:
            rep.line("REFUSED", "blake2b", out[-300:])
            return
        outs = read_outputs(consumer)
        shutil.copy(VEC, consumer / "golden.vec")
        shutil.copy(QUAL / "drivers" / "driver.py", consumer / "driver.py")
        r = sh(["python3", "driver.py", "golden.vec"], consumer)
    ref = reference_run(VEC.read_text(encoding="utf-8"), "blake2b256")
    py_ok = r.returncode == 0 and r.stdout.strip().split("\n") == ref
    others_sha = all('"sha256"' in outs[l] for l in ("ts", "rs", "ex")) and 'ALGORITHM = "blake2b256"' in outs["py"]
    rep.line("ALIVE" if py_ok and others_sha else "REFUSED", "blake2b",
             f"py digests==blake2b(32) reference: {py_ok}; ts/rs/ex remain sha256: {others_sha}")


def check_mutation(rep):
    """Rename PhaseOutcome's name -> outputs differ at that token only; then map back == baseline."""
    with tempfile.TemporaryDirectory() as t:
        t = Path(t)
        rc, out, base_c = render(PACK, consumer_text(), t / "a")
        if rc != 0:
            rep.line("REFUSED", "mutation", out[-300:])
            return
        base = read_outputs(base_c)
        mut_pack = t / "pack"
        shutil.copytree(PACK, mut_pack)
        onto = mut_pack / "ontology.ttl"
        s = onto.read_text()
        assert 'es:phaseName "outcome"' in s
        onto.write_text(s.replace('es:phaseName "outcome"', 'es:phaseName "verdict"'))
        # consumer entries name phases by individual, so a rename is transparent to them
        rc, out, mut_c = render(mut_pack, consumer_text(), t / "b")
        if rc != 0:
            rep.line("REFUSED", "mutation", out[-300:])
            return
        mut = read_outputs(mut_c)
    problems = []
    for l in LANGS:
        if base[l] == mut[l]:
            problems.append(f"{l}: unchanged")
        elif mut[l].replace('"verdict"', '"outcome"') != base[l]:
            problems.append(f"{l}: changed beyond the renamed token")
        elif 'verdict' not in mut[l]:
            problems.append(f"{l}: token absent")
    rep.line("ALIVE" if not problems else "REFUSED", "mutation", "rename outcome->verdict changes only that token in ts/py/rs/ex" if not problems else "; ".join(problems))


def b3(data: str) -> str:
    return subprocess.run(["b3sum", "--no-names"], input=data.encode(), capture_output=True).stdout.decode().strip()


def check_affidavit(rep):
    """Semantic diff vs affidavit-pack: rolling BLAKE3 chain_n = b3(hex(chain_{n-1}) || canonical_json(event_n)),
    chain_0 = b3(seed). The affidavit reference carries no fixed hex vectors (its tests are property tests), so the
    affidavit rule is MODELLED here from reference/affidavit_v26.6.22_src/chain.rs; UNVERIFIED against the crate itself."""
    if not shutil.which("b3sum"):
        rep.line("UNVERIFIED", "affidavit", "b3sum not installed")
        return
    seed = "affidavit-v26.6.22-genesis"
    events = [("e1", "pending", "sort"), ("e2", "outcome", "sort")]

    def aff(evs):
        acc = b3(seed)
        for i, (id_, ph, ac) in enumerate(evs):
            ev = json.dumps({"event_type": f"{ph}:{ac}", "id": id_, "objects": [], "payload_commitment": b3(ac), "seq": i},
                            sort_keys=True, separators=(",", ":"))
            acc = b3(acc + ev)
        return acc

    def ours(evs):
        chain, prev = [], GENESIS
        for id_, ph, ac in evs:
            e = {"entry_id": id_, "parent_hash": prev, "phase": ph, "standing": "unknown", "subject": "s", "action": ac}
            prev = digest("sha256", canon(e))
            chain.append(prev)
        return chain[-1]

    props = {
        "deterministic": lambda f: f(events) == f(events),
        "order-sensitive": lambda f: f(events) != f(events[::-1]),
        "tamper-changes-head": lambda f: f(events) != f([events[0], ("e2", "outcome", "other")]),
        "prefix-binding": lambda f: f(events[:1]) != f(events),
    }
    shared_ok = all(p(aff) and p(ours) for p in props.values())
    rep.line("ALIVE" if shared_ok else "REFUSED", "affidavit:shared-invariants", ", ".join(props))
    diffs = {
        "algorithm": ("blake3", "sha256 default | sha512 | blake2b256 (ChainPolicy individual, per-language supported set)"),
        "genesis": ("b3(seed string), version-bound: " + seed, "es:genesisHash literal individual (64 zero hex)"),
        "fold_input": ("hex(prev) || sorted-key JSON of event", "LF-joined name=value lines in es:fieldOrder incl. parent_hash"),
        "stored_per_entry_hash": ("no: only the rolling head is kept", "yes: every entry carries hash + parent_hash; verify walks the links"),
        "seal": ("finalize() consumes the assembler (value-level, one shot)", "explicit seal entry, gate 020 seal-once, verify requires seal last"),
        "phases_standing": ("none", "pending/outcome phases; unknown|partial_alive|alive|blocked|build_broken|unsupported"),
        "same_head_on_same_events": (aff(events)[:16] + "...", ours(events)[:16] + "..."),
    }
    assert aff(events) != ours(events)
    for k, (a, o) in diffs.items():
        rep.line("DIFF", f"affidavit:{k}", f"affidavit={a} | es-chain={o}")
    rep.line("UNVERIFIED", "affidavit:model-fidelity", "affidavit rule modelled from reference chain.rs, not executed")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--regen", action="store_true", help="rewrite consumer.ttl chain hashes")
    ap.add_argument("--freeze", action="store_true", help="rewrite golden.expected from the reference model")
    ap.add_argument("--only", choices=("consumer", "literal", "gates", "golden", "blake2b", "mutation", "affidavit"))
    a = ap.parse_args()
    rep = Report()
    steps = {"consumer": lambda: check_consumer(rep, a.regen), "literal": lambda: check_literal(rep),
             "gates": lambda: check_gates(rep), "golden": lambda: check_golden(rep, a.freeze),
             "blake2b": lambda: check_blake(rep), "mutation": lambda: check_mutation(rep),
             "affidavit": lambda: check_affidavit(rep)}
    for name, fn in steps.items():
        if a.only in (None, name):
            fn()
    return 1 if rep.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
