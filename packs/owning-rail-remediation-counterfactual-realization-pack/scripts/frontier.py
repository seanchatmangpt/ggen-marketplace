def current_model(models):
    if not models:
        return None
    max_generation=max(m[0] for m in models)
    current=[m for m in models if m[0]==max_generation]
    digests={m[1] for m in current}
    if len(digests)!=1:
        raise ValueError("REFUSED[DIVERGENT_CALIBRATION_FRONTIER]")
    return current[0]
