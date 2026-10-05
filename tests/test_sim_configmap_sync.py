"""Court: the gcp-marketplace-sim ConfigMap must not drift from server.py.

This manifest drifted once before (Lane 11 finding) and was hand-resynced
twice. This court makes that drift a loud, named failure instead.

Sync command on failure:

    python3 - <<'EOF'
    import yaml
    p = "k8s/gcp-marketplace-sim/gcp-procurement-simulator.yaml"
    docs = list(yaml.safe_load_all(open(p)))
    for d in docs:
        if d.get("kind") == "ConfigMap" and d["metadata"]["name"] == "gcp-procurement-simulator-code":
            d["data"]["server.py"] = open("k8s/gcp-marketplace-sim/server.py").read()
    with open(p, "w") as f:
        yaml.safe_dump_all(docs, f, sort_keys=False, width=10**6)
    EOF

(Or re-run the repo's ConfigMap resync flow; do NOT hand-patch the yaml.)
"""

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "k8s" / "gcp-marketplace-sim" / "gcp-procurement-simulator.yaml"
SERVER = REPO / "k8s" / "gcp-marketplace-sim" / "server.py"
CONFIGMAP_NAME = "gcp-procurement-simulator-code"

REQUIRED_ENV_VARS = ("AAIF_SIM_PORT", "AAIF_SIM_DISCOVERY_DIR")


def _docs():
    return list(yaml.safe_load_all(MANIFEST.read_text()))


def _inline_server_py():
    matches = [
        d
        for d in _docs()
        if d.get("kind") == "ConfigMap"
        and d["metadata"]["name"] == CONFIGMAP_NAME
        and "server.py" in d.get("data", {})
    ]
    assert matches, (
        f"No ConfigMap {CONFIGMAP_NAME!r} with a server.py data key in {MANIFEST}. "
        f"Sync command: copy k8s/gcp-marketplace-sim/server.py into the "
        f"ConfigMap data field (see module docstring)."
    )
    return matches[0]["data"]["server.py"]


def _normalize(text: str) -> str:
    # YAML block scalars legitimately strip per-line trailing whitespace.
    # Normalize both sides identically and separately assert the strip is
    # symmetric (so a one-sided strip can never mask a real difference).
    return "\n".join(line.rstrip() for line in text.splitlines())


def test_configmap_server_py_matches_disk():
    inline = _inline_server_py()
    disk = SERVER.read_text()
    if inline == disk:
        return  # exact bytes, no normalization needed
    norm_inline, norm_disk = _normalize(inline), _normalize(disk)
    assert norm_inline == norm_disk, (
        f"ConfigMap {CONFIGMAP_NAME}.data['server.py'] drifted from "
        f"k8s/gcp-marketplace-sim/server.py. "
        f"Sync command: copy k8s/gcp-marketplace-sim/server.py into the "
        f"ConfigMap data field (see module docstring)."
    )
    # Symmetry: the normalization itself must account for the ENTIRE
    # difference, i.e. each side is a pure trailing-whitespace strip of the
    # other. Otherwise normalization is hiding a real content difference.
    assert norm_inline == inline, (
        "inline ConfigMap copy carries non-trailing-whitespace differences "
        "masked by normalization"
    )
    assert norm_disk == disk, (
        "on-disk server.py carries non-trailing-whitespace differences "
        "masked by normalization"
    )


def test_deployment_sets_aaif_sim_env_explicitly():
    deployments = [d for d in _docs() if d.get("kind") == "Deployment"]
    assert deployments, (
        f"No Deployment found in {MANIFEST} (kinds present: "
        f"{[d.get('kind') for d in _docs()]}). "
        "The sim must be deployed via a Deployment whose container env "
        "sets AAIF_SIM_PORT and AAIF_SIM_DISCOVERY_DIR explicitly."
    )
    env_names: set[str] = set()
    for dep in deployments:
        containers = dep["spec"]["template"]["spec"].get("containers", [])
        for c in containers:
            for e in c.get("env", []) or []:
                env_names.add(e["name"])
    missing = [v for v in REQUIRED_ENV_VARS if v not in env_names]
    assert not missing, (
        f"Deployment(s) in {MANIFEST} do not set {missing} explicitly in "
        f"container env (found: {sorted(env_names)})."
    )
