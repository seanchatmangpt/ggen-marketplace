"""Resource-graph generator tests: rendered .tf -> f5ea: graph -> gates.

Closes the lattice-audit coupling gap: templates emitted HCL only, while
gates 120/140/150 evaluated an f5ea: resource-description graph that
nothing manufactured. These tests prove the loop
template -> HCL (rendered fixture) -> gen_resource_graph.py -> RDF -> gate
end to end, one gate per provider (120=aws, 140=gcp, 150=azure).

The end-to-end leg (test_gate_passes_over_rendered_templates) closes the last
static link: the .tf input is the ACTUAL render of templates/{p}-sbb.tf.tera
over the provider-template fixture contexts (shared via conftest.py), so
template -> HCL -> RDF -> gate runs with zero static intermediates. The
static fixtures under tests/fixtures/ remain as the generator's own unit-test
fallback (facts tests + non-vacuity mutations pin exact IRIs).
"""
import pathlib
import subprocess
import sys

import rdflib
import pytest

import test_provider_templates as tpt

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


def build_graph_from_rendered_template(provider):
    """End-to-end: render the real .tera template -> HCL -> RDF -> gate.

    Uses the same mini-Tera renderer and fixture contexts as
    test_provider_templates (shared via conftest.py) -- no static .tf input.
    """
    template, ctx = RENDER_SOURCES[provider]
    rendered = tpt.render(template.read_text(), dict(ctx))
    hcl = HERE / "__pycache__" / ("rendered_%s.tf" % provider)
    hcl.parent.mkdir(exist_ok=True)
    hcl.write_text(rendered)
    out = HERE / "__pycache__" / ("generated_from_template_%s.ttl" % provider)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--provider", provider,
         "--input", str(hcl), "--out", str(out)],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    g = rdflib.Graph()
    g.parse(out, format="turtle")
    return g, out


RENDER_SOURCES = {"aws": (tpt.AWS, tpt.AWS_CTX),
                  "gcp": (tpt.GCP, tpt.GCP_CTX),
                  "azure": (tpt.AZURE, tpt.AZURE_CTX)}


@pytest.mark.parametrize("provider,gate", sorted(PROVIDER_GATES.items()))
def test_gate_passes_over_generated_graph(provider, gate):
    g, _ = build_graph(provider)
    assert run_gate(provider, g) is True, "%s gate %s must pass" % (provider, gate)


@pytest.mark.parametrize("provider,gate", sorted(PROVIDER_GATES.items()))
def test_gate_passes_over_rendered_templates(provider, gate):
    """The closed loop: template render (real renderer, real context) ->
    extracted HCL -> gen_resource_graph.py -> f5ea: graph -> gate ASK."""
    g, _ = build_graph_from_rendered_template(provider)
    assert run_gate(provider, g) is True, (
        "%s gate %s must pass over the graph built from the live-rendered "
        "template" % (provider, gate))
    # the generated graph must carry a realization with at least one resource
    reals = list(g.subjects(rdflib.RDF.type, F5EA.Realization))
    assert len(reals) == 1
    assert list(g.objects(reals[0], F5EA.hasResource)), (
        "%s: rendered-template graph has no resources" % provider)


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


# --- real bodies for every kind x provider -------------------------------
# A body is "real" (non-stub) when the resource carries at least one
# f5ea:hcl.* scalar, f5ea:references or f5ea:varReference triple derived
# from its actual rendered HCL -- not just the structural tfType/tfName
# (plus provider-wide) triples.

BODY_PREDICATES = {F5EA["hcl"], F5EA.references, F5EA.varReference}
# predicate namespace check: any IRI starting with ...#hcl.
_HCL_NS = str(F5EA) + "hcl."


def _has_real_body(g, r):
    for p in set(g.predicates(r, None)):
        ps = str(p)
        if ps.startswith(_HCL_NS) or p in (F5EA.references, F5EA.varReference):
            return True
    return False


@pytest.mark.parametrize("provider", ["aws", "gcp", "azure"])
def test_every_kind_has_real_body(provider):
    """No stub kinds: every resource from BOTH the static fixture and the
    live-rendered template carries a real HCL-derived body."""
    graphs = [build_graph(provider)[0],
              build_graph_from_rendered_template(provider)[0]]
    for g in graphs:
        resources = set(g.subjects(rdflib.RDF.type, F5EA.SbbResource))
        assert resources, "%s: no resources" % provider
        stubs = [r for r in resources if not _has_real_body(g, r)]
        assert not stubs, "%s stub-bodied resources: %s" % (provider, stubs)


