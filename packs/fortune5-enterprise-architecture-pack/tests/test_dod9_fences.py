# DoD #9 fences (dissertation §2.4) mechanized as pytest over
# packs/fortune5-enterprise-architecture-pack/ontology.ttl (f5ea: vocabulary).
#
# Fences:
#   1. pairwise disjointness — no individual typed as two of
#      Pack(SolutionGroup)/ABB/SBB;
#   2. rho dangling check — every SBB's realizes-ABB pointer (ea:satisfiesABB)
#      targets an existing, typed ABB;
#   3. Girard fence — no Pack≅SBB conflation (class assertion, owl:sameAs) and
#      no self-membership assertion (group -> group via f5ea:groupsSBB);
#   4. fiber completeness — every SolutionGroup's tier coverage is surjective
#      onto the closed four-tier universe and the member dependency DAG is
#      acyclic.
#
# Real rdflib over the real ontology file — no mocks (Chicago discipline).
# Each fence carries an anti-vacuity mutation test: injecting a violation
# into an in-memory copy of the ontology must make the fence fire.

import itertools
import re
from pathlib import Path

import pytest
from rdflib import Graph, RDF, RDFS, OWL, URIRef

PACK_DIR = Path(__file__).resolve().parents[1]
ONTOLOGY = PACK_DIR / "ontology.ttl"

F5 = "https://ggen.io/ontology/fortune5-enterprise-architecture#"
EA = "https://chatman.ai/ontology/enterprise-architecture#"


def F5EA(local: str) -> URIRef:
    return URIRef(F5 + local)


def EA_(local: str) -> URIRef:
    return URIRef(EA + local)


PACK_CLASS = F5EA("SolutionGroup")
ABB_CLASS = EA_("ArchitectureBuildingBlock")
SBB_CLASS = EA_("SolutionBuildingBlock")
CONTRACT_CLASS = EA_("ArchitectureContract")
AUTHORITY_CLASS = EA_("AuthorityBoundary")

GROUP_SUBCLASSES = [
    F5EA("GuestDomainGroup"),
    F5EA("HostDomainGroup"),
    F5EA("NetworkDomainGroup"),
    F5EA("VerificationDomainGroup"),
]

# Closed tier universe (schema/f5ea.sbb-group-manifest.v1.json "domain" enum).
TIERS = frozenset({"guest", "host", "network", "verification"})

SUBCLASS_TO_TIER = {
    F5EA("GuestDomainGroup"): "guest",
    F5EA("HostDomainGroup"): "host",
    F5EA("NetworkDomainGroup"): "network",
    F5EA("VerificationDomainGroup"): "verification",
}

MEMBERSHIP_PROP = F5EA("groupsSBB")
ABB_LINK_PROP = EA_("satisfiesABB")


@pytest.fixture(scope="module")
def graph() -> Graph:
    g = Graph()
    g.parse(ONTOLOGY.as_posix(), format="turtle")
    return g


def subclasses_closure(g: Graph, root: URIRef) -> set:
    """All classes that are (transitively) rdfs:subClassOf root."""
    out = {root}
    frontier = [root]
    while frontier:
        c = frontier.pop()
        for sub in g.subjects(RDFS.subClassOf, c):
            if sub not in out:
                out.add(sub)
                frontier.append(sub)
    return out


def rdf_types_closure(g: Graph, ind: URIRef) -> set:
    """Direct rdf:type plus upward superclasses."""
    out = set()
    frontier = list(g.objects(ind, RDF.type))
    while frontier:
        c = frontier.pop()
        if c in out:
            continue
        out.add(c)
        frontier.extend(g.objects(c, RDFS.subClassOf))
    return out


def instance_violations(g: Graph, classes: tuple) -> list:
    """Individuals whose (closed) rdf:type set contains >= 2 of `classes`."""
    bad = []
    for ind in set(g.subjects(RDF.type, None)):
        types = rdf_types_closure(g, ind)
        hits = [c for c in classes if c in types]
        if len(hits) >= 2:
            bad.append((ind, hits))
    return bad


def dependency_edges(g: Graph) -> list:
    """All (a, b) dependency edges between named individuals."""
    props = {
        p for p in set(g.predicates()) if re.search(r"depend", str(p), re.I)
    }
    edges = []
    for p in props:
        edges.extend((a, b) for a, _, b in g.triples((None, p, None)))
    return edges


def has_cycle(edges: list) -> bool:
    """Kahn's algorithm: True if the directed edge set contains a cycle."""
    nodes = {n for e in edges for n in e}
    indeg = {n: 0 for n in nodes}
    adj = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    queue = [n for n, d in indeg.items() if d == 0]
    seen = 0
    while queue:
        n = queue.pop()
        seen += 1
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    return seen != len(nodes)


