"""Chicago-style tests for process-intelligence-pack's OCEL tap (26.9.13).

Real collaborators only: real `ggen sync run`, real SPARQL gates via rdflib, real
bun / python3 / rustc / elixir processes running the generated code. No mocks.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from rdflib import Dataset, Graph

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "process-intelligence-pack"
SCRIPTS = ROOT / "scripts"
PI = "https://ggen.dev/ontology/process-intelligence#"

for tool in ("ggen", "bun", "python3", "rustc", "elixir"):
    if shutil.which(tool) is None:
        pytest.skip(f"{tool} not installed", allow_module_level=True)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


literal_scan = _load("pi_literal_scan", PACK / "gates" / "080_template_literal_scan.py")


def ontology_text(consumer: bool = True) -> str:
    parts = [(PACK / "ontology.ttl").read_text()]
    if consumer:
        parts.append((PACK / "qualification" / "consumer.ttl").read_text())
    prefixes = sorted({l for p in parts for l in p.splitlines() if l.startswith("@prefix")})
    body = [l for p in parts for l in p.splitlines() if not l.startswith("@prefix")]
    return "\n".join(prefixes + body) + "\n"


def consumer_text() -> str:
    """The consumer graph alone: ggen composes the pack's own ontology from [packs]."""
    return (PACK / "qualification" / "consumer.ttl").read_text()


def generate(workdir: Path, ttl: str, pack: Path = PACK) -> Path:
    (workdir / "templates").mkdir(parents=True)
    (workdir / "ontology.ttl").write_text(ttl)
    (workdir / "ggen.toml").write_text(
        f'[project]\nname = "tap-test"\n[ontology]\nsource = "ontology.ttl"\n'
        f'[packs]\n"process-intelligence-pack" = {{ path = "{pack}" }}\n[templates]\ndir = "templates"\n'
    )
    run = subprocess.run(["ggen", "sync", "run"], cwd=workdir, capture_output=True, text=True, timeout=120)
    assert run.returncode == 0, run.stderr[-2000:]
    return workdir / "src" / "pi_ocel_tap"


@pytest.fixture(scope="module")
def generated(tmp_path_factory) -> Path:
    return generate(tmp_path_factory.mktemp("cap"), consumer_text())


def gate_rows(name: str, ttl: str) -> list:
    graph = Graph()
    graph.parse(data=ttl, format="turtle")
    return list(graph.query((PACK / "gates" / name).read_text()))


GATES = sorted(p.name for p in (PACK / "gates").glob("*.rq"))


# ---------------------------------------------------------------- gates
@pytest.mark.parametrize("gate", GATES)
def test_gate_passes_on_pack_plus_consumer_graph(gate):
    assert gate_rows(gate, ontology_text()) == []


def mutate(old: str, new: str) -> str:
    text = ontology_text()
    assert old in text, old
    return text.replace(old, new, 1)


def test_gate_020_refuses_relation_without_qualifier():
    text = mutate('pi:Rel-Ship-Order a pi:E2ORelation ; pi:relatesObjectType pi:ObjectType-Order ; pi:hasQualifier pi:Qualifier-Subject ;',
                  'pi:Rel-Ship-Order a pi:E2ORelation ; pi:relatesObjectType pi:ObjectType-Order ;')
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("020_relation_requires_qualifier.rq", text)] == ["Rel-Ship-Order"]


def test_gate_030_refuses_relation_without_object_path_and_conflicting_event_types():
    text = mutate('pi:hasQualifier pi:ConsumerQualifier-Target ; pi:objectIdPath "ticket.id" .', "pi:hasQualifier pi:ConsumerQualifier-Target .")
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("030_e2o_closure.rq", text)] == ["ConsumerRel-Open-Ticket"]
    text = ontology_text() + (
        "@prefix pi: <https://ggen.dev/ontology/process-intelligence#> .\n"
        'pi:Rule-Dup a pi:MappingRule ; pi:ruleId "rule-dup" ; pi:fromSource pi:Source-OrderHook ; '
        "pi:sourceEvent \"order.placed\" ; pi:emitsEventType pi:EventType-Ship ; pi:hasRelation pi:Rel-Ship-Order .\n"
    )
    flagged = {str(r[0]).rsplit("#", 1)[1] for r in gate_rows("030_e2o_closure.rq", text)}
    assert flagged == {"Rule-Dup", "Rule-Place"}


