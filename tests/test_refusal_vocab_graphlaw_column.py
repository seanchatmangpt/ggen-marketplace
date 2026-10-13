"""Crosswalk court: the ash_graphlaw column of the refusal-vocabulary-pack.

Mirrors tests/test_refusal_vocab_erlmcp_column.py: pins the crosswalk's fifth
column (rv:GraphlawMapping, 40 codes keyed by rv:ashGraphlawCode) against the
LIVE ash_graphlaw source at /Users/sac/ash_graphlaw/lib/ash_graphlaw/refusal.ex
(the GENERATED closed table: class_of/1 + broken_term_of/1 clauses, @codes).

Verdicts (Chicago: real file reads, no mocks):
  1. the pack ontology parses and carries a graphlaw mapping for every live
     ash_graphlaw code, each with exactly one rv:ashA2aClass;
  2. definition-site check (fail-closed): every crosswalk code has BOTH a
     `def class_of(:code), do: ...` AND a `def broken_term_of(:code), do: ...`
     clause in the live refusal.ex, and the pinned rv:graphlawClass /
     rv:brokenTerm match the live clauses exactly;
  3. graphlaw-class law holds: each crosswalk row's S42 target agrees with the
     declared class law (refused_admission -> refused_rule, ... ) except the
     pinned per-code refinements;
  4. emitted-but-unmapped: live codes the crosswalk lacks are real findings;
     the unmapped allowlist is EMPTY (fail-closed: a future code with no
     honest class must carry rv:unmappedDisposition and no rv:ashA2aClass —
     never a forced mapping);
  5. the S42 target resolves to a declared rv:RefusalClass, and
     rv:ashA2aClass / rv:unmappedDisposition are mutually exclusive;
  6. drift meta-test: the pin is re-derived from the LIVE pack file and the
     LIVE refusal.ex at test time (BLOCKED-skip when the sibling is absent);
  7. sabotage twin: mutating a copy of the ontology makes the comparator
     fail, proving the court is non-vacuous.
"""

import os
import re

import pytest

pytest.importorskip("rdflib")
import rdflib

PACK_DIR = "/Users/sac/ggen-marketplace/packs/refusal-vocabulary-pack"
PACK_ONTOLOGY = os.path.join(PACK_DIR, "ontology.ttl")
GRAPHLAW_EX = "/Users/sac/ash_graphlaw/lib/ash_graphlaw/refusal.ex"

RV = rdflib.Namespace("urn:refusal-vocabulary:")

CLASS_OF_RE = re.compile(r"def class_of\(:([a-z_]+)\), do: :([A-Za-z0-9_]+)\s*$", re.M)
BROKEN_TERM_RE = re.compile(r"def broken_term_of\(:([a-z_]+)\), do: :([A-Za-z0-9_]+)\s*$", re.M)
CODES_RE = re.compile(r"@codes\s*\[(.*?)\]", re.S)

# ---------------------------------------------------------------------------
# The class law + pinned per-code refinements (mirror of the ontology block's
# documented law; any delta between ontology and this pin is a drift finding).
# ---------------------------------------------------------------------------

CLASS_LAW = {
    "refused_admission": "refused_rule",
    "refused_authority": "refused_authority",
    "blocked_resource": "blocked_resource",
    "refused_structure": "refused_structure",
    "refused_identity": "refused_identity",
    "unsupported": "unsupported_profile",
}
PINNED_REFINEMENTS = {
    "plan_refused": "refused_plan",
    "receipt_required": "refused_receipt",
    "engine_unclassified": "blocked_unknown",
    "duplicate_admission": "refused_identity",
    "missing_law_module": "refused_meta_rigor",
    "unknown_capability": "refused_capability",
}

# Fail-closed: EMPTY. A live ash_graphlaw code absent from the crosswalk is a
# real finding. Codes with no honest S42 class must instead carry
# rv:unmappedDisposition and NO rv:ashA2aClass in the crosswalk.
KNOWN_UNMAPPED = set()

S42_CLASSES = {
    "refused_identity", "refused_namespace", "refused_structure",
    "refused_shacl", "refused_rule", "refused_falsifier",
    "refused_provenance", "refused_profile", "refused_plan",
    "refused_capability", "refused_authority", "refused_consequence",
    "refused_receipt", "refused_bounds", "refused_meta_rigor",
    "blocked_unknown", "blocked_resource", "unsupported_profile",
}


# ---------------------------------------------------------------------------
# Parsers (real file reads; fail-closed on absence).
# ---------------------------------------------------------------------------


def pack_present():
    return os.path.isfile(PACK_ONTOLOGY)


def sibling_present():
    return os.path.isfile(GRAPHLAW_EX)


