import re
SUBJECT = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}$")
def admit(value: str) -> str:
    if not SUBJECT.fullmatch(value):
        raise ValueError("REFUSED[INEXACT_SUBJECT]")
    return value
