from collections import defaultdict

def worst_stratum(rows):
    grouped=defaultdict(list)
    for stratum, relief in rows:
        grouped[stratum].append(relief)
    if not grouped:
        return None
    means={k:sum(v)/len(v) for k,v in grouped.items()}
    key=min(means,key=means.get)
    return key,means[key]

def all_nonnegative(rows) -> bool:
    worst=worst_stratum(rows)
    return worst is not None and worst[1] >= 0
