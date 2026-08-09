#!/usr/bin/env python3
"""Qualify every admitted marketplace pack through the real ggen runtime.

This court is deliberately filesystem-only. It does not execute manufactured
artifacts, pack-owned Python verifier gates, cloud APIs, or other external DO
surfaces. Each pack is given an isolated consumer capsule, manufactured twice,
and required to reach a byte-stable consequence within a bounded time.

A pack that needs positive consumer facts owns them under ``qualification/``:

* ``qualification/consumer.ttl`` or ``qualification/consumer/*.ttl`` augments
  the isolated consumer graph for projection packs;
* ``qualification/project/**`` overlays a temporary project-profile copy
  before ggen executes (for example ``qualification/project/input.ttl``).

Semantic-only packs are qualified as RDF+gate capabilities rather than being
misrepresented as template packs: their ontology files are loaded directly
into a throwaway ggen project and their native SPARQL gates are attached to
that project.
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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from marketplace import Pack, fingerprint_paths, require_admitted

DEFAULT_TIMEOUT_SECONDS = 5.0
DEFAULT_WORKERS = 8
IGNORED_RUNTIME_ROOTS = frozenset({".git", ".ggen", ".ggen-v2", ".cache", "target"})
PROBE_TEMPLATE = """---
to: "qualification/marketplace-probe.txt"
sparql:
  row: |
    SELECT (COUNT(*) AS ?triple_count) WHERE { ?s ?p ?o }