def test_gate_040_refuses_duplicate_rule_id():
    text = mutate('pi:ruleId "rule-ship"', 'pi:ruleId "rule-place"')
    flagged = {str(r[0]).rsplit("#", 1)[1] for r in gate_rows("040_unique_ids.rq", text)}
    assert flagged == {"Rule-Place", "Rule-Ship"}


def test_gate_050_coverage_refuses_unreasoned_and_unmapped_and_double_declared():
    # Unmapped without a reason.
    text = mutate('pi:unmappedReason "liveness ping; not a process step"', 'pi:note "x"')
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("050_runtime_event_coverage.rq", text)] == ["ConsumerRuntimeEvent-Heartbeat"]
    # A runtime event neither mapped nor declared Unmapped.
    text = ontology_text() + (
        "@prefix pi: <https://ggen.dev/ontology/process-intelligence#> .\n"
        'pi:RuntimeEvent-Orphan a pi:RuntimeEvent ; pi:runtimeEventName "order.refunded" ; pi:emittedBy pi:Source-OrderHook .\n'
    )
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("050_runtime_event_coverage.rq", text)] == ["RuntimeEvent-Orphan"]
    # Declared Unmapped while a rule maps it.
    text = mutate("pi:RuntimeEvent-OrderPlaced a pi:RuntimeEvent ;", "pi:RuntimeEvent-OrderPlaced a pi:RuntimeEvent , pi:Unmapped ; pi:unmappedReason \"x\" ;")
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("050_runtime_event_coverage.rq", text)] == ["RuntimeEvent-OrderPlaced"]
    # Mapped by a rule of a *different* source does not count.
    text = mutate('pi:RuntimeEvent-OrderShipped a pi:RuntimeEvent ; pi:runtimeEventName "order.shipped" ; pi:emittedBy pi:Source-OrderHook',
                  'pi:RuntimeEvent-OrderShipped a pi:RuntimeEvent ; pi:runtimeEventName "order.shipped" ; pi:emittedBy pi:ConsumerSource-Stream')
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("050_runtime_event_coverage.rq", text)] == ["RuntimeEvent-OrderShipped"]


def test_gate_060_refuses_unknown_kind_bad_id_and_missing_policy():
    bad_kind = mutate('pi:sourceKind "stream-json"', 'pi:sourceKind "carrier-pigeon"')
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("060_event_source.rq", bad_kind)] == ["ConsumerSource-Stream"]
    bad_id = mutate('pi:sourceId "ticket_otel"', 'pi:sourceId "Ticket-Otel"')
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("060_event_source.rq", bad_id)] == ["ConsumerSource-Otel"]
    no_policy = mutate('pi:timeField "at" ; pi:chainPolicy pi:ConsumerPolicy-Sha .', 'pi:timeField "at" .')
    assert [str(r[0]).rsplit("#", 1)[1] for r in gate_rows("060_event_source.rq", no_policy)] == ["ConsumerSource-Stream"]


def test_gate_070_refuses_algorithm_a_targeted_language_lacks():
    text = mutate('pi:hashAlgorithm "blake2b256" ; pi:targetLanguage "py"', 'pi:hashAlgorithm "blake2b256" ; pi:targetLanguage "py" , "ts"')
    rows = gate_rows("070_chain_policy_language_support.rq", text)
    assert [(str(r[0]).rsplit("#", 1)[1], str(r[1])) for r in rows] == [("ConsumerPolicy-Blake", "ts")]
    text = mutate('pi:ConsumerPolicy-Sha a pi:ChainPolicy ; pi:hashAlgorithm "sha256"', 'pi:ConsumerPolicy-Sha a pi:ChainPolicy ; pi:hashAlgorithm "blake3"')
    assert {str(r[1]) for r in gate_rows("070_chain_policy_language_support.rq", text)} == {"ts", "py", "rs", "ex"}


# ---------------------------------------------------------------- literal scan
def test_literal_scan_clean_on_shipped_templates():
    assert literal_scan.scan(PACK) == []


