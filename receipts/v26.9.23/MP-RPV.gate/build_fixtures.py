"""Scratch builder for MP-RPV qualification fixtures (data only; the builder is not shipped).
Each fixture = a real receipt + one recorded mutation. Prints a TSV derivation table."""
import copy, hashlib, json, sys
from pathlib import Path

PACK = Path("/Users/sac/wt/v26922/v23/MP-RPV/packs/receipt-provenance-unification-pack")
SRC = Path("/Users/sac/wt/v26922/fri/xaas-int/docs/sjira/v26.9.23/receipts/GC23-4.json")
raw = SRC.read_bytes()
base = json.loads(raw)
src_sha = hashlib.sha256(raw).hexdigest()
DF = PACK / "qualification/fixtures/dfcm_fleet_v1"
DU = PACK / "qualification/fixtures/durable"
DF.mkdir(parents=True, exist_ok=True); DU.mkdir(parents=True, exist_ok=True)
MARKET_BASE = "420bc91e7c1e291be73ab749b7e443252bc7bab8"  # marketplace origin/main at lane base
XAAS_DURABLE = "295e0200a9f61b78d4a631c667e4851cff7b8bb1"  # origin/friday/gc-fri-0800 (pushed)
XAAS_BASE = base["identity"]["base_sha"]
rows = []

def emit(d, name, doc, what):
    p = d / name
    if isinstance(doc, (dict, list)):
        p.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    else:
        p.write_text(doc)
    rows.append((str(p.relative_to(PACK)), what))

def mut(fn):
    d = copy.deepcopy(base); fn(d); return d

def setp(path, value):
    def f(d):
        node = d
        parts = path.split(".")
        for k in parts[:-1]:
            node = node[k] if not k.isdigit() else node[int(k)]
        last = parts[-1]
        if value is DELETE:
            del node[last]
        else:
            node[last] = value
    return f