def parse_live_refusal():
    """Parse the LIVE refusal.ex closed table.

    Returns (codes, {code: class}, {code: broken_term}).
    """
    text = open(GRAPHLAW_EX, encoding="utf-8", errors="replace").read()
    classes = {c: cls for c, cls in CLASS_OF_RE.findall(text)}
    broken = {c: bt for c, bt in BROKEN_TERM_RE.findall(text)}
    codes = re.findall(r":([a-z_]+)", CODES_RE.search(text).group(1))
    return set(codes), classes, broken


def parse_crosswalk(path=PACK_ONTOLOGY):
    """Parse the pack ontology's graphlaw column.

    Returns ({code: {graphlawClass, brokenTerm, ashA2aClass or None,
    unmappedDisposition or None}}, set of declared rv:RefusalClass IRIs).
    """
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    rows = {}
    for m in g.subjects(rdflib.RDF.type, RV.GraphlawMapping):
        code = g.value(m, RV.ashGraphlawCode)
        assert code is not None, f"{m} has no rv:ashGraphlawCode"
        cls = g.value(m, RV.ashA2aClass)
        rows[str(code)] = {
            "graphlawClass": str(g.value(m, RV.graphlawClass)),
            "brokenTerm": str(g.value(m, RV.brokenTerm)),
            "ashA2aClass": str(cls) if cls is not None else None,
            "unmappedDisposition": _opt(g.value(m, RV.unmappedDisposition)),
        }
    declared = {local_class_name(str(c))
                for c in g.subjects(rdflib.RDF.type, RV.RefusalClass)}
    return rows, declared


def _opt(node):
    return str(node) if node is not None else None


def expected_s42_class(code, graphlaw_class):
    return PINNED_REFINEMENTS.get(code, CLASS_LAW[graphlaw_class])


def local_class_name(iri):
    """`urn:refusal-vocabulary:cls-refused-rule` -> `refused_rule`."""
    return (iri.rsplit("#", 1)[-1].rsplit(":", 1)[-1].removeprefix("cls-")
            .replace("-", "_"))


def compare_live_vs_pin():
    """Comparator for the drift meta-test and sabotage twin (graphlaw column).

    Returns a list of drift findings against the LIVE pack file (empty ==
    pin matches).
    """
    findings = []
    rows, declared = parse_crosswalk()
    live_codes, live_classes, live_broken = parse_live_refusal()
    mapped = set(rows)
    missing = sorted(live_codes - mapped - KNOWN_UNMAPPED)
    if missing:
        findings.append(f"live graphlaw codes absent from crosswalk: {missing}")
    extra = sorted(mapped - live_codes)
    if extra:
        findings.append(f"crosswalk codes absent from live refusal.ex: {extra}")
    for code, row in rows.items():
        if code not in live_classes:
            continue
        if row["graphlawClass"] != live_classes[code]:
            findings.append(
                f"{code}: graphlawClass {row['graphlawClass']} != live "
                f"{live_classes[code]}")
        if row["brokenTerm"] != live_broken.get(code):
            findings.append(
                f"{code}: brokenTerm {row['brokenTerm']} != live "
                f"{live_broken.get(code)}")
        want = expected_s42_class(code, row["graphlawClass"])
        got = local_class_name(row["ashA2aClass"] or "")
        if got != want:
            findings.append(
                f"{code}: S42 target {got} != class-law expectation {want}")
    return findings


# ---------------------------------------------------------------------------
# Courts.
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not pack_present(),
                    reason="BLOCKED: refusal-vocabulary-pack absent")
@pytest.mark.skipif(not sibling_present(),
                    reason="BLOCKED: ash_graphlaw sibling absent")
class TestGraphlawColumnTotality:
    def test_every_live_code_mapped_exactly_once(self):
        rows, _ = parse_crosswalk()
        live_codes, _, _ = parse_live_refusal()
        missing = sorted(live_codes - set(rows) - KNOWN_UNMAPPED)
        assert not missing, (
            "live ash_graphlaw codes with NO crosswalk mapping "
            f"(extend the column or pin an rv:unmappedDisposition): {missing}")
        extra = sorted(set(rows) - live_codes)
        assert not extra, (
            f"crosswalk codes absent from the live refusal.ex table: {extra}")

    def test_each_mapping_targets_exactly_one_declared_s42_class(self):
        rows, declared = parse_crosswalk()
        for code, row in rows.items():
            assert row["ashA2aClass"] or row["unmappedDisposition"], (
                f"{code}: neither ashA2aClass nor unmappedDisposition (silent gap)")
            if row["ashA2aClass"]:
                assert local_class_name(row["ashA2aClass"]) in declared, (
                    f"{code}: S42 target {row['ashA2aClass']} not a declared "
                    "rv:RefusalClass")
                assert not row["unmappedDisposition"], (
                    f"{code}: ashA2aClass and unmappedDisposition both set "
                    "(forced-mapping shape is banned)")
            else:
                assert row["unmappedDisposition"], (
                    f"{code}: unmapped without an explicit disposition")


