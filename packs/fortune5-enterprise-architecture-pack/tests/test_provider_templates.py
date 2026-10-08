"""Provider skeleton validation for fortune5-enterprise-architecture-pack.

Renders the three provider skeletons (aws/gcp/azure sbb.tf.tera) with fixture
contexts and asserts the pack's provider laws:

  AWS   -- zero-wildcard IAM law: no "*" in any IAM action string; explicit region.
  GCP   -- CMEK: google_kms_crypto_key resources reference the key ring; no public IP.
  Azure -- confidential-computing stanza present; NIST-readiness annotation present.

Rendering uses a purpose-built mini-Tera evaluator covering exactly the
constructs these templates use ({% set %} with dict literals, {% for %},
{% if %}, {{ expr }} with the replace filter) -- the real Tera engine lives in
ggen (Rust); here we re-execute the same template logic over the actual
template text so the closed action maps / CMEK loop are exercised, not
re-described. Rendered AWS/GCP bodies are additionally parsed with
python-hcl2 as an independent structural gate.

Chicago discipline: real files on disk, real renderer, real HCL parse; no mocks.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

PACK = Path(__file__).resolve().parents[1]
TEMPLATES = PACK / "templates"

AWS = TEMPLATES / "aws-sbb.tf.tera"
GCP = TEMPLATES / "gcp-sbb.tf.tera"
AZURE = TEMPLATES / "azure-sbb.tf.tera"

# ---------------------------------------------------------------------------
# mini-Tera renderer
# ---------------------------------------------------------------------------

TAG = re.compile(r"\{[{%].*?[%}]\}", re.DOTALL)


def _split_tags(text: str):
    """Yield ("text"|"tag", content) chunks in order."""
    pos = 0
    for m in TAG.finditer(text):
        if m.start() > pos:
            yield "text", text[pos : m.start()]
        raw = m.group(0)
        content = raw[2:-2].strip()
        if content.startswith("-"):
            content = content[1:].lstrip()
        if content.endswith("-"):
            content = content[:-1].rstrip()
        yield "tag", content
        pos = m.end()
    if pos < len(text):
        yield "text", text[pos:]


class _Break(Exception):
    pass


def _eval(expr: str, ctx: dict):
    expr = expr.strip()
    # filters: var | replace(from="a", to="b")
    parts = [p.strip() for p in expr.split("|")]
    val = _eval_base(parts[0], ctx)
    for f in parts[1:]:
        m = re.fullmatch(r"replace\(from=\"(.*)\", to=\"(.*)\"\)", f)
        if m:
            val = str(val).replace(m.group(1), m.group(2))
        else:
            raise AssertionError(f"unsupported filter: {f}")
    return val


def _eval_base(expr: str, ctx: dict):
    m = re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z0-9_]+)*", expr)
    if m:
        val = ctx
        for part in expr.split("."):
            val = val[part]
        return val
    return ast.literal_eval(expr)


def parse_nodes(text: str):
    """Parse tag text into a node tree: ("text", s) | ("emit", expr) |
    ("set", name, expr) | ("for", heads, iterable, children) |
    ("if", cond, truthy, falsy)."""
    root: list = []
    stack = [root]
    for kind, content in _split_tags(text):
        if kind == "text":
            stack[-1].append(("text", content))
            continue
        kw = content.split(None, 1)[0] if content else ""
        if kw not in {"set", "for", "if", "else", "endif", "endfor"}:
            stack[-1].append(("emit", content))
            continue
        if kw == "set":
            if "=" not in content:  # e.g. literal "{% set %}" inside a comment
                stack[-1].append(("text", ""))
                continue
            name, expr = content[3:].split("=", 1)
            stack[-1].append(("set", name.strip(), expr.strip()))
        elif kw == "for":
            heads, iterable = content[3:].split(" in ", 1)
            node = ("for", heads.strip(), iterable.strip(), [])
            stack[-1].append(node)
            stack.append(node[3])
        elif kw == "if":
            node = ("if", content[2:].strip(), [], [])
            stack[-1].append(node)
            stack.append(node[2])
        elif kw == "else":
            if_node = stack[-2][-1]
            stack[-1] = if_node[3]
        elif kw in ("endif", "endfor"):
            stack.pop()
    if len(stack) != 1:
        raise AssertionError("unbalanced template tags")
    return root


def _render_nodes(nodes, ctx: dict, out: list):
    for node in nodes:
        kind = node[0]
        if kind == "text":
            out.append(node[1])
        elif kind == "emit":
            out.append(str(_eval(node[1], ctx)))
        elif kind == "set":
            expr = node[2]
            for name, val in ctx.items():
                expr = re.sub(
                    rf"\b{re.escape(name)}\b", repr(val), expr
                )
            ctx[node[1]] = ast.literal_eval(expr)
        elif kind == "for":
            _, heads, iterable, children = node
            seq = _eval(iterable, ctx)
            if isinstance(seq, dict) and "," in heads:
                items, names = list(seq.items()), [h.strip() for h in heads.split(",")]
            else:
                items, names = [(None, x) for x in seq], [heads]
            for a, b in items:
                local = dict(ctx)
                local[names[0]] = a if a is not None else b
                if a is not None:
                    local[names[1]] = b
                _render_nodes(children, local, out)
        elif kind == "if":
            _, cond, truthy, falsy = node
            _render_nodes(truthy if _eval_cond(cond, ctx) else falsy, ctx, out)


def render(text: str, ctx: dict) -> str:
    """Evaluate the subset of Tera used by the provider skeletons."""
    if text.startswith("---"):
        text = text.split("---", 2)[2]
    text = re.sub(r"\{#.*?#\}", "", text, flags=re.DOTALL)  # Tera comments
    out: list[str] = []
    _render_nodes(parse_nodes(text), ctx, out)
    return "".join(out)


def _eval_cond(cond: str, ctx: dict) -> bool:
    m = re.fullmatch(r"(.+?)\s*==\s*(.+)", cond)
    if m:
        return _eval(m.group(1), ctx) == _eval(m.group(2), ctx)
    return bool(_eval(cond, ctx))


# ---------------------------------------------------------------------------
# fixture contexts (mirror the frontmatter SPARQL SELECT projections)
# ---------------------------------------------------------------------------

AWS_CTX = {
    "row": {
        "sbbSlug": "test-sbb",
        "sbbDomain": "test-domain",
        "region": "us-gov-west-1",
        "providerVariant": "aws",
        "exactSubject": "https://ggen.io/ontology/f5ea#test-sbb",
    },
    "var": {},  # placeholder vars referenced as var.x are TF-side, not Tera
}

GCP_CTX = {
    "row": {
        "sbbId": "test-gcp-sbb",
        "fleetHostProject": "proj-fleet",
        "serviceProject": "proj-svc",
        "subnetSelfLink": "projects/proj-fleet/regions/us-west1/subnetworks/sbb",
        "pscSubnet": "projects/proj-fleet/regions/us-west1/subnetworks/psc",
        "orgId": "123456789",
        "keyringLocation": "us-west1",
    },
    "kmembers": [
        {"sbbId": "test-gcp-sbb", "kmsOrder": 1, "keyName": "sbb-workload-key", "keyPurpose": "ENCRYPT_DECRYPT"},
        {"sbbId": "test-gcp-sbb", "kmsOrder": 2, "keyName": "sbb-audit-key", "keyPurpose": "ENCRYPT_DECRYPT"},
        {"sbbId": "other-sbb", "kmsOrder": 3, "keyName": "foreign-key", "keyPurpose": "ENCRYPT_DECRYPT"},
    ],
}

AZURE_CTX = {
    "sbb": {
        "sbbSlug": "test-azure-sbb",
        "sbbDomain": "test-domain",
        "managementGroupId": "mg-test",
        "vwanId": "vwan-test",
        "region": "usgovvirginia",
    },
    "guest_config_assignments": [
        {"assignmentName": "assign-nist", "initiativeName": "nist-initiative"}
    ],
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        return text.split("---", 2)[2]
    return text


def assert_balanced_braces(text: str, label: str):
    """Structural minimum: { } and [ ] counts balance in the rendered HCL."""
    for open_c, close_c in (("{", "}"), ("[", "]")):
        assert text.count(open_c) == text.count(close_c), (
            f"{label}: unbalanced {open_c}{close_c} "
            f"({text.count(open_c)} vs {text.count(close_c)})"
        )


def parse_hcl(text: str, label: str) -> dict:
    import hcl2

    return hcl2.loads(text)


# ---------------------------------------------------------------------------
# structural checks (all three providers)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("tpl", [AWS, GCP, AZURE], ids=lambda p: p.name)
def test_template_exists_and_nonempty(tpl: Path):
    assert tpl.is_file() and tpl.stat().st_size > 0


def test_aws_render_balanced_and_hcl_parseable():
    rendered = render(AWS.read_text(), dict(AWS_CTX))
    assert_balanced_braces(rendered, "aws")
    doc = parse_hcl(rendered, "aws")
    assert any('"aws"' in blk for blk in doc.get("provider", [])), (
        "aws: no aws provider block parsed"
    )
    assert "resource" in doc and doc["resource"], "aws: no resources rendered"


def test_gcp_render_balanced_and_hcl_parseable():
    rendered = render(GCP.read_text(), dict(GCP_CTX))
    assert_balanced_braces(rendered, "gcp")
    doc = parse_hcl(rendered, "gcp")
    assert doc.get("resource"), "gcp: no resources rendered"


def test_azure_render_balanced_and_hcl_parseable():
    rendered = render(AZURE.read_text(), dict(AZURE_CTX))
    assert_balanced_braces(rendered, "azure")
    doc = parse_hcl(rendered, "azure")
    assert doc.get("resource"), "azure: no resources rendered"


# ---------------------------------------------------------------------------
# AWS: zero-wildcard IAM law + explicit region
# ---------------------------------------------------------------------------


def test_aws_no_wildcard_in_iam_action_strings():
    rendered = render(AWS.read_text(), dict(AWS_CTX))
    # every Action entry is rendered as one quoted string per line
    actions = re.findall(r"Action\s*=\s*\[(.*?)\]", rendered, re.DOTALL)
    assert actions, "aws: no Action lists rendered"
    for block in actions:
        entries = re.findall(r'"([^"]*)"', block)
        assert entries, f"aws: empty Action list: {block!r}"
        for entry in entries:
            assert "*" not in entry, (
                f"aws: wildcard in IAM action entry {entry!r} (zero-wildcard law)"
            )


def test_aws_closed_action_maps_contain_no_wildcard():
    """The {% set %} closed maps themselves (source of every action)."""
    src = strip_frontmatter(AWS.read_text())
    for m in re.finditer(r"\{%- set (\w+) = (\{.*?\}) -%\}", src, re.DOTALL):
        mapping = ast.literal_eval(m.group(2))
        for ns, acts in mapping.items():
            assert isinstance(acts, list) and acts, f"aws: empty map {ns}"
            for a in acts:
                assert "*" not in a, f"aws: wildcard in closed map {ns}: {a!r}"


def test_aws_explicit_region():
    rendered = render(AWS.read_text(), dict(AWS_CTX))
    m = re.search(r'provider\s+"aws"\s*\{(.*?)\}', rendered, re.DOTALL)
    assert m, "aws: no aws provider block"
    assert re.search(r'region\s*=\s*"\S+"', m.group(1)), (
        "aws: provider block lacks explicit region"
    )
    assert 'region = "us-gov-west-1"' in rendered


# ---------------------------------------------------------------------------
# GCP: CMEK + no public IP
# ---------------------------------------------------------------------------


def test_gcp_cmek_crypto_keys_present_and_reference_keyring():
    rendered = render(GCP.read_text(), dict(GCP_CTX))
    keys = re.findall(
        r'resource\s+"google_kms_crypto_key"\s+"(\w+)"\s*\{(.*?)\}',
        rendered,
        re.DOTALL,
    )
    assert keys, "gcp: no CMEK crypto_key resources rendered"
    assert len(keys) == 2, f"gcp: expected 2 CMEK keys for fixture, got {len(keys)}"
    for name, body in keys:
        assert re.search(r"key_ring\s*=\s*google_kms_key_ring\.keyring\.id", body), (
            f"gcp: crypto_key {name} does not reference the key ring"
        )
        assert re.search(r'rotation_period\s*=\s*"7776000s"', body), (
            f"gcp: crypto_key {name} missing 90-day rotation"
        )
    # fixture scoping: only this SBB's members render
    assert "foreign_key" not in rendered, "gcp: cross-SBB key member leaked in"


def test_gcp_no_public_ip():
    rendered = render(GCP.read_text(), dict(GCP_CTX))
    # PSC endpoint address is INTERNAL
    m = re.search(
        r'resource\s+"google_compute_address"\s+"psc_endpoint_ip"\s*\{(.*?)\}',
        rendered,
        re.DOTALL,
    )
    assert m, "gcp: no PSC endpoint address"
    assert 'address_type = "INTERNAL"' in m.group(1)
    # org policy denies external IPs outright
    m = re.search(
        r'resource\s+"google_org_policy_policy"\s+"no_public_ip"\s*\{(.*?)\n\}',
        rendered,
        re.DOTALL,
    )
    assert m, "gcp: no compute.vmExternalIpAccess deny policy"
    assert "compute.vmExternalIpAccess" in m.group(1)
    assert re.search(r"deny_all\s*=\s*\"TRUE\"", m.group(1))
    # no external forwarding scheme anywhere
    assert "EXTERNAL" not in rendered, "gcp: EXTERNAL scheme/address present"


# ---------------------------------------------------------------------------
# Azure: confidential computing stanza + NIST-readiness annotation
# ---------------------------------------------------------------------------


def test_azure_confidential_computing_stanza():
    rendered = render(AZURE.read_text(), dict(AZURE_CTX))
    assert "confidential-vm-dccv5-only" in rendered, (
        "azure: no confidential computing policy assignment"
    )
    m = re.search(
        r'resource\s+"azurerm_subscription_policy_assignment"\s+"confidential_vm"\s*\{(.*?)\n\}',
        rendered,
        re.DOTALL,
    )
    assert m, "azure: confidential_vm resource missing"
    assert "Standard_DC" in m.group(1), "azure: no DC-series (confidential) SKUs"


def test_azure_nist_readiness_annotation():
    src = strip_frontmatter(AZURE.read_text())
    assert re.search(r"NIST[- ]?800[- ]?53", src, re.IGNORECASE), (
        "azure: missing NIST 800-53 readiness annotation"
    )
    # control mappings annotated at the confidential-computing gate
    assert re.search(r"SC-28", src) and re.search(r"CM-6", src), (
        "azure: missing NIST control mappings at the confidential-computing gate"
    )