def test_literal_scan_refuses_injected_banned_literal(tmp_path):
    pack = tmp_path / "pack"
    shutil.copytree(PACK, pack)
    tmpl = pack / "templates" / "ocel_tap.ts.tmpl"
    tmpl.write_text(tmpl.read_text() + "\n// wired for zcode only\n")
    hits = literal_scan.scan(pack)
    assert len(hits) == 1 and hits[0].endswith(": zcode") and "ocel_tap.ts.tmpl" in hits[0]
    run = subprocess.run([sys.executable, str(PACK / "gates" / "080_template_literal_scan.py"), str(pack)], capture_output=True, text=True)
    assert run.returncode == 2 and "REFUSED[BANNED_LITERAL]" in run.stdout


# ---------------------------------------------------------------- generation
def test_generation_is_per_language_filtered_by_chain_policy(generated):
    ts = (generated / "ts" / "tap.ts").read_text()
    py = (generated / "py" / "tap.py").read_text()
    assert 'id: "ticket_stream"' in ts and "ticket_otel" not in ts and "order_hook" in ts
    assert '"ticket_otel"' in py and "blake2b256" in py and "blake2b" in py
    assert "blake2" not in ts and "blake3" not in (ts + py).lower()


def test_generation_is_deterministic_on_replay(tmp_path):
    a = generate(tmp_path / "a", consumer_text())
    b = generate(tmp_path / "b", consumer_text())
    for rel in ("ts/tap.ts", "py/tap.py", "rs/tap.rs", "ex/tap.ex"):
        assert (a / rel).read_bytes() == (b / rel).read_bytes()


# ---------------------------------------------------------------- mutation checks
def out_files(base: Path) -> dict[str, str]:
    return {rel: (base / rel).read_text() for rel in ("ts/tap.ts", "py/tap.py", "rs/tap.rs", "ex/tap.ex")}


def test_mutation_object_type_id_change_changes_only_that_id(tmp_path, generated):
    base = out_files(generated)
    changed = out_files(generate(tmp_path / "m", consumer_text().replace('pi:typeId "consumer_ticket"', 'pi:typeId "consumer_case"')))
    for rel, text in base.items():
        assert '"consumer_ticket"' in text
        assert changed[rel] == text.replace('"consumer_ticket"', '"consumer_case"'), rel


def test_mutation_source_id_change_changes_only_that_id(tmp_path, generated):
    base = out_files(generated)
    changed = out_files(generate(tmp_path / "m", consumer_text().replace('pi:sourceId "ticket_stream"', 'pi:sourceId "ticket_zstream"')))
    for rel, text in base.items():
        assert changed[rel] == text.replace('"ticket_stream"', '"ticket_zstream"'), rel


def test_mutation_iri_rename_changes_nothing(tmp_path, generated):
    base = out_files(generated)
    changed = out_files(generate(tmp_path / "m", consumer_text().replace("pi:ConsumerObjectType-Ticket", "pi:ConsumerObjectType-Case")))
    assert changed == base


def test_mutation_added_rule_adds_only_its_row(tmp_path, generated):
    extra = (
        'pi:ConsumerRule-Close a pi:MappingRule ; pi:ruleId "consumer-rule-close" ; pi:fromSource pi:ConsumerSource-Stream ; '
        'pi:sourceEvent "ticket.closed" ; pi:emitsEventType pi:ConsumerEventType-Open ; pi:hasRelation pi:ConsumerRel-Open-Ticket .\n'
    )
    changed = out_files(generate(tmp_path / "m", consumer_text() + extra))
    base = out_files(generated)
    for rel, text in base.items():
        removed = [l for l in text.splitlines() if l not in changed[rel].splitlines()]
        added = [l for l in changed[rel].splitlines() if l not in text.splitlines()]
        assert removed == [] and len(added) == 1 and "consumer-rule-close" in added[0], (rel, removed, added)


# ---------------------------------------------------------------- qualifier
def test_qualifier_capsule_regenerates_from_consumer_fixture_and_qualifies_alive():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    mp = _load("marketplace", SCRIPTS / "marketplace.py")
    qp = _load("qualify_packs_pi", SCRIPTS / "qualify_packs.py")
    pack = next(p for p in mp.inspect_marketplace()[0] if p.name == "process-intelligence-pack")
    with tempfile.TemporaryDirectory() as raw:
        consumer = qp.prepare_consumer(pack, Path(raw))
        assert "consumer_ticket" in (consumer / "ontology.ttl").read_text()
        run = subprocess.run(["ggen", "sync", "run"], cwd=consumer, capture_output=True, text=True, timeout=120)
        assert run.returncode == 0, run.stderr[-1500:]
        assert "consumer_open_ticket" in (consumer / "src/pi_ocel_tap/ts/tap.ts").read_text()
        assert "ticket_otel" in (consumer / "src/pi_ocel_tap/py/tap.py").read_text()
    record = qp.qualify_pack(pack, shutil.which("ggen"), 60.0)
    assert record["status"] == "ALIVE", record


