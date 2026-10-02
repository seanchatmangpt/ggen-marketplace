#!/usr/bin/env python3
"""Render determinism court (L3) - byte identity between two renders.

Default: test/fixtures/rendered/canonical vs test/fixtures/rendered/replay (the second
render). Laws: identical file sets; every file byte-identical; the replay manifest's
outputDigests must equal the actual sha256 of the named sibling render - so the manifest
cannot certify bytes it does not bind.

Usage: python3 test/test_render_determinism.py [dir_a dir_b]
"""
import hashlib
import json
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import courts  # noqa: E402


def _files(directory):
    directory = pathlib.Path(directory)
    return sorted(p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file())


def _sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def run(dir_a, dir_b=None):
    dir_b = dir_b or courts.RENDERED_REPLAY
    errs = []
    files_a, files_b = _files(dir_a), _files(dir_b)
    if files_a != files_b:
        errs.append(f"file sets differ: only-a={sorted(set(files_a) - set(files_b))} only-b={sorted(set(files_b) - set(files_a))}")
    for rel in sorted(set(files_a) & set(files_b)):
        a = pathlib.Path(dir_a) / rel
        b = pathlib.Path(dir_b) / rel
        if a.read_bytes() != b.read_bytes():
            errs.append(f"byte drift: {rel} differs between {dir_a} and {dir_b}")
    # replay manifest must bind the bytes it certifies
    for directory in (dir_a, dir_b):
        replay_path = pathlib.Path(directory) / "replay.json"
        if not replay_path.is_file():
            continue
        manifest = json.loads(replay_path.read_text())
        digests = manifest.get("outputDigests")
        if not isinstance(digests, dict) or not digests:
            errs.append(f"{directory}/replay.json: outputDigests must be a non-empty object")
            continue
        for rel, expected in sorted(digests.items()):
            actual_path = pathlib.Path(directory) / rel
            if not actual_path.is_file():
                errs.append(f"{directory}/replay.json: outputDigest names missing file {rel}")
            elif _sha256(actual_path) != expected:
                errs.append(f"{directory}/replay.json: outputDigest for {rel} does not match actual bytes (stale manifest)")
    return errs


def selftest(rendered_dir):
    """Anti-vacuity: a one-byte render drift and a stale manifest digest MUST both fire."""
    rendered_dir = pathlib.Path(rendered_dir)
    gaps = []
    with tempfile.TemporaryDirectory() as tmp:
        tampered = pathlib.Path(tmp, "tampered")
        shutil.copytree(rendered_dir, tampered)
        machine_path = tampered / "machine.json"
        machine_path.write_bytes(machine_path.read_bytes().replace(b'"machine"', b'"machines"', 1))
        if not run(rendered_dir, tampered):
            gaps.append("selftest: one-byte render drift did NOT fire (determinism court vacuous)")
    with tempfile.TemporaryDirectory() as tmp:
        stale = pathlib.Path(tmp, "stale")
        shutil.copytree(rendered_dir, stale)
        replay_path = stale / "replay.json"
        manifest = json.loads(replay_path.read_text())
        manifest["outputDigests"]["machine.json"] = "0" * 64
        replay_path.write_text(json.dumps(manifest, indent=2) + "\n")
        if not run(rendered_dir, stale):
            gaps.append("selftest: stale outputDigest did NOT fire (manifest not bound to bytes)")
    return gaps


if __name__ == "__main__":
    dir_a = sys.argv[1] if len(sys.argv) > 1 else str(courts.RENDERED_CANONICAL)
    dir_b = sys.argv[2] if len(sys.argv) > 2 else str(courts.RENDERED_REPLAY)
    errors = run(dir_a, dir_b) + selftest(dir_a)
    for err in errors:
        print(f"VIOLATION: {err}")
    print("RESULT:", "REFUSED" if errors else "RENDER_DETERMINISM_OK", f"({len(errors)} problems)")
    sys.exit(1 if errors else 0)
