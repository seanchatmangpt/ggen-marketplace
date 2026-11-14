#!/usr/bin/env python3
"""Parity receipts court: every repo x service x cloud cell of the hyperscaler parity
matrix must be pass (matrix PASS + indexed receipt that exists with standing PASS) or a
registered divergence (KD row cited). Anything else is MISSING; exit 1 if any.
Matrix: <fnox>/docs/HYPERSCALER_PARITY.md. Index: receipts/parity-receipts-index.md.
"""
import json
import os
import re
import sys

MP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FNOX = os.environ.get("FNOX_ROOT", "/Users/sac/fnox")
MATRIX = os.path.join(FNOX, "docs", "HYPERSCALER_PARITY.md")
INDEX = os.path.join(MP, "receipts", "parity-receipts-index.md")
CLOUDS = ("gcp", "aws", "azure")


def parse_matrix(path):
    cells, repo, hdr = {}, None, None
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"## (\S+)\s*$", line)
        if m:
            repo, hdr = m.group(1), None
            continue
        if not repo or not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if cols[0] == "service":
            hdr = cols[1:]
            continue
        if hdr is None or set(cols[0]) <= {"-"}:
            continue
        for cloud, val in zip(hdr, cols[1:]):
            cells[(repo, cloud, cols[0])] = val
    return cells


def parse_index(path):
    idx = {}
    if not os.path.exists(path):
        return idx
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cols = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cols) >= 4 and cols[0] in ("smalt", "arcus") and cols[1] in CLOUDS:
            idx[(cols[0], cols[1], cols[2])] = cols[3]
    return idx


def receipt_ok(p):
    if not os.path.isabs(p):
        p = os.path.join(FNOX, p)
    if not os.path.isfile(p):
        return False, "receipt file absent"
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        return False, f"unparseable receipt ({e})"
    if d.get("standing") != "PASS":
        return False, f"receipt standing {d.get('standing')!r}"
    return True, ""


REGISTERS = [
    os.environ.get("ARCUS_KD", "/Users/sac/arcus/KNOWN_DIVERGENCES.md"),
    os.environ.get("SMALT_KD", "/Users/sac/smalt/docs/jira/v26.10.14/KNOWN_DIVERGENCES.md"),
]


def register_ids():
    ids = set()
    for r in REGISTERS:
        if os.path.isfile(r):
            ids.update(re.findall(r"KD-[\w-]+", open(r, encoding="utf-8").read()))
    return ids


def main():
    if not os.path.isfile(MATRIX):
        print(f"MISSING matrix {MATRIX}")
        return 1
    cells, idx = parse_matrix(MATRIX), parse_index(INDEX)
    if not cells:
        print("MISSING: matrix parsed to zero cells")
        return 1
    bad, ok = [], 0
    regids = register_ids()
    for (repo, cloud, svc), val in sorted(cells.items()):
        key = f"{repo}/{cloud}/{svc}"
        if val.startswith("REGISTERED-DIVERGENCE"):
            cited = re.findall(r"[\w]*KD-[\w-]+", val)
            unresolved = [k for k in cited if k not in regids]
            if cited and not unresolved:
                ok += 1
            else:
                bad.append(f"MISSING {key}: KD id(s) not in arcus/smalt register: {unresolved or 'none cited'}")
        elif val.startswith("PASS") and not val.startswith("PASS-UNRECEIPTED"):
            if (repo, cloud, svc) not in idx:
                bad.append(f"MISSING {key}: matrix PASS but no index row")
                continue
            good, why = receipt_ok(idx[(repo, cloud, svc)])
            if good:
                ok += 1
            else:
                bad.append(f"MISSING {key}: {why}")
        else:
            bad.append(f"MISSING {key}: matrix says {val.split(' ')[0]}")
    for line in bad:
        print(line)
    print(f"cells={len(cells)} ok={ok} missing={len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