# ---------------------------------------------------------------- compare-loops
def test_compare_loops_query_runs_over_two_named_graphs_toy_pair():
    ds = Dataset()
    header = "@prefix pi: <https://ggen.dev/ontology/process-intelligence#> .\n"
    ds.graph(rdflib_uri("urn:loop:a")).parse(data=header + '''
        pi:S1 a pi:EventSource ; pi:sourceKind "hook" .
        pi:E1 a pi:EventType ; pi:typeId "shared_step" . pi:E2 a pi:EventType ; pi:typeId "only_a" .
    ''', format="turtle")
    ds.graph(rdflib_uri("urn:loop:b")).parse(data=header + '''
        pi:S2 a pi:EventSource ; pi:sourceKind "otel" .
        pi:E3 a pi:EventType ; pi:typeId "shared_step" . pi:E4 a pi:EventType ; pi:typeId "only_b" .
    ''', format="turtle")
    rows = {(str(r.kind), str(r.term), str(r.side)) for r in ds.query((PACK / "queries" / "compare-loops.rq").read_text())}
    assert rows == {
        ("event-type", "shared_step", "shared"),
        ("event-type", "only_a", "only-in-a"),
        ("event-type", "only_b", "only-in-b"),
        ("source-kind", "hook", "only-in-a"),
        ("source-kind", "otel", "only-in-b"),
    }
    assert (PACK / "queries" / "compare-loops.rq").read_text().startswith("# STATUS: UNVERIFIED")


def rdflib_uri(s: str):
    from rdflib import URIRef
    return URIRef(s)


# ---------------------------------------------------------------- runtime: real generated code
HOOK_EVENTS = [
    {"event": "order.placed", "id": "e1", "ts": "2026-01-01T00:00:00Z", "order": {"id": "o1"}, "items": ["i1", "i2"]},
    {"event": "order.audit", "id": "e2", "ts": "2026-01-01T00:00:01Z", "order": {"id": "o1"}},
    {"event": "order.shipped", "id": "e3", "ts": "2026-01-02T00:00:00Z", "order": {"id": "o1"}},
]
STREAM_TEXT = "\n".join(
    json.dumps(e)
    for e in [
        {"type": "ticket.opened", "uuid": "u1", "at": "2026-02-01T00:00:00Z", "ticket": {"id": "t \"9\"\né"}},
        {"type": "ticket.heartbeat", "uuid": "u2", "at": "2026-02-01T00:00:01Z"},
        {"type": "ticket.opened", "uuid": "u3", "at": "2026-02-01T00:00:02Z", "ticket": {"id": "t10"}},
    ]
) + "\n"
OTEL_RECORDS = [
    {"name": "ticket.trace", "spanId": "s1", "time": "2026-03-01T00:00:00Z", "attributes": [{"key": "ticket", "value": {"stringValue": "t7"}}]},
    {"name": "ticket.other", "spanId": "s2", "time": "2026-03-01T00:00:01Z", "attributes": []},
    {"name": "ticket.trace", "spanId": "s3", "time": "2026-03-01T00:00:02Z", "attributes": [{"key": "ticket", "value": {"stringValue": "t8"}}]},
]


def run(cmd, cwd, stdin=None):
    p = subprocess.run(cmd, cwd=cwd, input=stdin, capture_output=True, text=True, timeout=180)
    assert p.returncode == 0, (cmd, p.stdout[-1500:], p.stderr[-2500:])
    return p.stdout


