REQUIRED = {"reason", "marketplace_search", "why_existing_unsuitable", "why_extension_unsuitable", "why_new_pack_unsuitable"}
def admit(record: dict) -> dict:
    missing = REQUIRED - set(record)
    if missing:
        raise ValueError("REFUSED[HANDWRITTEN_IRREDUCIBLE_REASON_MISSING]:" + ",".join(sorted(missing)))
    if not str(record["reason"]).strip():
        raise ValueError("REFUSED[EMPTY_HANDWRITTEN_IRREDUCIBLE_REASON]")
    return record
