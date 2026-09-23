#!/usr/bin/env python3
"""MP-RPV mutation matrix (evidence harness, not product code).

For each mutant: copy the committed pack into a throwaway git repo whose object store borrows the
marketplace objects through alternates (so identity.repo "." fixtures resolve), apply one edit,
regenerate with `ggen sync run`, then run (a) the lane gate with the pack path substituted and
(b) generated/qualification_runner.py. A mutant is KILLED when either exits non-zero.
Usage: mutation_matrix.py <committed pack dir> <scratch dir> <lane gate template> [mutant ...]
"""
import json, os, re, shutil, subprocess, sys

PACK, SCRATCH, GATE = sys.argv[1], sys.argv[2], sys.argv[3]
ONLY = set(sys.argv[4:])
XAAS = "/Users/sac/wt/v26922/fri/xaas-int"
ALT = subprocess.run(["git", "-C", PACK, "rev-parse", "--git-common-dir"], capture_output=True, text=True, cwd=PACK).stdout.strip()
ALT = os.path.join(os.path.abspath(os.path.join(PACK, ALT)) if not os.path.isabs(ALT) else ALT, "objects")

def drop(pattern):
    def f(s):
        s2 = re.sub(pattern, "", s, count=1, flags=re.S)
        assert s2 != s, pattern
        return s2
    return f

def sub(old, new):
    def f(s):
        assert old in s, old
        return s.replace(old, new, 1)
    return f

MUTANTS = {
 "M1-drop-alive-rule": ("ontology.ttl", drop(r"rp:rule_alive_exit0 a rp:ImplicationRule.*?rp:sourceLine 18 \.\n")),
 "M2-drop-conditional-broken-term": ("ontology.ttl", sub('rp:requiredWhenPath "standing.value" ; rp:requiredWhenPattern "^(BLOCKED|BUILD_BROKEN|REFUSED)" ;', "")),
 "M3-drop-min-items": ("ontology.ttl", sub('skos:prefLabel "array-min1" ; rp:jsonType "array" ; rp:pattern "" ; rp:minItems 1 ;', 'skos:prefLabel "array-min1" ; rp:jsonType "array" ; rp:pattern "" ;')),
 "M4-drop-integral-float": ("ontology.ttl", sub('rp:pattern "" ; rp:admitsIntegralFloat true ;', 'rp:pattern "" ;')),
 "M5-json-string-min1": ("ontology.ttl", sub('skos:prefLabel "json-string" ; rp:jsonType "string" ; rp:pattern "" ; rp:minLength 0 ;', 'skos:prefLabel "json-string" ; rp:jsonType "string" ; rp:pattern "" ; rp:minLength 1 ;')),
 "M6-graph-hash-nullable": ("ontology.ttl", sub('rp:dottedPath "identity.graph_hash" ; rp:valueForm rp:vf_sha256_prefixed ; rp:mandatory false ; rp:nullable false ;', 'rp:dottedPath "identity.graph_hash" ; rp:valueForm rp:vf_sha256_prefixed ; rp:mandatory false ;')),
 "M7-drop-local-dir-probe": ("ontology.ttl", sub('rp:resolution rp:res_subject_commit ; rp:repoPath "identity.repo" ; rp:repoMode "local-dir" ;', "")),
 "M8-drop-durable-subject-probe": ("ontology.ttl", sub('rp:resolution rp:res_subject_commit ; rp:repoPath "identity.repo" ; rp:repoMode "repo-map" ;', "")),
 "M9-drop-notes-probe": ("ontology.ttl", sub("rp:resolution rp:res_notes_object , rp:res_ancestor_of ;", "rp:resolution rp:res_ancestor_of ;")),
 "M10-drop-blob-probe": ("ontology.ttl", sub("rp:resolution rp:res_blob_at_commit , rp:res_ancestor_of ;", "rp:resolution rp:res_ancestor_of ;")),
 "M11-drop-ancestor-probe": ("ontology.ttl", lambda s: sub("rp:resolution rp:res_notes_object , rp:res_ancestor_of ;", "rp:resolution rp:res_notes_object ;")(sub("rp:resolution rp:res_blob_at_commit , rp:res_ancestor_of ;", "rp:resolution rp:res_blob_at_commit ;")(s))),
 "M12-drop-durable-location-binding": ("ontology.ttl", drop(r"rp:f_dd_dloc a rp:FieldBinding.*?rp:sourceLine 55 \.\n")),
 "M13-drop-strict-standing": ("ontology.ttl", drop(r"rp:f_dd_sval a rp:FieldBinding.*?rp:sourceLine 18 \.\n")),
 "M14-drop-durable-location-term": ("ontology.ttl", lambda s: s.replace('rp:dottedPath "replay.durable_location" ; rp:valueForm rp:vf_durable_location ; rp:mandatory true ;\n    rp:brokenTerm "R_missing_replay" ;', 'rp:dottedPath "replay.durable_location" ; rp:valueForm rp:vf_durable_location ; rp:mandatory true ;', 1)),
 "M15-https-accepts-tmp": ("ontology.ttl", sub('rp:pattern "^https://[^/\\\\s]+/\\\\S*\\\\Z" ;', 'rp:pattern "^(https://|/)\\\\S*\\\\Z" ;')),
 "M16-template-no-fault-guard": ("templates/unified_receipt_validator.py.tmpl", sub("    except Exception as exc:  # a fault is never a verdict and never a traceback\n", "    except ZeroDivisionError as exc:\n")),
}

def run(cmd, cwd, log):
    with open(log, "wb") as fh:
        return subprocess.run(cmd, cwd=cwd, stdout=fh, stderr=subprocess.STDOUT).returncode

results = {}
for mid, (rel, edit) in MUTANTS.items():
    if ONLY and mid not in ONLY:
        continue
    root = os.path.join(SCRATCH, mid)
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    subprocess.run(["git", "init", "-q", root], check=True)
    with open(os.path.join(root, ".git/objects/info/alternates"), "w") as fh:
        fh.write(ALT + "\n")
    pack = os.path.join(root, "pack")
    shutil.copytree(PACK, pack, ignore=shutil.ignore_patterns(".ggen", ".ggen-v2"))
    path = os.path.join(pack, rel)
    src = open(path).read()
    new = edit(src)
    assert new != src, mid
    open(path, "w").write(new)
    sync = run(["ggen", "sync", "run"], pack, os.path.join(root, "sync.log"))
    gate_text = open(GATE).read().replace("/Users/sac/wt/v26922/v23/MP-RPV/packs/receipt-provenance-unification-pack", pack)
    gate_file = os.path.join(root, "gate.sh")
    open(gate_file, "w").write(gate_text)
    gate = run(["bash", gate_file], pack, os.path.join(root, "gate.log"))
    runner = run(["python3", "generated/qualification_runner.py", "--repo-map", f"seanchatmangpt/xaas={XAAS}"], pack, os.path.join(root, "runner.log"))
    tail = open(os.path.join(root, "runner.log")).read().strip().splitlines()
    fails = [l for l in tail if l.startswith("FAIL")][:3]
    div = [l for l in open(os.path.join(root, "gate.log")).read().splitlines() if l.startswith("DIVERGE")]
    killed = sync != 0 or gate != 0 or runner != 0
    results[mid] = {"sync": sync, "lane_gate": gate, "runner": runner, "killed": killed, "gate_diverge": div, "runner_fail": fails}
    print(json.dumps({mid: results[mid]}))
print("SURVIVORS", [m for m, r in results.items() if not r["killed"]])
