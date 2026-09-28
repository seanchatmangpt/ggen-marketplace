def admitted(p): return p.get('authority')=='NONE'
def test_do_refused(): assert not admitted({'authority':'DO'})