---
{{ row[0].triple_count }}
"""


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def pack_source_fingerprint(pack: Pack) -> str:
    files = tuple(path for path in pack.path.rglob("*") if path.is_file())
    return fingerprint_paths(files, pack.path)


def snapshot_tree(root: Path) -> tuple[tuple[str, str], ...]:
    records: list[tuple[str, str]] = []
    for path in sorted((p for p in root.rglob("*") if p.is_file()), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if relative.parts and relative.parts[0] in IGNORED_RUNTIME_ROOTS:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        records.append((relative.as_posix(), digest))
    return tuple(records)


def snapshot_digest(records: tuple[tuple[str, str], ...]) -> str:
    h = hashlib.sha256()
    for path, digest in records:
        h.update(path.encode("utf-8"))
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
    original_home = env.get("HOME", str(Path.home()))
    home = cwd / ".qualification-home"
    home.mkdir(exist_ok=True)
    env.update(
        {
            "HOME": str(home),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_DATA_HOME": str(home / ".local" / "share"),
            "RUSTUP_HOME": env.get("RUSTUP_HOME", str(Path(original_home) / ".rustup")),
            "CARGO_HOME": env.get("CARGO_HOME", str(Path(original_home) / ".cargo")),
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
    qualification = pack.path / "qualification"
    files: list[Path] = []
    single = qualification / "consumer.ttl"
    if single.is_file():
        files.append(single)
    directory = qualification / "consumer"
    if directory.is_dir():
        files.extend(sorted(directory.glob("*.ttl"), key=lambda item: item.name))
    return tuple(files)


def combine_rdf(paths: tuple[Path, ...], extra: str = "") -> str:
    parts: list[str] = []
    for path in paths:
        parts.append(f"# ===== QUALIFICATION SOURCE: {path.as_posix()} =====\n")
        parts.append(path.read_text(encoding="utf-8"))
        if not parts[-1].endswith("\n"):
            parts.append("\n")
        parts.append("\n")
    parts.append(extra)
    return "".join(parts)


def generic_ggen_toml(pack: Pack, include_pack: bool) -> str:
    lines = [
        "[project]",
        f'name = "marketplace-qualification-{pack.name}"',
    ]
    # ggen v26.8.8 uses a frontmatter-style consumer schema for local pack
    # imports. Adding project.version alongside [packs] makes that subject
    # structurally ambiguous. Semantic/no-pack capsules use the declarative
    # schema and therefore carry the required explicit project version.
    if not include_pack:
        lines.append('version = "0.0.0"')
    lines.extend(
        (
            "",
            "[ontology]",
            'source = "ontology.ttl"',
            "",
        )
    )
    if include_pack:
        pack_path = pack.path.resolve().as_posix().replace('"', '\\"')
        lines.extend(("[packs]", f'"{pack.name}" = {{ path = "{pack_path}" }}', ""))
    elif pack.native_gates:
        gate_values = ", ".join(json.dumps(path.resolve().as_posix()) for path in pack.native_gates)
        lines.extend(("[validation]", f"gates = [{gate_values}]", ""))
    lines.extend(("[templates]", 'dir = "templates"', ""))
    return "\n".join(lines)


def write_generic_consumer(pack: Pack, consumer: Path) -> None:
    consumer.mkdir(parents=True)
    (consumer / "templates").mkdir()
    is_semantic = pack.profile == "semantic"
    (consumer / "ggen.toml").write_text(generic_ggen_toml(pack, include_pack=not is_semantic), encoding="utf-8")

    probe_fact = (
        "@prefix mq: <https://ggen.dev/marketplace/qualification#> .\n"
        f'mq:subject mq:packName "{pack.name}" .\n'
    )
    sources: tuple[Path, ...]
    if is_semantic:
        sources = pack.ontologies + qualification_consumer_rdf(pack)
    else:
        sources = qualification_consumer_rdf(pack)
    (consumer / "ontology.ttl").write_text(combine_rdf(sources, probe_fact), encoding="utf-8")
    (consumer / "templates" / "marketplace-probe.txt.tmpl").write_text(PROBE_TEMPLATE, encoding="utf-8")


def overlay_project_qualification(pack: Pack, consumer: Path) -> None:
    overlay = pack.path / "qualification" / "project"
    if not overlay.is_dir():
        return
    for source in sorted((path for path in overlay.rglob("*") if path.is_file()), key=lambda item: item.as_posix()):
        relative = source.relative_to(overlay)
        destination = consumer / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def prepare_consumer(pack: Pack, capsule: Path) -> Path:
    consumer = capsule / "consumer"
    if pack.profile == "project":
        shutil.copytree(pack.path, consumer)
        overlay_project_qualification(pack, consumer)
    else:
        write_generic_consumer(pack, consumer)
    return consumer


def compact_output(result: CommandResult) -> str:
    combined = "\n".join(part.strip() for part in (result.stderr, result.stdout) if part.strip())
    if len(combined) > 3000:
        combined = combined[-3000:]
    return combined.replace("\x00", "<NUL>")


def refusal_record(pack: Pack, code: str, detail: str) -> dict[str, Any]:
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
    with tempfile.TemporaryDirectory(prefix=f"ggen-marketplace-{pack.name}-") as raw:
        capsule = Path(raw)
        consumer = prepare_consumer(pack, capsule)

        first = run_bounded([ggen_bin, "sync", "run"], consumer, timeout_seconds)
        if first.timed_out:
            return refusal_record(pack, "REFUSED:GGEN_PACK_TIMEOUT", f"pass=1 timeout_seconds={timeout_seconds:g}")
        if first.returncode != 0:
            return refusal_record(
                pack,
                "REFUSED:GGEN_PACK_SYNC_FAILED",
                f"pass=1 exit={first.returncode} output={compact_output(first)}",
            )

        snapshot_one = snapshot_tree(consumer)
        if pack.profile != "project":
            probe = consumer / "qualification" / "marketplace-probe.txt"
            if not probe.is_file() or not probe.read_text(encoding="utf-8").strip():
                return refusal_record(pack, "REFUSED:GGEN_PACK_PROBE_MISSING", probe.as_posix())

        second = run_bounded([ggen_bin, "sync", "run"], consumer, timeout_seconds)
        if second.timed_out:
            return refusal_record(pack, "REFUSED:GGEN_PACK_TIMEOUT", f"pass=2 timeout_seconds={timeout_seconds:g}")
        if second.returncode != 0:
            return refusal_record(
                pack,
                "REFUSED:GGEN_PACK_SYNC_FAILED",
                f"pass=2 exit={second.returncode} output={compact_output(second)}",
            )

        snapshot_two = snapshot_tree(consumer)
        if snapshot_two != snapshot_one:
            before = dict(snapshot_one)
            after = dict(snapshot_two)
            changed = sorted(
                path
                for path in set(before) | set(after)
                if before.get(path) != after.get(path)
            )
            return refusal_record(
                pack,
                "REFUSED:GGEN_PACK_NONDETERMINISTIC_REPLAY",
                "changed=" + ",".join(changed[:40]),
            )

    source_after = pack_source_fingerprint(pack)
    if source_after != source_before:
        return refusal_record(
            pack,
            "REFUSED:GGEN_PACK_SOURCE_MUTATED",
            f"before={source_before} after={source_after}",
        )

    return {
        "consequence_files": len(snapshot_two),
        "consequence_sha256": snapshot_digest(snapshot_two),
        "name": pack.name,
        "profile": pack.profile,
        "source_sha256": source_after,
        "status": "ALIVE",
        "version": pack.version,
    }


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
        futures = {
            executor.submit(qualify_pack, pack, args.ggen, args.timeout_seconds): pack.name
            for pack in packs
        }
        records = [future.result() for future in concurrent.futures.as_completed(futures)]

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
