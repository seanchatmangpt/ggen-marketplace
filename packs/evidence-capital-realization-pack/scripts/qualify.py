from .admission import admit
from .gain import summarize
from .calibration import calibrate
from .information import information_value
from .root_influence import root_influence, require_not_concentrated
from .monotonicity import require_monotone_realization
from .drift import cusum
from .strata import worst_stratum
from .standing import standing
from .receipt import manufacture
from .telemetry import project

def qualify(subject, trials, now, owner_state="PASS"):
    rows=admit(subject,trials,now)
    gain=summarize(rows); calibration=calibrate(rows); information=information_value(rows)
    roots=root_influence(rows); require_not_concentrated(roots)
    curve=require_monotone_realization(rows)
    drift=cusum(rows); worst=worst_stratum(rows)
    status=standing(calibration,True,drift["drifted"],worst,owner_state)
    receipt=None if status in {"BUILD_BROKEN","BLOCKED","REFUSED"} else manufacture(subject,calibration,gain,information,roots,worst,status)
    return {"standing":status,"gain":gain,"calibration":calibration,"information":information,"root_influence":roots,"curve":curve,"drift":drift,"worst_stratum":worst,"receipt":receipt,"telemetry":project(subject,rows,calibration,status),"actuation_performed":False}
