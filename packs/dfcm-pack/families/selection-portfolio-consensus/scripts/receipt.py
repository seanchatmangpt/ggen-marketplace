import hashlib, json

def issue(subject_sha, candidate_ids, evidence_digests):
    body = {
        "schema": "chatman.selection-portfolio-consensus/1",
        "subject_sha": subject_sha,
        "candidate_ids": sorted(candidate_ids),
        "evidence_digests": sorted(evidence_digests),
        "authority": "SELECT",
        "actuation_performed": False,
    }
    digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"body": body, "digest": digest}
