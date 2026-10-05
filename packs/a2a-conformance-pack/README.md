# a2a-conformance-pack

Conformance-machinery manufacturer for the A2A Protocol v1.0, projected
from the ash_a2a repository (truth source: `/Users/sac/ash_a2a`).

## What this pack packages

The conformance SURFACE, not protocol semantics (protocol surface lives
in the sibling `a2a-v1-protocol-pack`). Every individual cites the real
file it projects; nothing is synthesized:

| Individual | Truth source (real file) |
| --- | --- |
| CourtRunner | `lib/mix/tasks/ash_a2a.v1_conformance_report.ex` |
| CourtFile x25 | `test/ash_a2a_v1_*.exs` (the runner's `@v1_courts`) |
| SpecCorpus | `priv/a2a_v1_spec_corpus/v1_spec_examples.json` (36 examples) |
| SpecIdl | `priv/a2a_v1_spec_corpus/a2a.proto` (sha pinned) |
| TCKRun | 2026-10-05 jsonrpc compatibility run (69.2%) |
| ProtoFidelityCourt | `test/ash_a2a_v1_proto_fidelity_test.exs` (all-MATCH) |

Templates: a NEW spec requirement's conformance-court SKELETON
(ExUnit + positive control + kill, the house style of the cited family)
and a spec-corpus entry in exactly the frozen corpus's key shape.

## Running the conformance report

From the ash_a2a checkout:

```bash
mix ash_a2a.v1_conformance_report
mix ash_a2a.v1_conformance_report --out receipts/v1-conformance.json
mix ash_a2a.v1_conformance_report --only v1_pagination
```

The task takes the maintained court list (`@v1_courts`, 25 entries),
verifies each entry against the real filesystem, runs each existing
court as a real OS subprocess (`mix test <file> --include serial`),
and writes one JSON report: `courts` is
`[%{file, exit_code, summary_line, verdict: PASS|FAIL}]`, `totals` is
`%{pass, fail, total}`.

Exit status: this is a REPORT task (always exits 0); the gate is the
JSON itself -- `totals.fail == 0`. A listed court missing on disk
becomes a FAIL court-status entry, never a silent pass. Expect a LONG
run (minutes to tens of minutes; the serial tail drives real Bandit
loopback listeners). `--only SUBSTRING` iterates on a subset; a
zero-match substring is a well-formed empty report, not an error.

`mix ash_a2a.v1_conformance_report` is **not** the official A2A TCK.
A full-PASS report witnesses the same executed courts the statement
cites -- not TCK certification.

## The honest TCK matrix

The official `a2aproject/a2a-tck` compatibility suite ran once against
a real ash_a2a JSONRPC server (2026-10-05, lane Z19). Point-in-time
verdict on the JSONRPC binding -- not certification.

| Transport | Total | Pass | Fail | Skip |
| --- | --- | --- | --- | --- |
| agent_card | 10 | 10 | 0 | 0 |
| jsonrpc | 88 | 68 | 5 | 15 |
| grpc | 72 | 0 | 0 | 72 |
| http_json | 83 | 3 | 0 | 80 |

Overall: **69.2%** (MUST 70.4% / SHOULD 42.9% / MAY 100%).

- The 3 MUST infrastructure failures observed pre-fix were fixed
  in-session in `lib/ash_a2a/transport/plug.ex`: the `A2A-Version`
  header gate answers the spec-mandated `-32009`;
  `tasks/resubscribe` on an unknown/foreign task answers `-32001`
  TaskNotFound (spec §3.16, TCK STREAM-SUB-004); the agent card serves
  `Cache-Control`/`ETag` (spec §8.6.1).
- The 5 remaining jsonrpc failures are pinned as NOT spec violations:
  the TCK echo-SUT behavioral contract (DM-ART-001, DM-MSG-001) --
  prefix-keyed canned responses the reference Python SUT
  hand-implements; reproducing them would mean faking the contract.
- grpc and http_json were skipped because the served card declared the
  JSONRPC interface only at run time.

Raw reports were session-ephemeral (`/tmp/z19/tck_reports_ash_a2a_final`);
re-run the suite to regenerate.

## TCK recipe

```bash
git clone https://github.com/a2aproject/a2a-tck
cd a2a-tck
python3.12 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
# against the in-repo SUT (from the ash_a2a checkout):
python run_tck.py --transport jsonrpc
```

- The suite classifies results MUST / SHOULD / MAY; `compatibility.json`
  carries the per-transport matrix above.
- The in-repo SUT is `tck_sut.exs` (a real server over the real
  transport; the repo's dispatcher cannot reproduce the TCK's echo-SUT
  canned contract without faking it).
- Raw JUnit/HTML/`compatibility.json` reports are session-ephemeral;
  re-run to regenerate.
- grpc/http_json need the served card to declare those interfaces;
  the gRPC binding exists (`AshA2A.Transport.GRPC.Server`) but no TCK
  run over gRPC has been executed.

## Gates

```bash
# SPARQL half (ggen renders gates over ontology.ttl; directly with rdflib):
#   returns zero rows = pass
python3 -c "import rdflib; \
  g=rdflib.Graph(); g.parse('packs/a2a-conformance-pack/ontology.ttl'); \
  print(list(g.query(open('packs/a2a-conformance-pack/gates/010_corpus_integrity.rq').read())))"

# Executable half (real filesystem, real hashing):
bash packs/a2a-conformance-pack/gates/verify_corpus_integrity.sh [ASH_A2A_CHECKOUT]
bash packs/a2a-conformance-pack/gates/verify_runner_completeness.sh [ASH_A2A_CHECKOUT]
```

- `010_corpus_integrity.rq` + `verify_corpus_integrity.sh`: the vendored
  proto is pristine -- sha256 pinned in the gate header and ontology
  (`945df6e3...`); the script re-hashes the real file and refuses any
  drift; the frozen counts (36 = 30 + 6 codec_gap) and the closed
  9-family vocabulary are pinned, not derived.
- `020_runner_completeness.rq` + `verify_runner_completeness.sh`: the
  falsifier -- "the runner task exists and its court list matches the
  pack's inventory" -- executed against the real runner source and the
  real filesystem, order included.

## Templates

- `templates/conformance_court_skeleton.exs.tmpl` -- for a
  `a2ac:NewSpecRequirement` in the consumer's ontology; renders the
  three-leg house style (positive control, positive witness, kill).
  A rendered-but-unfilled skeleton FAILS its own court: the legs are
  `flunk`s until filled in, so an unfilled skeleton is a visible
  failure, never a green check.
- `templates/spec_corpus_entry.json.tmpl` -- for an
  `a2ac:NewCorpusEntry`; renders exactly the frozen corpus's key shape
  (id, family, source, expect, decode, deviations, finding,
  expected_error, wire) into
  `priv/a2a_v1_spec_corpus/entries/`; fold into
  `v1_spec_examples.json` with review -- the corpus court's integrity
  tests then take over.

## Falsifier

"the runner task exists and its court list matches the pack's
inventory" -- executed by `gates/verify_runner_completeness.sh`. All
kill legs witnessed in-session: tampered proto sha -> FAIL; missing
runner -> FAIL; listed court missing on disk -> FAIL; list drift ->
FAIL; sha drift / family-sum drift / duplicate index / list-size drift
in the graph -> SPARQL violation rows.
