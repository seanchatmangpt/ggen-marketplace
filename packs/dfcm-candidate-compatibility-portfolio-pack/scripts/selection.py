def select(portfolios, scores):
    if not portfolios: raise ValueError('REFUSED[NO_COMPATIBLE_PORTFOLIO]')
    def key(p):
        values=[scores[x] for x in p]
        return (min(v['evidence'] for v in values),sum(v['dependency_relief'] for v in values),-sum(v['rollback'] for v in values),len(p),tuple(p))
    return max(portfolios,key=key)
