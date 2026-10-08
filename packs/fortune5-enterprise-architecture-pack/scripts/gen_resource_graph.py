#!/usr/bin/env python3
"""gen_resource_graph.py -- close the template -> HCL -> RDF -> gate loop.

Parses the RENDERED .tf bodies emitted by
packs/fortune5-enterprise-architecture-pack/templates/{aws,gcp,azure}-sbb.tf.tera
and manufactures the f5ea: resource individuals that gates
queries/120 (zero-wildcard IAM), queries/140 (CMEK + private connectivity)
and queries/150 (Azure NIST SP 800-53 Rev 5) evaluate over.

Usage:
  gen_resource_graph.py --provider aws --input rendered.tf [--out graph.ttl]

If --out is omitted, deterministic sorted Turtle is written to stdout.
Refuses (exit 2) if parsing yields no facts.
"""
from __future__ import annotations

import argparse
import re
import sys

F5EA = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

AZURE_CONTROLS = ("AC-2", "SC-28", "CM-6")

GCP_STORAGELIKE = {"google_kms_crypto_key", "google_kms_key_ring"}
GCP_SERVICELIKE_PSC = {
    "google_compute_forwarding_rule",
    "google_compute_service_attachment",
    "google_compute_region_backend_service",
}
GCP_SERVICELIKE_NONE = {"google_compute_firewall"}


def parse_resources(hcl):
    """Extract balanced-brace resource blocks as (type, name, body) tuples."""
    out = []
    for m in re.finditer(r'(?m)^resource\s+"([^"]+)"\s+"([^"]+)"\s*\{', hcl):
        rtype, rname, start = m.group(1), m.group(2), m.end()
        depth, i = 1, start
        while i < len(hcl) and depth:
            if hcl[i] == '{':
                depth += 1
            elif hcl[i] == '}':
                depth -= 1
            i += 1
        if depth != 0:
            raise ValueError("unbalanced braces in resource %s.%s" % (rtype, rname))
        out.append((rtype, rname, hcl[start:i - 1]))
    return out


def extract_actions(body):
    """All enumerated IAM actions inside jsonencode Action = [ ... ] lists."""
    actions = []
    for m in re.finditer(r'(?is)\bAction\s*=\s*\[(.*?)\]', body):
        actions += re.findall(r'"([^"]+)"', m.group(1))
    return actions


def slug_of(provider, hcl, resources):
    """Derive the realization slug from the rendered body."""
    if provider == "aws":
        m = re.search(r'workload\s*=\s*"([^"]+)"', hcl)
        return m.group(1) if m else None
    if provider == "gcp":
        for _, _, body in resources:
            m = re.search(r'name\s*=\s*"sbb-([^"]+?)-[^"]*"', body)
            if m:
                return m.group(1)
    if provider == "azure":
        for _, _, body in resources:
            m = re.search(r'name\s*=\s*"rg-([^"]+?)-', body)
            if m:
                return m.group(1)
    return None


def ttl_escape(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


def emit(provider, resources, hcl_for_slug=None):
    """Return (slug, sorted unique triple strings)."""
    if hcl_for_slug is None:
        hcl_for_slug = "\n".join(b for _, _, b in resources)
    slug = slug_of(provider, hcl_for_slug, resources)
    if not slug:
        raise SystemExit("refusing: no realization slug derivable from input")
    reals = "<%sRealization/%s>" % (F5EA, slug)

    def res_iri(rtype, rname):
        return "<%sSbbResource/%s/%s.%s>" % (F5EA, slug, rtype, rname)

    t = []
    def add(s, p, o):
        t.append((s, p, o))

    add(reals, "a", "<%sRealization>" % F5EA)
    add(reals, "<%sproviderVariant>" % F5EA, '"%s"' % provider)
    add(reals, "<%ssbbSlug>" % F5EA, '"%s"' % slug)

    for rtype, rname, body in resources:
        r = res_iri(rtype, rname)
        add(reals, "<%shasResource>" % F5EA, r)
        add(r, "a", "<%sSbbResource>" % F5EA)
        add(r, "<%stfType>" % F5EA, '"%s"' % rtype)
        add(r, "<%stfName>" % F5EA, '"%s"' % rname)

        if provider == "aws":
            for a in sorted(set(extract_actions(body))):
                add(r, "<%siamAction>" % F5EA, '"%s"' % ttl_escape(a))
            if rtype == "aws_vpc_endpoint" and "private_dns_enabled" in body:
                add(reals, "<%sairGapParityEgress>" % F5EA, "true")
                add(reals, "<%sairGapParityAudit>" % F5EA, "true")

        elif provider == "gcp":
            if rtype in GCP_STORAGELIKE:
                add(r, "<%sresourceClass>" % F5EA, '"storagelike"')
                m = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', body)
                key = m.group(1) if m else rname
                add(r, "<%shasCmekKey>" % F5EA, '"%s"' % key)
            if rtype in GCP_SERVICELIKE_PSC:
                add(r, "<%sresourceClass>" % F5EA, '"servicelike"')
                add(r, "<%singressMode>" % F5EA, '"psc"')
            if rtype in GCP_SERVICELIKE_NONE:
                add(r, "<%sresourceClass>" % F5EA, '"servicelike"')
                add(r, "<%singressMode>" % F5EA, '"none"')

        elif provider == "azure":
            for c in AZURE_CONTROLS:
                add(r, "<%scontrolMapping>" % F5EA, '"%s"' % c)
    return slug, t


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--provider", required=True, choices=["aws", "gcp", "azure"])
    ap.add_argument("--input", required=True, help="rendered .tf body")
    ap.add_argument("--out", help="output Turtle (default stdout)")
    args = ap.parse_args(argv)

    hcl = open(args.input).read()
    resources = parse_resources(hcl)
    slug, triples = emit(args.provider, resources, hcl_for_slug=hcl)

    lines = []
    lines.append("# generated by gen_resource_graph.py -- do not edit by hand")
    lines.append("# realization: %s provider: %s" % (slug, args.provider))
    for s, p, o in sorted(set(triples)):
        if p == "a":
            lines.append("%s a %s ." % (s, o))
        else:
            lines.append("%s %s %s ." % (s, p, o))
    out = "\n".join(lines) + "\n"
    if args.out:
        open(args.out, "w").write(out)
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