@pytest.mark.skipif(not pack_present(),
                    reason="BLOCKED: refusal-vocabulary-pack absent")
@pytest.mark.skipif(not sibling_present(),
                    reason="BLOCKED: ash_graphlaw sibling absent")
class TestEveryCodeHasDefinitionSite:
    """Fail-closed: a crosswalk code with NO class_of/broken_term_of clause in
    the live refusal.ex is a real finding; the pinned class/brokenTerm must
    match the live clauses exactly."""

    def test_code_defined_with_matching_class_and_broken_term(self):
        rows, _ = parse_crosswalk()
        live_codes, live_classes, live_broken = parse_live_refusal()
        undefined = sorted(set(rows) - live_codes)
        assert not undefined, (
            "crosswalk codes with NO class_of/1 definition site in "
            f"lib/ash_graphlaw/refusal.ex: {undefined}")
        class_drift = {c: (r["graphlawClass"], live_classes[c])
                       for c, r in rows.items()
                       if r["graphlawClass"] != live_classes[c]}
        broken_drift = {c: (r["brokenTerm"], live_broken[c])
                        for c, r in rows.items()
                        if r["brokenTerm"] != live_broken[c]}
        assert not class_drift, f"rv:graphlawClass drift vs live table: {class_drift}"
        assert not broken_drift, f"rv:brokenTerm drift vs live table: {broken_drift}"

    def test_codes_list_agrees_with_clause_surface(self):
        """The GENERATED @codes list must equal the clause surface (if the
        generated file is internally inconsistent, the pin is unsound)."""
        live_codes, live_classes, live_broken = parse_live_refusal()
        assert live_codes == set(live_classes) == set(live_broken)


@pytest.mark.skipif(not pack_present(),
                    reason="BLOCKED: refusal-vocabulary-pack absent")
@pytest.mark.skipif(not sibling_present(),
                    reason="BLOCKED: ash_graphlaw sibling absent")
class TestClassLaw:
    def test_s42_targets_follow_class_law_or_pinned_refinements(self):
        rows, declared = parse_crosswalk()
        assert S42_CLASSES <= declared, (
            f"ontology no longer declares the 18-class universe: "
            f"{sorted(S42_CLASSES - declared)}")
        off_law = {}
        for code, row in rows.items():
            want = expected_s42_class(code, row["graphlawClass"])
            got = local_class_name(row["ashA2aClass"] or "")
            if got != want:
                off_law[code] = (got, want)
        assert not off_law, (
            "S42 targets off the class law and not in the pinned refinement "
            f"set {sorted(PINNED_REFINEMENTS)}: {off_law}")


@pytest.mark.skipif(not pack_present(),
                    reason="BLOCKED: refusal-vocabulary-pack absent")
@pytest.mark.skipif(not sibling_present(),
                    reason="BLOCKED: ash_graphlaw sibling absent")
class TestDriftMetaTest:
    """The pin must be re-derived from the LIVE pack + LIVE refusal.ex."""

    def test_live_pack_matches_pin(self):
        assert compare_live_vs_pin() == []


class TestSabotageTwin:
    """Mutating a copy of the ontology must make the comparator fail."""

    def test_dropped_mapping_is_detected(self, tmp_path):
        assert pack_present() and sibling_present()
        text = open(PACK_ONTOLOGY, encoding="utf-8").read()
        sabotaged = text.replace(
            'rv:ashGraphlawCode "not_admitted"',
            'rv:ashGraphlawCode "not_admitted_sabotaged"', 1)
        assert sabotaged != text, "sabotage edit did not apply"
        sab = tmp_path / "ontology.ttl"
        sab.write_text(sabotaged, encoding="utf-8")
        findings = compare_live_vs_pin_path(str(sab))
        assert findings, "sabotaged ontology produced NO findings (vacuous)"
        assert any("not_admitted_sabotaged" in f or "absent from crosswalk" in f
                   for f in findings)


def compare_live_vs_pin_path(path):
    rows, _ = parse_crosswalk(path)
    live_codes, _, _ = parse_live_refusal()
    findings = []
    missing = sorted(live_codes - set(rows))
    if missing:
        findings.append(f"live graphlaw codes absent from crosswalk: {missing}")
    extra = sorted(set(rows) - live_codes)
    if extra:
        findings.append(f"crosswalk codes absent from live refusal.ex: {extra}")
    return findings
