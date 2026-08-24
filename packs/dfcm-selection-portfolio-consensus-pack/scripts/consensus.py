from collections import Counter
from .models import Refused

def consensus(votes, minimum=2):
    values = tuple(votes)
    if len(values) < minimum:
        raise Refused("REFUSED_INSUFFICIENT_CONSENSUS_SUPPORT")
    counts = Counter(values)
    winner, count = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    tied = [value for value, n in counts.items() if n == count]
    if len(tied) != 1:
        raise Refused("REFUSED_AMBIGUOUS_CONSENSUS")
    return winner, count / len(values)
