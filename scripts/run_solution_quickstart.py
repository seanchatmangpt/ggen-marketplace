#!/usr/bin/env python3
"""run_solution_quickstart.py -- one-command SOLUTION-loop quickstart.

The hello-pack tutorial has run_quickstart.py; this is its SOLUTION-loop twin:
a real, self-contained pay-before-manufacture run against the real GCP
commerce sim, the real deployer subprocess (scripts/deploy_aaif_solution.py)
and the real ggen runtime -- all inside a temp capsule, never mutating the
repo tree (solutions/enterprise-aaif/solution.json pins pack digests that must
keep matching the committed trees).

Flow:
  1. start the real commerce sim (k8s/gcp-marketplace-sim/server.py) on an
     ephemeral port with a temp discovery dir;
  2. seed the partner account + entitlement (id == solution slug) via real
     HTTP approve;
  3. copy solutions/enterprise-aaif + the locked packs into a temp capsule
     (--profile team re-tailors the DeploymentProfile block inside the
     capsule; the capsule lock is then fully recomputed -- profile_sha256 and
     per-pack content hashes -- because the committed lock can drift from the
     pack trees; repo files are never touched);
  4. run the deployer: --solution <capsule>/solutions/enterprise-aaif --out
     <capsule solution>/dist --target kind --config <repo monetization.toml>
     --receipts-dir <tmp>/receipts (real ggen sync, real gates, real chain);
  5. verify the receipt chain via paid_delivery_receipt.verify;
  6. print a JSON summary {slug, receipt_chain_hash, dist_files, sim_port}.

Failures -> typed REFUSED:* on stderr + nonzero exit. --keep keeps the capsule
temp dir and prints its path in the summary.
"""

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEPLOY = ROOT / "scripts" / "deploy_aaif_solution.py"
SIM = ROOT / "k8s" / "gcp-marketplace-sim" / "server.py"
SOLUTION_NAME = "enterprise-aaif"
REPO_SOLUTION = ROOT / "solutions" / SOLUTION_NAME
CONFIG = ROOT / "monetization.toml"
PROFILE_SUBJECT = "EnterpriseAaifProfile"

# ONE fold law: the quickstart's drift check and capsule-lock recompute call
# the deployer's own input_folds (the same helper scripts/regen_solution_lock.py
# uses), so deployer, regen tool and quickstart cannot drift.
sys.path.insert(0, str(ROOT / "scripts"))
from deploy_aaif_solution import input_folds  # noqa: E402

# Per-profile DeploymentProfile tailoring, applied inside the capsule only.
# Values must be individuals of the authoritative pack ontology
# (packs/aaif-profile-tailoring-pack/ontology.ttl); the pack enum-closure gate
# (gates/010_profile_enum_closure.rq) refuses anything outside the closed set.
PROFILE_TAILORINGS: dict = {
    "enterprise": {},
    "team": {
        "namespace": '"team-aaif"',
        "replicas": "1",
        "cmekProvider": "NONE",
        "finopsTier": "STANDARD",
        "siemMode": "SIEM_NONE",
        "spiffeTrustDomain": '"team-aaif.example.com"',
        "pqcSuite": "PQC_NONE",
    },
}

ACCOUNT_ID = "acc-quickstart-001"


class Refused(Exception):
    def __init__(self, code: str, detail: str, exit_code: int = 1):
        super().__init__(f"REFUSED:{code}:{detail}")
        self.message = f"REFUSED:{code}:{detail}"
        self.exit_code = exit_code


