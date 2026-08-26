#!/usr/bin/env python3
"""Read-only GitHub repository census -> deterministic exact-subject Turtle.

Authenticated mode enumerates every owner-affiliated repository reachable by the
linked token and resolves each default branch to an exact SHA. Public fallback
uses the public owner repository surface and is therefore PARTIAL_ALIVE for
reachability completeness. No mutation endpoint is called.
"""
from __future__ import annotations
import argparse, json, os, sys, urllib.error, urllib.parse, urllib.request

API = "https://api.github.com"

def get(url, token=None):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response), dict(response.headers)

def esc(value):
    return str(value).replace("\\", "\\\\").replace('"', '\\"')

def census(owner, token=None):
    repos = []
    page = 1
    while True:
        if token:
            url = f"{API}/user/repos?per_page=100&page={page}&affiliation=owner&sort=full_name&direction=asc"
        else:
            url = f"{API}/users/{urllib.parse.quote(owner)}/repos?per_page=100&page={page}&type=owner&sort=full_name&direction=asc"
        batch, _ = get(url, token)
        if token:
            batch = [r for r in batch if r.get("owner", {}).get("login", "").lower() == owner.lower()]
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    dedup = {repo["full_name"]: repo for repo in repos}
    return [dedup[name] for name in sorted(dedup)]

def resolve_heads(repos, token=None):
    resolved = []
    failures = []
    for repo in repos:
        item = dict(repo)
        branch = item.get("default_branch")
        if not branch:
            item["exact_head"] = None
            item["head_resolved"] = False
            failures.append({"repository": item["full_name"], "reason": "MISSING_DEFAULT_BRANCH"})
            resolved.append(item)
            continue
        full_name = urllib.parse.quote(item["full_name"], safe="/")
        branch_name = urllib.parse.quote(branch, safe="")
        try:
            observation, _ = get(f"{API}/repos/{full_name}/branches/{branch_name}", token)
            item["exact_head"] = observation.get("commit", {}).get("sha")
            item["head_resolved"] = bool(item["exact_head"])
            if not item["head_resolved"]:
                failures.append({"repository": item["full_name"], "reason": "HEAD_SHA_ABSENT"})
        except urllib.error.HTTPError as exc:
            item["exact_head"] = None
            item["head_resolved"] = False
            failures.append({"repository": item["full_name"], "reason": f"HTTP_{exc.code}"})
        resolved.append(item)
    return resolved, failures

def project(owner, repos, observed_at):
    out = [
        "@prefix peo: <https://ggen.dev/ontology/portfolio-epistemic-observability#> .",
        "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "@prefix dcat: <http://www.w3.org/ns/dcat#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        "peo:r77-universe a peo:RepositoryUniverse ;",
        f"  peo:repositoryCount {len(repos)} ;",
        f"  peo:owner \"{esc(owner)}\" ;",
        f"  peo:observedAt \"{esc(observed_at)}\"^^xsd:dateTime .",
        "",
    ]
    for repo in repos:
        slug = repo["name"].replace("_", "-").replace(".", "-")
        lines = [
            f"peo:r77-repo-{slug} a peo:RepositorySnapshot ;",
            f"  peo:repository \"{esc(repo['full_name'])}\" ;",
            f"  peo:defaultBranch \"{esc(repo.get('default_branch') or '')}\" ;",
            f"  peo:headResolved {str(bool(repo.get('head_resolved'))).lower()} ;",
            f"  peo:headObservedAt \"{esc(observed_at)}\"^^xsd:dateTime ;",
            f"  peo:archived {str(bool(repo.get('archived'))).lower()} ;",
            f"  peo:fork {str(bool(repo.get('fork'))).lower()} ;",
            f"  peo:visibility \"{esc(repo.get('visibility', 'public'))}\" ;",
            f"  peo:language \"{esc(repo.get('language') or 'UNKNOWN')}\"",
        ]
        if repo.get("exact_head"):
            lines[-1] += " ;"
            lines.append(f"  peo:exactHead \"{esc(repo['exact_head'])}\"")
        lines[-1] += " ."
        out.extend(lines + [""])
    return "\n".join(out)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default="seanchatmangpt")
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--output", default="-")
    parser.add_argument("--skip-heads", action="store_true", help="enumerate only; output is necessarily PARTIAL_ALIVE")
    args = parser.parse_args()
    token = os.getenv("GITHUB_TOKEN")
    repos = census(args.owner, token)
    failures = []
    if args.skip_heads:
        repos = [dict(repo, exact_head=None, head_resolved=False) for repo in repos]
    else:
        repos, failures = resolve_heads(repos, token)
    ttl = project(args.owner, repos, args.observed_at)
    if args.output == "-":
        print(ttl)
    else:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(ttl + "\n")
    unresolved = sum(not repo.get("head_resolved") for repo in repos)
    standing = "ALIVE" if token and not args.skip_heads and unresolved == 0 else "PARTIAL_ALIVE"
    print(json.dumps({"owner": args.owner, "repository_count": len(repos), "resolved_heads": len(repos)-unresolved, "unresolved_heads": unresolved, "failures": failures, "authenticated": bool(token), "standing": standing}, sort_keys=True), file=sys.stderr)

if __name__ == "__main__":
    main()