# Each driver reads {"hook": [...], "stream": "...", "otel": [...]} on stdin and prints
# {"hook": {...}, "stream": {...}, "otel": {...}} where each value is
# {"doc": <ocel>, "head": <sealed hash>, "verify": null|reason, "tampered": null|reason,
#  "sealTwice": bool(refused), "ingestAfterSeal": bool(refused)}; "otel" only where the source exists.
TS_DRIVER = r'''
import { Tap, verifyChain } from "./tap.ts";
const input = JSON.parse(await Bun.stdin.text());
function finish(t: Tap, alg: string) {
  const doc = JSON.parse(t.serialize());
  const head = t.seal();
  let sealTwice = false, after = false;
  try { t.seal(); } catch { sealTwice = true; }
  try { t.ingest(input.hook[0]); } catch { after = true; }
  const bad = JSON.parse(t.serialize());
  if (bad.events.length) bad.events[0].relationships[0].objectId = "forged";
  return { doc, head, verify: verifyChain(doc, alg), tampered: verifyChain(bad, alg), sealTwice, ingestAfterSeal: after };
}
const out: any = {};
const h = new Tap("order_hook"); for (const r of input.hook) h.ingest(r); out.hook = finish(h, "sha256");
const s = new Tap("ticket_stream"); s.ingest(input.stream); out.stream = finish(s, "sha256");
const cb = new Tap("order_hook"); (() => { try { cb.attach(() => {}); out.attachHookRefused = false; } catch { out.attachHookRefused = true; } })();
console.log(JSON.stringify(out));
'''
PY_DRIVER = r'''
import json, sys
sys.path.insert(0, ".")
from tap import Tap, verify_chain
inp = json.load(sys.stdin)
def finish(t, alg):
    doc = json.loads(t.serialize()); head = t.seal()
    def refused(f):
        try: f()
        except Exception: return True
        return False
    bad = json.loads(t.serialize())
    if bad["events"]: bad["events"][0]["relationships"][0]["objectId"] = "forged"
    return {"doc": doc, "head": head, "verify": verify_chain(doc, alg), "tampered": verify_chain(bad, alg),
            "sealTwice": refused(t.seal), "ingestAfterSeal": refused(lambda: t.ingest(inp["hook"][0]))}
out = {}
h = Tap("order_hook")
for r in inp["hook"]: h.ingest(r)
out["hook"] = finish(h, "sha256")
s = Tap("ticket_stream"); s.ingest(inp["stream"]); out["stream"] = finish(s, "sha256")
o = Tap("ticket_otel")
for r in inp["otel"]: o.ingest(r)
out["otel"] = finish(o, "blake2b256")
seen = []
c = Tap("order_hook")
try: c.attach(lambda cb: None); out["attachHookRefused"] = False
except ValueError: out["attachHookRefused"] = True
print(json.dumps(out))
'''
RS_DRIVER = r'''
#[path = "tap.rs"]
mod tap;
use std::io::Read;
use tap::*;

fn jv(v: &Json) -> String {
    match v {
        Json::Null => "null".into(),
        Json::Bool(b) => b.to_string(),
        Json::Num(n) => n.clone(),
        Json::Str(s) => jstr(s),
        Json::Arr(a) => format!("[{}]", a.iter().map(jv).collect::<Vec<_>>().join(",")),
        Json::Obj(o) => format!("{{{}}}", o.iter().map(|(k, v)| format!("{}:{}", jstr(k), jv(v))).collect::<Vec<_>>().join(",")),
    }
}
fn opt(o: Option<String>) -> String { match o { Some(s) => jstr(&s), None => "null".into() } }

fn finish(mut t: Tap, alg: &str, first: &Json) -> String {
    let doc_text = t.serialize();
    let doc = parse_json(&doc_text).unwrap();
    let head = t.seal().unwrap();
    let twice = t.seal().is_err();
    let after = t.ingest(first).is_err() && t.ingest_text("{}").is_err();
    // tamper: swap the first relationship's object id text in the serialized doc
    let bad_text = doc_text.replacen("\"objectId\":\"", "\"objectId\":\"forged", 1);
    let bad = parse_json(&bad_text).unwrap();
    format!("{{\"doc\":{},\"head\":{},\"verify\":{},\"tampered\":{},\"sealTwice\":{},\"ingestAfterSeal\":{}}}",
        jv(&doc), jstr(&head), opt(verify_chain(&doc, alg)), opt(verify_chain(&bad, alg)), twice, after)
}

fn main() {
    let mut s = String::new();
    std::io::stdin().read_to_string(&mut s).unwrap();
    let inp = parse_json(&s).unwrap();
    let hook = match inp.get("hook") { Some(Json::Arr(a)) => a.clone(), _ => panic!() };
    let stream = match inp.get("stream") { Some(Json::Str(x)) => x.clone(), _ => panic!() };
    let mut h = Tap::new("order_hook").unwrap();
    for r in &hook { h.ingest(r).unwrap(); }
    let hook_out = finish(h, "sha256", &hook[0]);
    let mut st = Tap::new("ticket_stream").unwrap();
    st.ingest_text(&stream).unwrap();
    let stream_out = finish(st, "sha256", &hook[0]);
    let mut c = Tap::new("order_hook").unwrap();
    let refused = c.attach(|_| {}).is_err();
    println!("{{\"hook\":{},\"stream\":{},\"attachHookRefused\":{}}}", hook_out, stream_out, refused);
}
'''
EX_DRIVER = r'''
input = IO.read(:stdio, :eof) |> :json.decode()

finish = fn pid, alg, first ->
  doc = pid |> PiOcelTap.serialize() |> :json.decode()
  {:ok, head} = PiOcelTap.seal(pid)
  twice = match?({:error, _}, PiOcelTap.seal(pid))
  after_seal = match?({:error, _}, PiOcelTap.ingest(pid, first))
  [ev | rest] = doc["events"]
  [rel | rels] = ev["relationships"]
  bad = %{doc | "events" => [%{ev | "relationships" => [%{rel | "objectId" => "forged"} | rels]} | rest]}
  nn = fn nil -> :null; x -> x end
  %{"doc" => doc, "head" => head, "verify" => nn.(PiOcelTap.verify_chain(doc, alg)),
    "tampered" => nn.(PiOcelTap.verify_chain(bad, alg)), "sealTwice" => twice, "ingestAfterSeal" => after_seal}
end

{:ok, h} = PiOcelTap.start("order_hook")
for r <- input["hook"], do: {:ok, _} = PiOcelTap.ingest(h, r)
hook_out = finish.(h, "sha256", hd(input["hook"]))
{:ok, s} = PiOcelTap.start("ticket_stream")
{:ok, _} = PiOcelTap.ingest(s, input["stream"])
stream_out = finish.(s, "sha256", hd(input["hook"]))
{:ok, c} = PiOcelTap.start("order_hook")
refused = match?({:error, _}, PiOcelTap.attach(c, fn _ -> :ok end))
IO.puts(:json.encode(%{"hook" => hook_out, "stream" => stream_out, "attachHookRefused" => refused}) |> IO.iodata_to_binary())
'''


