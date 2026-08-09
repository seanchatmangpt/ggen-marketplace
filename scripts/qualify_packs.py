#!/usr/bin/env python3
"""Qualify every admitted marketplace pack through the real ggen runtime.

The court is filesystem-only: it never executes manufactured programs, cloud
APIs, pack-owned Python verifiers, or any BRCE DO surface. Each pack is loaded
through ggen twice in an isolated capsule and must converge to the same
non-runtime filesystem consequence within the five-second per-pass bound.

Pack-specific positive qualification data stays with the pack:

* ``qualification/consumer.ttl`` / ``qualification/consumer/*.ttl`` add
  synthetic consumer facts to projection/semantic qualification graphs;
* ``qualification/project/**`` overlays a temporary project-profile copy;
* ``qualification.toml`` may declare consumer-side extra ontologies that a
  real ggen pack reference must union into the selected pack graph.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from marketplace import Pack, fingerprint_paths, require_admitted

DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_WORKERS = 8
IGNORED_RUNTIME_ROOTS = frozenset(
    {".git", ".ggen", ".ggen-v2", ".cache", ".qualification-home", "target"}
)
FRONTMATTER_PROBE_TEMPLATE = """---
to: "qualification/marketplace-probe.txt"
sparql:
  row: |
    SELECT (COUNT(*) AS ?triple_count) WHERE { ?s ?p ?o }
