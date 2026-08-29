def select(candidates,strategy='MAX_GAIN'):
    values=tuple(candidates)
    if not values:
        raise ValueError('REFUSED[EMPTY_CONTROL_FRONTIER]')
    if strategy=='MAX_GAIN':
        return max(values,key=lambda x:(x['gain'],-x['false_rate'],-x['root_concentration'],x['id']))
    if strategy=='MIN_FALSE_CAPITAL':
        return min(values,key=lambda x:(x['false_rate'],-x['gain'],x['id']))
    if strategy=='MIN_CONCENTRATION':
        return min(values,key=lambda x:(x['root_concentration'],-x['gain'],x['id']))
    raise ValueError('REFUSED[UNKNOWN_CONTROL_STRATEGY]')
