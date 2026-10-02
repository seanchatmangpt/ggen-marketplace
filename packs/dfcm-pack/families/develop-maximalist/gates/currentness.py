def current(rows):
    rows = tuple(rows)
    if not rows:
        raise ValueError("REFUSED[NO_EVIDENCE_FRONTIER]")
    generation = max(int(row["generation"]) for row in rows)
    latest = [row for row in rows if int(row["generation"]) == generation]
    digests = {row["digest"] for row in latest}
    if len(digests) != 1:
        raise ValueError("REFUSED[SPLIT_CURRENT_EVIDENCE]")
    return latest[0]
