def cusum(errors, reference=0.0, slack=0.05, threshold=0.75):
    positive = 0.0
    negative = 0.0
    for error in errors:
        positive = max(0.0, positive + error - reference - slack)
        negative = min(0.0, negative + error - reference + slack)
        if positive > threshold or -negative > threshold:
            return "DRIFT"
    return "CURRENT"
