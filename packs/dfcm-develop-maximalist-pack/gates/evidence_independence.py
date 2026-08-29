def admit(records):
    records = tuple(records)
    identities = {(r["implementation"], r["model"], r["domain"], r["evidence_root"]) for r in records}
    if len(identities) != len(records):
        raise ValueError("REFUSED[PSEUDO_INDEPENDENT_EVIDENCE]")
    return records
