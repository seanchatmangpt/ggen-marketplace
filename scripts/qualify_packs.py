#!/usr/bin/env python3
"""Qualify every admitted marketplace pack through the real ggen runtime.

The court's core is filesystem-only: it never executes cloud APIs, pack-owned
Python verifiers, or any BRCE DO surface. Each pack is loaded through ggen
twice in an isolated capsule and must converge to the same non-runtime
filesystem consequence within the five-second per-pass bound.

One narrow, opt-in-by-presence exception (CI-05, added after the initial
filesystem-only design): if the generated-consequence tree contains one or
more `Cargo.toml` files that ggen's own generation rules actually targeted
(confirmed via the sync pass's own `decisions` map, never merely a file that
happens to sit in a project-profile pack's copied tree), each such manifest
is really `cargo build`'d and `cargo test`'d -- see
`discover_generated_cargo_manifests` / `verify_generated_cargo_manifest`
below. This closes a real gap: a pack could previously render a
syntactically-fine but semantically-broken Cargo.toml (e.g. a `path =`
dependency that only resolves inside the pack author's own working tree) and
still qualify ALIVE, because nothing downstream of `ggen sync run` was ever
actually compiled. Gated purely on artifact presence, never on pack name or
identity: a pack that generates no Rust crate is completely unaffected, and
gains no new subprocess, no new timeout exposure, and no new failure mode.

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
# Separate, wider ceiling for the opt-in-by-presence `cargo build`/`cargo
# test` verification below (CI-05). `cargo` compiling a real dependency tree
# is routinely far slower than one `ggen sync run` pass -- this must never
# silently reuse the 5s (or R18's 30s) sync ceiling. Bounded, not unbounded:
# a generated crate that hangs still fails closed, it just gets real headroom
# first.
CARGO_BUILD_TIMEOUT_SECONDS = 120.0
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


def copy_composed_packs(pack: Pack, capsule: Path) -> None:
    """For a project-profile pack whose own `ggen.toml` composes sibling
    marketplace packs via `[packs] name = { path = "../other-pack" }`
    (e.g. clap-noun-verb-zeroconfig-pack composing the six clap-noun-verb
    compiler packs), copy each referenced sibling into `capsule` alongside
    `consumer/` so those relative references still resolve inside the
    isolated qualification capsule.

    `prepare_consumer`'s `shutil.copytree(pack.path, consumer)` relocates
    only the pack itself, one level below where it naturally lives (its
    real siblings are `pack.path.parent`'s other entries; `consumer`'s
    capsule-relative sibling position is `capsule`, matching that same
    shape) -- without this, `consumer/../other-pack` resolves to a path
    that was never copied, and ggen refuses with a real
    `[FM-PACK-001] directory ... does not exist` error, not a synthetic
    qualification-only failure.

    Non-recursive by design: a composed sibling that itself composes
    further siblings via its own `[packs]` would need this run again on
    that sibling. None of this marketplace's current project-composable
    packs (the clap-noun-verb-* family, chicago-tdd-tools-pack) have their
    own `[packs]` table, so this is a real, disclosed scope limit, not
    (yet) an exercised gap.

    # Raises
    `QualificationContractError` if a composed path escapes the pack's own
    `packs/` directory (path traversal outside the marketplace's pack
    root) or resolves
    to something that does not exist -- fails closed, mirroring
    `qualification_extra_ontologies`'s existing escape-check discipline.
    """
    ggen_toml = pack.path / "ggen.toml"
    if not ggen_toml.is_file():
        return
    try:
        config = tomllib.loads(ggen_toml.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise QualificationContractError(f"pack `{pack.name}`: invalid ggen.toml: {error}") from error
    packs_table = config.get("packs")
    if not isinstance(packs_table, dict):
        return
    packs_root = pack.path.resolve().parent
    for name, entry in packs_table.items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        source = (pack.path / entry["path"]).resolve()
        try:
            source.relative_to(packs_root)
        except ValueError as error:
            raise QualificationContractError(
                f"pack `{pack.name}`: composed pack `{name}` path `{entry['path']}` "
                f"resolves to `{source}`, outside {packs_root} -- refused for qualification-capsule safety"
            ) from error
        if not source.is_dir():
            raise QualificationContractError(
                f"pack `{pack.name}`: composed pack `{name}` path `{entry['path']}` "
                f"resolves to `{source}`, which does not exist"
            )
        destination = capsule / source.name
        if not destination.exists():
            shutil.copytree(source, destination)


def prepare_consumer(pack: Pack, capsule: Path) -> Path:
    consumer = capsule / "consumer"
    if pack.profile == "project":
        shutil.copytree(pack.path, consumer)
        overlay_project_qualification(pack, consumer)
        copy_composed_packs(pack, capsule)
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


def discover_generated_cargo_manifests(consumer: Path, decisions: dict[str, str] | None = None) -> tuple[Path, ...]:
    """Every `Cargo.toml` under `consumer`'s generated-consequence tree that
    ggen's own generation rules actually targeted this sync pass (excluding
    `IGNORED_RUNTIME_ROOTS` -- `.git`, `.ggen`, `.ggen-v2`, `.cache`,
    `.qualification-home`, `target`), sorted for determinism.

    Presence-gated, never pack-name-gated (CI-05): any pack whose generated
    output happens to include a `Cargo.toml` gets real `cargo build`/`cargo
    test` verification for that manifest in `qualify_pack` below. A pack
    that generates no Rust crate is entirely unaffected: this returns an
    empty tuple and no cargo subprocess is ever spawned for it.

    `decisions` (when given -- the real `ggen sync run` JSON output's own
    `"decisions"` map, keyed by output path relative to `consumer`) narrows
    the artifact-presence check from "a Cargo.toml file exists somewhere in
    this tree" to "ggen itself wrote or considered writing this exact path
    this sync pass" -- excluding a project-profile pack's own committed,
    non-generated fixture content (e.g. a checked-in reference/example
    subtree) that `shutil.copytree` brought along but no `[[generation.rules]]`
    ever targets. Verified empirically against the real v26.9.1 corpus while
    building this: every `Cargo.toml` this marketplace currently ships
    (including every generated-consequence one with a real broken `path =`
    dependency) IS a `decisions` key, so this narrowing changes nothing
    about today's qualification outcomes -- it only guards a future pack
    that ships committed, non-generated Rust fixture content alongside real
    generation rules from getting swept into cargo verification it never
    asked for. Omitting `decisions` (`None`) falls back to the unfiltered,
    presence-only scan.
    """
    manifests = [
        path
        for path in consumer.rglob("Cargo.toml")
        if not (path.relative_to(consumer).parts and path.relative_to(consumer).parts[0] in IGNORED_RUNTIME_ROOTS)
        and (decisions is None or path.relative_to(consumer).as_posix() in decisions)
    ]
    return tuple(sorted(manifests, key=lambda item: item.relative_to(consumer).as_posix()))


def verify_generated_cargo_manifest(manifest: Path, timeout_seconds: float) -> tuple[str, str] | None:
    """Run `cargo build` then, on success, `cargo test`, against one real
    generated `Cargo.toml` -- both bounded by `timeout_seconds`
    (`CARGO_BUILD_TIMEOUT_SECONDS`, never the sync pass's own ceiling; see
    that constant's docstring). `cargo test` runs unconditionally after a
    successful build rather than trying to first detect whether the crate
    declares an explicit `[[test]]` target: a crate with no `#[test]`
    functions and no `tests/` directory still has cargo's default (empty)
    test harness, which `cargo test` reports as `0 passed; 0 failed` and
    exits 0 -- so this never fabricates a build-only pass as a test pass, and
    never needs brittle Cargo.toml introspection to decide whether to run it.

    Returns `None` on success, or `(refusal_code, detail)` naming exactly
    which step failed (build vs. test) on the first failure -- callers stop
    at the first failing manifest rather than aggregating every manifest's
    failure, mirroring the existing `qualify_pack` short-circuit shape for
    the sync passes above.
    """
    build = run_bounded(["cargo", "build", "--manifest-path", str(manifest)], manifest.parent, timeout_seconds)
    if build.timed_out:
        return (
            "REFUSED:GGEN_PACK_GENERATED_BUILD_FAILED",
            f"cargo build timed out after {timeout_seconds:g}s manifest={manifest}",
        )
    if build.returncode != 0:
        return (
            "REFUSED:GGEN_PACK_GENERATED_BUILD_FAILED",
            f"cargo build exit={build.returncode} manifest={manifest} output={compact_output(build)}",
        )
    test = run_bounded(["cargo", "test", "--manifest-path", str(manifest)], manifest.parent, timeout_seconds)
    if test.timed_out:
        return (
            "REFUSED:GGEN_PACK_GENERATED_TEST_FAILED",
            f"cargo test timed out after {timeout_seconds:g}s manifest={manifest}",
        )
    if test.returncode != 0:
        return (
            "REFUSED:GGEN_PACK_GENERATED_TEST_FAILED",
            f"cargo test exit={test.returncode} manifest={manifest} output={compact_output(test)}",
        )
    return None


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
                            # CI-05: opt-in-by-presence build/execute verification.
                            # `qualify_packs.py` stays filesystem-only for every pack
                            # that generates no Rust crate (see the module docstring);
                            # this only fires for the packs whose generated output
                            # actually contains a `Cargo.toml` ggen itself targeted
                            # this pass. Gated on artifact presence, never on
                            # `pack.name`. `second.stdout` is the real `ggen sync
                            # run` JSON payload (stderr carries tracing, verified
                            # empirically to never mix); a parse failure here
                            # degrades to the unfiltered presence-only scan rather
                            # than introducing an unrelated new failure mode.
                            try:
                                second_decisions = json.loads(second.stdout).get("decisions", {})
                            except (json.JSONDecodeError, AttributeError):
                                second_decisions = None
                            manifests = discover_generated_cargo_manifests(consumer, second_decisions)
                            build_failure: tuple[str, str] | None = None
                            for manifest in manifests:
                                build_failure = verify_generated_cargo_manifest(manifest, CARGO_BUILD_TIMEOUT_SECONDS)
                                if build_failure is not None:
                                    break
                            if build_failure is not None:
                                code, detail = build_failure
                                record = refusal(pack, code, detail)
                            else:
                                record = {
                                    "consequence_files": len(snapshot_two),
                                    "consequence_sha256": snapshot_digest(snapshot_two),
                                    "generated_build": {
                                        "manifests_verified": [
                                            manifest.relative_to(consumer).as_posix()
                                            for manifest in manifests
                                        ],
                                    },
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


def shard(packs: list[Pack], index: int, count: int) -> list[Pack]:
    """Deterministically partition `packs` (already sorted by name — see
    `require_admitted`'s caller) into `count` near-equal, non-overlapping
    shards and return shard `index`'s slice (0-based). Used to spread
    qualification of a growing pack corpus across parallel CI matrix jobs
    instead of one long serial job — see .github/workflows/ci.yml's
    `qualify` matrix. Slicing by position (not hashing) on an
    already-name-sorted list keeps shard membership stable and human-
    predictable as packs are added, and every pack lands in exactly one
    shard for any fixed `count` (verified by the CI aggregate step, which
    sums each shard's own `pack_count` against a fresh, un-sharded
    `require_admitted()` count).
    """
    if count <= 0:
        raise QualificationContractError(f"shard count must be positive, got {count}")
    if not (0 <= index < count):
        raise QualificationContractError(f"shard index {index} out of range for count {count}")
    return [pack for position, pack in enumerate(packs) if position % count == index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ggen", default=os.environ.get("GGEN_BIN") or shutil.which("ggen"))
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--shard-index", type=int, default=None,
        help="0-based shard to qualify (requires --shard-count); omit both for the full corpus",
    )
    parser.add_argument(
        "--shard-count", type=int, default=None,
        help="total number of shards (requires --shard-index); omit both for the full corpus",
    )
    args = parser.parse_args()

    if (args.shard_index is None) != (args.shard_count is None):
        print("REFUSED:GGEN_PACK_SHARD_ARGS:shard_index_and_shard_count_must_both_be_set_or_both_omitted", file=sys.stderr)
        return 2

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

    packs = sorted(require_admitted(), key=lambda pack: pack.name)
    if args.shard_index is not None:
        try:
            packs = shard(packs, args.shard_index, args.shard_count)
        except QualificationContractError as error:
            print(f"REFUSED:GGEN_PACK_SHARD_INVALID:{error}", file=sys.stderr)
            return 2

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
        "shard_count": args.shard_count,
        "shard_index": args.shard_index,
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
