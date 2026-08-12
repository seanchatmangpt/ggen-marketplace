#!/usr/bin/env python3
"""Fail-closed validator and CATALOG transition for Enterprise Connection v1.

The envelope is a transport/provenance object. Its SHA-256 content identity is
not a BRCE receipt and never grants DO authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re
from typing import Any

SCHEMA = "urn:ggen:enterprise-connection:v1"
STAGES = ("RECONSTITUTE", "GENERALIZE", "CATALOG", "MANUFACTURE", "EXERCISE")
STAGE_NEXT = dict(zip(STAGES, STAGES[1:]))
STANDINGS = {"UNKNOWN", "PARTIAL_ALIVE", "ALIVE", "BLOCKED", "BUILD_BROKEN", "UNSUPPORTED"}
CEILINGS = {"CONSTRUCT_ONLY", "BOUNDED_GYM", "BRCE_REQUIRED"}
ADMISSIONS = {"REQUESTED", "CANDIDATE", "ADMITTED", "QUALIFIED"}
TOP_KEYS = {"schema", "connection_id", "stage", "producer", "subject", "architecture", "packs", "artifacts", "authority", "standing", "parent", "evidence", "next", "labels"}
HEX40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
REFUSED = re.compile(r"^REFUSED(?::[A-Z0-9_]+)?$")

class ConnectionRefusal(ValueError):
    pass

def _refuse(code: str, detail: str) -> None:
    raise ConnectionRefusal(f"REFUSED:{code}:{detail}")

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()

def _safe_rel(value: str) -> bool:
    if not isinstance(value, str) or not value or "\x00" in value:
        return False
    normalized = value.replace("\\", "/")
    p = PurePosixPath(normalized)
    w = PureWindowsPath(value)
    return normalized not in {".", ".."} and not p.is_absolute() and not w.is_absolute() and not w.drive and all(part not in {"", ".."} for part in p.parts)

def _object(value: Any, name: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict): _refuse("SCHEMA", f"{name} must be object")
    unknown = set(value) - keys
    if unknown: _refuse("UNKNOWN_FIELD", f"{name}:{','.join(sorted(unknown))}")
    missing = keys - set(value)
    if missing: _refuse("MISSING_FIELD", f"{name}:{','.join(sorted(missing))}")
    return value

def _nonempty(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value: _refuse("SCHEMA", f"{name} must be non-empty string")
    return value

def validate_envelope(value: Any, *, raw: bytes | None = None) -> dict[str, Any]:
    env = _object(value, "envelope", TOP_KEYS)
    if env["schema"] != SCHEMA: _refuse("SCHEMA_VERSION", repr(env["schema"]))
    _nonempty(env["connection_id"], "connection_id")
    if env["stage"] not in STAGES: _refuse("STAGE", repr(env["stage"]))
    producer = _object(env["producer"], "producer", {"repository", "revision", "component"})
    if not REPO.fullmatch(_nonempty(producer["repository"], "producer.repository")): _refuse("REPOSITORY", producer["repository"])
    if not HEX40.fullmatch(_nonempty(producer["revision"], "producer.revision")): _refuse("REVISION", producer["revision"])
    _nonempty(producer["component"], "producer.component")
    subject = _object(env["subject"], "subject", {"id", "kind", "revision"})
    for key in ("id", "kind", "revision"): _nonempty(subject[key], f"subject.{key}")
    architecture = _object(env["architecture"], "architecture", {"graph", "capabilities", "constraints"})
    graph = architecture["graph"]
    if graph is not None:
        graph = _object(graph, "architecture.graph", {"path", "media_type", "digest"})
        if not _safe_rel(graph["path"]): _refuse("UNSAFE_PATH", f"architecture.graph:{graph['path']!r}")
        _nonempty(graph["media_type"], "architecture.graph.media_type")
        if not isinstance(graph["digest"], str) or not DIGEST.fullmatch(graph["digest"]): _refuse("DIGEST", "architecture.graph.digest")
    for name in ("capabilities", "constraints"):
        values = architecture[name]
        if not isinstance(values, list) or any(not isinstance(x, str) or not x for x in values): _refuse("SCHEMA", f"architecture.{name}")
        if len(values) != len(set(values)): _refuse("DUPLICATE", f"architecture.{name}")
    if not isinstance(env["packs"], list): _refuse("SCHEMA", "packs")
    seen_packs = set()
    for index, pack in enumerate(env["packs"]):
        pack = _object(pack, f"packs[{index}]", {"name", "version", "digest", "admission"})
        name = _nonempty(pack["name"], f"packs[{index}].name"); version = pack["version"]
        if version is not None and (not isinstance(version, str) or not version): _refuse("SCHEMA", f"packs[{index}].version")
        digest = pack["digest"]
        if digest is not None and (not isinstance(digest, str) or not DIGEST.fullmatch(digest)): _refuse("DIGEST", f"packs[{index}].digest")
        if pack["admission"] not in ADMISSIONS: _refuse("PACK_ADMISSION", repr(pack["admission"]))
        key=(name,version)
        if key in seen_packs: _refuse("DUPLICATE_PACK", f"{name}@{version}")
        seen_packs.add(key)
    if not isinstance(env["artifacts"], list): _refuse("SCHEMA", "artifacts")
    seen_paths=set()
    for index, artifact in enumerate(env["artifacts"]):
        artifact=_object(artifact,f"artifacts[{index}]",{"path","role","media_type","digest"}); path=artifact["path"]
        if not _safe_rel(path): _refuse("UNSAFE_PATH",f"artifacts[{index}]:{path!r}")
        if path in seen_paths: _refuse("DUPLICATE_ARTIFACT",path)
        seen_paths.add(path); _nonempty(artifact["role"],f"artifacts[{index}].role"); _nonempty(artifact["media_type"],f"artifacts[{index}].media_type")
        if not isinstance(artifact["digest"],str) or not DIGEST.fullmatch(artifact["digest"]): _refuse("DIGEST",f"artifacts[{index}].digest")
    authority=_object(env["authority"],"authority",{"ceiling","do_authority"})
    if authority["ceiling"] not in CEILINGS: _refuse("AUTHORITY_CEILING",repr(authority["ceiling"]))
    if authority["do_authority"] is not False: _refuse("AMBIENT_ACTUATION","ConnectionEnvelope never grants DO authority")
    standing=_object(env["standing"],"standing",{"state","claim"}); state=standing["state"]
    if state not in STANDINGS and not (isinstance(state,str) and REFUSED.fullmatch(state)): _refuse("STANDING",repr(state))
    _nonempty(standing["claim"],"standing.claim")
    parent=env["parent"]
    if env["stage"]=="RECONSTITUTE":
        if parent is not None: _refuse("PARENT","RECONSTITUTE must be root")
    else:
        parent=_object(parent,"parent",{"digest","producer"})
        if not isinstance(parent["digest"],str) or not DIGEST.fullmatch(parent["digest"]): _refuse("DIGEST","parent.digest")
        _nonempty(parent["producer"],"parent.producer")
    if not isinstance(env["evidence"],list): _refuse("SCHEMA","evidence")
    for index,evidence in enumerate(env["evidence"]):
        evidence=_object(evidence,f"evidence[{index}]",{"kind","identity","digest"}); _nonempty(evidence["kind"],f"evidence[{index}].kind"); _nonempty(evidence["identity"],f"evidence[{index}].identity")
        digest=evidence["digest"]
        if digest is not None and (not isinstance(digest,str) or not DIGEST.fullmatch(digest)): _refuse("DIGEST",f"evidence[{index}].digest")
    if not isinstance(env["next"],list): _refuse("SCHEMA","next")
    for index,nxt in enumerate(env["next"]):
        nxt=_object(nxt,f"next[{index}]",{"consumer","operation"})
        if not REPO.fullmatch(_nonempty(nxt["consumer"],f"next[{index}].consumer")): _refuse("REPOSITORY",nxt["consumer"])
        _nonempty(nxt["operation"],f"next[{index}].operation")
    labels=env["labels"]
    if not isinstance(labels,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in labels.items()): _refuse("SCHEMA","labels")
    if raw is not None and raw != canonical_bytes(env): _refuse("NON_CANONICAL","envelope bytes must be compact sorted UTF-8 JSON")
    return env

def load(path: Path):
    raw=path.read_bytes()
    try: value=json.loads(raw)
    except json.JSONDecodeError as exc: _refuse("JSON",str(exc))
    return validate_envelope(value,raw=raw),raw

def verify_artifacts(env, root: Path, *, role_prefix=None):
    checked=0; root=root.resolve()
    for artifact in env["artifacts"]:
        if role_prefix is not None and not artifact["role"].startswith(role_prefix): continue
        path=(root/artifact["path"]).resolve()
        try: path.relative_to(root)
        except ValueError: _refuse("PATH_ESCAPE",artifact["path"])
        if not path.is_file(): _refuse("ARTIFACT_MISSING",artifact["path"])
        if sha256_bytes(path.read_bytes()) != artifact["digest"]: _refuse("ARTIFACT_DRIFT",artifact["path"])
        checked += 1
    return checked

def catalog(input_path: Path,out: Path,*,revision: str,artifact_root: Path|None):
    env,raw=load(input_path)
    if env["stage"] != "GENERALIZE": _refuse("TRANSITION",f"CATALOG requires GENERALIZE, got {env['stage']}")
    if not HEX40.fullmatch(revision): _refuse("REVISION",revision)
    checked=verify_artifacts(env,artifact_root,role_prefix="ggen-create:") if artifact_root is not None else 0
    if artifact_root is not None and checked==0: _refuse("NO_CANDIDATE_FACTORY_ARTIFACTS",str(artifact_root))
    next_env={**env,"stage":"CATALOG","producer":{"repository":"seanchatmangpt/ggen-marketplace","revision":revision,"component":"enterprise-architecture-connection-pack"},"parent":{"digest":sha256_bytes(raw),"producer":f"{env['producer']['repository']}@{env['producer']['revision']}"},"authority":{"ceiling":"CONSTRUCT_ONLY","do_authority":False},"standing":{"state":"PARTIAL_ALIVE","claim":"CONNECTION_CONTRACT_ADMITTED"+(f"; CANDIDATE_FACTORY_ARTIFACTS_VERIFIED={checked}" if checked else "")+"; MARKETPLACE_PACK_PUBLICATION_NOT_INFERRED"},"evidence":env["evidence"]+[{"kind":"connection-contract-admission","identity":"enterprise-architecture-connection-pack@0.1.0","digest":None}],"next":[{"consumer":"seanchatmangpt/ggen","operation":"manufacture"}],"labels":{**env["labels"],"catalog_status":"CONTRACT_ADMITTED"}}
    out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(canonical_bytes(validate_envelope(next_env))); return next_env

def validate_chain(paths):
    if not paths: _refuse("CHAIN_EMPTY","at least one envelope required")
    loaded=[load(path) for path in paths]; stages=[env["stage"] for env,_ in loaded]
    if stages[0] != "RECONSTITUTE": _refuse("CHAIN_ROOT",stages[0])
    for index in range(1,len(loaded)):
        previous,previous_raw=loaded[index-1]; current,_=loaded[index]; expected_stage=STAGE_NEXT.get(previous["stage"])
        if current["stage"] != expected_stage: _refuse("CHAIN_STAGE",f"{previous['stage']}->{current['stage']}")
        if current["connection_id"] != previous["connection_id"]: _refuse("CHAIN_ID",f"index={index}")
        if current["parent"]["digest"] != sha256_bytes(previous_raw): _refuse("CHAIN_DIGEST",f"index={index}")
        expected=f"{previous['producer']['repository']}@{previous['producer']['revision']}"
        if current["parent"]["producer"] != expected: _refuse("CHAIN_PRODUCER",f"index={index}")
        if current["authority"]["do_authority"] is not False: _refuse("AMBIENT_ACTUATION",f"index={index}")
    return {"valid":True,"schema":"enterprise-connection-chain-receipt/1","connection_id":loaded[0][0]["connection_id"],"envelopes":len(loaded),"stages":stages,"head_digest":sha256_bytes(loaded[-1][1]),"do_authority":False,"standing":"ALIVE","claim":"ENTERPRISE_CONNECTION_TRANSPORT_COMPOSITION_ONLY"}

def main(argv=None):
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command",required=True)
    p=sub.add_parser("validate"); p.add_argument("path",type=Path)
    p=sub.add_parser("chain"); p.add_argument("paths",nargs="+",type=Path)
    p=sub.add_parser("catalog"); p.add_argument("path",type=Path); p.add_argument("--revision",required=True); p.add_argument("--artifact-root",type=Path); p.add_argument("--out",type=Path,required=True)
    args=parser.parse_args(argv)
    try:
        if args.command=="validate": env,raw=load(args.path); result={"valid":True,"stage":env["stage"],"digest":sha256_bytes(raw)}
        elif args.command=="chain": result=validate_chain(args.paths)
        else: env=catalog(args.path,args.out,revision=args.revision,artifact_root=args.artifact_root); result={"valid":True,"stage":env["stage"],"out":str(args.out),"digest":sha256_bytes(args.out.read_bytes())}
    except (ConnectionRefusal,OSError) as exc: print(json.dumps({"valid":False,"error":str(exc)},sort_keys=True)); return 2
    print(json.dumps(result,sort_keys=True)); return 0

if __name__=="__main__": raise SystemExit(main())
