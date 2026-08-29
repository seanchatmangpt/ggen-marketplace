from .admission import admit
from .calibration import calibrate
from .strata import worst_stratum
from .standing import standing
from .receipt import manufacture
def qualify(subject,rows,now,owner_state='PASS',fresh=True):
 rows=admit(subject,rows,now);cal=calibrate(rows);worst=worst_stratum(rows);status=standing(cal,worst[0],owner_state,fresh);receipt=None if status in {'BUILD_BROKEN','BLOCKED'} else manufacture(subject,cal,worst,status)
 return {'standing':status,'calibration':cal,'worst_stratum':worst,'receipt':receipt,'actuation_performed':False}