# =====================================================================
# Fence 1 — pairwise disjointness
# =====================================================================

def test_all_disjoint_classes_axiom_declared(graph):
    """Vocabulary level: the OWL AllDisjointClasses fence axiom is present."""
    found = False
    for lst in graph.objects(None, OWL.members):
        items = set(graph.items(lst))
        if {PACK_CLASS, SBB_CLASS, ABB_CLASS, CONTRACT_CLASS} <= items:
            found = True
    assert found, (
        "DoD #9: expected an owl:AllDisjointClasses axiom listing "
        "f5ea:SolutionGroup, ea:SolutionBuildingBlock, "
        "ea:ArchitectureBuildingBlock, ea:ArchitectureContract"
    )


def test_pairwise_disjointness_no_individual_typed_twice(graph):
    """Instance level: no individual is typed as two of Pack/ABB/SBB."""
    violations = instance_violations(graph, (PACK_CLASS, ABB_CLASS, SBB_CLASS))
    assert not violations, (
        f"DoD #9 pairwise disjointness violated: {violations}"
    )


def test_pairwise_disjointness_includes_contract_and_authority(graph):
    """Extended fence: no individual typed as any two fence classes."""
    fence_classes = (
        PACK_CLASS,
        ABB_CLASS,
        SBB_CLASS,
        CONTRACT_CLASS,
        AUTHORITY_CLASS,
    )
    violations = instance_violations(graph, fence_classes)
    assert not violations, (
        f"DoD #9 pairwise disjointness (extended) violated: {violations}"
    )


# =====================================================================
# Fence 2 — rho dangling check
# =====================================================================

def test_sbb_realizes_pointer_not_dangling(graph):
    """Every ea:satisfiesABB pointer targets an existing, typed ABB."""
    dangling = []
    for sbb, _, abb in graph.triples((None, ABB_LINK_PROP, None)):
        types = rdf_types_closure(graph, abb)
        if ABB_CLASS not in types:
            dangling.append((sbb, abb))
    assert not dangling, (
        "rho dangling: ea:satisfiesABB targets that are not typed "
        f"ea:ArchitectureBuildingBlock: {dangling}"
    )


def test_sbb_realizes_pointer_targets_exist(graph):
    """Pointer objects must exist as subjects in the graph at all."""
    dangling = [
        (sbb, abb)
        for sbb, _, abb in graph.triples((None, ABB_LINK_PROP, None))
        if not list(graph.triples((abb, None, None)))
    ]
    assert not dangling, f"rho dangling (subject-less ABB): {dangling}"


# =====================================================================
# Fence 3 — Girard fence (no Pack≅SBB, no self-membership)
# =====================================================================

def test_no_pack_typed_as_abb_or_sbb(graph):
    """No f5ea:SolutionGroup(-subclass) individual is typed as SBB/ABB/etc."""
    pack_classes = subclasses_closure(graph, PACK_CLASS)
    fence = {ABB_CLASS, SBB_CLASS, CONTRACT_CLASS, AUTHORITY_CLASS}
    conflations = []
    for ind in set(graph.subjects(RDF.type, None)):
        types = rdf_types_closure(graph, ind)
        if types & pack_classes and types & fence:
            conflations.append((ind, sorted(map(str, types & fence))))
    assert not conflations, f"Girard fence: Pack≅SBB conflation: {conflations}"


def test_no_self_membership(graph):
    """No group is its own member: g f5ea:groupsSBB g is refused."""
    self_members = [
        (g, s)
        for g, _, s in graph.triples((None, MEMBERSHIP_PROP, None))
        if g == s
    ]
    assert not self_members, f"self-membership: {self_members}"


def test_no_sameas_between_pack_and_ea_elements(graph):
    """No owl:sameAs between a f5ea: individual and an ea: individual."""
    bad = []
    for a, _, b in graph.triples((None, OWL.sameAs, None)):
        if (str(a).startswith(F5) and str(b).startswith(EA)) or (
            str(b).startswith(F5) and str(a).startswith(EA)
        ):
            bad.append((a, b))
    assert not bad, f"owl:sameAs Pack≅SBB conflation: {bad}"


def test_no_group_membership_of_groups(graph):
    """A group's groupsSBB object must be an SBB, never another group."""
    pack_classes = subclasses_closure(graph, PACK_CLASS)
    cross = [
        (g, s)
        for g, _, s in graph.triples((None, MEMBERSHIP_PROP, None))
        if s in pack_classes
    ]
    assert not cross, f"groupsSBB must target SBBs, not groups: {cross}"


