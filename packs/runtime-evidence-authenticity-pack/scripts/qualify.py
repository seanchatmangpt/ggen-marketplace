from .admission import admit
from .authenticity import measure
from .independence import require_independent_roots
from .standing import standing
from .receipt import manufacture
def qualify(subject,rows,calibration,now,owner_state="PASS"):
    rows=admit(subject,rows,now);require_independent_roots(rows);auth=measure(rows);status=standing(auth,calibration,owner_state)
    return {"standing":status,"authenticity":auth,"receipt":None if status in {"BUILD_BROKEN","BLOCKED","REFUSED"} else manufacture(subject,auth,calibration,status),"actuation_performed":False}
