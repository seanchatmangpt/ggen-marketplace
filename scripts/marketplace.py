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
from typing import Any, Iterable

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED") from exc

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
TEMPLATE_SUFFIXES = (".tmpl", ".tera")
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
    ontologies: tuple[Path, ...]
    templates: tuple[Path, ...]
    native_gates: tuple[Path, ...]
    verifier_gates: tuple[Path, ...]

    @property
    def profile(self) -> str:
        if (self.path / "ggen.toml").is_file():
            return "project"
        if self.templates:
            return "projection"
        return "semantic"

    def catalog_record(self) -> dict[str, Any]:
        manifest = self.path / "pack.toml"
        return {
            "description": self.description,
            "manifest_sha256": sha256_file(manifest),
            "name": self.name,
            "native_gates": len(self.native_gates),
            "ontology_files": len(self.ontologies),
            "ontology_fingerprint_sha256": fingerprint_paths(self.ontologies, self.path),
            "path": self.path.relative_to(ROOT).as_posix(),
            "profile": self.profile,
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


def fingerprint_paths(paths: Iterable[Path], base: Path) -> str:
    digest = hashlib.sha256()
    ordered = sorted(paths, key=lambda path: path.relative_to(base).as_posix())
    for path in ordered:
        relative = path.relative_to(base).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def visible_files(directory: Path) -> tuple[Path, ...]:
    if not directory.is_dir():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in directory.rglob("*")
                if path.is_file() and not any(part.startswith(".") for part in path.relative_to(directory).parts)
            ),
            key=lambda path: path.relative_to(directory).as_posix(),
        )
    )


def ontology_files(directory: Path) -> tuple[Path, ...]:
    candidates: set[Path] = set()
    for path in directory.glob("*.ttl"):
        if path.is_file():
            candidates.add(path)
    nested = directory / "ontology"
    if nested.is_dir():
        for path in nested.rglob("*.ttl"):
            if path.is_file():
                candidates.add(path)
    return tuple(sorted(candidates, key=lambda path: path.relative_to(directory).as_posix()))


def inspect_marketplace() -> tuple[list[Pack], list[str]]:
    issues: list[str] = []
    packs: list[Pack] = []
    seen: set[str] = set()

    if not PACKS.is_dir():
        return [], [refusal("PACKS_DIRECTORY_MISSING", "packs")]

    for path in sorted(PACKS.rglob("*"), key=lambda item: item.as_posix()):
        if path.is_symlink():
            issues.append(refusal("PACK_SYMLINK", path.relative_to(ROOT).as_posix()))

    directories = sorted((path for path in PACKS.iterdir() if path.is_dir()), key=lambda path: path.name)
    if not directories:
        issues.append(refusal("EMPTY_MARKETPLACE", "packs"))

    for directory in directories:
        manifest = directory / "pack.toml"
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
            table = document.get("pack")
            if not isinstance(table, dict):
                issues.append(refusal("MANIFEST_PACK_TABLE", directory.name))
            else:
                raw_name = table.get("name")
                raw_version = table.get("version")
                raw_description = table.get("description")
                if not isinstance(raw_name, str) or not raw_name.strip():
                    issues.append(refusal("PACK_NAME", directory.name))
                else:
                    name = raw_name
                    if name != directory.name:
                        issues.append(refusal("PACK_DIRECTORY_IDENTITY", f"directory={directory.name},name={name}"))
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

        ontologies = ontology_files(directory)
        if not ontologies:
            issues.append(refusal("ONTOLOGY_SOURCE_MISSING", directory.name))

        templates = visible_files(directory / "templates")
        for path in templates:
            if not path.name.endswith(TEMPLATE_SUFFIXES):
                issues.append(refusal("TEMPLATE_EXTENSION", path.relative_to(ROOT).as_posix()))

        native_gates: tuple[Path, ...] = ()
        verifier_gates: tuple[Path, ...] = ()
        gates_dir = directory / "gates"
        if gates_dir.exists():
            if not gates_dir.is_dir():
                issues.append(refusal("GATES_NOT_DIRECTORY", directory.name))
            else:
                gate_sources = visible_files(gates_dir)
                for path in gate_sources:
                    if path.suffix not in GATE_SOURCE_SUFFIXES:
                        issues.append(refusal("GATE_SOURCE_EXTENSION", path.relative_to(ROOT).as_posix()))
                native_gates = tuple(path for path in gate_sources if path.suffix == ".rq")
                verifier_gates = tuple(path for path in gate_sources if path.suffix == ".py")

        if name is not None and version is not None and description is not None and ontologies:
            packs.append(Pack(name, version, description, directory, ontologies, templates, native_gates, verifier_gates))

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
    profile_counts = {profile: sum(pack.profile == profile for pack in packs) for profile in ("projection", "semantic", "project")}
    print(
        f"validated packs={len(packs)} manifests={len(packs)} "
        f"ontologies={sum(len(pack.ontologies) for pack in packs)} "
        f"templates={sum(len(pack.templates) for pack in packs)} "
        f"native_gates={sum(len(pack.native_gates) for pack in packs)} "
        f"verifier_gates={sum(len(pack.verifier_gates) for pack in packs)} "
        f"profiles={json.dumps(profile_counts, sort_keys=True, separators=(',', ':'))} "
        f"diataxis={len(REQUIRED_DOCS)}"
    )
    return 0


def catalog() -> int:
    packs = require_admitted()
    payload = {"schema": "https://ggen.dev/marketplace/catalog/v1", "packs": [pack.catalog_record() for pack in packs]}
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def fingerprint() -> int:
    require_admitted()
    files = tuple(path for path in PACKS.rglob("*") if path.is_file())
    print(f"sha256:{fingerprint_paths(files, ROOT)} files={len(files)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "catalog", "fingerprint"))
    args = parser.parse_args()
    return {"validate": validate, "catalog": catalog, "fingerprint": fingerprint}[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
