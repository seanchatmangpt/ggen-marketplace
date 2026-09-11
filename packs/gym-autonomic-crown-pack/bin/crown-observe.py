#!/usr/bin/env python3
"""Lift the gym-ecosystem submodule crown into RDF observations.

READ-ONLY. This program never mutates git state: it runs only
`git ls-tree`, `git ls-remote`, `git rev-parse`, `git config --get`.
It carries NO runtime actuation authority -- it observes and serializes.
Consequential DO (checkout/commit/push) stays with the superproject's
GymAct/BRCE-admitted crown workflow, exactly as scripts/crown-submodules.py
and .github/workflows/autonomic-crown.yml already gate it.

Two modes:
  --observe          real git reads against a working tree (network for ls-remote)
  --from-receipt F   lift an already-emitted autonomic-crown.json into RDF
                     (offline; used to prove the template is byte-exact)

Output: Turtle on stdout, appended to the pack vocabulary by the caller.
"""
from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
import sys
from pathlib import Path

NS = "https://seanchatmangpt.github.io/ontology/gym-autonomic-crown#"
SCHEMA = "https://ggen.dev/receipts/gym-autonomic-crown/v2"
BOUNDARY = "gitlinks+lock-only"


def run(*args: str, cwd: Path, check: bool = True) -> str:
    cp = subprocess.run(args, cwd=cwd, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if check and cp.returncode:
        raise SystemExit(f"CROWN_OBSERVE_BLOCKED[{cp.returncode}]: {' '.join(args)}\n{cp.stderr}")
    return cp.stdout


def declared_submodules(root: Path) -> list[dict[str, str]]:
    parser = configparser.ConfigParser()
    parser.read(root / ".gitmodules")
    rows = []
    for section in parser.sections():
        if not section.startswith("submodule "):
            continue
        rows.append({
            "name": section[len("submodule "):].strip('"'),
            "path": parser[section]["path"],
            "url": parser[section]["url"],
        })
    return sorted(rows, key=lambda r: r["path"])


def gitlink(root: Path, path: str) -> tuple[str, str]:
    line = run("git", "ls-tree", "HEAD", "--", path, cwd=root).strip()
    if not line:
        raise SystemExit(f"CROWN_OBSERVE_BLOCKED[MISSING_GITLINK]:{path}")
    mode, kind, sha, _ = line.split(None, 3)
    if mode != "160000" or kind != "commit":
        raise SystemExit(f"CROWN_OBSERVE_BLOCKED[NOT_GITLINK]:{path}:{mode}:{kind}")
    return mode, sha


def remote_head(url: str, root: Path) -> tuple[str, str]:
    text = run("git", "ls-remote", "--symref", url, "HEAD", cwd=root)
    default_ref = head_sha = ""
    for line in text.splitlines():
        if line.startswith("ref:") and line.endswith("\tHEAD"):
            default_ref = line.split()[1]
        elif re.fullmatch(r"[0-9a-f]{40}\tHEAD", line):
            head_sha = line.split("\t", 1)[0]
    if not default_ref or not head_sha:
        raise SystemExit(f"CROWN_OBSERVE_BLOCKED[REMOTE_HEAD_UNRESOLVED]:{url}")
    return default_ref, head_sha


def observe(root: Path) -> dict:
    rows = []
    for sub in declared_submodules(root):
        mode, current = gitlink(root, sub["path"])
        default_ref, latest = remote_head(sub["url"], root)
        rows.append({**sub, "current": current, "default_ref": default_ref,
                     "latest": latest, "changed": current != latest, "mode": mode})
    return {
        "schema": SCHEMA,
        "repository": run("git", "config", "--get", "remote.origin.url",
                          cwd=root, check=False).strip(),
        "base_sha": run("git", "rev-parse", "HEAD", cwd=root).strip(),
        "authority_boundary": BOUNDARY,
        "submodules": rows,
        "changed_count": sum(1 for r in rows if r["changed"]),
    }


def esc(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def to_turtle(doc: dict) -> str:
    out = [
        f"@prefix crown: <{NS}> .",
        "@prefix sosa:  <http://www.w3.org/ns/sosa/> .",
        "@prefix prov:  <http://www.w3.org/ns/prov#> .",
        "@prefix dcat:  <http://www.w3.org/ns/dcat#> .",
        "@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "crown:receipt a crown:CrownReceipt , prov:Entity ;",
        f'    crown:schema "{esc(doc["schema"])}" ;',
        f'    crown:repository "{esc(doc["repository"])}" ;',
        f'    crown:baseSha "{doc["base_sha"]}" ;',
        f'    crown:authorityBoundary "{BOUNDARY}" ;',
        f'    crown:changedCount "{doc["changed_count"]}" .',
        "",
    ]
    for row in doc["submodules"]:
        slug = re.sub(r"[^A-Za-z0-9]", "_", row["path"])
        e = f"crown:edge_{slug}"
        changed = "true" if row["changed"] else "false"
        state = "crown:Drifted" if row["changed"] else "crown:Converged"
        out += [
            f"{e} a crown:SubmoduleEdge , sosa:FeatureOfInterest ;",
            f'    crown:edgeName "{esc(row["name"])}" ;',
            f'    crown:edgePath "{esc(row["path"])}" ;',
            f'    crown:remoteUrl "{esc(row["url"])}" ;',
            f'    crown:currentSha "{row["current"]}" ;',
            f'    crown:latestSha "{row["latest"]}" ;',
            f'    crown:defaultRef "{esc(row["default_ref"])}" ;',
            f'    crown:changed "{changed}" ;',
            f"    crown:driftState {state} .",
            "",
            f"{e}_remote a dcat:Distribution ;",
            f'    dcat:accessURL "{esc(row["url"])}" .',
            "",
            f"{e}_gitlink a crown:GitlinkObservation , sosa:Observation ;",
            f"    sosa:hasFeatureOfInterest {e} ;",
            "    sosa:usedProcedure crown:GitLsTree ;",
            f'    crown:gitlinkMode "{row.get("mode", "160000")}" ;',
            f'    sosa:hasSimpleResult "{row["current"]}" .',
            "",
            f"{e}_remotehead a crown:RemoteHeadObservation , sosa:Observation ;",
            f"    sosa:hasFeatureOfInterest {e} ;",
            "    sosa:usedProcedure crown:GitLsRemoteSymref ;",
            f'    sosa:hasSimpleResult "{row["latest"]}" .',
            "",
            f"crown:receipt crown:hasEdge {e} .",
            "",
        ]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--observe", action="store_true")
    ap.add_argument("--from-receipt")
    args = ap.parse_args()
    if args.from_receipt:
        doc = json.loads(Path(args.from_receipt).read_text())
    elif args.observe:
        doc = observe(Path(args.root).resolve())
    else:
        raise SystemExit("CROWN_OBSERVE_REFUSED[NO_MODE]: pass --observe or --from-receipt")
    sys.stdout.write(to_turtle(doc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
