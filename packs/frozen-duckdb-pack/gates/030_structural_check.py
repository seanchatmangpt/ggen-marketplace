#!/usr/bin/env python3
"""frozen-duckdb-pack structural gate — executable structural check script.

Verifies the pack's own structure and its qualification fixture against the
frozen-duckdb domain laws WITHOUT any actuation:
  1. Pack layout: pack.toml / ontology.ttl / README.md / fixture present, at
     least one SPARQL gate and one template (marketplace gate sources are
     .rq/.py only — scripts/marketplace.py GATE_SOURCE_SUFFIXES).
  2. pack.toml [pack] name matches the directory name.
  3. All five law handles (skos:notation) are present in the ontology.
  4. Every template carries `to:` and `sparql:` frontmatter.
  5. Asset-naming law: every arch-suffixed release-asset literal in the graph
     files matches libduckdb_{arch}.{dylib|so} (bare link names like
     libduckdb.dylib are the cache-normalization/soname law, not assets).
  6. Version-encoding law (structural form): every crate-shaped version
     literal MAJOR.<4+ digit middle>.0 equals
     MAJOR.(MAJOR*10000+MINOR*100+PATCH).0 of some engine-shaped literal
     MAJOR.MINOR.PATCH in the graph files.
  7. Cache-normalization law: every prov:value literal under ~ is either the
     exact central cache root or a v{version}-{arch} cache dir. (Falsified
     once: a cache literal relocated to ~/duckdb-libs/1.5.5 escaped
     prefix-based extraction — prov:value is the fact-bearing property; prose
     is not scanned.)

Usage: gates/030_structural_check.py [pack-dir]   (default: this gate's ../)
Exit 0 = all checks hold; exit 1 = refusals, with diagnostics. Refusal of a
structural law is a valid gate outcome, not an error to hide.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ASSET_RE = re.compile(r"libduckdb_[A-Za-z0-9_]+\.[A-Za-z0-9.]+")
ASSET_LAW_RE = re.compile(r"^libduckdb_[A-Za-z0-9_]+\.(dylib|so)$")
VERSION_RE = re.compile(r"(?<![\w.])(\d+)\.(\d+)\.(\d+)(?![\w.])")
CACHE_ROOT_LITERAL = "~/.frozen-duckdb/cache"
CACHE_DIR_RE = re.compile(r"^~/\.frozen-duckdb/cache/v\d+\.\d+\.\d+-[A-Za-z0-9_]+$")
PROV_VALUE_TILDE_RE = re.compile(r'prov:value\s+"(~[^"]*)"')
LAW_HANDLES = (
    "version-pinning",
    "release-asset-name",
    "cache-normalization",
    "docs-rs-no-link",
    "soname-rpath",
)

failures: list[str] = []


def check(ok: bool, message: str) -> None:
    print(("PASS " if ok else "FAIL ") + message)
    if not ok:
        failures.append(message)


def main(argv: list[str]) -> int:
    pack = Path(argv[1]).resolve() if len(argv) > 1 else Path(__file__).resolve().parent.parent
    ontology = pack / "ontology.ttl"
    fixture = pack / "qualification" / "consumer.ttl"

    # --- 1. pack layout ------------------------------------------------------
    for rel in ("pack.toml", "ontology.ttl", "README.md", "qualification/consumer.ttl"):
        p = pack / rel
        check(p.is_file() and p.stat().st_size > 0, f"layout: {rel} present and non-empty")
    check(any((pack / "gates").glob("*.rq")), "layout: SPARQL gates present")
    check(any((pack / "templates").glob("*.tmpl")), "layout: templates present")
    check((pack / "gates" / "030_structural_check.py").is_file(),
          "layout: structural check script present")

    # --- 2. pack.toml identity -------------------------------------------------
    name_match = re.search(r'^name = "(.*)"$', (pack / "pack.toml").read_text(), re.M)
    toml_name = name_match.group(1) if name_match else ""
    check(toml_name == pack.name,
          f"identity: pack.toml name '{toml_name}' matches directory '{pack.name}'")

    # --- 3. the five law handles ------------------------------------------------
    ontology_text = ontology.read_text()
    for handle in LAW_HANDLES:
        check(f'skos:notation "{handle}"' in ontology_text,
              f"laws: handle '{handle}' present")

    # --- 4. template frontmatter -------------------------------------------------
    for tmpl in sorted((pack / "templates").glob("*.tmpl")):
        text = tmpl.read_text()
        check(re.search(r"^to:", text, re.M) and re.search(r"^sparql:", text, re.M),
              f"template: {tmpl.name} carries to: + sparql: frontmatter")

    # --- graph literals for laws 2/3/6 ------------------------------------------
    graph_text = "\n".join(p.read_text() for p in (ontology, fixture))

    # --- 5. asset-naming law ------------------------------------------------------
    assets = sorted(set(ASSET_RE.findall(graph_text)))
    bad = [a for a in assets if not ASSET_LAW_RE.match(a)]
    check(assets and not bad,
          f"asset law: {len(assets)} asset literals, all match libduckdb_{{arch}}.{{dylib|so}}"
          + (f" (violations: {bad})" if bad else ""))
    extensions = {a.rsplit(".", 1)[1] for a in assets if ASSET_LAW_RE.match(a)}
    check(extensions == {"dylib", "so"}, "asset law: both .dylib and .so assets represented")

    # --- 6. version-encoding law (structural form) ---------------------------------
    engines: set[tuple[int, int, int]] = set()
    crates: set[tuple[int, int, int]] = set()
    for m in VERSION_RE.finditer(graph_text):
        maj, mid, patch = int(m.group(1)), int(m.group(2)), int(m.group(3))
        (crates if mid >= 1000 else engines).add((maj, mid, patch))
    if not crates:
        check(False, "version law: no crate-shaped version literal found to check")
    if not engines:
        check(False, "version law: no engine-shaped version literal found to check against")
    for c_maj, c_mid, c_patch in sorted(crates):
        hit = next(
            (
                f"{c_maj}.{c_mid}.{c_patch} encodes {e_maj}.{e_min}.{e_patch}"
                f" (={e_maj * 10000 + e_min * 100 + e_patch})"
                for e_maj, e_min, e_patch in sorted(engines)
                if c_maj == e_maj and c_patch == 0
                and c_mid == e_maj * 10000 + e_min * 100 + e_patch
            ),
            None,
        )
        check(hit is not None,
              f"version law: {hit}" if hit else
              f"version law: crate version {c_maj}.{c_mid}.{c_patch} translates to no engine "
              "literal by MAJOR.(M*10000+m*100+p).0")

    # --- 7. cache-normalization law -------------------------------------------------
    tilde_values = sorted(set(PROV_VALUE_TILDE_RE.findall(graph_text)))
    bad_cache = [v for v in tilde_values
                 if v != CACHE_ROOT_LITERAL and not CACHE_DIR_RE.match(v)]
    check(bool(tilde_values) and not bad_cache,
          "cache law: all ~/ prov:value literals are the central cache root or "
          "v{version}-{arch} cache dirs"
          + (f" (violations: {bad_cache})" if bad_cache else ""))

    if failures:
        print(f"STRUCTURAL GATE: REFUSED ({len(failures)} refusal(s))")
        return 1
    print(f"STRUCTURAL GATE: PASS ({pack})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