DELETE = object()
cmd0 = "replay.commands.0"
emit(DF, "pos-base-GC23-4.json", base, f"unmodified copy (re-serialized, sorted keys) of {SRC} sha256:{src_sha}")
cases = [
 ("pos", "exit-integral-float", f"{cmd0}.exit", 75.0, "replay exit 75 -> 75.0 (JSON Schema draft 4+ integer admits an integral float)"),
 ("pos", "durable-location-empty", "replay.durable_location", "", "replay.durable_location -> \"\" (schema: type string, no minLength)"),
 ("pos", "files-changed-empty-string", "consequence.files_changed", [""], "consequence.files_changed -> [\"\"] (items type string, no minLength)"),
 ("pos", "alive-exit0", None, None, "standing.value -> ALIVE and replay exit -> 0"),
 ("pos", "local-repo-known-commit", None, None, f"identity.repo -> \".\" and subject_sha -> {MARKET_BASE} (marketplace commit; validate_receipt.py:20-25 probes it)"),
 ("neg", "notasha", "identity.subject_sha", "NOTASHA", "identity.subject_sha -> NOTASHA"),
 ("neg", "no-standing-value", "standing.value", DELETE, "standing.value deleted"),
 ("neg", "alive-nonzero-exit", "standing.value", "ALIVE", "standing.value -> ALIVE with the replay exit 75 kept (admission_vacuous, validate_receipt.py:18)"),
 ("pos", "alive-trailing-newline-exit75", "standing.value", "ALIVE\n", "standing.value -> \"ALIVE\\n\": passes the schema pattern ($) but is not == ALIVE, so validate_receipt.py admits it"),
 ("neg", "empty-replay", "replay.commands", [], "replay.commands -> [] (minItems 1)"),
 ("neg", "no-consequence", "consequence", DELETE, "consequence deleted"),
 ("neg", "commits-not-array", "consequence.commits", "abc1234", "consequence.commits -> \"abc1234\" (type array)"),
 ("neg", "commit-bad-item", "consequence.commits", ["NOTASHA"], "consequence.commits -> [NOTASHA] (items pattern)"),
 ("neg", "files-changed-int-item", "consequence.files_changed", [1], "consequence.files_changed -> [1] (items type string)"),
 ("neg", "blocked-no-broken-term", "standing.value", "BLOCKED:operator", "standing.value -> BLOCKED:operator without broken_term (allOf if/then)"),
 ("neg", "bad-broken-term", "standing.broken_term", "R_missing_everything", "standing.broken_term -> R_missing_everything (enum)"),
 ("neg", "bad-ceiling", "authority.ceiling", "ROOT", "authority.ceiling -> ROOT (enum)"),
 ("neg", "ceiling-trailing-newline", "authority.ceiling", "DO\n", "authority.ceiling -> \"DO\\n\" (enum equality refuses the newline)"),
 ("neg", "bad-output-sha", f"{cmd0}.output_sha256", "xyz", "replay output_sha256 -> xyz (pattern)"),
 ("neg", "graph-hash-null", "identity.graph_hash", None, "identity.graph_hash -> null (optional but typed string)"),
 ("neg", "summary-int", f"{cmd0}.summary", 5, "replay summary -> 5 (type string)"),
 ("neg", "exit-bool", f"{cmd0}.exit", True, "replay exit -> true (bool is not an integer)"),
 ("neg", "exit-fractional", f"{cmd0}.exit", 0.5, "replay exit -> 0.5"),
 ("neg", "grant-empty", "authority.grant", "", "authority.grant -> \"\" (minLength 1)"),
 ("pos", "subject-newline-only", "identity.subject", "\n", "identity.subject -> \"\\n\": minLength 1 passes"),
 ("neg", "local-repo-missing-commit", None, None, "identity.repo -> \".\" and subject_sha -> 000..0 (validate_receipt.py:20-25 refuses: not a commit)"),
 ("neg", "standing-not-object", "standing", "ALIVE", "standing -> \"ALIVE\" (type object)"),
 ("neg", "root-array", None, None, "document -> [] (type object)"),
]
for sign, name, path, value, what in cases:
    if name == "alive-exit0":
        d = mut(lambda d: (d["standing"].__setitem__("value", "ALIVE"), d["replay"]["commands"][0].__setitem__("exit", 0)))
    elif name == "local-repo-known-commit":
        d = mut(lambda d: (d["identity"].__setitem__("repo", "."), d["identity"].__setitem__("subject_sha", MARKET_BASE)))
    elif name == "local-repo-missing-commit":
        d = mut(lambda d: (d["identity"].__setitem__("repo", "."), d["identity"].__setitem__("subject_sha", "0" * 40)))
    elif name == "root-array":
        d = []
    else:
        d = mut(setp(path, value))
    emit(DF, f"{sign}-{name}.json", d, what)

# durable profile fixtures
import shutil
for src, dst in [("/private/tmp/claude-501/v23-scratch/SCAN-stale-evidence/forged-GC23-4.json", "neg-forged-GC23-4.json"),
                 ("/private/tmp/claude-501/v23-scratch/SCAN-CE23-9-validator-durable-identity-profile/forged-slug-notes-sha0.json", "neg-forged-slug-notes-sha0.json")]:
    b = Path(src).read_bytes()
    (DU / dst).write_bytes(b)
    rows.append((str((DU / dst).relative_to(PACK)), f"byte copy of {src} sha256:{hashlib.sha256(b).hexdigest()}"))

def dur(fn):
    d = copy.deepcopy(base); d["identity"]["repo"] = "seanchatmangpt/xaas"; fn(d); return d
path = "docs/sjira/v26.9.23/receipts/GC23-4.json"
emit(DU, "pos-git-blob.json", dur(lambda d: d["replay"].__setitem__("durable_location", f"git:seanchatmangpt/xaas@{XAAS_DURABLE}:{path}")),
     f"GC23-4 with identity.repo -> seanchatmangpt/xaas and durable_location -> git:seanchatmangpt/xaas@{XAAS_DURABLE}:{path} (blob exists there; subject 11a24fb is its ancestor)")