---
{{ row[0].triple_count }}
"""
DECLARATIVE_PROBE_QUERY = "SELECT ?s WHERE { ?s ?p ?o } ORDER BY ?s LIMIT 1\n"
DECLARATIVE_PROBE_TEMPLATE = """{% for row in sparql_results %}loaded{% endfor %}
"""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class QualificationContractError(ValueError):
    """A pack-owned qualification contract is malformed or unsafe."""


def pack_source_fingerprint(pack: Pack) -> str:
    files = tuple(path for path in pack.path.rglob("*") if path.is_file())
    return fingerprint_paths(files, pack.path)


def snapshot_tree(root: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in IGNORED_RUNTIME_ROOTS:
            continue
        records.append((relative.as_posix(), hashlib.sha256(path.read_bytes()).hexdigest()))
    return tuple(records)


def snapshot_digest(records: tuple[tuple[str, str], ...]) -> str:
    h = hashlib.sha256()
    for path, digest in records:
        h.update(path.encode())
        h.update(b"\0")
        h.update(digest.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def terminate_process_group(process: subprocess.Popen[str]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=0.5)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=0.5)
    except subprocess.TimeoutExpired:
        pass


def run_bounded(command: list[str], cwd: Path, timeout_seconds: float) -> CommandResult:
    env = os.environ.copy()
    original_home = Path(env.get("HOME", str(Path.home())))
    home = cwd / ".qualification-home"
    home.mkdir(exist_ok=True)
    env.update(
        {
            "HOME": str(home),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".local" / "share"),
            # Isolate ordinary state without hiding the admitted runner toolchain.
            "RUSTUP_HOME": env.get("RUSTUP_HOME", str(original_home / ".rustup")),
            "CARGO_HOME": env.get("CARGO_HOME", str(original_home / ".cargo")),
        }
    )
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        terminate_process_group(process)
        stdout, stderr = process.communicate()
        return CommandResult(124, stdout, stderr, timed_out=True)
    return CommandResult(process.returncode, stdout, stderr)


def qualification_consumer_rdf(pack: Pack) -> tuple[Path, ...]:
    root = pack.path / "qualification"
    files: list[Path] = []
    single = root / "consumer.ttl"
    if single.is_file():
        files.append(single)
    directory = root / "consumer"
    if directory.is_dir():
        files.extend(sorted(directory.glob("*.ttl"), key=lambda item: item.name))
    return tuple(files)


def qualification_extra_ontologies(pack: Pack) -> tuple[Path, ...]:
    contract = pack.path / "qualification.toml"
    if not contract.is_file():
        return ()
    try:
        payload = tomllib.loads(contract.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise QualificationContractError(f"invalid qualification.toml: {error}") from error
    consumer = payload.get("consumer", {})
    if not isinstance(consumer, dict):
        raise QualificationContractError("qualification.toml [consumer] must be a table")
    raw = consumer.get("extra_ontologies", [])
    if not isinstance(raw, list) or not all(isinstance(item, str) and item for item in raw):
        raise QualificationContractError("consumer.extra_ontologies must be an array of non-empty strings")

    pack_root = pack.path.resolve()
    paths: list[Path] = []
    for item in raw:
        relative = Path(item)
        if relative.is_absolute() or ".." in relative.parts:
            raise QualificationContractError(f"unsafe extra ontology path: {item}")
        source = (pack.path / relative).resolve()
        try:
            source.relative_to(pack_root)
        except ValueError as error:
            raise QualificationContractError(f"extra ontology escapes pack: {item}") from error
        if not source.is_file():
            raise QualificationContractError(f"extra ontology does not exist: {item}")
        paths.append(source)
    return tuple(paths)


def combine_rdf(paths: tuple[Path, ...], extra: str = "") -> str:
    parts: list[str] = []
    for path in paths:
        parts.append(f"# ===== QUALIFICATION SOURCE: {path.as_posix()} =====\n")
        text = path.read_text(encoding="utf-8")
        parts.append(text)
        if not text.endswith("\n"):
            parts.append("\n")
        parts.append("\n")
    parts.append(extra)
    return "".join(parts)


def projection_ggen_toml(pack: Pack, extra_paths: tuple[str, ...]) -> str:
    pack_path = pack.path.resolve().as_posix().replace('"', '\\"')
    entry = f'"{pack.name}" = {{ path = "{pack_path}"'
    if extra_paths:
        entry += ", extra_ontologies = [" + ", ".join(json.dumps(path) for path in extra_paths) + "]"
    entry += " }"
    return "\n".join(
        (
            "[project]",
            f'name = "marketplace-qualification-{pack.name}"',
            "",
            "[ontology]",
            'source = "ontology.ttl"',
            "",
            "[packs]",
            entry,
            "",
            "[templates]",
            'dir = "templates"',
            "",
        )
    )


def semantic_ggen_toml(pack: Pack) -> str:
    lines = [
        "[project]",
        f'name = "marketplace-qualification-{pack.name}"',
        'version = "0.0.0"',
        "",
        "[ontology]",
        'source = "ontology.ttl"',
        "",
    ]
    if pack.native_gates:
        gates = ", ".join(json.dumps(path.resolve().as_posix()) for path in pack.native_gates)
        lines.extend(("[validation]", f"gates = [{gates}]", ""))
    lines.extend(
        (
            "[generation]",
            'output_dir = "qualification/"',
            "",
            "[[generation.rules]]",
            'name = "marketplace-qualification-probe"',
            'query = { file = "queries/qualification.rq" }',
            'template = { file = "templates/marketplace-probe.txt.tera" }',
            'output_file = "marketplace-probe.txt"',
            'mode = "Overwrite"',
            "",
            "[templates]",
            'dir = "templates"',
            "",
        )
    )
    return "\n".join(lines)


def write_projection_consumer(pack: Pack, consumer: Path) -> None:
    consumer.mkdir(parents=True)
    (consumer / "templates").mkdir()
    extras = qualification_extra_ontologies(pack)
    extra_names: list[str] = []
    if extras:
        extra_root = consumer / ".qualification-extra"
        extra_root.mkdir()
        for index, source in enumerate(extras):
            relative = f".qualification-extra/{index:03d}-{source.name}"
            shutil.copy2(source, consumer / relative)
            extra_names.append(relative)
    (consumer / "ggen.toml").write_text(projection_ggen_toml(pack, tuple(extra_names)), encoding="utf-8")
    (consumer / "ontology.ttl").write_text(
        combine_rdf(
            qualification_consumer_rdf(pack),
            "@prefix mq: <https://ggen.dev/marketplace/qualification#> .\n"
            f'mq:subject mq:packName "{pack.name}" .\n',
        ),
        encoding="utf-8",
    )
    (consumer / "templates" / "marketplace-probe.txt.tmpl").write_text(
        FRONTMATTER_PROBE_TEMPLATE, encoding="utf-8"
    )


def write_semantic_consumer(pack: Pack, consumer: Path) -> None:
    consumer.mkdir(parents=True)
    (consumer / "templates").mkdir()
    (consumer / "queries").mkdir()
    (consumer / "ggen.toml").write_text(semantic_ggen_toml(pack), encoding="utf-8")
    (consumer / "ontology.ttl").write_text(
        combine_rdf(
            pack.ontologies + qualification_consumer_rdf(pack),
            "@prefix mq: <https://ggen.dev/marketplace/qualification#> .\n"
            f'mq:subject mq:packName "{pack.name}" .\n',
        ),
        encoding="utf-8",
    )
    (consumer / "queries" / "qualification.rq").write_text(DECLARATIVE_PROBE_QUERY, encoding="utf-8")
    (consumer / "templates" / "marketplace-probe.txt.tera").write_text(
        DECLARATIVE_PROBE_TEMPLATE, encoding="utf-8"
    )


def overlay_project_qualification(pack: Pack, consumer: Path) -> None:
    overlay = pack.path / "qualification" / "project"
    if not overlay.is_dir():
        return
    for source in sorted((p for p in overlay.rglob("*") if p.is_file()), key=lambda item: item.as_posix()):
        destination = consumer / source.relative_to(overlay)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def prepare_consumer(pack: Pack, capsule: Path) -> Path:
    consumer = capsule / "consumer"
    if pack.profile == "project":
        shutil.copytree(pack.path, consumer)
        overlay_project_qualification(pack, consumer)
    elif pack.profile == "semantic":
        write_semantic_consumer(pack, consumer)
    else:
        write_projection_consumer(pack, consumer)
    return consumer


def compact_output(result: CommandResult) -> str:
    combined = "\n".join(part.strip() for part in (result.stderr, result.stdout) if part.strip())
    if len(combined) > 3000:
        combined = combined[-3000:]
    return combined.replace("\x00", "<NUL>")


def refusal(pack: Pack, code: str, detail: str) -> dict[str, Any]:
    return {
        "code": code,
        "detail": detail,
        "name": pack.name,
        "profile": pack.profile,
        "status": "REFUSED",
        "version": pack.version,
    }


def qualify_pack(pack: Pack, ggen_bin: str, timeout_seconds: float) -> dict[str, Any]:
    source_before = pack_source_fingerprint(pack)
    record: dict[str, Any]
    try:
        with tempfile.TemporaryDirectory(prefix=f"ggen-marketplace-{pack.name}-") as raw:
            consumer = prepare_consumer(pack, Path(raw))
            first = run_bounded([ggen_bin, "sync", "run"], consumer, timeout_seconds)
            if first.timed_out:
                record = refusal(pack, "REFUSED:GGEN_PACK_TIMEOUT", f"pass=1 timeout_seconds={timeout_seconds:g}")
            elif first.returncode != 0:
                record = refusal(
                    pack,
                    "REFUSED:GGEN_PACK_SYNC_FAILED",
                    f"pass=1 exit={first.returncode} output={compact_output(first)}",
                )
            else:
                snapshot_one = snapshot_tree(consumer)
                probe = consumer / "qualification" / "marketplace-probe.txt"
                if pack.profile != "project" and (not probe.is_file() or not probe.read_text(encoding="utf-8").strip()):
                    record = refusal(pack, "REFUSED:GGEN_PACK_PROBE_MISSING", probe.as_posix())
                else:
                    second = run_bounded([ggen_bin, "sync", "run"], consumer, timeout_seconds)
                    if second.timed_out:
                        record = refusal(pack, "REFUSED:GGEN_PACK_TIMEOUT", f"pass=2 timeout_seconds={timeout_seconds:g}")
                    elif second.returncode != 0:
                        record = refusal(
                            pack,
                            "REFUSED:GGEN_PACK_SYNC_FAILED",
                            f"pass=2 exit={second.returncode} output={compact_output(second)}",
                        )
                    else:
                        snapshot_two = snapshot_tree(consumer)
                        if snapshot_two != snapshot_one:
                            before, after = dict(snapshot_one), dict(snapshot_two)
                            changed = sorted(
                                path for path in set(before) | set(after) if before.get(path) != after.get(path)
                            )
                            record = refusal(
                                pack,
                                "REFUSED:GGEN_PACK_NONDETERMINISTIC_REPLAY",
                                "changed=" + ",".join(changed[:40]),
                            )
                        else:
                            record = {
                                "consequence_files": len(snapshot_two),
                                "consequence_sha256": snapshot_digest(snapshot_two),
                                "name": pack.name,
                                "profile": pack.profile,
                                "source_sha256": source_before,
                                "status": "ALIVE",
                                "version": pack.version,
                            }
    except QualificationContractError as error:
        record = refusal(pack, "REFUSED:QUALIFICATION_CONTRACT_INVALID", str(error))

    source_after = pack_source_fingerprint(pack)
    if source_after != source_before:
        return refusal(
            pack,
            "REFUSED:GGEN_PACK_SOURCE_MUTATED",
            f"before={source_before} after={source_after}",
        )
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ggen", default=os.environ.get("GGEN_BIN") or shutil.which("ggen"))
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    if not args.ggen:
        print("REFUSED:GGEN_BINARY_REQUIRED", file=sys.stderr)
        return 2
    if args.timeout_seconds <= 0 or args.timeout_seconds > 5:
        print("REFUSED:GGEN_PACK_TIMEOUT_BOUND:must_be_gt_0_and_lte_5", file=sys.stderr)
        return 2
    if args.workers <= 0 or args.workers > 16:
        print("REFUSED:GGEN_PACK_WORKER_BOUND:must_be_1_to_16", file=sys.stderr)
        return 2

    version = subprocess.run([args.ggen, "--version"], check=False, capture_output=True, text=True, timeout=5)
    if version.returncode != 0:
        print(f"REFUSED:GGEN_VERSION_FAILED:exit={version.returncode}", file=sys.stderr)
        return 2
    version_text = (version.stdout or version.stderr).strip()

    packs = require_admitted()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        records = list(
            executor.map(
                lambda pack: qualify_pack(pack, args.ggen, args.timeout_seconds),
                packs,
            )
        )
    records.sort(key=lambda item: item["name"])
    failures = [record for record in records if record["status"] != "ALIVE"]
    payload = {
        "ggen": version_text,
        "pack_count": len(records),
        "packs": records,
        "schema": "https://ggen.dev/marketplace/qualification/v1",
        "timeout_seconds": args.timeout_seconds,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        for record in failures:
            print(f"{record['code']}:{record['name']}:{record['detail']}", file=sys.stderr)
        print(f"REFUSED:GGEN_PACK_QUALIFICATION_FAILED:failed={len(failures)} total={len(records)}", file=sys.stderr)
        return 2

    profiles = {
        profile: sum(record["profile"] == profile for record in records)
        for profile in ("project", "projection", "semantic")
    }
    print(
        "qualified "
        f"packs={len(records)} profiles={json.dumps(profiles, sort_keys=True, separators=(',', ':'))} "
        f"ggen={json.dumps(version_text)} timeout_seconds={args.timeout_seconds:g}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
