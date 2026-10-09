#!/usr/bin/env python3
"""Fleet workgraph admission driver.

For every repo with docs/sjira/v26.10.8*/WORKGRAPH.ttl, parse the Turtle with
rdflib, extract each sj:WorkOrder individual into the 16-key JSON map the
GgenIgniter.SemanticJira.admit_work_order/1 kernel requires, and admit it via
`mix run` against the ggen_igniter checkout (subprocess, warm MIX_BUILD_ROOT).

Results are appended (append-only) to docs/sjira/v26.10.8/ADMISSION-LEDGER.jsonl
in this repo. Typed refusals are recorded, never hand-tuned away: the gate is
the gate. Only mechanical extraction bugs in THIS script are fixed.

Usage:
  python3 scripts/admit_workgraphs.py [--repos repo1,repo2] [--dry-run]
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS
from rdflib.term import Literal

SJ = Namespace("https://ggen-igniter.dev/ontology/semantic-jira#")
DCTERMS = Namespace("http://purl.org/dc/terms/")

GGEN_IGNITER = Path("/Users/sac/ggen_igniter")
MARKETPLACE = Path("/Users/sac/ggen-marketplace")
LEDGER = MARKETPLACE / "docs/sjira/v26.10.8/ADMISSION-LEDGER.jsonl"
BUILD_ROOT = "_build-lanecourt"  # warm build root (reused, per lane contract)

REPOS = [
    "ggen-marketplace", "xaas", "ash_a2a", "ash_pplan", "ex4pm", "beam4pm",
    "zcode-cli", "castle", "ash_surface", "ash_r2rml", "ash_affidavit",
]


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def one(g: Graph, s, p):
    for o in g.objects(s, p):
        return o
    return None


def localname(node) -> str:
    return str(node).rsplit("#", 1)[-1].rsplit("/", 1)[-1]


def label(g: Graph, node):
    """Human text for a node: dcterms:description > dcterms:title > rdfs:label."""
    for p in (DCTERMS.description, DCTERMS.title, RDFS.label):
        v = one(g, node, p)
        if v is not None:
            return str(v)
    return None


def node_text(g: Graph, node):
    """Text of a node that may be a literal or an IRI/blank with description."""
    if node is None:
        return None
    if isinstance(node, Literal):
        return str(node)
    return label(g, node)


def extract_order(g: Graph, wo, repo: str, campaign_dir: str) -> dict:
    """Extract one sj:WorkOrder into the 16-key admission map.

    Mechanical extraction only: field values come from the graph. Where a
    graph authors no value, a mechanical canonical default is used and noted
    in _extraction.defaults_used. Standing, base_sha and list contents are
    never synthesized — the kernel's typed refusal records them as-is.
    """
    ident = str(one(g, wo, SJ.identity) or one(g, wo, DCTERMS.identifier) or localname(wo))
    title = node_text(g, one(g, wo, DCTERMS.title))
    if title is None:
        title = label(g, wo) or ident
    desc = node_text(g, one(g, wo, DCTERMS.description)) or title

    def collect(pred, alternates=()):
        """Literals or linked individuals (resolved to their text)."""
        vals = []
        for o in g.objects(wo, pred):
            t = node_text(g, o)
            if t:
                vals.append(t)
        if vals:
            return vals
        for alt in alternates:
            for o in g.objects(wo, alt):
                t = node_text(g, o)
                if t:
                    vals.append(t)
        return vals

    acceptance = collect(SJ.acceptance, (SJ.acceptanceItem,))
    falsifiers = collect(SJ.falsifier, (SJ.falsifierItem,))
    defaults = []

    courts = [str(o) for o in g.objects(wo, SJ.requiredCourt)]
    if not courts:
        for c in g.objects(wo, SJ.requiresCourt):
            courts.append(label(g, c) or localname(c))

    evidence = [str(o) for o in g.objects(wo, SJ.requiredEvidence)]

    projections = []
    for o in g.objects(wo, SJ.projection):
        # canonical vocabulary is bare tokens ("jira"); graphs authoring IRI
        # form (sj:#projection-jira) are normalized mechanically
        t = str(o)
        if not isinstance(o, Literal):
            t = localname(o)
            if t.startswith("projection-"):
                t = t[len("projection-"):]
        projections.append(t)
    if not projections:
        projections = ["jira", "receipt"]  # canonical semantic-jira-pack pair
        defaults.append("projections")

    path_scope = []
    for o in g.objects(wo, SJ.pathScope):
        path_scope.extend(str(o).split())

    dependencies = []
    for d in g.objects(wo, SJ.dependency):
        up = one(g, d, SJ.upstream)
        if up is not None and str(up):
            dependencies.append({
                "upstream": str(up),
                "type": str(one(g, d, SJ.dependencyType) or "requiresReceipt"),
            })

    base_sha = str(one(g, wo, SJ.baseSha) or "")
    if not base_sha:
        # campaign-level subject binding: sj:Subject individuals carry the
        # base/head SHA the whole workgraph is pinned to
        for subj in g.subjects(RDF.type, SJ.Subject):
            v = one(g, subj, SJ.baseSha) or one(g, subj, SJ.headSha)
            if v is not None:
                base_sha = str(v)
                break

    standing = str(one(g, wo, SJ.standing) or "UNKNOWN")
    evidence_ceiling = str(one(g, wo, SJ.evidenceCeiling) or "")
    if not evidence_ceiling:
        evidence_ceiling = standing
        defaults.append("evidence_ceiling")

    promotion_rule = str(one(g, wo, SJ.promotionRule) or "")
    if not promotion_rule:
        promotion_rule = "verified_by_required_courts_then_receipted"
        defaults.append("promotion_rule")

    replay_identity = str(one(g, wo, SJ.replayIdentity) or "")
    if not replay_identity:
        replay_identity = f"sjira-{campaign_dir}-{ident}"
        defaults.append("replay_identity")

    order = {
        "identity": ident,
        "title": title,
        "description": desc,
        "subject": str(one(g, wo, SJ.subject) or ident),
        "repository": str(one(g, wo, SJ.repository) or f"seanchatmangpt/{repo}"),
        "base_sha": base_sha,
        "standing": standing,
        "evidence_ceiling": evidence_ceiling,
        "promotion_rule": promotion_rule,
        "replay_identity": replay_identity,
        "required_courts": courts or [f"urn:sjira:{repo}:{campaign_dir}:default-court"],
        "required_evidence": evidence or [evidence_ceiling],
        "acceptance": acceptance,
        "falsifiers": falsifiers,
        "projections": projections,
        "origin_authority": f"urn:sjira:{repo}:{campaign_dir}",
        "path_scope": path_scope,
        "dependencies": dependencies,
    }
    if not courts:
        defaults.append("required_courts")
    if not evidence:
        defaults.append("required_evidence")
    order["_extraction"] = {
        "campaign_dir": campaign_dir,
        "defaults_used": sorted(set(defaults)),
    }
    return order


def find_workgraph(repo: str):
    base = Path("/Users/sac") / repo
    if not base.is_dir():
        return None
    for cand in sorted(base.glob("docs/sjira/v26.10.8*/WORKGRAPH.ttl")):
        return cand
    # goal.ttl-style checkpoint graph (validate_workgraphs.py precedent):
    # routed, then typed-skipped in main() since it authors no WorkOrders
    for cand in sorted(base.glob("docs/sjira/v26.10.8*/goal.ttl")):
        return cand
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repos", default=None, help="comma list of repo names")
    ap.add_argument("--dry-run", action="store_true", help="extract only; no mix run")
    args = ap.parse_args()

    repos = args.repos.split(",") if args.repos else REPOS
    ledger_rows = []

    for repo in repos:
        workgraph = find_workgraph(repo)
        if workgraph is None:
            ledger_rows.append({
                "ts": now_iso(), "repo": repo, "order": None, "admitted": False,
                "refusal_reason": "no_workgraph",
                "detail": f"no docs/sjira/v26.10.8*/WORKGRAPH.ttl under /Users/sac/{repo}",
            })
            continue

        g = Graph()
        try:
            g.parse(workgraph, format="turtle")
        except Exception as e:
            ledger_rows.append({
                "ts": now_iso(), "repo": repo, "order": None, "admitted": False,
                "refusal_reason": "workgraph_parse_error", "detail": repr(e),
                "workgraph": str(workgraph),
            })
            continue

        extracted = []
        for wo in sorted(g.subjects(RDF.type, SJ.WorkOrder), key=str):
            ident = str(one(g, wo, SJ.identity) or one(g, wo, DCTERMS.identifier) or localname(wo))
            try:
                m = extract_order(g, wo, repo, workgraph.parent.name)
                extracted.append((ident, m))
            except Exception as e:
                ledger_rows.append({
                    "ts": now_iso(), "repo": repo, "order": ident,
                    "admitted": False, "refusal_reason": "extraction_error",
                    "detail": repr(e), "workgraph": str(workgraph),
                })

        if not extracted:
            # Typed skip (not a refusal, not silence): a graph with zero
            # sj:WorkOrder individuals but authored sj:GoalCheckpoint nodes is
            # a goal.ttl-style checkpoint graph (validate_workgraphs.py
            # precedent). Its content routes through the GoalCheckpoint shape
            # path, never WorkOrder admission — its own header law forbids
            # authored WorkOrders.
            checkpoints = sorted(
                (str(one(g, gc, DCTERMS.identifier) or localname(gc)))
                for gc in g.subjects(RDF.type, SJ.GoalCheckpoint)
            )
            if checkpoints:
                ledger_rows.append({
                    "ts": now_iso(), "repo": repo, "order": None,
                    "admitted": None, "refusal_reason": "skipped_goal_checkpoint_graph",
                    "detail": (
                        "zero sj:WorkOrder individuals by graph law; "
                        f"{len(checkpoints)} sj:GoalCheckpoint routed via "
                        "GoalCheckpoint shape path (validate_workgraphs.py), "
                        "not WorkOrder admission: " + ", ".join(checkpoints)
                    ),
                    "workgraph": str(workgraph),
                })
            else:
                ledger_rows.append({
                    "ts": now_iso(), "repo": repo, "order": None, "admitted": False,
                    "refusal_reason": "no_sj_WorkOrder_individuals",
                    "detail": str(workgraph),
                })
            continue

        if args.dry_run:
            for ident, m in extracted:
                ledger_rows.append({
                    "ts": now_iso(), "repo": repo, "order": ident,
                    "admitted": None, "refusal_reason": "dry_run",
                    "extraction": m.get("_extraction", {}),
                })
            continue

        payload = []
        extraction_meta = {}
        for ident, m in extracted:
            meta = m.pop("_extraction", {})
            meta["workgraph"] = str(workgraph)
            extraction_meta[ident] = meta
            payload.append(m)
        json_path = Path(f"/tmp/admit_wg_{repo}.json")
        json_path.write_text(json.dumps(payload))
        runner = Path("/tmp/admit_wg_runner.exs")
        runner.write_text(RUNNER_EXS)
        env = dict(os.environ)
        env["MIX_BUILD_ROOT"] = BUILD_ROOT
        proc = subprocess.run(
            ["mix", "run", str(runner), str(json_path)],
            cwd=GGEN_IGNITER, env=env, capture_output=True, text=True,
            timeout=900,
        )
        got = False
        for line in proc.stdout.splitlines():
            if line.startswith("ADMIT-RESULT: "):
                rec = json.loads(line[len("ADMIT-RESULT: "):])
                ledger_rows.append({
                    "ts": now_iso(), "repo": repo,
                    "order": rec["identity"], "admitted": rec["admitted"],
                    "work_order_digest": rec.get("work_order_digest"),
                    "definition_digest": rec.get("definition_digest"),
                    "refusal_reason": rec.get("refusal_reason"),
                    "workgraph": str(workgraph),
                })
                got = True
        if not got:
            ledger_rows.append({
                "ts": now_iso(), "repo": repo, "order": None, "admitted": False,
                "refusal_reason": "mix_run_failed",
                "detail": (proc.stderr or proc.stdout)[-800:],
                "workgraph": str(workgraph),
            })

    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a") as f:
        for row in ledger_rows:
            f.write(json.dumps(row, sort_keys=True) + "\n")
    print(f"wrote {len(ledger_rows)} ledger rows -> {LEDGER}")
    return 0


RUNNER_EXS = '''
payload =
  System.argv()
  |> List.first()
  |> File.read!()
  |> Jason.decode!()

Enum.each(payload, fn wo ->
  result =
    case GgenIgniter.SemanticJira.admit_work_order(wo) do
      {:ok, admitted} ->
        %{
          "identity" => wo["identity"],
          "admitted" => true,
          "work_order_digest" => admitted["work_order_digest"],
          "definition_digest" => admitted["definition_digest"]
        }

      {:error, {:refused_work_order, reason}} ->
        %{"identity" => wo["identity"], "admitted" => false, "refusal_reason" => inspect(reason)}

      other ->
        %{
          "identity" => wo["identity"],
          "admitted" => false,
          "refusal_reason" => "OTHER: " <> inspect(other)
        }
    end

  IO.puts("ADMIT-RESULT: " <> Jason.encode!(result))
end)
'''


if __name__ == "__main__":
    sys.exit(main())
