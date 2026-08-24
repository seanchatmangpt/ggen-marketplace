def cusum(trials, target_error=0.1, allowance=0.02, threshold=1.0):
    positive=0.0
    maximum=0.0
    for t in trials:
        error=abs(t.prediction-t.truth)
        positive=max(0.0, positive + error - target_error - allowance)
        maximum=max(maximum,positive)
    return {"statistic":maximum,"drifted":maximum>threshold,"threshold":threshold}
