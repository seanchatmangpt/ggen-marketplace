"""Golden-vector driver (python). Usage: python3 driver.py <golden.vec>; imports generated src/es/chain.py."""
import sys
sys.path.insert(0, "src/es")
import chain as C

chain = []
for raw in open(sys.argv[1], encoding="utf-8").read().split("\n"):
    if not raw or raw.startswith("#"):
        continue
    p = raw.split("|")
    if raw.startswith("case "):
        chain = []
        print("case", raw[5:])
    elif p[0] in ("append", "seal"):
        try:
            e = C.append(chain, *p[1:]) if p[0] == "append" else C.seal(chain, *p[1:])
            print("ok", e["hash"])
        except ValueError:
            print("err")
    elif p[0] == "verify":
        print("verify", "true" if C.verify(chain) else "false")
    elif p[0] == "tamper":
        chain[0]["subject"] = "tampered"
        print("tampered")
