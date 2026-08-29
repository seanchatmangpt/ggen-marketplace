def classify(realized_gain,false_capital_rate,root_concentration,owner_state='PASS'):
    if owner_state in {'FAIL','BUILD_BROKEN','BLOCKED'}:
        return 'BUILD_BROKEN'
    if realized_gain < 0:
        return 'REFUSED[NEGATIVE_REALIZED_GAIN]'
    if false_capital_rate > 0.2:
        return 'UNKNOWN'
    if root_concentration > 0.8:
        return 'REFUSED[CONCENTRATED_EVIDENCE_CAPITAL]'
    return 'PARTIAL_ALIVE'
