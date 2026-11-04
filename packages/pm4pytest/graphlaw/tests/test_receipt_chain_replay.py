"""PM1 court 4 (lane PM8): receipt chain reconstruction from OUTSIDE graphlaw.

Replays the fold rule of /Users/sac/graphlaw/scripts/receipt_chain_sync.sh in
pure Python (hashlib has no BLAKE3; the `blake3` pip package is used), against
the real /Users/sac/graphlaw/receipts tree — no Rust code, no mocks.

Fold rule replicated from receipt_chain_sync.sh:
  FILES  = every file under receipts/ except CHAIN.blake3, recursive,
           sorted by relative path (LC_ALL=C sort), prefixed "receipts/".
  CURRENT = one line per file: "<blake3-hex>  <relpath>"  (b3sum format,
           two spaces).
  chain_head = blake3( CURRENT lines joined with "\n", no trailing newline )
           — i.e. `printf '%s' "$CURRENT" | b3sum`.
"""

import subprocess

import pytest
from blake3 import blake3

REPO = "/Users/sac/graphlaw"
CHAIN = f"{REPO}/receipts/CHAIN.blake3"


def parse_chain():
    rows = []
    head = None
    with open(CHAIN, "r", encoding="utf-8") as f:
        for line in f.read().splitlines():
            if not line.strip():
                continue
            if line.startswith("chain_head"):
                # b3sum convention: key and digest separated by a whitespace
                # run (chain_head<2 spaces><digest>) — split on runs, never a
                # fixed single space.
                head = line.split()[1]
                continue
            digest, _, relpath = line.partition("  ")
            rows.append((digest, relpath))
    assert head is not None, "CHAIN.blake3 has no chain_head line"
    return rows, head


def b3sum(path):
    h = blake3()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="module")
def chain():
    return parse_chain()


def test_chain_file_exists_with_rows(chain):
    rows, _ = chain
    assert len(rows) > 0, "chain lists zero receipts"


def test_every_row_digest_matches_file_on_disk(chain):
    rows, _ = chain
    bad = []
    for digest, relpath in rows:
        path = f"{REPO}/{relpath}"
        assert path.startswith(REPO + "/receipts/"), f"row escapes receipts/: {relpath}"
        actual = b3sum(path)
        if actual != digest:
            bad.append((relpath, digest, actual))
    assert not bad, f"TAMPER-DETECTED in {len(bad)} row(s): {bad}"


def test_no_extra_receipt_files_outside_chain(chain):
    rows, _ = chain
    listed = {relpath for _, relpath in rows}
    find = subprocess.run(
        ["find", "receipts", "-type", "f", "!", "-name", "CHAIN.blake3"],
        cwd=REPO, capture_output=True, text=True, check=True,
    )
    on_disk = {p for p in find.stdout.splitlines() if p}
    missing_from_chain = on_disk - listed
    assert not missing_from_chain, f"receipt files not covered by chain: {missing_from_chain}"


def test_chain_head_matches_recomputed_fold(chain):
    rows, stored_head = chain
    # Replicate: CURRENT = b3sum of FILES in LC_ALL=C sorted relpath order,
    # lines "<digest>  <path>"; head = blake3(CURRENT without trailing newline).
    ordered = sorted(rows, key=lambda r: r[1])
    current = "\n".join(f"{d}  {p}" for d, p in ordered)
    recomputed = blake3(current.encode("utf-8")).hexdigest()
    assert recomputed == stored_head, (
        f"chain_head mismatch: stored={stored_head} recomputed={recomputed}"
    )


def test_chain_rows_are_sorted_by_relpath(chain):
    rows, _ = chain
    paths = [p for _, p in rows]
    assert paths == sorted(paths), "chain rows are not in sorted relpath order"


def test_fold_rule_agrees_with_b3sum_shim():
    """Non-vacuity: the Python blake3 fold must agree with the system b3sum
    on a small synthetic corpus, proving the two implementations fold alike
    (not that the test merely re-encodes its own assumptions)."""
    import os, tempfile

    try:
        subprocess.run(["b3sum", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("b3sum not on PATH; cannot cross-check implementations")

    with tempfile.TemporaryDirectory() as td:
        corpus = {}
        for name, content in [("a.txt", b"alpha"), ("b.txt", b"beta\n"), ("c/d.txt", b"gamma")]:
            p = os.path.join(td, name)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f:
                f.write(content)
            corpus[f"receipts/{name}"] = b3sum(p)

        ordered = sorted(corpus.items())
        current = "\n".join(f"{d}  {p}" for p, d in ordered)
        py_head = blake3(current.encode("utf-8")).hexdigest()

        files = [os.path.join(td, rel.split("receipts/", 1)[1]) for rel, _ in ordered]
        b3 = subprocess.run(["b3sum", *files], capture_output=True, text=True, check=True).stdout
        sh_head = subprocess.run(
            ["b3sum"], input=current, capture_output=True, text=True, check=True
        ).stdout.split()[0]

        # per-file digests agree between python and b3sum
        for line in b3.strip().splitlines():
            d, _, p = line.partition("  ")
            rel = "receipts/" + os.path.relpath(p, td)
            assert corpus[rel] == d, f"per-file digest disagree for {rel}"
        assert py_head == sh_head, f"fold disagreement: python={py_head} b3sum={sh_head}"
