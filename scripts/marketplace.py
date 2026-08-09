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


class Refusal(RuntimeError):
    pass


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


def refuse(code: str, detail: str) -> None:
    raise Refusal(f"REFUSED:{code}:{detail}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_symlinks() -> None:
    if not PACKS.is_dir():
        refuse("PACKS_DIRECTORY_MISSING", "packs")
    for path in sorted(PACKS.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            refuse("PACK_SYMLINK", path.relative_to(ROOT).as_posix())


def load_packs() -> list[Pack]:
    reject_symlinks()
    directories = sorted((p for p in PACKS.iterdir() if p.is_dir()), key=lambda p: p.name)
    if not directories:
        refuse("EMPTY_MARKETPLACE", "packs")

    packs: list[Pack] = []
    seen: set[str] = set()
    for directory in directories:
        manifest = directory / "pack.toml"
        ontology = directory / "ontology.ttl"
        templates_dir = directory / "templates"
        gates_dir = directory / "gates"

        if not manifest.is_file():
            refuse("MANIFEST_MISSING", directory.name)
        try:
            document = tomllib.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            refuse("MANIFEST_INVALID", f"{directory.name}:{exc}")

        if set(document) != {"pack"} or not isinstance(document.get("pack"), dict):
            refuse("MANIFEST_SHAPE", directory.name)
        table = document["pack"]
        name = table.get("name")
        version = table.get("version")
        description = table.get("description")
        if not isinstance(name, str) or not name.strip():
            refuse("PACK_NAME", directory.name)
        if name != directory.name:
            refuse("PACK_DIRECTORY_IDENTITY", f"directory={directory.name},name={name}")
        if name in seen:
            refuse("DUPLICATE_PACK_NAME", name)
        seen.add(name)
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            refuse("PACK_VERSION_SEMVER", f"{name}:{version!r}")
        if not isinstance(description, str) or not description.strip():
            refuse("PACK_DESCRIPTION", name)
        if not ontology.is_file():
            refuse("ONTOLOGY_MISSING", name)
        if not templates_dir.is_dir():
            refuse("TEMPLATES_DIRECTORY_MISSING", name)
        templates = tuple(
            sorted(
                (p for p in templates_dir.rglob("*") if p.is_file()),
                key=lambda p: p.relative_to(directory).as_posix(),
            )
        )
        if not templates:
            refuse("TEMPLATE_MISSING", name)
        invalid_templates = [p for p in templates if not p.name.endswith(".tmpl")]
        if invalid_templates:
            refuse("TEMPLATE_EXTENSION", invalid_templates[0].relative_to(ROOT).as_posix())

        native_gates: tuple[Path, ...] = ()
        verifier_gates: tuple[Path, ...] = ()
        if gates_dir.exists():
            if not gates_dir.is_dir():
                refuse("GATES_NOT_DIRECTORY", name)
            gate_sources = tuple(
                sorted(
                    (p for p in gates_dir.rglob("*") if p.is_file()),
                    key=lambda p: p.relative_to(directory).as_posix(),
                )
            )
            invalid_gates = [p for p in gate_sources if p.suffix not in GATE_SOURCE_SUFFIXES]
            if invalid_gates:
                refuse("GATE_SOURCE_EXTENSION", invalid_gates[0].relative_to(ROOT).as_posix())
            native_gates = tuple(p for p in gate_sources if p.suffix == ".rq")
            verifier_gates = tuple(p for p in gate_sources if p.suffix == ".py")

        packs.append(
            Pack(
                name,
                version,
                description.strip(),
                directory,
                templates,
                native_gates,
                verifier_gates,
            )
        )
    return packs


def validate_docs() -> None:
    for relative in REQUIRED_DOCS:
        path = ROOT / relative
        if not path.is_file() or not path.read_text(encoding="utf-8").strip():
            refuse("DIATAXIS_DOCUMENT_MISSING", relative)


def validate() -> int:
    packs = load_packs()
    validate_docs()
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
    packs = load_packs()
    payload = {
        "schema": "https://ggen.dev/marketplace/catalog/v1",
        "packs": [pack.catalog_record() for pack in packs],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def fingerprint() -> int:
    load_packs()  # fingerprint only admitted structure
    digest = hashlib.sha256()
    files = sorted((p for p in PACKS.rglob("*") if p.is_file()), key=lambda p: p.relative_to(ROOT).as_posix())
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
    try:
        return {"validate": validate, "catalog": catalog, "fingerprint": fingerprint}[args.command]()
    except Refusal as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
