#!/usr/bin/env python3
import json, pathlib, sys

REQUIRED = {"schema", "waves", "mode"}

def main(path: str) -> int:
    data = json.loads(pathlib.Path(path).read_text())
    missing = REQUIRED - set(data)
    if missing:
        print(f"REFUSED[MISSING_FIELDS]: {sorted(missing)}")
        return 2
    if data["mode"] != "construct_only":
        print("REFUSED[AMBIENT_DO_AUTHORITY]")
        return 3
    for wave in data["waves"]:
        if wave.get("grants_do_authority") is not False:
            print("REFUSED[AMBIENT_DO_AUTHORITY]")
            return 4
        if wave.get("requires_receipt") is not True:
            print("REFUSED[UNRECEIPTED_REBLOOM]")
            return 5
        if int(wave.get("max_depth", 0)) < 1 or int(wave.get("max_order", 0)) < 2:
            print("REFUSED[NON_EXPANDING_BOUND]")
            return 6
    print("ALIVE: bounded construct-only rebloom plan")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
