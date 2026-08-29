def project(plan_id, subject_sha, predicted, realized, standing):
    return {
        "ocel:activity":"remediation_counterfactual_realization",
        "ocel:object":plan_id,
        "subject_sha":subject_sha,
        "predicted_relief":predicted,
        "realized_relief":realized,
        "standing":standing,
        "actuation_performed":False,
    }
