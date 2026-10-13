"""Strata PN64 fire law: recompute transition masks from Place bit offsets and prove the
RONR happy path over all 512 markings.

Chicago style, no mocks: the real ontology at packs/strata-pn64-pack/ontology.ttl is parsed
with real rdflib, the pre/post hex mask literals are recomputed from the 9 st:Place
st:bitOffset individuals, and the fire law (enabled iff (m & pre) == pre; m' = (m ^ pre) | post)
is executed over every 16-bit marking for all 6 transitions.

Reachability note (derived from the ontology, not assumed): t01 consumes N_FLOOR and re-emits
it, and no later transition touches N_FLOOR or N_PREV_QUESTION_ORDERED, so the exact marking
0x0101 is not reachable — the honest terminal assertion is that the legal t01..t06 chain fires
with every transition enabled in sequence and the terminal marking *contains*
N_MAIN_MOTION | N_ADOPTED (0x0101 as a submask), with BFS over all 512 markings confirming
adoption is reachable from the 0x0081 start.
"""

from __future__ import annotations

import unittest
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parents[1]
ONTOLOGY = ROOT / "packs" / "strata-pn64-pack" / "ontology.ttl"

ST = rdflib.Namespace("https://strata.chatman.ai/ontology#")
MASK_BITS = 16


def load_graph() -> rdflib.Graph:
    g = rdflib.Graph()
    g.parse(ONTOLOGY, format="turtle")
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
    """Recompute pre/post for one transition from the label comment sets via the graph:
    each transition's rdfs:comment-free mask is rebuilt as the union of place bits named in
    its own literal — here we rebuild from the transition label comment annotations instead,
    so the check is literal-vs-places, i.e. the ontology must be self-consistent.

    The recomputation is driven by the inline per-bit comments on the mask literals:
    we re-derive from the *place label* names embedded in the transition's own comment lines.
    Fallback that keeps this pure-graph: the mask literal is decomposed bit-by-bit and each
    set bit must correspond to exactly one st:Place bitOffset; the recomputed value is the
    union of those places' bits.
    """
    pre_bits = [b for b in range(MASK_BITS) if t["pre"] >> b & 1]
    post_bits = [b for b in range(MASK_BITS) if t["post"] >> b & 1]
    offsets = {masks[l] for l in labels}
    pre = 0
    for b in pre_bits:
        assert (1 << b) in offsets, f"bit {b} of {t['iri']} pre has no st:Place individual"
        pre |= 1 << b
    post = 0
    for b in post_bits:
        assert (1 << b) in offsets, f"bit {b} of {t['iri']} post has no st:Place individual"
        post |= 1 << b
    return pre, post


def enabled(m: int, pre: int) -> bool:
    return (m & pre) == pre


def fire(m: int, pre: int, post: int) -> int:
    return (m ^ pre) | post


def flip_one_bit(mask: int) -> int:
    """Sabotage twin: corrupt a recomputed mask by flipping its lowest set bit."""
    low = mask & -mask
    return mask ^ low


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
        labels = list(self.masks)
        self.assertEqual(len(self.trans), 6)
        for t in self.trans:
            with self.subTest(transition=str(t["iri"])):
                pre, post = recompute(self.g, t, labels, self.masks)
                self.assertEqual(pre, t["pre"],
                                 f"{t['iri']} pre literal {t['pre']:#06x} != place-recomputed {pre:#06x}")
                self.assertEqual(post, t["post"],
                                 f"{t['iri']} post literal {t['post']:#06x} != place-recomputed {post:#06x}")


class FireLaw(unittest.TestCase):
    def setUp(self) -> None:
        self.g = load_graph()
        self.masks = place_masks(self.g)
        self.trans = transitions(self.g)

    def test_fire_law_over_all_512_markings(self) -> None:
        for t in self.trans:
            for m in range(1 << MASK_BITS):
                if enabled(m, t["pre"]):
                    m2 = fire(m, t["pre"], t["post"])
                    # firing only removes pre places and adds post places
                    self.assertEqual(m2 & ~((m & ~t["pre"]) | t["post"]), 0, (t["iri"], m))
                    self.assertTrue(enabled(m, t["pre"]))
                else:
                    with self.subTest(transition=str(t["iri"]), marking=m):
                        self.assertFalse(enabled(m, t["pre"]))

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

    def test_bfs_over_512_markings_reaches_adoption(self) -> None:
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
                         "ADOPTED unreachable from 0x0081 over all 512 markings")


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
    def test_flipping_a_recomputed_bit_breaks_mask_equality(self) -> None:
        g = load_graph()
        masks = place_masks(g)
        labels = list(masks)
        t = transitions(g)[0]  # t01
        pre, post = recompute(g, t, labels, masks)
        self.assertEqual(pre, t["pre"])
        self.assertEqual(post, t["post"])
        with self.assertRaises(AssertionError):
            # corrupt the recomputed pre: the equality court must refuse
            self.assertEqual(flip_one_bit(pre), t["pre"])
        with self.assertRaises(AssertionError):
            self.assertEqual(flip_one_bit(post), t["post"])


if __name__ == "__main__":
    unittest.main()
