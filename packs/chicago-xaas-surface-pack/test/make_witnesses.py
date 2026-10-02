#!/usr/bin/env python3
"""Mint the same-stem witness corpus for the pack gates (L3 lane, v26.10.1).

  python3 test/make_witnesses.py

Writes test/fixtures/witnesses/pass/<gate>.ttl and test/fixtures/witnesses/fail/<gate>.ttl
for every gates/*.rq. The pass fixture is one self-contained minimal Chicago v26.10.1
source graph (clean on ALL gates); each fail fixture is the pass fixture plus ONE minimal
mutation named in MUTATIONS. Fixtures are consequences of this file - edit here, re-mint.

Also writes test/fixtures/corpus/corpus_full_pass.ttl (a copy of the clean graph) so
`run_courts.py corpus` has a lawful default corpus while L2's source/ is absent.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
PASS_DIR = ROOT / "test" / "fixtures" / "witnesses" / "pass"
FAIL_DIR = ROOT / "test" / "fixtures" / "witnesses" / "fail"
CORPUS_DIR = ROOT / "test" / "fixtures" / "corpus"

SUBJECT = "urn:chicago:agentic-payment:purchase-001"

PASS_TTL = f"""\
# L3 witness fixture (pass) - chicago-xaas-surface-pack
# Self-contained minimal Chicago v26.10.1 source graph for witness runs.
# Exact subject (literal): {SUBJECT}
@prefix sj: <https://ggen-igniter.dev/ontology/semantic-jira#> .
@prefix chi: <https://ggen-igniter.dev/sjira/v26.10.1/chicago#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

chi:purchase-001 a prov:Entity ;
    dcterms:identifier "{SUBJECT}" ;
    dcterms:isPartOf chi:GC-XAAS-26.10.1-CHICAGO .

chi:GC-XAAS-26.10.1-CHICAGO a sj:GoalCheckpoint ;
    dcterms:identifier "GC-XAAS-26.10.1-CHICAGO" ;
    rdfs:label "XaaS v26.10.1 Chicago ecosystem demo" ;
    sj:repository "seanchatmangpt/xaas" ;
    sj:projection chi:projection-machine, chi:projection-verification,
        chi:projection-executive, chi:projection-replay ;
    dcterms:hasPart
        chi:layer-sjira, chi:layer-graphlaw, chi:layer-sa2a, chi:layer-pplan,
        chi:layer-xaas, chi:layer-ocel, chi:layer-beam4pm, chi:layer-affidavit,
        chi:layer-surface, chi:layer-marketplace .

chi:layer-sjira a sj:GoalCheckpoint ; dcterms:identifier "CHI-101-SJIRA" ;
    sj:repository "seanchatmangpt/ggen_igniter" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-sjira .
chi:layer-graphlaw a sj:GoalCheckpoint ; dcterms:identifier "CHI-102-GRAPHLAW" ;
    sj:repository "seanchatmangpt/ash_graphlaw" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-graphlaw .
chi:layer-sa2a a sj:GoalCheckpoint ; dcterms:identifier "CHI-103-SA2A" ;
    sj:repository "seanchatmangpt/ash_a2a" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-sa2a .
chi:layer-pplan a sj:GoalCheckpoint ; dcterms:identifier "CHI-104-PPLAN" ;
    sj:repository "seanchatmangpt/ash_pplan" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-pplan .
chi:layer-xaas a sj:GoalCheckpoint ; dcterms:identifier "CHI-105-XAAS" ;
    sj:repository "seanchatmangpt/xaas" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-xaas .
chi:layer-ocel a sj:GoalCheckpoint ; dcterms:identifier "CHI-106-OCEL" ;
    sj:repository "seanchatmangpt/ash_ex4pm" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-ocel .
chi:layer-beam4pm a sj:GoalCheckpoint ; dcterms:identifier "CHI-107-BEAM4PM" ;
    sj:repository "seanchatmangpt/beam4pm" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-beam4pm .
chi:layer-affidavit a sj:GoalCheckpoint ; dcterms:identifier "CHI-108-AFFIDAVIT" ;
    sj:repository "seanchatmangpt/ash_affidavit" ; sj:boundaryClass sj:Core ;
    sj:requiresCapability chi:cap-affidavit .
chi:layer-surface a sj:GoalCheckpoint ; dcterms:identifier "CHI-109-SURFACE" ;
    sj:repository "seanchatmangpt/ash_surface" ; sj:boundaryClass sj:LastMile ;
    sj:requiresCapability chi:cap-surface .
chi:layer-marketplace a sj:GoalCheckpoint ; dcterms:identifier "CHI-110-MARKETPLACE" ;
    sj:repository "seanchatmangpt/ggen-marketplace" ; sj:boundaryClass sj:LastMile ;
    sj:requiresCapability chi:cap-marketplace .

chi:cap-sjira a sj:Capability ; sj:capabilityId "sjira:goal-graph" .
chi:cap-graphlaw a sj:Capability ; sj:capabilityId "graphlaw:semantic-admission" .
chi:cap-sa2a a sj:Capability ; sj:capabilityId "sa2a:capability-route" .
chi:cap-pplan a sj:Capability ; sj:capabilityId "ash_pplan:plan" .
chi:cap-xaas a sj:Capability ; sj:capabilityId "xaas:runtime" .
chi:cap-ocel a sj:Capability ; sj:capabilityId "ex4pm:ocel" .
chi:cap-beam4pm a sj:Capability ; sj:capabilityId "beam4pm:conformance" .
chi:cap-affidavit a sj:Capability ; sj:capabilityId "affidavit:standing" .
chi:cap-surface a sj:Capability ; sj:capabilityId "ash_surface:projection" .
chi:cap-marketplace a sj:Capability ; sj:capabilityId "ggen_marketplace:render" .

