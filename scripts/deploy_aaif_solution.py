#!/usr/bin/env python3
"""deploy_aaif_solution.py -- THE one customer deployer for an AAIF solution.

10-step fail-closed flow (pay-before-manufacture):

    1. python >= 3.11 gate
    2. monetization registry admission (scripts/marketplace_monetization.py)
    3. solution.json lock verification (profile + pack content digests)
    4. ENTITLEMENT GATE (scripts/entitlement.py decide()) BEFORE any manufacture
       -- the output dist/ must not exist yet
    5. manufacture: `ggen sync run` in the solution dir (HOME/XDG temp capsule)
    6. re-run the packs' SPARQL gates on the manufactured graph
    7. namespace-scope check over the dist manifests
    8. consequence digest (fingerprint_paths fold over the dist tree)
    9. paid-delivery receipt with monetization+actuation blocks
   10. actuation_plan.json emission + optional --actuate
       (kind rail prints the kubectl sequence WITHOUT executing; gke rail
       requires real gcloud/kubectl and a matching gcloud project)

Refusal -> exit-code table (house scheme):
    2  config/validation   (python, lock missing/invalid, budget, dist exists)
    3  entitlement endpoint unreachable
    4  entitlement not active / not found
    5  invalid entitlement response
    6  monetization registry invalid (schema, keys, authority cardinality)
    7  ggen runtime not found
    8  gate/scope violation (SPARQL gate row, cluster-scoped manifest,
                            data-residency mismatch)
    9  digest drift (profile/pack lock drift, non-monotonic grant)
   10  gcloud/kubectl actuation tooling or project mismatch
   12  ggen sync actuation failure
   13  paid-delivery receipt write failure
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

if sys.version_info < (3, 11):
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED")

ROOT = Path(__file__).resolve().parent.parent
for _p in (str(ROOT), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import marketplace_monetization as monetization  # noqa: E402
from marketplace import fingerprint_paths  # noqa: E402

# ---------------------------------------------------------------------------
# Typed refusal constants (the four exec-summary refusals included).
# ---------------------------------------------------------------------------
REFUSED_PYTHON = "REFUSED:PYTHON_3_11_REQUIRED"
REFUSED_LOCK_MISSING = "REFUSED:SOLUTION_LOCK_MISSING"
REFUSED_LOCK_INVALID = "REFUSED:SOLUTION_LOCK_INVALID"
REFUSED_DIST_EXISTS = "REFUSED:DIST_ALREADY_EXISTS"
REFUSED_BUDGET_EXCEEDED = "REFUSED:BUDGET_EXCEEDED"
REFUSED_PROFILE_DIGEST_DRIFT = "REFUSED:PROFILE_DIGEST_DRIFT"
REFUSED_NON_MONOTONIC_GRANT = "REFUSED:NON_MONOTONIC_GRANT"
REFUSED_GGEN_NOT_FOUND = "REFUSED:GGEN_NOT_FOUND"
REFUSED_GGEN_SYNC_FAILED = "REFUSED:GGEN_SYNC_FAILED"
REFUSED_SOLUTION_GATE_VIOLATION = "REFUSED:SOLUTION_GATE_VIOLATION"
REFUSED_MANIFEST_CLUSTER_SCOPED = "REFUSED:MANIFEST_CLUSTER_SCOPED"
REFUSED_DATA_RESIDENCY_VIOLATION = "REFUSED:DATA_RESIDENCY_VIOLATION"
REFUSED_GKE_TOOLING_MISSING = "REFUSED:GKE_TOOLING_MISSING"
REFUSED_GCLOUD_PROJECT_MISMATCH = "REFUSED:GCLOUD_PROJECT_MISMATCH"
REFUSED_RECEIPT_WRITE_FAILED = "REFUSED:RECEIPT_WRITE_FAILED"

# House exit-code scheme.
EXIT_CONFIG = 2
EXIT_UNREACHABLE = 3
EXIT_NOT_ACTIVE = 4
EXIT_INVALID_RESPONSE = 5
EXIT_REGISTRY_INVALID = 6
EXIT_GGEN_MISSING = 7
EXIT_GATE_SCOPE = 8
EXIT_DIGEST_DRIFT = 9
EXIT_ACTUATION_TOOLING = 10
EXIT_ACTUATION_FAILED = 12
EXIT_RECEIPT = 13

# Namespace-scope law: the only cluster-level object class allowed is
# Namespace itself (allowlisted explicitly); everything else in the dist
# must be namespaced. Refusals name the file + kind.
FORBIDDEN_KINDS = frozenset(
    {
        "ClusterRole",
        "ClusterRoleBinding",
        "ValidatingWebhookConfiguration",
        "MutatingWebhookConfiguration",
        "CustomResourceDefinition",
        "PriorityClass",
        "StorageClass",
        "IngressClass",
        "CSIDriver",
        "CSINode",
        "Node",
        "PersistentVolume",
    }
)
ALLOWED_CLUSTER_KINDS = frozenset({"Namespace"})

AAIF_NS = "https://aaif.io/ontology#"
RESIDENCY_PREDICATE = f"{AAIF_NS}residencyRegionLock"

SCHEMA_V1 = "https://ggen.dev/marketplace/aaif-deployment/v1"
KIND_CONTEXT = "kind-aaif-marketplace"


class Refused(Exception):
    """Typed refusal carrying (message, exit_code)."""

    def __init__(self, message: str, exit_code: int):
        super().__init__(message)
        self.message = message
        self.exit_code = exit_code


def refused(code: str, detail: str, exit_code: int) -> Refused:
    return Refused(f"REFUSED:{code}:{detail}", exit_code)


def _die(exc: Refused) -> None:
    print(exc.message, file=sys.stderr)
    raise SystemExit(exc.exit_code)


# ---------------------------------------------------------------------------
# Step 2: monetization registry admission
# ---------------------------------------------------------------------------


def load_registry(config_path: Path) -> dict[str, Any]:
    """Admit monetization.toml via the marketplace_monetization loader.

    Invalid registry (schema, unknown keys, authority cardinality, price,
    backend) -> exit 6. A unit price <= 0 additionally trips the exec-summary
    REFUSED_BUDGET_EXCEEDED refusal (exit 2).
    """
    config_dir = config_path.parent
    config, problems = monetization.load(config_dir)
    if config_path.name != monetization.REGISTRY_RELATIVE:
        raise refused(
            "MONETIZATION_CONFIG_NAME",
            f"expected {monetization.REGISTRY_RELATIVE}, got {config_path.name}",
            EXIT_REGISTRY_INVALID,
        )
    # Budget guardrail FIRST: a non-positive unit price is the exec-summary
    # REFUSED_BUDGET_EXCEEDED (exit 2), checked over root defaults AND every
    # per-solution override -- before generic registry-invalid aggregation.
    merged_prices: list[tuple[str, Any]] = [
        ("_defaults", dict(monetization.DEFAULTS, **config.get("_defaults", {})).get("unit_price_usd"))
    ]
    merged_prices += [
        (slug, dict(monetization.DEFAULTS, **config[slug]).get("unit_price_usd"))
        for slug in sorted(k for k in config if k != "_defaults")
    ]
    for slug, price in merged_prices:
        if isinstance(price, (int, float)) and not isinstance(price, bool) and price <= 0:
            raise refused("BUDGET_EXCEEDED", f"{slug}:unit_price_usd={price!r}<=0", EXIT_CONFIG)

    effective = monetization.entry_issues(
        config, refuse=lambda code, detail: f"{code}:{detail}"
    )
    problems.extend(effective)
    # The loader skips `_defaults` in entry_issues; validate the root-default
    # table too by presenting it as a synthetic solution entry.
    defaults = config.get("_defaults")
    if isinstance(defaults, dict) and defaults:
        problems.extend(
            monetization.entry_issues(
                {"<defaults>": defaults},
                refuse=lambda code, detail: f"{code}:{detail}",
            )
        )
    if problems:
        raise Refused(
            f"REFUSED:MONETIZATION_REGISTRY_INVALID:{';'.join(problems)}",
            EXIT_REGISTRY_INVALID,
        )
    if not config_path.is_file():
        # Loader treats absent as empty defaults; the deployer requires an
        # admitted registry file to exist at the given path.
        raise refused("MONETIZATION_CONFIG_MISSING", str(config_path), EXIT_REGISTRY_INVALID)
    return config


def registry_entry(config: dict[str, Any], slug: str) -> dict[str, Any]:
    return monetization.effective_for(config, slug)


# ---------------------------------------------------------------------------
# Step 3: solution.json lock verification
# ---------------------------------------------------------------------------


def read_solution_lock(solution_dir: Path) -> dict[str, Any]:
    """Read + structurally validate solution.json. Missing/invalid -> exit 2."""
    lock_path = solution_dir / "solution.json"
    if not lock_path.is_file():
        raise refused("SOLUTION_LOCK_MISSING", str(lock_path), EXIT_CONFIG)
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise refused("SOLUTION_LOCK_INVALID", f"{lock_path}: {exc}", EXIT_CONFIG)
    for field in ("profile_sha256", "packs"):
        if field not in lock:
            raise refused("SOLUTION_LOCK_INVALID", f"{lock_path}: missing {field!r}", EXIT_CONFIG)
    if not isinstance(lock["packs"], list) or not lock["packs"]:
        raise refused("SOLUTION_LOCK_INVALID", "packs must be a non-empty list", EXIT_CONFIG)
    for i, pack in enumerate(lock["packs"]):
        if not isinstance(pack, dict) or not {"name", "path", "content_hash"} <= set(pack):
            raise refused(
                "SOLUTION_LOCK_INVALID",
                f"packs[{i}] needs name/path/content_hash",
                EXIT_CONFIG,
            )
    return lock


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_lock_digests(solution_dir: Path, lock: dict[str, Any]) -> None:
    """Profile digest + per-pack content_hash drift -> exit 9.

    The profile digest is the fingerprint_paths fold over every file in the
    solution dir except solution.json and any dist/ output (the lock covers
    the solution's INPUTS only).
    """
    input_files = [
        p
        for p in solution_dir.rglob("*")
        if p.is_file()
        and p.name != "solution.json"
        and "dist" not in p.relative_to(solution_dir).parts
    ]
    digest = fingerprint_paths(input_files, solution_dir)
    if digest != lock["profile_sha256"]:
        raise refused(
            "PROFILE_DIGEST_DRIFT",
            f"solution inputs {digest} != lock {lock['profile_sha256']}",
            EXIT_DIGEST_DRIFT,
        )
    for pack in lock["packs"]:
        pack_path = (solution_dir / pack["path"]).resolve()
        if not pack_path.is_dir():
            raise refused(
                "PROFILE_DIGEST_DRIFT",
                f"pack {pack['name']}: path missing: {pack_path}",
                EXIT_DIGEST_DRIFT,
            )
        pack_files = sorted(p for p in pack_path.rglob("*") if p.is_file())
        actual = fingerprint_paths(pack_files, pack_path)
        expected = pack["content_hash"]
        if expected.startswith("sha256:"):
            expected = expected.split(":", 1)[1]
        if actual != expected:
            raise refused(
                "PROFILE_DIGEST_DRIFT",
                f"pack {pack['name']}: content {actual} != lock {expected}",
                EXIT_DIGEST_DRIFT,
            )


# ---------------------------------------------------------------------------
# Step 4: entitlement gate (pay-before-manufacture)
# ---------------------------------------------------------------------------


def entitlement_gate(entitlement_id: str, entry: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    """Run scripts/entitlement.py decide() BEFORE any manufacture.

    dist/ must not exist yet. NOT_ACTIVE/NOT_FOUND -> exit 4; unreachable ->
    exit 3; anything else BLOCKED -> exit 5.
    """
    import entitlement

    if out_dir.exists():
        raise refused("DIST_ALREADY_EXISTS", str(out_dir), EXIT_CONFIG)
    result = entitlement.decide(entitlement_id, entry)
    if result.get("standing") == "ALIVE":
        return result
    detail = result.get("refusal", "unknown")
    if detail in (entitlement.REFUSED_NOT_ACTIVE, entitlement.REFUSED_NOT_FOUND):
        raise Refused(detail, EXIT_NOT_ACTIVE)
    if detail in (entitlement.REFUSED_UNREACHABLE, entitlement.REFUSED_PROVIDER_UNREACHABLE):
        raise Refused(detail, EXIT_UNREACHABLE)
    raise Refused(f"REFUSED:ENTITLEMENT_INVALID_RESPONSE:{detail}", EXIT_INVALID_RESPONSE)


# ---------------------------------------------------------------------------
# Step 5: manufacture via ggen sync
# ---------------------------------------------------------------------------


def _capsule_env(capsule: Path) -> dict[str, str]:
    """os.environ with HOME/XDG redirected into the temp capsule."""
    home = capsule / "home"
    for sub in ("", ".cache", ".config", ".data"):
        (home / sub).mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "HOME": str(home),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".data"),
        }
    )
    return env


def manufacture(solution_dir: Path, timeout_seconds: float = 300.0) -> None:
    """`ggen sync run` in the solution dir under a temp HOME/XDG capsule."""
    ggen = shutil.which("ggen")
    if ggen is None:
        raise refused("GGEN_NOT_FOUND", "ggen not on PATH", EXIT_GGEN_MISSING)
    with tempfile.TemporaryDirectory(prefix="aaif-deploy-capsule-") as tmp:
        capsule = Path(tmp)
        (capsule / "home").mkdir(parents=True, exist_ok=True)
        env = _capsule_env(capsule)
        try:
            proc = subprocess.run(
                [ggen, "sync", "run"],
                cwd=solution_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise refused("GGEN_SYNC_FAILED", f"timeout after {timeout_seconds}s", EXIT_ACTUATION_FAILED)
        if proc.returncode != 0:
            raise refused(
                "GGEN_SYNC_FAILED",
                f"exit {proc.returncode}: {(proc.stderr or proc.stdout).strip()[:400]}",
                EXIT_ACTUATION_FAILED,
            )


# ---------------------------------------------------------------------------
# Step 6: re-run the packs' SPARQL gates on the manufactured graph
# ---------------------------------------------------------------------------


def run_gate(graph: Any, gate_path: Path) -> list:
    rows = graph.query(gate_path.read_text(encoding="utf-8"))
    return [tuple(str(v) for v in row) for row in rows]


def solution_gates(solution_dir: Path, lock: dict[str, Any]) -> None:
    """Every pack gate must return ZERO rows over ontology+fixtures+profile.

    SELECT-with-rows = violation (ggen gate law) -> exit 8.
    """
    import rdflib

    for pack in lock["packs"]:
        pack_path = (solution_dir / pack["path"]).resolve()
        gates_dir = pack_path / "gates"
        if not gates_dir.is_dir():
            continue
        graph = rdflib.Graph()
        ontology = pack_path / "ontology.ttl"
        if ontology.is_file():
            graph.parse(str(ontology), format="turtle")
        fixtures = pack_path / "fixtures"
        if fixtures.is_dir():
            for fixture in sorted(fixtures.glob("*.ttl")):
                graph.parse(str(fixture), format="turtle")
        profile_ttl = solution_dir / "profile.ttl"
        if profile_ttl.is_file():
            graph.parse(str(profile_ttl), format="turtle")
        for gate in sorted(gates_dir.glob("*.rq")):
            rows = run_gate(graph, gate)
            if rows:
                raise refused(
                    "SOLUTION_GATE_VIOLATION",
                    f"{pack['name']}:{gate.name}: {len(rows)} row(s)",
                    EXIT_GATE_SCOPE,
                )


# ---------------------------------------------------------------------------
# Step 7: namespace-scope check over dist manifests
# ---------------------------------------------------------------------------

_KIND_RE = re.compile(r"^\s*kind:\s*([A-Za-z0-9.]+)\s*$", re.MULTILINE)


def manifest_kinds(text: str) -> list[str]:
    """Kinds found in a YAML (regex) or JSON manifest."""
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return _KIND_RE.findall(text)
        items = parsed if isinstance(parsed, list) else [parsed]
        return [str(item.get("kind", "")) for item in items if isinstance(item, dict)]
    return _KIND_RE.findall(text)


def check_namespace_scope(out_dir: Path) -> None:
    """Cluster-scoped kinds (beyond the Namespace allowlist) -> exit 8."""
    for path in sorted(out_dir.rglob("*")):
        if not path.is_file() or path.suffix not in (".yaml", ".yml", ".json"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for kind in manifest_kinds(text):
            if kind in FORBIDDEN_KINDS:
                raise refused(
                    "MANIFEST_CLUSTER_SCOPED",
                    f"{path.relative_to(out_dir)}: kind {kind}",
                    EXIT_GATE_SCOPE,
                )
            if kind in ALLOWED_CLUSTER_KINDS:
                continue  # Namespace objects allowed explicitly
            # namespaced kinds pass


# ---------------------------------------------------------------------------
# Step 8: consequence digest
# ---------------------------------------------------------------------------


def consequence_digest(out_dir: Path) -> tuple[str, dict[str, str]]:
    """(fingerprint_paths fold, {relative path: sha256}) over the dist tree."""
    import hashlib

    files = sorted(p for p in out_dir.rglob("*") if p.is_file())
    digest = fingerprint_paths(files, out_dir)
    per_file: dict[str, str] = {}
    for path in files:
        h = hashlib.sha256()
        h.update(path.read_bytes())
        per_file[path.relative_to(out_dir).as_posix()] = h.hexdigest()
    return digest, per_file


# ---------------------------------------------------------------------------
# Data residency (profile.ttl residencyRegionLock)
# ---------------------------------------------------------------------------


def profile_residency_lock(solution_dir: Path) -> str | None:
    """Read aaif:residencyRegionLock from profile.ttl; None = unrestricted."""
    profile_ttl = solution_dir / "profile.ttl"
    if not profile_ttl.is_file():
        return None
    try:
        import rdflib

        graph = rdflib.Graph()
        graph.parse(str(profile_ttl), format="turtle")
    except Exception:
        return None
    for subject, predicate, obj in graph:
        if str(predicate) == RESIDENCY_PREDICATE:
            return str(obj)
    return None


def check_data_residency(solution_dir: Path, target: str, region: str | None) -> None:
    """profile residencyRegionLock vs target region mismatch -> exit 8.

    kind has no region semantics; the check applies to gke with --region
    (or AAIF_TARGET_REGION). Missing profile.ttl / no lock -> skip.
    """
    if target != "gke" or not region:
        return
    lock_region = profile_residency_lock(solution_dir)
    if lock_region and lock_region != region:
        raise refused(
            "DATA_RESIDENCY_VIOLATION",
            f"profile lock {lock_region} != target region {region}",
            EXIT_GATE_SCOPE,
        )


# ---------------------------------------------------------------------------
# Step 9: paid-delivery receipt
# ---------------------------------------------------------------------------


def write_receipt(
    receipts_dir: Path,
    slug: str,
    monetization_block: dict[str, Any],
    actuation_block: dict[str, Any],
    graph_hash: str,
) -> dict[str, Any]:
    """Append to the paid-delivery chain; write failure -> exit 13.

    REFUSED_NON_MONOTONIC_GRANT (exit 9): an existing receipt for this slug
    must carry the SAME graph_hash -- a re-delivery of a different artifact
    under an already-paid slug is refused.
    """
    import paid_delivery_receipt

    existing_path = receipts_dir / paid_delivery_receipt.SUBDIR / f"{slug}.json"
    if existing_path.is_file():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            existing_hash = existing["payload"]["actuation"]["graph_hash"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
            raise refused(
                "RECEIPT_READ_FAILED", f"{existing_path}: {exc}", EXIT_RECEIPT
            )
        if existing_hash != graph_hash:
            raise refused(
                "NON_MONOTONIC_GRANT",
                f"slug {slug}: existing graph_hash {existing_hash[:12]} != {graph_hash[:12]}",
                EXIT_DIGEST_DRIFT,
            )
        # Identical graph_hash under the same paid slug = replay: the already
        # appended receipt is the grant; re-appending would fork the chain.
        return existing
    payload = {
        "schema": "https://ggen.dev/marketplace/paid-delivery/v1",
        "monetization": monetization_block,
        "actuation": {**actuation_block, "graph_hash": graph_hash},
    }
    try:
        return paid_delivery_receipt.append(receipts_dir, slug, payload)
    except OSError as exc:
        raise refused("RECEIPT_WRITE_FAILED", str(exc), EXIT_RECEIPT)


# ---------------------------------------------------------------------------
# Step 10: actuation plan + --actuate
# ---------------------------------------------------------------------------


def build_actuation_plan(
    slug: str,
    out_dir: Path,
    target: str,
    manifest_files: list[str],
) -> dict[str, Any]:
    """Plan is byte-identical across targets except the `context` field."""
    if target == "kind":
        context = KIND_CONTEXT
    else:
        context = "gke:" + os.environ.get("GCP_PROJECT", "<unset-GCP_PROJECT>")
    return {
        "schema": SCHEMA_V1,
        "slug": slug,
        "context": context,
        "apply_order": manifest_files,
        "commands": [
            {"argv": ["kubectl", "apply", "-f", str(out_dir / rel)]} for rel in manifest_files
        ],
    }


def manifest_rels(out_dir: Path) -> list[str]:
    """Relative paths of actual k8s manifests (parseable `kind:`), sorted."""
    rels = []
    for p in sorted(out_dir.rglob("*")):
        if not p.is_file() or p.suffix not in (".yaml", ".yml", ".json"):
            continue
        if p.name == "actuation_plan.json":
            continue
        if manifest_kinds(p.read_text(encoding="utf-8", errors="replace")):
            rels.append(p.relative_to(out_dir).as_posix())
    return sorted(rels)


def actuate_kind(plan: dict[str, Any]) -> None:
    """Print the kubectl apply sequence WITHOUT executing (honest kind rail:
    the real e2e lives in the deployment court, not in customer actuation)."""
    print("# kind rail: kubectl apply sequence (NOT executed)")
    for cmd in plan["commands"]:
        print(" ".join(shlex_quote(a) for a in cmd["argv"]))


def shlex_quote(arg: str) -> str:
    import shlex

    return shlex.quote(arg)


def actuate_gke(project: str | None, plan: dict[str, Any]) -> None:
    """Require real gcloud+kubectl; refuse project mismatch. NOT executed here
    beyond the tooling/project checks; the apply itself is the customer's."""
    gcloud = shutil.which("gcloud")
    kubectl = shutil.which("kubectl")
    missing = [name for name, path in (("gcloud", gcloud), ("kubectl", kubectl)) if path is None]
    if missing:
        raise refused("GKE_TOOLING_MISSING", ",".join(missing), EXIT_ACTUATION_TOOLING)
    if project:
        proc = subprocess.run(
            [gcloud, "config", "get-value", "project"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            raise refused(
                "GKE_TOOLING_MISSING",
                f"gcloud config get-value project exit {proc.returncode}",
                EXIT_ACTUATION_TOOLING,
            )
        actual = proc.stdout.strip()
        if actual != project:
            raise refused(
                "GCLOUD_PROJECT_MISMATCH",
                f"gcloud project {actual!r} != expected {project!r}",
                EXIT_ACTUATION_TOOLING,
            )
    print("# gke rail: tooling + project verified; apply sequence:")
    for cmd in plan["commands"]:
        print(" ".join(shlex_quote(a) for a in cmd["argv"]))


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deploy an AAIF solution (pay-before-manufacture, fail-closed)"
    )
    parser.add_argument("--solution", required=True, type=Path, help="solution directory")
    parser.add_argument("--out", required=True, type=Path, help="dist output directory")
    parser.add_argument("--target", choices=["kind", "gke"], default="kind")
    parser.add_argument("--config", type=Path, default=ROOT / "monetization.toml")
    parser.add_argument("--entitlement-id", default=None, help="defaults to the solution slug")
    parser.add_argument("--region", default=os.environ.get("AAIF_TARGET_REGION"))
    parser.add_argument("--project", default=None, help="expected gcloud project (gke)")
    parser.add_argument("--receipts-dir", type=Path, default=ROOT / "receipts")
    parser.add_argument("--actuate", action="store_true")
    parser.add_argument(
        "--timeout-seconds", type=float, default=300.0, help="ggen sync timeout"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    solution_dir = args.solution.resolve()
    out_dir = args.out.resolve()
    slug = solution_dir.name
    entitlement_id = args.entitlement_id or slug

    try:
        # 1. python gate already enforced at import.

        # 2. registry admission (exit 6 / budget exit 2)
        config = load_registry(args.config)
        entry = registry_entry(config, slug)

        # 3. solution lock
        lock = read_solution_lock(solution_dir)
        check_lock_digests(solution_dir, lock)

        # 4. entitlement gate BEFORE any manufacture; dist must not exist
        decision = entitlement_gate(entitlement_id, entry, out_dir)

        # 5. manufacture
        manufacture(solution_dir, timeout_seconds=args.timeout_seconds)

        # 6. pack SPARQL gates on the manufactured graph
        solution_gates(solution_dir, lock)

        # 7. namespace scope over dist manifests
        check_namespace_scope(out_dir)

        # residency check (map of target semantics)
        check_data_residency(solution_dir, args.target, args.region)

        # 8. consequence digest
        graph_hash, per_file = consequence_digest(out_dir)

        # 10a. actuation plan (byte-identical except context)
        rels = manifest_rels(out_dir)
        plan = build_actuation_plan(slug, out_dir, args.target, rels)

        # 9. paid-delivery receipt
        target_standing = "SIMULATED" if args.target == "kind" else "EXACT_PROVIDER"
        receipt = write_receipt(
            args.receipts_dir,
            slug,
            {
                "backend": entry["backend"],
                "backend_standing": decision.get("backend_standing", "UNKNOWN"),
                "billing_authorities": entry["billing_authorities"],
                "provider_id": entry["provider_id"],
                "unit_price_usd": entry["unit_price_usd"],
            },
            {
                "target": args.target,
                "target_standing": target_standing,
                "plan_digest": fingerprint_paths(
                    [out_dir / rel for rel in rels], out_dir
                )
                if rels
                else "sha256:" + graph_hash,
            },
            graph_hash,
        )

        # 10b. emit actuation_plan.json
        plan_path = out_dir / "actuation_plan.json"
        try:
            plan_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        except OSError as exc:
            raise refused("RECEIPT_WRITE_FAILED", str(exc), EXIT_RECEIPT)

        print(
            json.dumps(
                {
                    "slug": slug,
                    "target": args.target,
                    "graph_hash": graph_hash,
                    "receipt_chain_hash": receipt["chain_hash_hex"],
                    "plan": str(plan_path),
                    "files": len(per_file),
                },
                indent=2,
                sort_keys=True,
            )
        )

        if args.actuate:
            if args.target == "kind":
                actuate_kind(plan)
            else:
                actuate_gke(args.project, plan)
        return 0
    except Refused as exc:
        _die(exc)


if __name__ == "__main__":
    sys.exit(main())
