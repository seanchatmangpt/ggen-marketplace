#!/usr/bin/env python3
"""Read-only GitHub repository census -> deterministic Turtle projection.

Uses authenticated /user/repos when GITHUB_TOKEN is present, otherwise public
/users/{owner}/repos. No mutation endpoints are called.
"""
from __future__ import annotations
import argparse, json, os, sys, time, urllib.parse, urllib.request

API="https://api.github.com"
PEO="https://ggen.dev/ontology/portfolio-epistemic-observability#"
PROV="http://www.w3.org/ns/prov#"
DCAT="http://www.w3.org/ns/dcat#"

def get(url, token=None):
    req=urllib.request.Request(url, headers={"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28", **({"Authorization":f"Bearer {token}"} if token else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r), dict(r.headers)

def esc(s): return str(s).replace('\\','\\\\').replace('"','\\"')

def census(owner, token=None):
    repos=[]; page=1
    while True:
        if token:
            url=f"{API}/user/repos?per_page=100&page={page}&affiliation=owner&sort=full_name&direction=asc"
        else:
            url=f"{API}/users/{urllib.parse.quote(owner)}/repos?per_page=100&page={page}&type=owner&sort=full_name&direction=asc"
        batch, hdr=get(url, token)
        if token: batch=[r for r in batch if r.get("owner",{}).get("login","").lower()==owner.lower()]
        repos.extend(batch)
        if len(batch)<100: break
        page+=1
    dedup={r["full_name"]:r for r in repos}
    return [dedup[k] for k in sorted(dedup)]

def project(owner, repos, observed_at):
    out=["@prefix peo: <https://ggen.dev/ontology/portfolio-epistemic-observability#> .","@prefix prov: <http://www.w3.org/ns/prov#> .","@prefix dcat: <http://www.w3.org/ns/dcat#> .","@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",""]
    out += [f"peo:r77-universe a peo:RepositoryUniverse ;",f"  peo:repositoryCount {len(repos)} ;",f"  peo:owner \"{esc(owner)}\" ;",f"  peo:observedAt \"{esc(observed_at)}\"^^xsd:dateTime .",""]
    for r in repos:
        slug=r['name'].replace('_','-').replace('.','-')
        out += [f"peo:r77-repo-{slug} a peo:RepositorySnapshot ;",f"  peo:repository \"{esc(r['full_name'])}\" ;",f"  peo:defaultBranch \"{esc(r.get('default_branch') or '')}\" ;",f"  peo:archived {str(bool(r.get('archived'))).lower()} ;",f"  peo:fork {str(bool(r.get('fork'))).lower()} ;",f"  peo:visibility \"{esc(r.get('visibility','public'))}\" ;",f"  peo:language \"{esc(r.get('language') or 'UNKNOWN')}\" .",""]
    return "\n".join(out)

def main():
    p=argparse.ArgumentParser(); p.add_argument("--owner",default="seanchatmangpt"); p.add_argument("--observed-at",required=True); p.add_argument("--output",default="-"); a=p.parse_args()
    token=os.getenv("GITHUB_TOKEN"); repos=census(a.owner, token); ttl=project(a.owner,repos,a.observed_at)
    if a.output=="-": print(ttl)
    else: open(a.output,"w",encoding="utf-8").write(ttl+"\n")
    print(json.dumps({"owner":a.owner,"repository_count":len(repos),"authenticated":bool(token),"standing":"PARTIAL_ALIVE" if not token else "ALIVE"},sort_keys=True),file=sys.stderr)
if __name__=="__main__": main()