emit(DU, "pos-https-form-only.json", dur(lambda d: d["replay"].__setitem__("durable_location", "https://github.com/seanchatmangpt/xaas/blob/295e0200a9f61b78d4a631c667e4851cff7b8bb1/docs/sjira/v26.9.23/receipts/GC23-4.json")),
     "GC23-4 with slug repo and an https durable_location (accepted by form only; the VALID output says so)")
emit(DU, "neg-blob-not-descendant.json", dur(lambda d: d["replay"].__setitem__("durable_location", f"git:seanchatmangpt/xaas@{XAAS_BASE}:mix.exs")),
     f"durable_location -> git:...@{XAAS_BASE}:mix.exs: the blob exists but that commit is the subject's base, not a descendant (ancestor_of fails)")
emit(DU, "neg-blob-missing-path.json", dur(lambda d: d["replay"].__setitem__("durable_location", f"git:seanchatmangpt/xaas@{XAAS_DURABLE}:docs/does-not-exist.json")),
     "durable_location names a path absent at that commit (blob_at_commit fails)")
emit(DU, "neg-relative-path.json", dur(lambda d: None),
     "durable_location left as the committed relative path docs/sjira/.../GC23-4.json: names no repository and no commit")
emit(DU, "neg-tmp-location.json", dur(lambda d: d["replay"].__setitem__("durable_location", "/tmp/GC23-4.json")),
     "durable_location -> /tmp/GC23-4.json (ephemeral local path)")
emit(DU, "neg-var-folders-location.json", dur(lambda d: d["replay"].__setitem__("durable_location", "/var/folders/xx/T/GC23-4.json")),
     "durable_location -> /var/folders/... (ephemeral local path)")
emit(DU, "neg-unmapped-slug.json", dur(lambda d: (d["identity"].__setitem__("repo", "seanchatmangpt/not-mapped"), d["replay"].__setitem__("durable_location", f"git:seanchatmangpt/not-mapped@{XAAS_DURABLE}:{path}"))),
     "identity.repo and the location repo -> seanchatmangpt/not-mapped (no --repo-map entry)")
emit(DU, "neg-subject-not-in-repo.json", dur(lambda d: d["identity"].__setitem__("subject_sha", MARKET_BASE)),
     f"identity.subject_sha -> {MARKET_BASE} (a real commit, but of ggen-marketplace, not of the mapped xaas repository)")
emit(DU, "neg-dotdot-slug.json", dur(lambda d: d["identity"].__setitem__("repo", "../xaas")),
     "identity.repo -> ../xaas (path segment, not a slug)")
for p, w in rows:
    print(f"{p}\t{w}")

DS = PACK / "qualification/fixtures/durable_standing"
DS.mkdir(parents=True, exist_ok=True)
emit(DS, "neg-alive-trailing-newline.json",
     dur(lambda d: (d["replay"].__setitem__("durable_location", f"git:seanchatmangpt/xaas@{XAAS_DURABLE}:{path}"), d["standing"].__setitem__("value", "ALIVE\n"))),
     "pos-git-blob.json with standing.value -> \"ALIVE\\n\" and the replay exit 75 kept: admitted by the default profile (schema $), refused by the durable profile (\\Z)")
emit(DS, "pos-unknown-exact.json",
     dur(lambda d: d["replay"].__setitem__("durable_location", f"git:seanchatmangpt/xaas@{XAAS_DURABLE}:{path}")),
     "same receipt as durable/pos-git-blob.json (standing UNKNOWN, exact): the strict standing binding admits it")
for p, w in rows[-2:]:
    print(f"{p}\t{w}")

emit(DU, "neg-sha0-https.json",
     dur(lambda d: (d["identity"].__setitem__("subject_sha", "0" * 40), d["replay"].__setitem__("durable_location", "https://github.com/seanchatmangpt/xaas/blob/295e0200a9f61b78d4a631c667e4851cff7b8bb1/docs/sjira/v26.9.23/receipts/GC23-4.json"))),
     "slug repo, subject_sha -> 000..0, https durable_location: only the durable subject_commit probe can refuse it (R_missing_identity)")
print("\t".join(rows[-1]))
