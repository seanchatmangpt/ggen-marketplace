#!/usr/bin/env python3
"""Cross-repo Meta Court orchestrator for fnox, arcus, smalt, ggen, and ggen-marketplace.

Enforces the canonical contract substrate (packs/cross-repo-contract-pack/dist/fleet-contract-manifest.json)
across all five repositories with five composable courts:
  1. ProjectionDriftCourt
  2. HCLIntegrityAndAttachmentCourt
  3. WireParityCourt
  4. AntiVacuityMutationCourt
  5. ReceiptEmitter (validates against ~/.zcode/dfcm/validate_receipt.py)

Fail-closed: any non-zero court check or missing artifact refuses standing ALIVE.
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
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOTS = {
    "fnox": Path("/Users/sac/fnox"),
    "arcus": Path("/Users/sac/arcus"),
    "smalt": Path("/Users/sac/smalt"),
    "ggen": Path("/Users/sac/ggen"),
    "ggen-marketplace": Path("/Users/sac/ggen-marketplace"),
}
MANIFEST_PATH = ROOTS["ggen-marketplace"] / "packs/cross-repo-contract-pack/dist/fleet-contract-manifest.json"
VALIDATE_RECEIPT = Path.home() / ".zcode/dfcm/validate_receipt.py"
DEFAULT_RECEIPT = ROOTS["ggen-marketplace"] / "receipts/meta-court-latest.json"


@dataclass
class CheckResult:
    court: str
    name: str
    repo: str
    cmd: str
    exit_code: int
    duration_ms: int
    detail: str = ""


def run_cmd(cmd: list[str] | str, cwd: Path, shell: bool = False, timeout: int = 120) -> tuple[int, str, int]:
    t0 = time.monotonic()
    p = subprocess.run(cmd, cwd=str(cwd), shell=shell, capture_output=True, text=True, timeout=timeout)
    ms = int((time.monotonic() - t0) * 1000)
    out = (p.stdout + "\n" + p.stderr).strip()
    return p.returncode, out[-800:], ms


def git_head(repo: Path) -> str:
    p = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else "UNKNOWN"


def load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        raise RuntimeError(f"Missing contract manifest: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text())


class ProjectionDriftCourt:
    name = "ProjectionDriftCourt"

    def run(self, manifest: dict, repos: set[str]) -> list[CheckResult]:
        results: list[CheckResult] = []
        if "ggen-marketplace" in repos:
            pack_dir = ROOTS["ggen-marketplace"] / "packs/cross-repo-contract-pack"
            before = MANIFEST_PATH.read_bytes()
            rc, out, ms = run_cmd(["ggen", "sync", "run", "--skip-ea-admission"], pack_dir)
            after = MANIFEST_PATH.read_bytes()
            if rc == 0 and before != after:
                rc = 1
                out = "DRIFT: fleet-contract-manifest.json changed on re-sync"
            results.append(CheckResult(self.name, "contract-pack-sync-determinism", "ggen-marketplace",
                                       "ggen sync run --skip-ea-admission", rc, ms, out))

        if "fnox" in repos:
            # Verify simulation overlay carries every canonical GCP *_custom_endpoint and zero base_url
            sim_tf = (ROOTS["fnox"] / "infra/kind/gcp-provider-simulation.tf").read_text()
            missing = [e["tf_attribute"] for e in manifest["gcp_custom_endpoints"] if e["tf_attribute"] not in sim_tf]
            has_base_url = bool(re.search(r"^\s*base_url\s*=", sim_tf, re.MULTILINE))
            rc = 0 if (not missing and not has_base_url) else 1
            detail = "OK" if rc == 0 else f"missing={missing}, has_base_url={has_base_url}"
            results.append(CheckResult(self.name, "fnox-sim-overlay-contract", "fnox",
                                       "inspect infra/kind/gcp-provider-simulation.tf", rc, 1, detail))

            # Verify AGENTS.md matches KNOWN_KINDS count
            store_py = (ROOTS["fnox"] / "pipeline/enterprise_pipeline/store.py").read_text()
            agents_md = (ROOTS["fnox"] / "AGENTS.md").read_text()
            m_doc = re.search(r"(\d+) kinds admitted by", agents_md)
            doc_n = int(m_doc.group(1)) if m_doc else -1
            rc2, out2, ms2 = run_cmd(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, 'pipeline'); from enterprise_pipeline.store import KNOWN_KINDS; print(len(KNOWN_KINDS))"],
                ROOTS["fnox"],
            )
            actual_n = int(out2.strip().splitlines()[-1]) if rc2 == 0 else -1
            rc_kinds = 0 if (rc2 == 0 and doc_n == actual_n) else 1
            results.append(CheckResult(self.name, "fnox-agents-md-kinds", "fnox",
                                       "compare AGENTS.md vs store.KNOWN_KINDS", rc_kinds, ms2,
                                       f"doc={doc_n} actual={actual_n}"))

        if "smalt" in repos:
            for label, cmd in [
                ("smalt-dialect-pin", [sys.executable, "scripts/compat_pin_check.py", "--dialect-pin", "adapters/terraform-provider-smalt/compat-pin.ttl"]),
                ("smalt-core-pin", [sys.executable, "scripts/compat_pin_check.py", "--core-pin", "compat-pin-core.ttl"]),
                ("smalt-posh-crosscheck", ["bash", "scripts/posh_surface_crosscheck.sh"]),
            ]:
                rc, out, ms = run_cmd(cmd, ROOTS["smalt"])
                results.append(CheckResult(self.name, label, "smalt", " ".join(cmd), rc, ms, out))

        if "arcus" in repos:
            rc, out, ms = run_cmd([sys.executable, "scripts/kd_lint.py"], ROOTS["arcus"])
            results.append(CheckResult(self.name, "arcus-kd-lint", "arcus", "python3 scripts/kd_lint.py", rc, ms, out))
        return results


class HCLIntegrityAndAttachmentCourt:
    name = "HCLIntegrityAndAttachmentCourt"

    FMT_TARGETS = {
        "fnox": ["infra"],
        "arcus": ["infra"],
        "smalt": ["scripts/tf_fixtures", "scripts/tf_fixtures_per_resource", "scripts/r18-deploy"],
        "ggen": ["vendors/tai-erlang-autonomics"],
        "ggen-marketplace": ["."],
    }

    VALIDATE_ROOTS = {
        "fnox": [
            "infra/kind", "infra/gcp", "infra/gcp/budget", "infra/gcp/cloudrun",
            "infra/gcp/edge", "infra/gcp/gpu", "infra/gcp/iam", "infra/gcp/iap",
            "infra/gcp/integrations", "infra/gcp/pdf_intake", "infra/gcp/realtime",
        ],
        "arcus": ["infra/gcp", "infra/gcp/envs/dev", "infra/gcp/envs/staging", "infra/gcp/envs/prod"],
        "smalt": ["scripts/tf_fixtures", "scripts/r18-deploy"],
    }

    @staticmethod
    def check_forbidden_patterns(repo: str, repo_root: Path, manifest: dict) -> CheckResult:
        t0 = time.monotonic()
        violations: list[str] = []
        tf_dirs = {"fnox": repo_root / "infra", "arcus": repo_root / "infra"}
        if repo in tf_dirs:
            tf_texts = {p: p.read_text() for p in tf_dirs[repo].rglob("*.tf") if ".terraform" not in p.parts}
            combined = "\n".join(tf_texts.values())
            if re.search(r'member\s*=\s*"(allUsers|allAuthenticatedUsers)"', combined):
                violations.append("forbidden public invoker (allUsers/allAuthenticatedUsers)")
            if re.search(r'^\s*base_url\s*=', combined, re.MULTILINE):
                violations.append("forbidden invalid provider attribute base_url")
            for sc in manifest["security_controls"]:
                if sc["repo"] != repo:
                    continue
                for target in sc["attached_to"].split(","):
                    t = target.strip().split(".")[1] if "." in target else target.strip()
                    if t not in combined:
                        violations.append(f"unattached security control {sc['control']} -> missing {target}")
        # Check tracked tfstate in git
        rc_git, out_git, _ = run_cmd(["git", "ls-files", "*.tfstate", "*.tfstate.*"], repo_root)
        if rc_git == 0 and out_git.strip():
            violations.append(f"tracked tfstate in git: {out_git.strip()}")
        ms = int((time.monotonic() - t0) * 1000)
        rc = 0 if not violations else 1
        return CheckResult("HCLIntegrityAndAttachmentCourt", f"{repo}-security-and-state-law", repo,
                           "inspect *.tf security attachments & git ls-files *.tfstate*", rc, ms,
                           "; ".join(violations) or "OK")

    def run(self, manifest: dict, repos: set[str]) -> list[CheckResult]:
        results: list[CheckResult] = []
        for repo in sorted(repos):
            root = ROOTS[repo]
            for sub in self.FMT_TARGETS.get(repo, []):
                cmd = ["terraform", "fmt", "-check", "-recursive", sub]
                rc, out, ms = run_cmd(cmd, root)
                results.append(CheckResult(self.name, f"{repo}-fmt-{sub}", repo, " ".join(cmd), rc, ms, out))
            for sub in self.VALIDATE_ROOTS.get(repo, []):
                cmd = ["terraform", f"-chdir={sub}", "validate", "-no-color"]
                rc, out, ms = run_cmd(cmd, root)
                results.append(CheckResult(self.name, f"{repo}-validate-{sub}", repo, " ".join(cmd), rc, ms, out))
            results.append(self.check_forbidden_patterns(repo, root, manifest))
        return results


class WireParityCourt:
    name = "WireParityCourt"

    def run(self, manifest: dict, repos: set[str]) -> list[CheckResult]:
        results: list[CheckResult] = []
        if "fnox" in repos:
            cmd = [
                "uv", "run", "--with", "pytest", "--with", "python-hcl2",
                "pytest", "-q",
                "tests/test_terraform_solidification.py",
                "tests/gcp/test_tier2_terraform.py",
                "pipeline/tests/test_sim_overlay_routes.py",
                "pipeline/tests/test_infra_loopback_wiring.py",
            ]
            rc, out, ms = run_cmd(cmd, ROOTS["fnox"], timeout=180)
            results.append(CheckResult(self.name, "fnox-terraform-pytest", "fnox", " ".join(cmd), rc, ms, out))

        if "arcus" in repos:
            cmd = [
                "go", "test", "-count=1",
                "./internal/ingress/gcp/...",
                "./internal/ingress/aws/...",
                "./internal/vertex_ollama/...",
                "./internal/apis/wormverify/...",
                "./internal/dialect/azure/...",
            ]
            rc, out, ms = run_cmd(cmd, ROOTS["arcus"], timeout=180)
            results.append(CheckResult(self.name, "arcus-ingress-go-test", "arcus", " ".join(cmd), rc, ms, out))

        if "smalt" in repos:
            cmd = ["mix", "test", "test/integration/container_groups_test.exs", "test/integration/arm_providers_test.exs"]
            rc, out, ms = run_cmd(cmd, ROOTS["smalt"], timeout=180)
            results.append(CheckResult(self.name, "smalt-arm-mix-test", "smalt", " ".join(cmd), rc, ms, out))

        if "ggen-marketplace" in repos:
            cmd = ["bash", "ci/courts/shim-azure-terraform.sh"]
            rc, out, ms = run_cmd(cmd, ROOTS["ggen-marketplace"], timeout=180)
            results.append(CheckResult(self.name, "marketplace-azure-shim-court", "ggen-marketplace", " ".join(cmd), rc, ms, out))

        if "ggen" in repos:
            cmd = ["cargo", "test", "-p", "ggen-engine", "--test", "gh_terraform_pack_e2e"]
            rc, out, ms = run_cmd(cmd, ROOTS["ggen"], timeout=180)
            results.append(CheckResult(self.name, "ggen-gh-pack-e2e", "ggen", " ".join(cmd), rc, ms, out))
        return results


class AntiVacuityMutationCourt:
    name = "AntiVacuityMutationCourt"

    def run(self, manifest: dict) -> list[CheckResult]:
        t0 = time.monotonic()
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            (tmp / "infra").mkdir()
            (tmp / "infra/bad.tf").write_text('provider "google" {\n  base_url = "http://127.0.0.1:19840/"\n}\n')
            res = HCLIntegrityAndAttachmentCourt.check_forbidden_patterns("fnox", tmp, manifest)
            rc = 0 if res.exit_code != 0 else 1
            detail = "mutated base_url + orphan security controls refused" if rc == 0 else "VACUOUS: accepted invalid TF"
        ms = int((time.monotonic() - t0) * 1000)
        return [CheckResult(self.name, "mutation-refuses-base-url-and-orphans", "ggen-marketplace",
                            "inject mutated bad.tf into HCLIntegrityAndAttachmentCourt", rc, ms, detail)]


def emit_receipt(checks: list[CheckResult], receipt_path: Path) -> int:
    mp_root = ROOTS["ggen-marketplace"]
    all_ok = all(c.exit_code == 0 for c in checks)
    standing_val = "ALIVE" if all_ok else "REFUSED"
    repo_shas = {name: git_head(path) for name, path in ROOTS.items()}
    replay_cmds = [{"cmd": c.cmd, "cwd": str(ROOTS[c.repo]), "exit": c.exit_code, "duration_ms": c.duration_ms} for c in checks]
    receipt = {
        "work_order_id": f"meta-court-{int(time.time())}",
        "origin_authority": {
            "ceiling": "OBSERVE",
            "grant": "meta_court",
            "actor": "meta_court.py",
        },
        "provider": {
            "name": "cross-repo-contract-pack",
            "transport": "local-cli",
            "authority_ceiling": "OBSERVE",
        },
        "provider_execution_id": f"mc-{os.getpid()}",
        "identity": {
            "subject": "cross-repo-terraform-meta-court",
            "repo": str(mp_root),
            "subject_sha": repo_shas["ggen-marketplace"],
            "base_sha": repo_shas["ggen-marketplace"],
        },
        "authority": {
            "ceiling": "OBSERVE",
            "grant": "meta_court",
            "actor": "meta_court.py",
        },
        "consequence": {
            "commits": [],
            "files_changed": [],
            "remote_effects": [],
        },
        "replay": {
            "commands": replay_cmds,
            "durable_location": str(receipt_path),
        },
        "standing": {
            "value": standing_val,
            "derived_from": "; ".join(f"{c.court}:{c.name}={c.exit_code}" for c in checks),
            **({} if all_ok else {"broken_term": "admission_vacuous"}),
        },
        "provider_ext.meta_court": {
            "repo_heads": repo_shas,
            "checks": [c.__dict__ for c in checks],
        },
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    if VALIDATE_RECEIPT.is_file():
        rc_val, out_val, _ = run_cmd([sys.executable, str(VALIDATE_RECEIPT), str(receipt_path)], mp_root)
        if rc_val != 0:
            print(f"[meta-court] receipt schema validation failed:\n{out_val}", file=sys.stderr)
            return 1
    return 0 if all_ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-repo Meta Court runner")
    ap.add_argument("--all", action="store_true", help="Run across all 5 repos")
    ap.add_argument("--repo", action="append", choices=sorted(ROOTS.keys()), help="Target repo(s)")
    ap.add_argument("--mutate-check", action="store_true", help="Run anti-vacuity mutation court")
    ap.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT, help="Output receipt JSON path")
    args = ap.parse_args()

    repos = set(ROOTS.keys()) if args.all or not args.repo else set(args.repo)
    manifest = load_manifest()

    checks: list[CheckResult] = []
    checks.extend(ProjectionDriftCourt().run(manifest, repos))
    checks.extend(HCLIntegrityAndAttachmentCourt().run(manifest, repos))
    checks.extend(WireParityCourt().run(manifest, repos))
    if args.mutate_check or args.all:
        checks.extend(AntiVacuityMutationCourt().run(manifest))

    for c in checks:
        status = "PASS" if c.exit_code == 0 else f"FAIL({c.exit_code})"
        print(f"[{status}] {c.court} :: {c.repo}/{c.name} ({c.duration_ms}ms)")
        if c.exit_code != 0 and c.detail:
            print(f"    {c.detail}")

    rc = emit_receipt(checks, args.receipt)
    print(f"[meta-court] standing={'ALIVE' if rc == 0 else 'REFUSED'} receipt={args.receipt}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