@pytest.fixture(scope="module")
def outputs(generated, tmp_path_factory):
    stdin = json.dumps({"hook": HOOK_EVENTS, "stream": STREAM_TEXT, "otel": OTEL_RECORDS})
    work = tmp_path_factory.mktemp("run")
    res = {}
    d = work / "ts"; d.mkdir(); shutil.copy(generated / "ts/tap.ts", d / "tap.ts"); (d / "drv.ts").write_text(TS_DRIVER)
    res["ts"] = json.loads(run(["bun", "run", "drv.ts"], d, stdin))
    d = work / "py"; d.mkdir(); shutil.copy(generated / "py/tap.py", d / "tap.py"); (d / "drv.py").write_text(PY_DRIVER)
    res["py"] = json.loads(run([sys.executable, "drv.py"], d, stdin))
    d = work / "rs"; d.mkdir(); shutil.copy(generated / "rs/tap.rs", d / "tap.rs"); (d / "main.rs").write_text(RS_DRIVER)
    run(["rustc", "--edition", "2021", "-O", "main.rs", "-o", "drv"], d)
    res["rs"] = json.loads(run(["./drv"], d, stdin))
    d = work / "ex"; d.mkdir(); shutil.copy(generated / "ex/tap.ex", d / "tap.ex"); (d / "drv.exs").write_text(EX_DRIVER)
    res["ex"] = json.loads(run(["elixir", "-r", "tap.ex", "drv.exs"], d, stdin))
    return res


LANGS = ["ts", "py", "rs", "ex"]


