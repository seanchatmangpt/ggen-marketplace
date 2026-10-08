"""Resource-graph generator tests: rendered .tf -> f5ea: graph -> gates.

Closes the lattice-audit coupling gap: templates emitted HCL only, while
gates 120/140/150 evaluated an f5ea: resource-description graph that
nothing manufactured. These tests prove the loop
template -> HCL (rendered fixture) -> gen_resource_graph.py -> RDF -> gate
end to end, one gate per provider (120=aws, 140=gcp, 150=azure).
"""
import pathlib
import subprocess
import sys

import rdflib
import pytest

HERE = pathlib.Path(__file__).resolve().parent
PACK = HERE.parent
SCRIPT = PACK / "scripts" / "gen_resource_graph.py"
FIXTURES = HERE / "fixtures"
QUERIES = PACK / "queries"
F5EA = rdflib.Namespace("https://ggen.io/ontology/fortune5-enterprise-architecture#")

PROVIDER_GATES = {"aws": "120-zero-wildcard-iam.rq",
                  "gcp": "140-cmek-and-private-connectivity.rq",
                  "azure": "150-azure-nist-800-53-rev5.rq"}


def build_graph(provider):
    fixture = FIXTURES / ("%s_sbb.rendered.tf" % provider)
    out = HERE / "__pycache__" / ("generated_%s.ttl" % provider)
    out.parent.mkdir(exist_ok=True)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--provider", "PROV".replace("PROV", provider),
         "--input", str(fixture), "--out", str(out)],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    g = rdflib.Graph()
    g.parse(out, format="turtle")
    return g, out


def run_gate(provider, g):
    q = (QUERIES / PROVIDER_GATES[provider]).read_text()
    res = g.query(q)
    return bool(res.askAnswer)


@pytest.mark.parametrize("provider,gate", sorted(PROVIDER_GATES.items()))
def test_gate_passes_over_generated_graph(provider, gate):
    g, _ = build_graph(provider)
    assert run_gate(provider, g) is True, "%s gate %s must pass" % (provider, gate)


def test_aws_graph_facts():
    g, _ = build_graph("aws")
    slug = F5EA["Realization/finance-sbb"]
    assert (slug, rdflib.RDF.type, F5EA.Realization) in g
    assert (slug, F5EA.providerVariant, rdflib.Literal("aws")) in g
    acts = set()
    for r in g.objects(slug, F5EA.hasResource):
        acts |= set(g.objects(r, F5EA.iamAction))
    assert '"*"' not in {str(a) for a in acts}
    assert "sso:ListInstances" in {str(a) for a in acts}
    assert (slug, F5EA.airGapParityEgress, rdflib.Literal(True)) in g
    assert (slug, F5EA.airGapParityAudit, rdflib.Literal(True)) in g


def test_gcp_graph_facts():
    g, _ = build_graph("gcp")
    slug = F5EA["Realization/fin1"]
    classes = {}
    for r in g.objects(slug, F5EA.hasResource):
        for c in g.objects(r, F5EA.resourceClass):
            classes.setdefault(str(c), []).append(r)
    assert classes["storagelike"], "kms resources must be storagelike"
    for r in classes["storagelike"]:
        assert list(g.objects(r, F5EA.hasCmekKey)), "storagelike carries CMEK"
    for r in classes["servicelike"]:
        modes = {str(m) for m in g.objects(r, F5EA.ingressMode)}
        assert modes <= {"psc", "none"}
    public = [r for r in g.objects(slug, F5EA.hasResource)
              if rdflib.Literal("public") in set(g.objects(r, F5EA.ingressMode))]
    assert not public, "no public ingress anywhere"


def test_azure_graph_facts():
    g, _ = build_graph("azure")
    slug = F5EA["Realization/fin"]
    resources = list(g.objects(slug, F5EA.hasResource))
    assert resources
    for r in resources:
        for c in ("AC-2", "SC-28", "CM-6"):
            assert (r, F5EA.controlMapping, rdflib.Literal(c)) in g






def _violated(provider, extra_triples):
    """Build the good graph, inject violating triples, re-run the gate."""
    g, out = build_graph(provider)
    violated = out.with_name("violated_%s.ttl" % provider)
    violated.write_text(out.read_text() + extra_triples)
    bad = rdflib.Graph()
    bad.parse(violated, format="turtle")
    return run_gate(provider, bad)


def _mutated(provider, transform):
    """Build the good graph, transform its serialization, re-run the gate."""
    g, out = build_graph(provider)
    ns = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
    violated = out.with_name("violated_%s.ttl" % provider)
    violated.write_text(transform(out.read_text(), ns))
    bad = rdflib.Graph()
    bad.parse(violated, format="turtle")
    return run_gate(provider, bad)


def test_gates_are_not_vacuous():
    ns = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
    # aws: an injected wildcard iamAction must fail gate 120
    wild = "<%sSbbResource/finance-sbb/aws_iam_role_policy_inline.wild>" % ns
    assert _violated("aws", '%s a <%sSbbResource> .\n%s <%siamAction> "*" .'
                     % (wild, ns, wild, ns)) is False
    # gcp: public ingress must fail gate 140
    svc = "<%sSbbResource/fin1/google_compute_region_backend_service.svc>" % ns
    assert _violated("gcp", '%s <%singressMode> "public" .' % (svc, ns)) is False
    # azure: a resource carrying none of the three controls must fail gate 150
    rg = "<%sSbbResource/fin/azurerm_resource_group.connectivity>" % ns
    def drop_controls(text, ns):
        kept = [ln for ln in text.splitlines()
                if not (ln.startswith(rg + " ") and "controlMapping" in ln)]
        return "\n".join(kept) + "\n"
    assert _mutated("azure", drop_controls) is False
