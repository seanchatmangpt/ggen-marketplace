import hashlib, json

def canonical_receipt(subject, selected, alternatives, ggen_sha):
    body={
      "schema":"chatman.selection-frontier-execution/1",
      "subject":subject,
      "selected":list(selected),
      "preserved_alternatives":list(alternatives),
      "ggen_sha":ggen_sha,
      "authority":"SELECT",
      "actuation_performed":False,
    }
    encoded=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
    return body | {"sha256":hashlib.sha256(encoded).hexdigest()}