def canon_event(e):
    rels = ",".join('{"objectId":%s,"qualifier":%s}' % (json.dumps(r["objectId"], ensure_ascii=False), json.dumps(r["qualifier"], ensure_ascii=False)) for r in e["relationships"])
    return '{"id":%s,"relationships":[%s],"time":%s,"type":%s}' % (
        json.dumps(e["id"], ensure_ascii=False), rels, json.dumps(e["time"], ensure_ascii=False), json.dumps(e["type"], ensure_ascii=False))


def oracle_head(events, hasher):
    parent = ""
    for e in events:
        parent = hasher((parent + "\n" + canon_event(e)).encode("utf-8"))
    return parent


@pytest.mark.parametrize("lang", LANGS)
def test_runtime_hook_source_maps_to_ocel_2(outputs, lang):
    doc = outputs[lang]["hook"]["doc"]
    assert sorted(doc) == ["eventTypes", "events", "objectTypes", "objects"]
    assert [e["id"] for e in doc["events"]] == ["e1", "e3"]  # order.audit is Unmapped and dropped
    assert [e["type"] for e in doc["events"]] == ["place_order", "ship_order"]
    assert [(r["objectId"], r["qualifier"]) for r in doc["events"][0]["relationships"]] == [("i1", "contains"), ("i2", "contains"), ("o1", "subject")]
    assert {(o["id"], o["type"]) for o in doc["objects"]} == {("o1", "order"), ("i1", "item"), ("i2", "item")}
    assert {t["name"] for t in doc["objectTypes"]} == {"consumer_ticket", "item", "order"}
    # e2o closure: every relationship targets a listed object
    ids = {o["id"] for o in doc["objects"]}
    assert all(r["objectId"] in ids for e in doc["events"] for r in e["relationships"])


@pytest.mark.parametrize("lang", LANGS)
def test_runtime_stream_json_adapter_and_unicode_escaping(outputs, lang):
    doc = outputs[lang]["stream"]["doc"]
    assert [e["id"] for e in doc["events"]] == ["u1", "u3"]
    assert doc["events"][0]["relationships"][0] == {"objectId": 't "9"\né', "qualifier": "consumer_target"}


@pytest.mark.parametrize("lang", LANGS)
def test_runtime_head_hash_matches_independent_sha256_oracle(outputs, lang):
    for source in ("hook", "stream"):
        out = outputs[lang][source]
        assert out["head"] == oracle_head(out["doc"]["events"], lambda b: hashlib.sha256(b).hexdigest()), (lang, source)
        assert out["doc"]["events"][-1]["attributes"][1] == {"name": "pi_hash", "value": out["head"]}


def test_runtime_all_languages_produce_identical_documents_and_heads(outputs):
    for source in ("hook", "stream"):
        ref = outputs["ts"][source]
        for lang in LANGS[1:]:
            assert outputs[lang][source]["head"] == ref["head"], (lang, source)
            assert outputs[lang][source]["doc"] == ref["doc"], (lang, source)


@pytest.mark.parametrize("lang", LANGS)
def test_runtime_chain_verifies_and_tamper_is_detected(outputs, lang):
    for source in ("hook", "stream"):
        out = outputs[lang][source]
        assert out["verify"] is None
        assert out["tampered"] is not None and "mismatch" in out["tampered"]


@pytest.mark.parametrize("lang", LANGS)
def test_runtime_seal_once_and_kind_gating(outputs, lang):
    for source in ("hook", "stream"):
        assert outputs[lang][source]["sealTwice"] is True
        assert outputs[lang][source]["ingestAfterSeal"] is True
    assert outputs[lang]["attachHookRefused"] is True


def test_runtime_otel_source_uses_blake2b256_in_python_only(outputs, generated):
    out = outputs["py"]["otel"]
    assert [e["id"] for e in out["doc"]["events"]] == ["s1", "s3"]
    assert [r["objectId"] for e in out["doc"]["events"] for r in e["relationships"]] == ["t7", "t8"]
    assert out["head"] == oracle_head(out["doc"]["events"], lambda b: hashlib.blake2b(b, digest_size=32).hexdigest())
    assert out["verify"] is None and out["tampered"] is not None
    for lang, rel in (("ts", "ts/tap.ts"), ("rs", "rs/tap.rs"), ("ex", "ex/tap.ex")):
        assert "ticket_otel" not in (generated / rel).read_text(), lang
