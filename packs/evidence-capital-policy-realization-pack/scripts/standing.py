def standing(calibration, worst_stratum_value, gamma_ok, owner_state="PASS"):
    if owner_state in {"FAIL", "BUILD_BROKEN"}:
        return "BUILD_BROKEN"
    if owner_state == "BLOCKED":
        return "BLOCKED"
    if calibration.state != "CALIBRATED":
        return "UNKNOWN"
    if worst_stratum_value is None or worst_stratum_value < 0:
        return "UNKNOWN"
    if not all(gamma_ok.values()):
        return "UNKNOWN"
    return "PARTIAL_ALIVE"
