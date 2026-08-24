def standing(authenticity,calibration,owner_state="PASS"):
    if owner_state in {"FAIL","BUILD_BROKEN"}:return "BUILD_BROKEN"
    if owner_state=="BLOCKED":return "BLOCKED"
    if authenticity.state=="UNAUTHENTIC":return "REFUSED"
    if authenticity.state in {"INSUFFICIENT","DIVERGED"}:return "UNKNOWN"
    if calibration.state!="CALIBRATED":return "UNKNOWN"
    return "PARTIAL_ALIVE"
