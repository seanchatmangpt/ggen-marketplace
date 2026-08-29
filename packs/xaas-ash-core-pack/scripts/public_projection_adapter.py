from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

XAR_NS = "https://ggen.io/ontology/xaas-ash-render#"
PCC_NS = "https://seanchatmangpt.github.io/chatman-ecosystem/ontology/platform-console-capabilities#"


class AdmissionError(ValueError):
    pass


@dataclass(frozen=True, order=True)
class RenderTarget:
    capability: str
    module_name: str
    domain_module: str
    action_name: str

    def as_dict(self) -> dict[str, str]:
        return {
            "capability": self.capability,
            "module_name": self.module_name,
            "domain_module": self.domain_module,
            "action_name": self.action_name,
        }


_BLOCK = re.compile(
    r"(?ms)^xar:(?P<id>[A-Za-z0-9_]+)\s+a\s+xar:RenderTarget\s*;(?P<body>.*?)\.\s*$"
)
_FIELD = {
    "capability": re.compile(r"xar:renderOf\s+pcc:([A-Za-z0-9_]+)\s*;"),
    "module_name": re.compile(r'xar:moduleName\s+"([^"]+)"\s*;'),
    "domain_module": re.compile(r'xar:domainModule\s+"([^"]+)"\s*;'),
    "action_name": re.compile(r'xar:actionName\s+"([^"]+)"\s*;'),
}


def parse_legacy_render_hints(text: str) -> tuple[RenderTarget, ...]:
    targets: list[RenderTarget] = []
    seen_capabilities: set[str] = set()

    for match in _BLOCK.finditer(text):
        body = match.group("body") + ";"
        values: dict[str, str] = {}

        for name, pattern in _FIELD.items():
            found = pattern.findall(body)
            if len(found) != 1:
                raise AdmissionError(
                    f"REFUSED_RENDER_HINT_CARDINALITY:{match.group('id')}:{name}:{len(found)}"
                )
            values[name] = found[0]

        capability = PCC_NS + values["capability"]
        if capability in seen_capabilities:
            raise AdmissionError(f"REFUSED_DUPLICATE_CAPABILITY:{capability}")
        seen_capabilities.add(capability)

        targets.append(
            RenderTarget(
                capability=capability,
                module_name=values["module_name"],
                domain_module=values["domain_module"],
                action_name=values["action_name"],
            )
        )

    if not targets:
        raise AdmissionError("REFUSED_NO_RENDER_TARGETS")

    return tuple(sorted(targets))


def assert_public_semantic_graph(text: str) -> None:
    if XAR_NS in text or "xar:" in text:
        raise AdmissionError("REFUSED_PRIVATE_RENDER_VOCAB_IN_PUBLIC_GRAPH")


def build_manifest(text: str) -> dict[str, object]:
    targets = parse_legacy_render_hints(text)
    payload = {
        "schema": "ggen.xaas.render-manifest.v1",
        "authority": "CONSTRUCT_ONLY",
        "source_vocabulary": XAR_NS,
        "targets": [target.as_dict() for target in targets],
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {**payload, "receipt_sha256": hashlib.sha256(canonical).hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ontology", type=Path)
    parser.add_argument("--public-semantic-graph", type=Path)
    args = parser.parse_args()

    if args.public_semantic_graph:
        assert_public_semantic_graph(args.public_semantic_graph.read_text())

    manifest = build_manifest(args.ontology.read_text())
    print(json.dumps(manifest, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
