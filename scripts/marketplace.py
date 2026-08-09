#!/usr/bin/env python3
"""Local-first acceptance calculus for the ggen Marketplace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover - explicit runtime refusal
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED") from exc

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
GATE_SOURCE_SUFFIXES = frozenset({".rq", ".py"})
REQUIRED_DOCS = (
    "docs/index.md",
    "docs/tutorials/first-pack.md",
    "docs/tutorials/consume-a-pack.md",
    "docs/how-to/publish-a-pack.md",
    "docs/how-to/update-a-pack.md",
    "docs/how-to/validate-locally.md",
    "docs/how-to/consume-a-pack.md",
    "docs/how-to/migrate-a-pack.md",
    "docs/reference/repository-layout.md",
    "docs/reference/pack-contract.md",
    "docs/reference/catalog-command.md",
    "docs/reference/validation-contract.md",
    "docs/reference/provenance.md",
    "docs/reference/standing.md",
    "docs/explanation/why-a-separate-marketplace.md",
    "docs/explanation/source-of-truth.md",
    "docs/explanation/pack-lifecycle.md",
    "docs/explanation/security-and-authority.md",
)


@dataclass(frozen=True)
class Pack:
    name: str
    version: str
    description: str
    path: Path
    templates: tuple[Path, ...]
    native_gates: tuple[Path, ...]
    verifier_gates: tuple[Path, ...]

    def catalog_record(self) -> dict[str, Any]:
        manifest = self.path / "pack.toml"
        ontology = self.path / "ontology.ttl"
        return {
            "description": self.description,
            "manifest_sha256": sha256_file(manifest),
            "name": self.name,
            "native_gates": len(self.native_gates),
            "ontology_sha256": sha256_file(ontology),
            "path": self.path.relative_to(ROOT).as_posix(),
            "templates": len(self.templates),
            "verifier_gates": len(self.verifier_gates),
            "version": self.version,
        }


def refusal(code: str, detail: str) -> str:
    return f"REFUSED:{code}:{detail}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_marketplace() -> tuple[list[Pack], list[str]]:
    issues: list[str] = []
    packs: list[Pack] = []
    seen: set[str] = set()

    if not PACKS.is_dir():
        return [], [refusal("PACKS_DIRECTORY_MISSING", "packs")]

    for path in sorted(PACKS.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            issues.append(refusal("PACK_SYMLINK", path.relative_to(ROOT).as_posix()))

    directories = sorted((p for p in PACKS.iterdir() if p.is_dir()), key=lambda p: p.name)
    if not directories:
        issues.append(refusal("EMPTY_MARKETPLACE", "packs"))

    for directory in directories:
        manifest = directory / "pack.toml"
        ontology = directory / "ontology.ttl"
        templates_dir = directory / "templates"
        gates_dir = directory / "gates"

        document: dict[str, Any] | None = None
        if not manifest.is_file():
            issues.append(refusal("MANIFEST_MISSING", directory.name))
        else:
            try:
                parsed = tomllib.loads(manifest.read_text(encoding="utf-8"))
                if isinstance(parsed, dict):
                    document = parsed
            except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
                issues.append(refusal("MANIFEST_INVALID", f"{directory.name}:{exc}"))

        name: str | None = None
        version: str | None = None
        description: str | None = None
        if document is not None:
            if set(document) != {"pack"} or not isinstance(document.get("pack"), dict):
                issues.append(refusal("MANIFEST_SHAPE", directory.name))
            else:
                table = document["pack"]
                raw_name = table.get("name")
                raw_version = table.get("version")
                raw_description = table.get("description")

                if not isinstance(raw_name, str) or not raw_name.strip():
                    issues.append(refusal("PACK_NAME", directory.name))
                else:
                    name = raw_name
                    if name != directory.name:
                        issues.append(
                            refusal(
                                "PACK_DIRECTORY_IDENTITY",
                                f"directory={directory.name},name={name}",
                            )
                        )
                    if name in seen:
                        issues.append(refusal("DUPLICATE_PACK_NAME", name))
                    seen.add(name)

                if not isinstance(raw_version, str) or not SEMVER.fullmatch(raw_version):
                    issues.append(refusal("PACK_VERSION_SEMVER", f"{directory.name}:{raw_version!r}"))
                else:
                    version = raw_version

                if not isinstance(raw_description, str) or not raw_description.strip():
                    issues.append(refusal("PACK_DESCRIPTION", directory.name))
                else:
                    description = raw_description.strip()

        if not ontology.is_file():
            issues.append(refusal("ONTOLOGY_MISSING", directory.name))

        templates: tuple[Path, ...] = ()
        if not templates_dir.is_dir():
            issues.append(refusal("TEMPLATES_DIRECTORY_MISSING", directory.name))
        else:
            templates = tuple(
                sorted(
                    (p for p in templates_dir.rglob("*") if p.is_file()),
                    key=lambda p: p.relative_to(directory).as_posix(),
                )
            )
            if not templates:
                issues.append(refusal("TEMPLATE_MISSING", directory.name))
            for path in templates:
                if not path.name.endswith(".tmpl"):
                    issues.append(refusal("TEMPLATE_EXTENSION", path.relative_to(ROOT).as_posix()))

        native_gates: tuple[Path, ...] = ()
        verifier_gates: tuple[Path, ...] = ()
        if gates_dir.exists():
            if not gates_dir.is_dir():
                issues.append(refusal("GATES_NOT_DIRECTORY", directory.name))
            else:
                gate_sources = tuple(
                    sorted(
                        (p for p in gates_dir.rglob("*") if p.is_file()),
                        key=lambda p: p.relative_to(directory).as_posix(),
                    )
                )
                for path in gate_sources:
                    if path.suffix not in GATE_SOURCE_SUFFIXES:
                        issues.append(refusal("GATE_SOURCE_EXTENSION", path.relative_to(ROOT).as_posix()))
                native_gates = tuple(p for p in gate_sources if p.suffix == ".rq")
                verifier_gates = tuple(p for p in gate_sources if p.suffix == ".py")

        if name is not None and version is not None and description is not None and ontology.is_file() and templates:
            packs.append(
                Pack(
                    name,
                    version,
                    description,
                    directory,
                    templates,
                    native_gates,
                    verifier_gates,
                )
            )

    for relative in REQUIRED_DOCS:
        path = ROOT / relative
        if not path.is_file():
            issues.append(refusal("DIATAXIS_DOCUMENT_MISSING", relative))
            continue
        try:
            if not path.read_text(encoding="utf-8").strip():
                issues.append(refusal("DIATAXIS_DOCUMENT_EMPTY", relative))
        except (OSError, UnicodeError) as exc:
            issues.append(refusal("DIATAXIS_DOCUMENT_INVALID", f"{relative}:{exc}"))

    return packs, sorted(set(issues))


def require_admitted() -> list[Pack]:
    packs, issues = inspect_marketplace()
    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        raise SystemExit(2)
    return packs


def validate() -> int:
    packs = require_admitted()
    template_count = sum(len(pack.templates) for pack in packs)
    native_gate_count = sum(len(pack.native_gates) for pack in packs)
    verifier_gate_count = sum(len(pack.verifier_gates) for pack in packs)
    print(
        f"validated packs={len(packs)} manifests={len(packs)} templates={template_count} "
        f"native_gates={native_gate_count} verifier_gates={verifier_gate_count} "
        f"diataxis={len(REQUIRED_DOCS)}"
    )
    return 0


def catalog() -> int:
    packs = require_admitted()
    payload = {
        "schema": "https://ggen.dev/marketplace/catalog/v1",
        "packs": [pack.catalog_record() for pack in packs],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def fingerprint() -> int:
    require_admitted()
    digest = hashlib.sha256()
    files = sorted(
        (p for p in PACKS.rglob("*") if p.is_file()),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )
    for path in files:
        relative = path.relative_to(ROOT).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    print(f"sha256:{digest.hexdigest()} files={len(files)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "catalog", "fingerprint"))
    args = parser.parse_args()
    return {"validate": validate, "catalog": catalog, "fingerprint": fingerprint}[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
