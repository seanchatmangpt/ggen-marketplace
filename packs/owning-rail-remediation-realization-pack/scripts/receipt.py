import hashlib
import json

def manufacture(subject_sha, semantic_digest, state, blocker_before, blocker_after):
    body = {
        "schema": "ggen.owning-rail-remediation-realization/1",
        "subject_sha": subject_sha,
        "semantic_digest": semantic_digest,
        "realization_state": state,
        "blocker_before": blocker_before,
        "blocker_after": blocker_after,
        "authority": "OBSERVE|VERIFY",
        "actuation_performed": False,
    }
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return {"body": body, "sha256": hashlib.sha256(raw.encode()).hexdigest()}