def refused(code, detail, exit_code=1):
    return Refused(code, detail, exit_code)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class CommerceSim:
    """The real sim server as a subprocess: ephemeral port + temp discovery dir."""

    def __init__(self):
        self.port = free_port()
        self.proc = None
        self._tmp = None

    def __enter__(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="aaif-quickstart-sim-")
        discovery = Path(self._tmp.name)
        for name in ("procurement_discovery.json", "servicecontrol_discovery.json"):
            shutil.copy2(ROOT / "k8s" / "gcp-marketplace-sim" / name, discovery / name)
        env = dict(os.environ)
        env["AAIF_SIM_PORT"] = str(self.port)
        env["AAIF_SIM_DISCOVERY_DIR"] = str(discovery)
        self.proc = subprocess.Popen(
            [sys.executable, str(SIM)],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        deadline = time.time() + 30
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise refused("SIM_EXITED", "sim exited before /healthz", 3)
            try:
                with urllib.request.urlopen(
                    f"http://127.0.0.1:{self.port}/healthz", timeout=2
                ) as r:
                    if r.status == 200:
                        return self
            except Exception:
                time.sleep(0.1)
        self.stop()
        raise refused("SIM_NOT_READY", "sim not healthy within 30s", 3)

    def __exit__(self, *exc):
        self.stop()
        return False

    def stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self.proc = None
        if self._tmp is not None:
            self._tmp.cleanup()
            self._tmp = None

    @property
    def base(self):
        return f"http://127.0.0.1:{self.port}"

    def seed(self, account_id, entitlement_id):
        """Real HTTP approve of the partner account, then the entitlement."""
        base = self.base
        flows = (
            (f"{base}/v1/providers/demo-provider/accounts/{account_id}:approve", {}),
            (
                f"{base}/v1/providers/demo-provider/entitlements/{entitlement_id}:approve",
                {
                    "account": f"providers/demo-provider/accounts/{account_id}",
                    "plan": "enterprise-unlimited",
                },
            ),
        )
        record = {}
        for url, body in flows:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    raise refused("SEED_FAILED", f"{url} -> HTTP {resp.status}", 3)
                record = json.loads(resp.read())
        return record


def retaylor_ontology(text, tailoring):
    """Rewrite DeploymentProfile block values inside the capsule copy.

    Literal turtle lines only; anything the regexes do not match is left
    untouched, so drift in the committed ontology surfaces as digest or gate
    failures downstream instead of silent tailoring loss.
    """
    subj = PROFILE_SUBJECT

    def swap(pred, value):
        nonlocal text
        # Value region = rest of the line up to the turtle terminator (" ;"
        # or " ."), which must not be consumed. Quoted strings may contain
        # dots (spiffe trust domains), so [^;.] is wrong here.
        text = re.sub(
            rf"(?m)^(\s*aaift:{pred}\s+).*?(?=\s*[.;]\s*$)",
            lambda m: m.group(1) + value,
            text,
            count=1,
        )

    swap("cmekProvider", "aaift:" + tailoring["cmekProvider"])
    swap("finopsTier", "aaift:" + tailoring["finopsTier"])
    swap("siemMode", "aaift:" + tailoring["siemMode"])
    swap("pqcSuite", "aaift:" + tailoring["pqcSuite"])
    swap("namespace", tailoring["namespace"])
    swap("replicas", tailoring["replicas"])
    swap("spiffeTrustDomain", tailoring["spiffeTrustDomain"])
    return text


def retaylor_profile_json(body, tailoring):
    data = json.loads(body)
    data["namespace"] = tailoring["namespace"].strip('"')
    data["replicas"] = int(tailoring["replicas"])
    data["cmek_provider"] = tailoring["cmekProvider"]
    data["finops_tier"] = tailoring["finopsTier"]
    data["siem_mode"] = tailoring["siemMode"]
    data["spiffe_trust_domain"] = tailoring["spiffeTrustDomain"].strip('"')
    data["pqc_suite"] = tailoring["pqcSuite"]
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def _pack_fold(pack_path):
    """Deployer's ONE fold law, applied to a single pack tree.

    Calls deploy_aaif_solution.input_folds with an empty pack list so the
    pack fold is exactly the profile fold of that subtree -- the same helper
    the deployer's admission gate and scripts/regen_solution_lock.py use,
    so the three tools cannot drift (pack-local dist/ and ggen runtime
    state -- .ggen/.ggen-v2/.clap-noun-verb/__pycache__ -- never folded).
    """
    fold, _ = input_folds(pack_path, {"packs": []})
    return fold


def refuse_symlinks_in(*roots):
    """Defense-in-depth: no symlink may appear in any capsule source tree.

    A symlink smuggles host-file content (or arbitrary paths) into the
    capsule copy and therefore into the receipt digest chain. Walk every
    source tree first and refuse before any copy.
    """
    for root in roots:
        for p in sorted(root.rglob("*")):
            if p.is_symlink():
                raise refused("SYMLINK_IN_SOURCE", f"{p} (-> {os.readlink(p)})", 2)


def check_repo_lock_drift(repo_root):
    """Recompute the REPO tree's lock (in memory, same folds as the deployer)
    and diff field-by-field against the committed solution.json.

    Returns the list of drifted key names. Empty list == no drift. Always
    operates on repo paths -- never the (possibly tailored) capsule copy.
    """
    solution_dir = repo_root / "solutions" / SOLUTION_NAME
    committed = json.loads(
        (solution_dir / "solution.json").read_text(encoding="utf-8")
    )

    profile_fold, pack_folds = input_folds(solution_dir, committed)
    computed_hashes = {
        pack["name"]: "sha256:" + fold
        for pack, fold in zip(committed["packs"], pack_folds)
    }

    diffs = []
    if committed["profile_sha256"] != profile_fold:
        diffs.append("profile_sha256")
    committed_packs = {p["name"]: p for p in committed.get("packs", [])}
    for name, content_hash in computed_hashes.items():
        c = committed_packs.get(name)
        if c is None:
            diffs.append(f"packs[{name}] (absent from committed lock)")
        elif c.get("content_hash") != content_hash:
            diffs.append(f"packs[{name}].content_hash")
    for name in sorted(set(committed_packs) - set(computed_hashes)):
        diffs.append(f"packs[{name}] (in committed lock, absent from repo tree)")
    return diffs


def recompute_lock(solution_dir, repo_root, accept_drift):
    """Detect repo-vs-lock drift, then recompute the whole capsule lock.

    First the REPO tree's lock is recomputed (same folds, repo paths) and
    diffed field-by-field against the committed solution.json. Any mismatch
    is a typed refusal -- silently overwriting the lock would launder
    repo-vs-lock drift past the deployer's digest law. --accept-drift is the
    explicit regeneration workflow: it prints the diff and proceeds, and the
    capsule recompute then runs only from that accepted basis.
    """
    diffs = check_repo_lock_drift(repo_root)
    if diffs:
        detail = ";".join(diffs)
        if not accept_drift:
            raise refused(
                "LOCK_DRIFT",
                f"repo tree differs from committed solution lock: {detail}"
                " (pass --accept-drift to regenerate the lock deliberately)",
                2,
            )
        print(
            f"WARNING: --accept-drift: regenerating lock over "
            f"REFUSED:LOCK_DRIFT basis: {detail}",
            file=sys.stderr,
        )

    lock = json.loads((solution_dir / "solution.json").read_text(encoding="utf-8"))
    profile_fold, pack_folds = input_folds(solution_dir, lock)
    lock["profile_sha256"] = profile_fold
    for pack, fold in zip(lock["packs"], pack_folds):
        pack["content_hash"] = "sha256:" + fold
    (solution_dir / "solution.json").write_text(
        json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def build_capsule(tmp, profile, repo_root=ROOT, accept_drift=False):
    """Temp capsule: solutions/enterprise-aaif + locked packs; repo untouched."""
    repo_solution = repo_root / "solutions" / SOLUTION_NAME
    capsule = tmp / "capsule"
    solution_dir = capsule / "solutions" / SOLUTION_NAME
    # Preserve, never follow: a symlinked entry would copy host-file content
    # into the capsule (and its digests). The guard below refuses first.
    shutil.copytree(repo_solution, solution_dir, symlinks=True)
    refuse_symlinks_in(solution_dir)
    lock = json.loads((solution_dir / "solution.json").read_text(encoding="utf-8"))
    for pack in lock["packs"]:
        pack_src = repo_root / "packs" / pack["name"]
        refuse_symlinks_in(pack_src)
        shutil.copytree(
            pack_src,
            capsule / "packs" / pack["name"],
            symlinks=True,
            ignore=shutil.ignore_patterns(".clap-noun-verb", "__pycache__", ".*"),
        )
    if PROFILE_TAILORINGS[profile]:
        tailoring = PROFILE_TAILORINGS[profile]
        ontology = solution_dir / "ontology.ttl"
        ontology.write_text(
            retaylor_ontology(ontology.read_text(encoding="utf-8"), tailoring),
            encoding="utf-8",
        )
        profile_json = solution_dir / "profile.json"
        profile_json.write_text(
            retaylor_profile_json(profile_json.read_text(encoding="utf-8"), tailoring),
            encoding="utf-8",
        )
    recompute_lock(solution_dir, repo_root, accept_drift)
    return capsule, solution_dir


def run_deployer(capsule_solution, out_dir, receipts_dir, endpoint):
    env = dict(os.environ)
    env["AAIF_ENTITLEMENT_ENDPOINT"] = endpoint
    cmd = [
        sys.executable,
        str(DEPLOY),
        "--solution",
        str(capsule_solution),
        "--out",
        str(out_dir),
        "--target",
        "kind",
        "--config",
        str(CONFIG),
        "--receipts-dir",
        str(receipts_dir),
    ]
    return subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600)


def verify_chain(receipts_dir):
    sys.path.insert(0, str(ROOT / "scripts"))
    import paid_delivery_receipt

    ok, problems = paid_delivery_receipt.verify(receipts_dir)
    if not ok:
        raise refused("RECEIPT_CHAIN_INVALID", ";".join(problems[:5]), 13)
    chain = receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl"
    lines = [line for line in chain.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise refused("RECEIPT_CHAIN_EMPTY", str(chain), 13)
    head = json.loads(lines[-1])
    return head["chain_hash_hex"]


def count_dist_files(out_dir):
    return sum(1 for p in out_dir.rglob("*") if p.is_file())


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="One-command AAIF SOLUTION-loop quickstart (temp capsule, real sim)"
    )
    parser.add_argument("--profile", choices=["enterprise", "team"], default="enterprise")
    parser.add_argument(
        "--keep", action="store_true", help="keep the temp capsule dir on success"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
        help="source root for solutions/ + packs/ capsule inputs "
        "(injectable seam; defaults to this repo)",
    )
    parser.add_argument(
        "--accept-drift",
        action="store_true",
        help="accept repo-vs-committed-lock drift: print the diff loudly and "
        "regenerate the capsule lock from it (legit regeneration workflow)",
    )
    args = parser.parse_args(argv)

    repo_solution = args.repo_root / "solutions" / SOLUTION_NAME
    if not shutil.which("ggen"):
        raise refused("GGEN_NOT_FOUND", "ggen not on PATH; run scripts/install-ggen.sh", 7)
    if not DEPLOY.is_file() or not SIM.is_file() or not repo_solution.is_dir():
        raise refused("INPUTS_MISSING", f"{DEPLOY} / {SIM} / {repo_solution}", 2)

    work = Path(tempfile.mkdtemp(prefix="aaif-solution-quickstart-"))
    sim = CommerceSim()
    try:
        with sim:
            sim.seed(ACCOUNT_ID, SOLUTION_NAME)
            capsule, capsule_solution = build_capsule(
                work, args.profile, args.repo_root, args.accept_drift
            )
            out_dir = capsule_solution / "dist"
            receipts_dir = work / "receipts"
            result = run_deployer(
                capsule_solution, out_dir, receipts_dir, endpoint=sim.base
            )
            if result.returncode != 0:
                tail = (result.stderr or result.stdout).strip()[-800:]
                raise refused(
                    "DEPLOYER_FAILED",
                    f"deployer exit {result.returncode}: {tail}",
                    result.returncode or 1,
                )
            chain_hash = verify_chain(receipts_dir)
            summary = {
                "slug": SOLUTION_NAME,
                "receipt_chain_hash": chain_hash,
                "dist_files": count_dist_files(out_dir),
                "sim_port": sim.port,
                "profile": args.profile,
            }
            if args.keep:
                summary["keep_path"] = str(work)
            print(json.dumps(summary, indent=2, sort_keys=True))
            if args.keep:
                work = None  # do not remove
    finally:
        sim.stop()
        if not args.keep and work is not None and work.exists():
            shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Refused as exc:
        print(exc.message, file=sys.stderr)
        raise SystemExit(exc.exit_code)
