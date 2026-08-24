def standing(calibration,worst_gain,owner_state='PASS',fresh=True):
 if owner_state in {'FAIL','BUILD_BROKEN'}: return 'BUILD_BROKEN'
 if owner_state=='BLOCKED': return 'BLOCKED'
 if not fresh or calibration.state!='CALIBRATED' or worst_gain<0: return 'UNKNOWN'
 return 'PARTIAL_ALIVE'
