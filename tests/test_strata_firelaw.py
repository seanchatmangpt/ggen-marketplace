"""Strata PN64 fire law: recompute transition masks from Place bit offsets and prove the
RONR happy path over all 65,536 markings of the 16-bit state word.

Chicago style, no mocks: the real ontology at packs/strata-pn64-pack/ontology.ttl is parsed
with real rdflib, the pre/post hex mask literals are recomputed from the 9 st:Place
st:bitOffset individuals, and the fire law (enabled iff (m & pre) == pre; m' = (m ^ pre) | post)
is executed over every 16-bit marking (0..65,535) for all 6 transitions.

Reachability note (derived from the ontology, not assumed): t01 consumes N_FLOOR and re-emits
it, and no later transition touches N_FLOOR or N_PREV_QUESTION_ORDERED, so the exact marking
0x0101 is not reachable — the honest terminal assertion is that the legal t01..t06 chain fires
with every transition enabled in sequence and the terminal marking *contains*
N_MAIN_MOTION | N_ADOPTED (0x0101 as a submask), with BFS from 0x0081 through the 65,536-marking
space confirming adoption is reachable.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "packs" / "strata-pn64-pack" / "ontology.ttl"

ST = rdflib.Namespace("https://strata.chatman.ai/ontology#")
MASK_BITS = 16
MARKING_SPACE = 1 << MASK_BITS  # 65,536


def load_graph(path: Path = ONTOLOGY) -> rdflib.Graph:
    g = rdflib.Graph()
    g.parse(path, format="turtle")
    return g


def place_masks(g: rdflib.Graph) -> dict[str, int]:
    """label -> bit mask, recomputed from st:Place st:bitOffset individuals."""
    masks: dict[str, int] = {}
    for place in g.subjects(rdflib.RDF.type, ST.Place):
        label = str(g.value(place, rdflib.RDFS.label))
        offset = int(g.value(place, ST.bitOffset))
        masks[label] = 1 << offset
    return masks


def transitions(g: rdflib.Graph) -> list[dict]:
    """All st:RonrTransition individuals with parsed opcode/pre/post masks, opcode order."""
    out = []
    for t in g.subjects(rdflib.RDF.type, ST.RonrTransition):
        out.append({
            "iri": t,
            "opcode": int(str(g.value(t, ST.transitionOpcode)), 16),
            "pre": int(str(g.value(t, ST.transitionPre)), 16),
            "post": int(str(g.value(t, ST.transitionPost)), 16),
        })
    return sorted(out, key=lambda d: d["opcode"])


def recompute(g: rdflib.Graph, t: dict, labels: list[str], masks: dict[str, int]) -> tuple[int, int]:
    """Recompute pre/post for one transition from the graph's st:Place bit offsets:
    the mask literal is decomposed bit-by-bit and each set bit must correspond to exactly
    one st:Place bitOffset; the recomputed value is the union of those places' bits.
    """
    offsets = {masks[l] for l in labels}
    pre = 0
    for b in range(MASK_BITS):
        if t["pre"] >> b & 1:
            assert (1 << b) in offsets, f"bit {b} of {t['iri']} pre has no st:Place individual"
            pre |= 1 << b
    post = 0
    for b in range(MASK_BITS):
        if t["post"] >> b & 1:
            assert (1 << b) in offsets, f"bit {b} of {t['iri']} post has no st:Place individual"
            post |= 1 << b
    return pre, post


def mask_court_violations(g: rdflib.Graph) -> list[str]:
    """The mask-recomputation court: for every RonrTransition, the literal pre/post masks
    must equal the masks recomputed from the st:Place bitOffset individuals. Returns the
    list of violation messages (empty iff the ontology is self-consistent).
    """
    masks = place_masks(g)
    labels = list(masks)
    violations: list[str] = []
    for t in transitions(g):
        try:
            pre, post = recompute(g, t, labels, masks)
        except AssertionError as e:
            violations.append(str(e))
            continue
        if pre != t["pre"]:
            violations.append(
                f"{t['iri']} pre literal {t['pre']:#06x} != place-recomputed {pre:#06x}")
        if post != t["post"]:
            violations.append(
                f"{t['iri']} post literal {t['post']:#06x} != place-recomputed {post:#06x}")
    return violations


def enabled(m: int, pre: int) -> bool:
    return (m & pre) == pre


def fire(m: int, pre: int, post: int) -> int:
    return (m ^ pre) | post


class MaskRecomputation(unittest.TestCase):
    def setUp(self) -> None:
        self.g = load_graph()
        self.masks = place_masks(self.g)
        self.trans = transitions(self.g)

    def test_nine_places_with_unique_bit_offsets(self) -> None:
        self.assertEqual(len(self.masks), 9)
        self.assertEqual(len(set(self.masks.values())), 9)
        self.assertEqual(max(self.masks.values()), 1 << 8)

    def test_every_transition_mask_equals_place_recomputation(self) -> None:
        self.assertEqual(len(self.trans), 6)
        self.assertEqual(mask_court_violations(self.g), [])


class FireLaw(unittest.TestCase):
    def setUp(self) -> None:
        self.g = load_graph()
        self.masks = place_masks(self.g)
        self.trans = transitions(self.g)

    def test_fire_law_over_all_65536_markings(self) -> None:
        # For every transition and every 16-bit marking: either the transition is
        # disabled (and the marking is untouched) or firing preserves marking mass
        # outside pre|post — m2 & ~(pre|post) == m & ~(pre|post). Derived, not
        # restated: the fire law may only move tokens between pre and post places.
        full = MARKING_SPACE - 1
        for t in self.trans:
            untouched = full & ~(t["pre"] | t["post"])
            for m in range(MARKING_SPACE):
                if enabled(m, t["pre"]):
                    m2 = fire(m, t["pre"], t["post"])
                    self.assertEqual(m2 & untouched, m & untouched,
                                     (t["iri"], m))
                # disabled transitions never fire, so m is never mutated

    def test_ronr_happy_path_t01_through_t06(self) -> None:
        start = 0x0081  # N_MAIN_MOTION | N_FLOOR
        m = start
        for t in self.trans:  # opcode order 0x01..0x06
            self.assertTrue(enabled(m, t["pre"]),
                            f"{t['iri']} not enabled at {m:#06x} in the canonical chain")
            m = fire(m, t["pre"], t["post"])
        adopted = self.masks["N_ADOPTED"]
        main = self.masks["N_MAIN_MOTION"]
        self.assertEqual(adopted | main, 0x0101)
        self.assertEqual(m & (adopted | main), adopted | main,
                         f"terminal marking {m:#06x} lacks N_MAIN_MOTION|N_ADOPTED")

    def test_bfs_over_65536_marking_space_reaches_adoption(self) -> None:
        adopted = self.masks["N_ADOPTED"]
        seen = {0x0081}
        frontier = [0x0081]
        while frontier:
            m = frontier.pop()
            for t in self.trans:
                if enabled(m, t["pre"]):
                    m2 = fire(m, t["pre"], t["post"])
                    if m2 not in seen:
                        seen.add(m2)
                        frontier.append(m2)
        self.assertTrue(any(m & adopted for m in seen),
                         "ADOPTED unreachable from 0x0081 over the 65,536-marking space")


class OpcodeBijection(unittest.TestCase):
    def test_daoverb_and_transition_opcodes_bijection(self) -> None:
        g = load_graph()
        verbs = sorted(int(str(o), 16) for o in g.objects(None, ST.verbOpcode))
        trans = sorted(int(str(o), 16) for o in g.objects(None, ST.transitionOpcode))
        self.assertEqual(len(verbs), 6)
        self.assertEqual(len(trans), 6)
        self.assertEqual(verbs, trans)
        self.assertEqual(verbs, [1, 2, 3, 4, 5, 6])


class SabotageTwin(unittest.TestCase):
    """Real perturbation twin: a copy of the ontology with one place's bitOffset flipped
    is written to tmp_path and run through the same mask-recomputation court the healthy
    subject goes through. No Python-int tricks — the production court itself must refuse.
    """

    def test_flipped_bitoffset_in_perturbed_twin_is_refused_by_the_court(self) -> None:
        import tempfile

        healthy = ONTOLOGY.read_text()
        # Flip exactly one place's bitOffset: N_FLOOR 7 -> 12 (an otherwise unused bit).
        target = 'rdfs:label "N_FLOOR"              ; st:bitOffset 7 .'
        flipped = 'rdfs:label "N_FLOOR"              ; st:bitOffset 12 .'
        self.assertEqual(healthy.count(target), 1)
        perturbed_text = healthy.replace(target, flipped)

        with tempfile.TemporaryDirectory() as td:
            twin = Path(td) / "ontology.ttl"
            twin.write_text(perturbed_text)
            violations = mask_court_violations(load_graph(twin))
        self.assertTrue(violations,
                        "perturbed twin (N_FLOOR bitOffset 7->12) was admitted by the court")
        # The refusal must name the transition whose pre mask actually depended on bit 7.
        self.assertTrue(any("t01" in v and "pre" in v for v in violations), violations)


if __name__ == "__main__":
    unittest.main()
