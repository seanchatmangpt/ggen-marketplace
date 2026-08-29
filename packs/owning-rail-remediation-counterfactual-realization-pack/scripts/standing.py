def standing(owner_state: str, calibration_state: str, fresh: bool, support: int) -> str:
    if owner_state in {"BUILD_BROKEN","FAIL"}: return "BUILD_BROKEN"
    if owner_state == "BLOCKED": return "BLOCKED"
    if owner_state == "REFUSED": return "REFUSED"
    if owner_state in {"UNKNOWN","PENDING"}: return "UNKNOWN"
    if not fresh or calibration_state != "CALIBRATED" or support <= 0: return "UNKNOWN"
    if owner_state == "UNSUPPORTED": return "UNSUPPORTED"
    return "PARTIAL_ALIVE"