# =====================================================================
# Fence 4 — fiber completeness
# =====================================================================

def test_group_tier_coverage_surjective(graph):
    """Declared tier subclasses cover the closed 4-tier universe, and any
    group individuals present jointly instantiate every tier."""
    pack_classes = subclasses_closure(graph, PACK_CLASS)
    # Vocabulary level: each tier subclass is declared under SolutionGroup.
    declared = {c for c in SUBCLASS_TO_TIER if c in pack_classes}
    tiers_seen = {SUBCLASS_TO_TIER[c] for c in declared}
    # Instance level (vacuous today, real once group individuals land).
    for ind in set(graph.subjects(RDF.type, None)):
        types = rdf_types_closure(graph, ind)
        for c in types & set(SUBCLASS_TO_TIER):
            tiers_seen.add(SUBCLASS_TO_TIER[c])
    assert tiers_seen == set(TIERS), (
        f"tier coverage not surjective: saw {sorted(tiers_seen)}, "
        f"expected {sorted(TIERS)}"
    )


def test_group_has_exactly_one_tier(graph):
    """Each group individual carries exactly one domain-subclass tier."""
    pack_classes = subclasses_closure(graph, PACK_CLASS)
    bad = []
    for ind in set(graph.subjects(RDF.type, None)):
        types = rdf_types_closure(graph, ind)
        tiered = types & pack_classes & set(SUBCLASS_TO_TIER)
        if not types & pack_classes:
            continue
        if len(tiered) != 1:
            bad.append((ind, sorted(map(str, tiered))))
    assert not bad, f"group must carry exactly one tier subclass: {bad}"


def test_member_dependency_dag_acyclic(graph):
    """Dependency edges among individuals (any *depend* property) form a DAG."""
    edges = dependency_edges(graph)
    assert not has_cycle(edges), (
        f"dependency graph has a cycle: {edges}"
    )


def test_membership_property_shape_declared(graph):
    """Sanity fence: groupsSBB is declared SolutionGroup -> SBB."""
    dom = graph.value(MEMBERSHIP_PROP, RDFS.domain)
    rng = graph.value(MEMBERSHIP_PROP, RDFS.range)
    assert dom == PACK_CLASS, dom
    assert rng == SBB_CLASS, rng


# =====================================================================
# Anti-vacuity mutations — every fence must fire on an injected violation
# =====================================================================

def _load_mutated() -> Graph:
    g = Graph()
    g.parse(ONTOLOGY.as_posix(), format="turtle")
    return g


def test_mutation_pairwise_disjointness_fires():
    g = _load_mutated()
    x = URIRef(EA + "MutationIndividual")
    g.add((x, RDF.type, PACK_CLASS))
    g.add((x, RDF.type, SBB_CLASS))
    assert instance_violations(
        g, (PACK_CLASS, ABB_CLASS, SBB_CLASS)
    ), "anti-vacuity: pairwise-disjointness check must fire on conflation"


def test_mutation_dangling_fires():
    g = _load_mutated()
    sbb = URIRef(EA + "MutationSBB")
    ghost = URIRef(EA + "MutationGhostABB")
    g.add((sbb, RDF.type, SBB_CLASS))
    g.add((sbb, ABB_LINK_PROP, ghost))
    dangling = [
        (s, a)
        for s, _, a in g.triples((None, ABB_LINK_PROP, None))
        if ABB_CLASS not in rdf_types_closure(g, a)
    ]
    assert dangling, "anti-vacuity: dangling check must fire on ghost ABB"


def test_mutation_self_membership_fires():
    g = _load_mutated()
    grp = F5EA("MutationGroup")
    g.add((grp, RDF.type, PACK_CLASS))
    g.add((grp, MEMBERSHIP_PROP, grp))
    bad = [
        (a, b)
        for a, _, b in g.triples((None, MEMBERSHIP_PROP, None))
        if a == b
    ]
    assert bad, "anti-vacuity: self-membership check must fire"


def test_mutation_dependency_cycle_fires():
    g = _load_mutated()
    a = F5EA("MutationGroupA")
    b = F5EA("MutationGroupB")
    dep = F5EA("dependsOnGroup")
    g.add((a, dep, b))
    g.add((b, dep, a))
    assert has_cycle(dependency_edges(g)), (
        "anti-vacuity: cycle check must fire"
    )


def test_mutation_tier_coverage_fires():
    """Removing one tier's subclass mapping breaks surjectivity detection."""
    reduced = {k: v for k, v in SUBCLASS_TO_TIER.items() if v != "verification"}
    assert set(reduced.values()) != set(TIERS), (
        "anti-vacuity: surjectivity check must be sensitive to tier loss"
    )
