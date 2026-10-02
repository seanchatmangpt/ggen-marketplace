"""Reconciliation court: population truth x conservation records."""
import pathlib, unittest

rdflib = None
try:
    import rdflib
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parents[1]
FTA = "https://ggen.dev/ontology/forced-top25-admissibility#"
FTR = "https://ggen.dev/ontology/forced-top25-reconciliation#"


def _graphs():
    if rdflib is None:
        raise unittest.SkipTest("rdflib unavailable")
    g = rdflib.Graph()
    for p in sorted((ROOT / "ontology").glob("*.ttl")):
        g.parse(p, format="turtle")
    g.parse(ROOT / "targets" / "population.ttl", format="turtle")
    return g


class ReconciliationCourt(unittest.TestCase):
    def test_population_is_exactly_25_one_per_repo(self):
        g = _graphs()
        rows = list(g.query(f"SELECT ?repo (COUNT(DISTINCT ?t) AS ?n) WHERE {{ ?t a <{FTA}FanoutTarget> ; <{FTA}repo> ?repo . }} GROUP BY ?repo HAVING(COUNT(DISTINCT ?t) != 1)"))
        self.assertEqual(rows, [])
        total = list(g.query(f"SELECT (COUNT(DISTINCT ?t) AS ?n) WHERE {{ ?t a <{FTA}FanoutTarget> . }}"))
        self.assertEqual(int(total[0][0]), 25)

    def test_every_repo_has_a_reconciliation_record(self):
        g = _graphs()
        missing = list(g.query(f"""
            SELECT ?repo WHERE {{
              ?t a <{FTA}FanoutTarget> ; <{FTA}repo> ?repo .
              FILTER NOT EXISTS {{ ?rec a <{FTR}HeadReconciliation> ; <{FTR}repo> ?repo . }} }}"""))
        self.assertEqual(missing, [])

    def test_three_real_sha_conflicts_recorded_and_b_won(self):
        g = _graphs()
        rows = list(g.query(f"""
            SELECT ?repo ?winner WHERE {{
              ?rec a <{FTR}HeadReconciliation> ; <{FTR}conflictClass> "REAL_SHA_CONFLICT" ;
                   <{FTR}repo> ?repo ; <{FTR}winnerHead> ?winner ; <{FTR}winnerSourcePack> ?pack .
              FILTER(?pack = "forced-top25-standard-consumer-factory-pack") }} ORDER BY ?repo"""))
        repos = [str(r[0]) for r in rows]
        self.assertEqual(repos, [
            "seanchatmangpt/ex4pm", "seanchatmangpt/gymact", "seanchatmangpt/xaas"])

    def test_real_sha_conflict_winners_are_newest(self):
        g = _graphs()
        stale = list(g.query(f"""
            SELECT ?rec WHERE {{
              ?rec a <{FTR}HeadReconciliation> ; <{FTR}conflictClass> "REAL_SHA_CONFLICT" ;
                   <{FTR}winnerObservedAt> ?w ; <{FTR}losingObservedAt> ?l .
              FILTER(?w < ?l) }}"""))
        self.assertEqual(stale, [])
        # UNKNOWN_SUPERSEDED rows: the loser asserted no head, so recency does
        # not decide; the winner is carried by population (checked below).
        uncarrried = list(g.query(f"""
            SELECT ?rec WHERE {{
              ?rec a <{FTR}HeadReconciliation> ; <{FTR}repo> ?repo ; <{FTR}winnerHead> ?winner .
              FILTER NOT EXISTS {{
                ?t a <{FTA}FanoutTarget> ; <{FTA}repo> ?repo .
                {{ ?t <{FTA}exactCurrentHead> ?winner }} UNION {{ ?t <{FTA}exactHead> ?winner }} }} }}"""))
        self.assertEqual(uncarrried, [])

    def test_population_records_stamped(self):
        g = _graphs()
        unstamped = list(g.query(f"""
            SELECT ?t WHERE {{ ?t a <{FTA}FanoutTarget> .
              FILTER NOT EXISTS {{ ?t <{FTA}observedAt> ?ts }} }}"""))
        self.assertEqual(unstamped, [])


if __name__ == "__main__":
    unittest.main()
