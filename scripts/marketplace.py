#!/usr/bin/env python3
"""Local-first acceptance calculus for the ggen Marketplace."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import re
import subprocess
import sys
import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    import tomllib
except ModuleNotFoundError as exc:  # pragma: no cover
    raise SystemExit("REFUSED:PYTHON_3_11_REQUIRED") from exc

from marketplace_scope import select_packs
import marketplace_tiers

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
MARKETPLACE_TOML = ROOT / "marketplace.toml"
GITHUB_ORG = "seanchatmangpt"
GITHUB_REPO = "ggen-marketplace"
RELEASE_TAG = "packs"
SEMVER = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
TEMPLATE_SUFFIXES = (".tmpl", ".tera", ".eex")
GATE_SOURCE_SUFFIXES = frozenset({".rq", ".py"})
# Packs retired from normal marketplace discovery (docs/jira/v26.8.19/
# 01-TICKET-retire-clap-noun-verb-legacy.md). The directory and its content
# stay on disk for compatibility resolution by path-pinned consumers; only
# catalog-level discoverability changes. Value is the tuple of successor
# pack names that replace it.
DEPRECATED_PACKS: dict[str, tuple[str, ...]] = {
    "clap-noun-verb-pack": (
        "clap-noun-verb-schema-pack",
        "clap-noun-verb-crate-pack",
        "clap-noun-verb-routing-pack",
        "clap-noun-verb-behavior-pack",
        "clap-noun-verb-boundary-pack",
        "clap-noun-verb-verification-pack",
    ),
}
# Portfolio-role classification, orthogonal to Pack.profile's generation
# shape (docs/jira/v26.8.19/02-TICKET-pack-class-taxonomy.md). See
# docs/reference/pack-classes.md for the seven-class definitions. Optional/
# nullable: only packs whose file contents were actually checked in the
# source audit are seeded here — every other pack is deliberately
# unclassified (None) rather than guess-classified.
PACK_CLASSES: dict[str, str] = {
    "clap-noun-verb-pack": "CompatibilityPack",
    "clap-noun-verb-schema-pack": "ProfilePack",
    "clap-noun-verb-crate-pack": "ProfilePack",
    "clap-noun-verb-routing-pack": "ProfilePack",
    "clap-noun-verb-behavior-pack": "ProfilePack",
    "clap-noun-verb-boundary-pack": "ProfilePack",
    "clap-noun-verb-verification-pack": "ProfilePack",
    "pack-authoring-pack": "KernelPack",
    "pack-maturity-pack": "EvidencePack",
    "wasm4pm-pack": "CapabilityPack",
}
# The real ggen loader deserializes [pack] with deny-unknown-fields; anything else is
# refused at pack-load time, so refuse it here first (see CLAUDE.md, "Pack profiles").
PACK_TABLE_KEYS = frozenset({"name", "version", "description", "deprecated", "superseded_by"})
VERSION_TAG = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
REQUIRED_DOCS = (
    "docs/index.md",
    "docs/tutorials/first-pack.md",
    "docs/tutorials/consume-a-pack.md",
    "docs/how-to/publish-a-pack.md",
    "docs/how-to/update-a-pack.md",
    "docs/how-to/validate-locally.md",
    "docs/how-to/qualify-all-packs.md",
    "docs/how-to/consume-a-pack.md",
    "docs/how-to/migrate-a-pack.md",
    "docs/reference/repository-layout.md",
    "docs/reference/pack-contract.md",
    "docs/reference/catalog-command.md",
    "docs/reference/validation-contract.md",
    "docs/reference/ggen-qualification-contract.md",
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
    target_languages: tuple[str, ...] = ()

    @property
    def profile(self) -> str:
        if (self.path / "ggen.toml").is_file():
            return "project"
        if self.templates:
            return "projection"
        return "semantic"

    def catalog_record(self) -> dict[str, Any]:
        manifest = self.path / "pack.toml"
        archive = build_pack_archive(self)
        sig = marketplace_tiers.signals(self.path)
        life = marketplace_tiers.lifecycle(self.name, marketplace_tiers.manifest_pack_table(self.path), DEPRECATED_PACKS)
        record = {
            "deprecated": life["deprecated"],
            "description": self.description,
            "digest": f"sha256:{hashlib.sha256(archive).hexdigest()}",
            "download_url": (
                f"https://github.com/{GITHUB_ORG}/{GITHUB_REPO}/releases/"
                f"download/{RELEASE_TAG}/{self.name}-{self.version}.tar.gz"
            ),
            "manifest_sha256": sha256_file(manifest),
            "name": self.name,
            "native_gates": len(self.native_gates),
            "ontology_files": len(self.ontologies),
            "ontology_fingerprint_sha256": fingerprint_paths(self.ontologies, self.path),
            "pack_class": PACK_CLASSES.get(self.name),
            "path": self.path.relative_to(ROOT).as_posix(),
            "profile": self.profile,
            "size_bytes": len(archive),
            "readiness": sig,
            "status": life["status"],
            "successors": life["successors"],
            "target_languages": list(self.target_languages),
            "templates": len(self.templates),
            "tier": marketplace_tiers.tier(sig, marketplace_tiers.file_count(self.path)),
            "verifier_gates": len(self.verifier_gates),
            "version": self.version,
        }
        qualification = marketplace_tiers.load_baseline(ROOT).get(self.name)
        if qualification is not None:
            record["qualification"] = qualification
        return record


def marketplace_version() -> str:
    if not MARKETPLACE_TOML.is_file():
        raise SystemExit(refusal("MARKETPLACE_TOML_MISSING", "marketplace.toml"))
    try:
        document = tomllib.loads(MARKETPLACE_TOML.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise SystemExit(refusal("MARKETPLACE_TOML_INVALID", str(exc))) from exc
    table = document.get("marketplace")
    version = table.get("version") if isinstance(table, dict) else None
    if not isinstance(version, str) or not version.strip():
        raise SystemExit(refusal("MARKETPLACE_VERSION_MISSING", "marketplace.toml:[marketplace].version"))
    return version


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


def build_pack_archive(pack: Pack) -> bytes:
    tar_buf = io.BytesIO()
    with tarfile.open(fileobj=tar_buf, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for path in visible_files(pack.path):
            data = path.read_bytes()
            info = tarfile.TarInfo(name=f"{pack.name}/{path.relative_to(pack.path).as_posix()}")
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = 0
            info.gid = 0
            info.uname = ""
            info.gname = ""
            tar.addfile(info, io.BytesIO(data))
    gz_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode="wb", mtime=0, compresslevel=9) as gz:
        gz.write(tar_buf.getvalue())
    return gz_buf.getvalue()


def visible_files(directory: Path) -> tuple[Path, ...]:
    if not directory.is_dir():
        return ()
    return tuple(
        sorted(
            (
                path
                for path in directory.rglob("*")
                if path.is_file()
                and not any(
                    part.startswith(".") or part == "__pycache__"
                    for part in path.relative_to(directory).parts
                )
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

        target_languages: tuple[str, ...] = ()
        targets_path = directory / "targets.toml"
        if document is not None and "targets" in document:
            issues.append(refusal("TARGETS_IN_MANIFEST", f"{directory.name}:ggen-engine denies unknown pack.toml tables; use targets.toml"))
        elif targets_path.is_file():
            langs = None
            try:
                targets = tomllib.loads(targets_path.read_text(encoding="utf-8")).get("targets")
                langs = targets.get("languages") if isinstance(targets, dict) else None
            except (OSError, UnicodeError, tomllib.TOMLDecodeError):
                pass
            if (
                not isinstance(langs, list)
                or not langs
                or not all(isinstance(x, str) and re.fullmatch(r"[a-z][a-z0-9_+-]*", x) for x in langs)
                or len(set(langs)) != len(langs)
            ):
                issues.append(refusal("TARGETS_LANGUAGES", f"{directory.name}:{langs!r}"))
            else:
                target_languages = tuple(langs)

        name: str | None = None
        version: str | None = None
        description: str | None = None
        extra_pack_keys: tuple[str, ...] = ()
        if document is not None:
            table = document.get("pack")
            if not isinstance(table, dict):
                issues.append(refusal("MANIFEST_PACK_TABLE", directory.name))
            else:
                extra_pack_keys = tuple(sorted(set(table) - PACK_TABLE_KEYS))
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

        # Observed against ggen 26.9.28: the loader denies unknown [pack] keys for projection
        # packs (templates, no ggen.toml); project and semantic packs qualify ALIVE with them.
        if extra_pack_keys and templates and not (directory / "ggen.toml").is_file():
            issues.append(refusal("PACK_KEY_UNADMITTED", f"{directory.name}:[pack].{','.join(extra_pack_keys)}:ggen admits only {sorted(PACK_TABLE_KEYS)}"))

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
            packs.append(Pack(name, version, description, directory, ontologies, templates, native_gates, verifier_gates, target_languages))

    issues.extend(
        marketplace_tiers.lifecycle_issues(
            {d.name: marketplace_tiers.manifest_pack_table(d) for d in directories},
            (d.name for d in directories),
            refusal,
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


def scoped_packs(scope: str = "active") -> list[Pack]:
    try:
        return select_packs(require_admitted(), scope)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc


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


def catalog(scope: str = "active") -> int:
    packs = scoped_packs(scope)
    payload = {
        "schema": "https://ggen.dev/marketplace/catalog/v2",
        "marketplace_version": marketplace_version(),
        "scope": scope,
        "packs": [pack.catalog_record() for pack in packs],
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def search(terms: list[str], scope: str) -> int:
    if not terms:
        print(refusal("SEARCH_TERMS_MISSING", "search <terms...>"), file=sys.stderr)
        return 2
    records = [pack.catalog_record() for pack in scoped_packs(scope)]
    for record in marketplace_tiers.search(records, terms):
        print(f"{record['name']} {record['version']} {record['tier']} {record['status']}")
    return 0


def show(names: list[str], scope: str) -> int:
    if len(names) != 1:
        print(refusal("SHOW_PACK_ARGUMENT", "show <pack>"), file=sys.stderr)
        return 2
    match = [pack for pack in scoped_packs("all") if pack.name == names[0]]
    if not match:
        print(refusal("PACK_UNKNOWN", names[0]), file=sys.stderr)
        return 2
    json.dump(match[0].catalog_record(), sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


def browse() -> int:
    records = [pack.catalog_record() for pack in scoped_packs("all")]
    target = ROOT / marketplace_tiers.BROWSE_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(marketplace_tiers.browse_markdown(records), encoding="utf-8")
    print(f"wrote {marketplace_tiers.BROWSE_RELATIVE} packs={len(records)}")
    return 0


def archive(scope: str = "active") -> int:
    packs = scoped_packs(scope)
    out_dir = ROOT / "dist" / "packs"
    out_dir.mkdir(parents=True, exist_ok=True)
    for pack in packs:
        data = build_pack_archive(pack)
        (out_dir / f"{pack.name}-{pack.version}.tar.gz").write_bytes(data)
        print(f"{pack.name} {pack.version} sha256:{hashlib.sha256(data).hexdigest()}")
    return 0


def fingerprint() -> int:
    require_admitted()
    files = tuple(path for path in PACKS.rglob("*") if path.is_file())
    print(f"sha256:{fingerprint_paths(files, ROOT)} files={len(files)}")
    return 0


def version() -> int:
    print(marketplace_version())
    return 0


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(refusal("GIT_FAILED", f"git {' '.join(args)}: {result.stderr.strip()}"))
    return result.stdout


def release_tags() -> list[tuple[tuple[int, int, int], str]]:
    tags = []
    for tag in git("tag", "--list", "v*").split():
        match = VERSION_TAG.fullmatch(tag)
        if match:
            tags.append((tuple(int(part) for part in match.groups()), tag))
    return sorted(tags)


def diff_since(base_tag: str) -> dict[str, list[str]]:
    """Classify packs against a previous release by git tree identity (read-only)."""
    def pack_trees(ref: str) -> dict[str, str]:
        out = git("ls-tree", ref, "packs/")
        return {line.split("\t", 1)[1].removeprefix("packs/"): line.split()[2] for line in out.splitlines() if " tree " in line}

    def pack_version(ref: str, name: str) -> str | None:
        show = subprocess.run(["git", "show", f"{ref}:packs/{name}/pack.toml"], cwd=ROOT, capture_output=True, text=True, check=False)
        if show.returncode != 0:
            return None
        try:
            return tomllib.loads(show.stdout).get("pack", {}).get("version")
        except tomllib.TOMLDecodeError:
            return None

    old, new = pack_trees(base_tag), pack_trees("HEAD")
    report: dict[str, list[str]] = {"added": [], "removed": [], "changed": [], "unbumped": []}
    report["added"] = sorted(set(new) - set(old))
    report["removed"] = sorted(set(old) - set(new))
    for name in sorted(set(old) & set(new)):
        if old[name] != new[name]:
            report["changed"].append(name)
            if pack_version(base_tag, name) == pack_version("HEAD", name):
                report["unbumped"].append(name)
    return report


def diff(base_tag: str | None) -> int:
    require_admitted()
    if base_tag is None:
        tags = release_tags()
        if not tags:
            raise SystemExit(refusal("NO_RELEASE_TAG", "no v*.*.* tag to diff against"))
        base_tag = tags[-1][1]
    report = diff_since(base_tag)
    print(f"# packs since {base_tag}")
    for key in ("added", "removed", "changed", "unbumped"):
        print(f"{key}={len(report[key])}")
        for name in report[key]:
            print(f"  {name}")
    return 0


def release_check(allow_unbumped: bool) -> int:
    """Gate run immediately before an immutable release is cut."""
    require_admitted()
    current = marketplace_version()
    match = VERSION_TAG.fullmatch(current)
    if not match:
        raise SystemExit(refusal("RELEASE_VERSION_FORMAT", f"{current!r} is not vYY.M.P"))
    tags = release_tags()
    if current in {tag for _, tag in tags}:
        raise SystemExit(refusal("RELEASE_TAG_EXISTS", f"{current} already exists; releases are immutable, bump [marketplace].version"))
    key = tuple(int(part) for part in match.groups())
    if tags and key <= tags[-1][0]:
        raise SystemExit(refusal("RELEASE_VERSION_NOT_MONOTONIC", f"{current} <= latest tag {tags[-1][1]}"))
    if tags:
        report = diff_since(tags[-1][1])
        if report["unbumped"] and not allow_unbumped:
            raise SystemExit(refusal("CONTENT_CHANGED_WITHOUT_VERSION_BUMP", f"{len(report['unbumped'])} packs: {', '.join(report['unbumped'][:12])}"))
    print(f"release-check ok version={current} previous={tags[-1][1] if tags else 'none'}")
    return 0


def turtle_issues(packs: list[Pack]) -> list[str]:
    try:
        import logging

        import rdflib
    except ImportError:
        return [refusal("RDFLIB_REQUIRED", "pip install rdflib to run the Turtle syntax check")]
    logging.getLogger("rdflib").setLevel(logging.ERROR)
    issues = []
    for pack in packs:
        for path in sorted(pack.path.rglob("*.ttl")):
            try:
                rdflib.Graph().parse(path, format="turtle")
            except Exception as exc:  # rdflib raises several parser-specific types
                issues.append(refusal("TURTLE_SYNTAX", f"{path.relative_to(ROOT).as_posix()}:{str(exc).splitlines()[0][:120]}"))
    return issues


def check(names: list[str], qualify: bool) -> int:
    """Single-pack (or whole-corpus) preflight: validate + Turtle syntax + real-ggen qualification."""
    packs = require_admitted()
    if names:
        unknown = sorted(set(names) - {pack.name for pack in packs})
        if unknown:
            raise SystemExit(refusal("UNKNOWN_PACK", ", ".join(unknown)))
        packs = [pack for pack in packs if pack.name in names]
    issues = turtle_issues(packs)
    if qualify:
        sys.path.insert(0, str(ROOT / "scripts"))
        import shutil

        import qualify_packs

        ggen = shutil.which("ggen")
        if not ggen:
            issues.append(refusal("GGEN_BINARY_REQUIRED", "install ggen (scripts/install-ggen.sh) or pass --no-qualify"))
        else:
            for pack in packs:
                record = qualify_packs.qualify_pack(pack, ggen, 5.0)
                if record["status"] == "REFUSED":
                    issues.append(refusal("GGEN_QUALIFICATION", f"{pack.name}:{record['code']}:{record['detail'][-200:]!r}"))
    for issue in issues:
        print(issue, file=sys.stderr)
    if issues:
        return 2
    print(f"check ok packs={len(packs)} turtle=ok qualify={'ok' if qualify else 'skipped'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "catalog", "fingerprint", "archive", "version", "check", "diff", "release-check", "search", "show", "browse"))
    parser.add_argument("packs", nargs="*", help="check: pack names (default: all); diff: optional base tag")
    parser.add_argument("--scope", choices=("active", "all"), default="active")
    parser.add_argument("--no-qualify", action="store_true", help="check: skip the real-ggen qualification step")
    parser.add_argument("--allow-unbumped", action="store_true", help="release-check: tolerate changed packs whose version was not bumped")
    args = parser.parse_args()
    if args.command == "check":
        return check(args.packs, not args.no_qualify)
    if args.command == "diff":
        return diff(args.packs[0] if args.packs else None)
    if args.command == "release-check":
        return release_check(args.allow_unbumped)
    if args.command == "search":
        return search(args.packs, args.scope)
    if args.command == "show":
        return show(args.packs, args.scope)
    if args.command == "browse":
        return browse()
    if args.command == "catalog":
        return catalog(args.scope)
    if args.command == "archive":
        return archive(args.scope)
    return {
        "validate": validate,
        "fingerprint": fingerprint,
        "version": version,
    }[args.command]()


if __name__ == "__main__":
    raise SystemExit(main())
