def project(subject, trials, calibration, status):
    events=[]
    for t in trials:
        events.append({"activity":"evidence_capital_realization_trial","repo":subject.repo,"sha":subject.sha,"trial_id":t.trial_id,"evidence_root":t.evidence_root,"claimed_capital":t.claimed_capital,"loss_reduction":t.baseline_loss-t.augmented_loss,"information_gain":t.information_gain})
    events.append({"activity":"evidence_capital_realization_qualified","repo":subject.repo,"sha":subject.sha,"support":calibration.support,"calibration_state":calibration.state,"standing":status})
    return tuple(events)
