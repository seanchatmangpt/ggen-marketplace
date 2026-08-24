import hashlib
import json

def manufacture(subject, calibration, worst, status):
    body = {
        "schema": "chatman.evidence-capital-policy-realization/1",
        "repo": subject.repo,
        "sha": subject.sha,
        "semantic_digest": subject.semantic_digest,
        "generation": subject.generation,
        "support": calibration.support,
        "mae": calibration.mae,
        "bias": calibration.bias,
        "worst_stratum": worst,
        "standing": status,
        "authority": "OBSERVE|VERIFY",
        "actuation_performed": False,
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return {"body": body, "sha256": hashlib.sha256(raw.encode()).hexdigest()}
