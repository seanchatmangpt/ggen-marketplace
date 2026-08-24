from .admission import admit
from .calibration import calibrate
from .gamma import gamma_robustness
from .strata import worst_stratum
from .standing import standing
from .receipt import manufacture
from .telemetry import project

def qualify(subject, decisions, outcomes, now, owner_state="PASS"):
    rows = admit(subject, decisions, outcomes, now)
    calibration = calibrate(rows)
    gamma = gamma_robustness(rows)
    worst = worst_stratum(rows)
    status = standing(calibration, None if worst is None else worst[1], gamma, owner_state)
    receipt = None if status in {"BUILD_BROKEN", "BLOCKED"} else manufacture(subject, calibration, worst, status)
    return {
        "standing": status,
        "calibration": calibration,
        "gamma": gamma,
        "worst_stratum": worst,
        "receipt": receipt,
        "telemetry": project(rows, status),
        "actuation_performed": False,
    }
