ALLOWED = {"OBSERVE", "SELECT", "CONSTRUCT", "VERIFY"}
def admit(authority: str, broker: str | None = None) -> str:
    if authority == "DO":
        if broker != "BRCE":
            raise ValueError("REFUSED[BRCE_REQUIRED_FOR_DO]")
        return authority
    if authority not in ALLOWED:
        raise ValueError("REFUSED[INVALID_AUTHORITY]")
    return authority
