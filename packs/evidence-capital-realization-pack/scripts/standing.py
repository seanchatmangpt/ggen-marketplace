def standing(calibration, monotone, drifted, worst, owner_state="PASS"):
    if owner_state in {"FAIL","BUILD_BROKEN"}: return "BUILD_BROKEN"
    if owner_state == "BLOCKED": return "BLOCKED"
    if calibration.state != "CALIBRATED": return "UNKNOWN"
    if not monotone: return "REFUSED"
    if drifted: return "UNKNOWN"
    if worst["mean_loss_reduction"] <= 0: return "UNKNOWN"
    return "PARTIAL_ALIVE"
