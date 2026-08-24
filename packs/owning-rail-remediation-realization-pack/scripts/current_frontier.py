def current(observations):
    values=tuple(observations)
    if not values:
        raise ValueError("REFUSED[EMPTY_REALIZATION_FRONTIER]")
    generation=max(o[0] for o in values)
    latest=[o for o in values if o[0]==generation]
    digests={o[1] for o in latest}
    if len(digests)!=1:
        raise ValueError("REFUSED[SPLIT_REALIZATION_FRONTIER]")
    return latest[0]