# Per-kind assertions: the emitted predicates must match the real rendered
# attribute values, per provider. (pred, {expected objects}); kinds present
# only in the live-rendered template are covered by
# test_rendered_org_policy_bodies below.
KIND_SPECS = [
    # AWS
    ("aws", "aws_ssoadmin_permission_set", F5EA["hcl.session_duration"],
     {"PT1H"}, False),
    ("aws", "aws_vpc_endpoint", F5EA["hcl.vpc_endpoint_type"],
     {"Interface"}, False),
    ("aws", "aws_vpc_endpoint", F5EA["hcl.private_dns_enabled"],
     {"true"}, False),
    ("aws", "aws_cloudtrail_event_data_store", F5EA["hcl.retention_period"],
     {"3650"}, False),
    ("aws", "aws_cloudtrail_event_data_store",
     F5EA["hcl.termination_protection_enabled"], {"true"}, False),
    ("aws", "aws_ec2_transit_gateway_vpc_attachment", F5EA.references,
     {"aws_ec2_transit_gateway.sbb"}, False),
    ("aws", "aws_ssoadmin_managed_policy_attachment", F5EA.references,
     {"aws_ssoadmin_permission_set.sbb"}, False),
    ("aws", "aws_ssoadmin_managed_policy_attachment", F5EA.varReference,
     {"var.sso_managed_policy_arn"}, False),
    # GCP
    ("gcp", "google_compute_address", F5EA["hcl.address_type"],
     {"INTERNAL"}, False),
    ("gcp", "google_compute_forwarding_rule", F5EA.references,
     {"google_compute_address.psc_endpoint_ip",
      "google_compute_service_attachment.svc_att"}, False),
    ("gcp", "google_compute_service_attachment",
     F5EA["hcl.connection_preference"], {"ACCEPT_MANUAL"}, False),
    ("gcp", "google_kms_crypto_key", F5EA["hcl.purpose"],
     {"ENCRYPT_DECRYPT"}, False),
    ("gcp", "google_kms_crypto_key", F5EA["hcl.rotation_period"],
     {"7776000s"}, False),
    # Azure
    ("azure", "azurerm_management_group", F5EA["hcl.display_name"],
     {"finance-enclave-root", "finance-landing-zone", "finance-enclave"},
     False),
    ("azure", "azurerm_virtual_hub", F5EA.references,
     {"azurerm_virtual_wan.this", "azurerm_resource_group.connectivity"},
     False),
    ("azure", "azurerm_dedicated_hardware_security_module",
     F5EA.varReference, {"var.hsm_sku", "var.hsm_subnet_id"}, False),
    ("azure", "azurerm_subscription_policy_assignment", F5EA["hcl.name"],
     {"confidential-vm-dccv5-only"}, False),
]


@pytest.mark.parametrize(
    "provider,tf_type,pred,expected",
    [(s[0], s[1], s[2], s[3]) for s in KIND_SPECS])
def test_kind_bodies_carry_real_values(provider, tf_type, pred, expected):
    g, _ = build_graph(provider)
    resources = list(g.subjects(F5EA.tfType, rdflib.Literal(tf_type)))
    hits = set()
    for r in resources:
        hits |= {str(o) for o in g.objects(r, pred)}
    assert hits == expected, (
        "%s/%s: %s -> %s != %s" % (provider, tf_type, pred, hits, expected))


def test_rendered_org_policy_bodies():
    """org_policy_policy resources (live-render only) carry real parents."""
    g, _ = build_graph_from_rendered_template("gcp")
    policies = list(g.subjects(F5EA.tfType,
                               rdflib.Literal("google_org_policy_policy")))
    assert len(policies) == 3, policies
    parents = set()
    for p in policies:
        parents |= {str(o) for o in g.objects(p, F5EA["hcl.parent"])}
    assert parents == {"projects/proj-svc"}






def _violated(provider, extra_triples):
    """Build the good graph, inject violating triples, re-run the gate."""
    _, out = build_graph(provider)
    violated = out.with_name("violated_%s.ttl" % provider)
    violated.write_text(out.read_text() + extra_triples)
    bad = rdflib.Graph()
    bad.parse(violated, format="turtle")
    return run_gate(provider, bad)


def _mutated(provider, transform):
    """Build the good graph, transform its serialization, re-run the gate."""
    _, out = build_graph(provider)
    violated = out.with_name("violated_%s.ttl" % provider)
    violated.write_text(transform(out.read_text()))
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
    def drop_controls(text):
        kept = [ln for ln in text.splitlines()
                if not (ln.startswith(rg + " ") and "controlMapping" in ln)]
        return "\n".join(kept) + "\n"
    assert _mutated("azure", drop_controls) is False
