class Refused(ValueError): pass
def current(rows):
    rows=tuple(rows)
    if not rows: raise Refused('REFUSED[NO_CONTROL_FRONTIER]')
    g=max(r['generation'] for r in rows); latest=[r for r in rows if r['generation']==g]
    ids={(r['subject_sha'],r['semantic_digest']) for r in latest}
    if len(ids)!=1: raise Refused('REFUSED[SPLIT_CONTROL_FRONTIER]')
    return sorted(latest,key=lambda r:(r['subject_sha'],r['semantic_digest']))[0]
