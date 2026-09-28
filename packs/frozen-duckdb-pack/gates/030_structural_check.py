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
  8. Consumer-config law: every config-form stanza carries an
     operative/refused status; "operative" is legal only for the two forms
     the declarative schema binds ([ontology].imports, [[generation.rules]]);
     a "refused" form cites a dcterms:references anchor whose label carries
     the witnessed FM- error code; the imports form is present and operative.
  9. Rendered-consequence ownership: a stanza titled "rendered consequence"
     carries prov:wasDerivedFrom and names its owning rule ("owning rule:").
 10. Receipt runtime state: a prov:value literal under .ggen* must belong to
     a stanza declaring it runtime/untracked — declaring receipt state as
     tracked source is the violation.
 11. Single-writer fact files: consumer-fact subjects live only in the
     consumer fixture, pack subjects only in the ontology — a concern
     bleeding into a foreign writer's file is the multi-writer violation.

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
PROV_VALUE_RE = re.compile(r'prov:value\s+"([^"]*)"')
TITLE_RE = re.compile(r'dcterms:title\s+"([^"]*)"')
SUBJECT_RE = re.compile(r"^<([^>]+)>")
REFERENCES_RE = re.compile(r"dcterms:references\s+<([^>]+)>")
OPERATIVE_NOTATIONS = {"[ontology].imports", "[[generation.rules]]"}
LAW_HANDLES = (
    "version-pinning",
    "release-asset-name",
    "cache-normalization",
    "docs-rs-no-link",
    "soname-rpath",
    "ggen-consumer-config",
    "rendered-consequence-ownership",
    "fact-file-per-concern",
    "receipt-runtime-state",
)

failures: list[str] = []


def check(ok: bool, message: str) -> None:
    print(("PASS " if ok else "FAIL ") + message)
    if not ok:
        failures.append(message)


def ttl_stanzas(text: str) -> list[tuple[str, str]]:
    """Blank-line-separated TTL stanzas as (subject-iri | '', body) pairs.
    Comment-only and @prefix blocks are skipped (the pack's source files are
    stanza-formatted; this is a structural gate, not a Turtle parser)."""
    stanzas: list[tuple[str, str]] = []
    for raw in re.split(r"\n\s*\n", text):
        body = raw.strip()
        if not body or body.startswith("#") or body.startswith("@"):
            continue
        m = SUBJECT_RE.match(body)
        stanzas.append((m.group(1) if m else "", body))
    return stanzas


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

    # --- 3. the nine law handles -------------------------------------------------
    ontology_text = ontology.read_text()
    for handle in LAW_HANDLES:
        check(f'skos:notation "{handle}"' in ontology_text,
              f"laws: handle '{handle}' present")

    # --- 4. template frontmatter -------------------------------------------------
    for tmpl in sorted((pack / "templates").glob("*.tmpl")):
        text = tmpl.read_text()
        check(re.search(r"^to:", text, re.M) and re.search(r"^sparql:", text, re.M),
              f"template: {tmpl.name} carries to: + sparql: frontmatter")

    # --- graph literals for laws 2/3/6-9 ------------------------------------------
    fixture_text = fixture.read_text()
    graph_text = ontology_text + "\n" + fixture_text
    ontology_stanzas = ttl_stanzas(ontology_text)
    fixture_stanzas = ttl_stanzas(fixture_text)
    graph_stanzas = ontology_stanzas + fixture_stanzas
    stanza_by_subject = {subj: body for subj, body in graph_stanzas if subj}

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

    # --- 8. consumer-config law (config-form statuses) -------------------------------
    config_stanzas = [body for _, body in graph_stanzas
                      if 'prov:value "operative"' in body or 'prov:value "refused"' in body]
    check(bool(config_stanzas),
          "config law: config-form collection non-empty")
    operative_imports = False
    for body in config_stanzas:
        notation_m = re.search(r'skos:notation\s+"([^"]*)"', body)
        notation = notation_m.group(1) if notation_m else "(no notation)"
        if 'prov:value "operative"' in body:
            ok = notation in OPERATIVE_NOTATIONS
            operative_imports = operative_imports or notation == "[ontology].imports"
            check(ok, f"config law: operative form '{notation}' is in the lawful operative set"
                  if ok else
                  f"config law: form '{notation}' claims operative status outside "
                  f"{sorted(OPERATIVE_NOTATIONS)}")
        elif 'prov:value "refused"' in body:
            refs = REFERENCES_RE.findall(body)
            labeled = [r for r in refs
                       if "FM-" in stanza_by_subject.get(r, "")]
            ok = bool(refs) and bool(labeled)
            check(ok, f"config law: refused form '{notation}' cites FM- error-code evidence"
                  if ok else
                  f"config law: refused form '{notation}' lacks a dcterms:references anchor "
                  "whose label carries the witnessed FM- error code")
    check(operative_imports,
          "config law: [ontology].imports present and operative (the lawful pack binding)")

    # --- 9. rendered-consequence ownership -------------------------------------------
    owned = True
    for _, body in graph_stanzas:
        title_m = TITLE_RE.search(body)
        if title_m and "rendered consequence" in title_m.group(1):
            if "prov:wasDerivedFrom" not in body or "owning rule:" not in title_m.group(1):
                owned = False
                check(False, f"rendered-consequence law: '{title_m.group(1)}' must carry "
                      "prov:wasDerivedFrom and name its owning rule")
    check(owned and any("rendered consequence" in TITLE_RE.search(b).group(1)
                        for _, b in graph_stanzas if TITLE_RE.search(b)),
          "rendered-consequence law: every rendered-consequence fact is anchored and rule-owned")

    # --- 10. receipt runtime state -----------------------------------------------------
    receipt_ok = True
    saw_receipt_state = False
    for _, body in graph_stanzas:
        for value in PROV_VALUE_RE.findall(body):
            if value.startswith(".ggen"):
                saw_receipt_state = True
                title_m = TITLE_RE.search(body)
                title = title_m.group(1) if title_m else "(no title)"
                if "runtime state" not in title and "untracked" not in title:
                    receipt_ok = False
                    check(False, f"receipt law: '.ggen' state literal '{value}' declared without "
                          "runtime-state/untracked marking (secrets law)")
    check(receipt_ok and saw_receipt_state,
          "receipt law: .ggen* prov:value literals exist and are all marked untracked runtime state")

    # --- 11. single-writer fact files ----------------------------------------------------
    consumer_in_ontology = [s for s, _ in ontology_stanzas if ":consumer:" in s]
    check(not consumer_in_ontology,
          "fact-file law: no consumer-fact subjects in the pack ontology (single writer per file)"
          + (f" (violations: {consumer_in_ontology})" if consumer_in_ontology else ""))
    pack_in_fixture = [s for s, _ in fixture_stanzas if s and ":consumer:" not in s]
    check(not pack_in_fixture,
          "fact-file law: fixture carries only consumer-fact subjects"
          + (f" (violations: {pack_in_fixture})" if pack_in_fixture else ""))

    if failures:
        print(f"STRUCTURAL GATE: REFUSED ({len(failures)} refusal(s))")
        return 1
    print(f"STRUCTURAL GATE: PASS ({pack})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
