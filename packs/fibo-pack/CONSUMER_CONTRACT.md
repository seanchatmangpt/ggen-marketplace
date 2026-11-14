# FIBO physics contract (FortNox / fnox)

Brand FortNox; `fnox` = shortname, CLI, and the ONLY private namespace prefix (`fnox:`).
Doctrine (operator): the domain we own is the PUBLIC ontology (EDM Council FIBO, W3C OWL/RDF/SHACL/
PROV-O/TIME/ODRL, OCEL 2.0). A private `fnox:` term is admitted ONLY with an exhaustion proof:
public candidates tried + why none can express it without loss of determinism. Exhaust public first.
"Physics" = conservation / ordering / timing laws expressed as SHACL + SPARQL and executable checkers
over a run (`walkthrough.engine.run()` / `walkthrough.live.run_live()` dict). Money = integer cents.
Subject data: /Users/sac/fnox/walkthrough/steps.py, rules.py, economics.py, engine.py, scenario/.
Never trust a FIBO IRI from memory or from chat transcripts: every cited class/property must be
verified against real FIBO source (lane F1 produces fibo/verified_iris.json). Unverified => not used.

## Interfaces
- `fibo/verified_iris.json`: {"<full IRI>": {"label","module","exists":bool,"source":"path-or-url"}}
- `fibo/physics/<law>.py`: `check(run:dict) -> {"law":str,"ok":bool,"violations":[str],"evidence":dict}`; never raises.
- `fibo/validate.py`: `main()` builds RDF data graph from a run (fibo/run_graph.py `to_graph(run)->rdflib.Graph`),
  loads ontology/fibo/*.ttl shapes, runs pySHACL + all physics checkers, prints a table, exit 1 on any violation.
- `fibo/exhaustion.py`: `audit(ttl_paths)->{"private_terms":[..],"admitted":[..],"refused":[..]}`; exit 1 if any
  `fnox:` term lacks an entry in fibo/exhaustion_register.ttl.
- Ontologies live in ontology/fibo/*.ttl (public classes only; shapes in sh:). Prefix IRIs must be real FIBO IRIs.
## Rules for every lane
Absolute paths only. Own only your listed files (disjoint). No git. Python: /Users/sac/fnox/planner/.venv/bin/python
with PYTHONPATH=/Users/sac/fnox:/Users/sac/fnox/pipeline; run from /Users/sac/fnox (a stray /tmp/bisect.py shadows the
stdlib if you run from /tmp). The nocompile hook may refuse build/test commands for subagents: if blocked, say so in the
receipt as UNVERIFIED with the exact gate command for the coordinator; never claim a pass you did not observe.
Chicago-style tests, no mocks. Receipts: /Users/sac/fnox/fibo/receipts/<lane>.md with `Standing:` line + exact file list.

## Sync check
exhaustion_register.ttl is a copy of fnox/fibo/exhaustion_register.ttl; verify with
`diff /Users/sac/fnox/fibo/exhaustion_register.ttl packs/fibo-pack/ontology/exhaustion_register.ttl`.