chi:projection-machine a sj:ProjectionSpec ;
    sj:projectionType "machine" ; sj:extension "json" ; sj:authorityClaim "NONE" .
chi:projection-verification a sj:ProjectionSpec ;
    sj:projectionType "verification" ; sj:extension "json" ; sj:authorityClaim "NONE" .
chi:projection-executive a sj:ProjectionSpec ;
    sj:projectionType "executive" ; sj:extension "json" ; sj:authorityClaim "NONE" .
chi:projection-replay a sj:ProjectionSpec ;
    sj:projectionType "replay" ; sj:extension "json" ; sj:authorityClaim "NONE" .

chi:case-authorized-bounded a sj:Prediction ;
    dcterms:identifier "CHI-CASE-001" ;
    sj:subject "{SUBJECT}" ;
    sj:candidateOnly true ; sj:authorityClaim "NONE" ; sj:observedStanding "UNKNOWN" .
chi:case-over-limit a sj:Prediction ;
    dcterms:identifier "CHI-CASE-002" ;
    sj:subject "{SUBJECT}" ;
    sj:candidateOnly true ; sj:authorityClaim "NONE" ; sj:observedStanding "UNKNOWN" .
"""

# gate stem -> (old, new): ONE minimal mutation per fail witness.
# The (old, new) pair must occur exactly once in PASS_TTL; asserted below.
MUTATIONS = {
    # REFUSED_CHICAGO_SUBJECT_DRIFT: one case drifts to a different subject literal.
    "010_subject_exact": (
        'dcterms:identifier "CHI-CASE-002" ;\n    sj:subject "%s" ;' % SUBJECT,
        'dcterms:identifier "CHI-CASE-002" ;\n    sj:subject "urn:chicago:agentic-payment:purchase-002" ;',
    ),
    # REFUSED_CHICAGO_LAYER_IDENTITY: two layers collide on one layer identifier.
    "020_layer_identity": (
        'dcterms:identifier "CHI-103-SA2A"',
        'dcterms:identifier "CHI-102-GRAPHLAW"',
    ),
    # REFUSED_CHICAGO_CAPABILITY_UNRESOLVED: a required capability loses its capabilityId.
    "030_capability_id": (
        'chi:cap-sa2a a sj:Capability ; sj:capabilityId "sa2a:capability-route" .',
        "chi:cap-sa2a a sj:Capability .",
    ),
    # REFUSED_CHICAGO_REPOSITORY_OWNER_MISSING: a required layer loses its repository owner.
    "040_repository_owner": (
        'chi:layer-xaas a sj:GoalCheckpoint ; dcterms:identifier "CHI-105-XAAS" ;\n    sj:repository "seanchatmangpt/xaas" ; sj:boundaryClass sj:Core ;',
        'chi:layer-xaas a sj:GoalCheckpoint ; dcterms:identifier "CHI-105-XAAS" ;\n    sj:boundaryClass sj:Core ;',
    ),
    # REFUSED_CHICAGO_IDENTITY_COLLISION: two capabilities claim one capabilityId.
    "050_identity_unique": (
        'sj:capabilityId "ex4pm:ocel"',
        'sj:capabilityId "beam4pm:conformance"',
    ),
    # REFUSED_CHICAGO_PROJECTION_VOCABULARY: projectionType leaves the closed vocabulary.
    "060_projection_vocab": (
        'sj:projectionType "replay"',
        'sj:projectionType "movie"',
    ),
    # REFUSED_CHICAGO_AUTHORITY_WIDENING: a projection claims authority it must not have.
    "070_authority_none": (
        'chi:projection-executive a sj:ProjectionSpec ;\n    sj:projectionType "executive" ; sj:extension "json" ; sj:authorityClaim "NONE" .',
        'chi:projection-executive a sj:ProjectionSpec ;\n    sj:projectionType "executive" ; sj:extension "json" ; sj:authorityClaim "DO" .',
    ),
}


def main():
    PASS_DIR.mkdir(parents=True, exist_ok=True)
    FAIL_DIR.mkdir(parents=True, exist_ok=True)
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    for stem, (old, new) in sorted(MUTATIONS.items()):
        if PASS_TTL.count(old) != 1:
            raise SystemExit(f"mutation anchor for {stem} occurs {PASS_TTL.count(old)}x, need exactly 1")
        (PASS_DIR / f"{stem}.ttl").write_text(PASS_TTL)
        (FAIL_DIR / f"{stem}.ttl").write_text(PASS_TTL.replace(old, new))
        print(f"minted {stem}: pass + fail (mutation: {new.strip()[:72]!r})")
    (CORPUS_DIR / "corpus_full_pass.ttl").write_text(PASS_TTL)
    print(f"minted corpus_full_pass.ttl (clean graph, {len(MUTATIONS)} witness pairs)")


if __name__ == "__main__":
    main()
