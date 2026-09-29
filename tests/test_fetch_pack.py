"""Chicago-style tests for scripts/fetch_pack.py: real catalog, real archive, file:// URLs."""
from __future__ import annotations

import gzip
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MP = ROOT / "scripts" / "marketplace.py"
FP = ROOT / "scripts" / "fetch_pack.py"
DIST = ROOT / "dist"


def run(*args, cwd=ROOT):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, capture_output=True, text=True)


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("fetch")
    existed = DIST.exists()
    cat = run(MP, "catalog")
    assert cat.returncode == 0, cat.stderr
    catalog = json.loads(cat.stdout)
    rec = catalog["packs"][0]
    name = rec["name"]
    arch = run(MP, "archive")
    assert arch.returncode == 0, arch.stderr
    src = DIST / "packs" / f"{name}-{rec['version']}.tar.gz"
    archive = tmp / src.name
    shutil.copy(src, archive)
    if not existed:
        shutil.rmtree(DIST)
    # rewrite download_url to file:// so no network is needed
    rec["download_url"] = archive.as_uri()
    catalog_path = tmp / "catalog.json"
    catalog_path.write_text(json.dumps(catalog))
    return {"tmp": tmp, "name": name, "rec": rec, "archive": archive, "catalog": catalog_path}


def test_lock_verify_fetch_roundtrip(world):
    tmp, name = world["tmp"], world["name"]
    lock = tmp / "packs.lock.json"
    r = run(FP, "lock", world["catalog"], name, "--out", lock)
    assert r.returncode == 0, r.stderr
    entry = json.loads(lock.read_text())["packs"][0]
    assert set(entry) == {"name", "version", "digest", "download_url"}
    assert entry["digest"] == world["rec"]["digest"]

    v = run(FP, "verify", world["archive"], name, "--lock", lock)
    assert v.returncode == 0, v.stderr

    out = tmp / "out"
    f = run(FP, "fetch", name, "--catalog", world["catalog"], "--lock", lock, "--out", out)
    assert f.returncode == 0, f.stderr
    assert (out / name / "pack.toml").is_file()


def test_tampered_archive_refused(world):
    tmp, name = world["tmp"], world["name"]
    bad = tmp / "tampered.tar.gz"
    data = bytearray(world["archive"].read_bytes())
    data[len(data) // 2] ^= 0xFF
    bad.write_bytes(bytes(data))
    v = run(FP, "verify", bad, name, "--catalog", world["catalog"])
    assert v.returncode == 2
    assert "REFUSED:DIGEST_MISMATCH" in v.stderr


def test_fetch_tampered_download_refused_and_nothing_extracted(world):
    tmp, name = world["tmp"], world["name"]
    bad = tmp / "served-bad.tar.gz"
    data = bytearray(world["archive"].read_bytes())
    data[-5] ^= 0x01
    bad.write_bytes(bytes(data))
    cat = json.loads(world["catalog"].read_text())
    cat["packs"][0]["download_url"] = bad.as_uri()
    cp = tmp / "catalog-bad.json"
    cp.write_text(json.dumps(cat))
    out = tmp / "out-bad"
    f = run(FP, "fetch", name, "--catalog", cp, "--out", out)
    assert f.returncode == 2 and "REFUSED:DIGEST_MISMATCH" in f.stderr
    assert not out.exists()


def _evil_archive(tmp, member_name, kind="file", linkname=""):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo(member_name)
        if kind == "symlink":
            info.type = tarfile.SYMTYPE
            info.linkname = linkname
            tar.addfile(info)
        else:
            payload = b"x"
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
    return gzip.compress(buf.getvalue(), mtime=0)


@pytest.mark.parametrize(
    "member,kind,link,code",
    [
        ("/etc/evil", "file", "", "UNSAFE_PATH"),
        ("evilpack/../../escape", "file", "", "UNSAFE_PATH"),
        ("evilpack/link", "symlink", "/etc/passwd", "LINK_MEMBER"),
        ("other/file", "file", "", "OUTSIDE_PACK_ROOT"),
    ],
)
def test_unsafe_archives_refused_even_with_valid_digest(world, member, kind, link, code):
    import hashlib

    tmp = world["tmp"]
    data = _evil_archive(tmp, member, kind, link)
    served = tmp / f"evil-{code}.tar.gz"
    served.write_bytes(data)
    cat = {"packs": [{"name": "evilpack", "version": "1", "digest": "sha256:" + hashlib.sha256(data).hexdigest(),
                      "download_url": served.as_uri()}]}
    cp = tmp / f"cat-{code}.json"
    cp.write_text(json.dumps(cat))
    out = tmp / f"out-{code}"
    f = run(FP, "fetch", "evilpack", "--catalog", cp, "--out", out)
    assert f.returncode == 2 and f"REFUSED:{code}" in f.stderr
    assert not out.exists()
    assert not (tmp / "escape").exists()


def test_lock_unknown_pack_refused(world):
    r = run(FP, "lock", world["catalog"], "no-such-pack", "--out", world["tmp"] / "x.json")
    assert r.returncode == 2 and "REFUSED:PACK_NOT_IN_CATALOG" in r.stderr
