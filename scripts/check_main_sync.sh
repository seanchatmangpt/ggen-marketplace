#!/bin/sh
# check_main_sync.sh — hub main-sync guard (R31)
# Verifies origin/main is a strict ancestor of hdit-v2-structs.
# Repair (fast-forward only): git push origin hdit-v2-structs:main
set -u

BRANCH=hdit-v2-structs

git fetch origin -q || { echo "FAIL: git fetch origin failed"; exit 2; }

if git merge-base --is-ancestor "origin/main" "$BRANCH"; then
    if [ "$(git rev-parse origin/main)" = "$(git rev-parse "$BRANCH")" ]; then
        echo "OK: origin/main == $BRANCH ($(git rev-parse --short "$BRANCH"))"
    else
        echo "OK: origin/main ($(git rev-parse --short origin/main)) is an ancestor of $BRANCH ($(git rev-parse --short "$BRANCH")); repair if due: git push origin $BRANCH:main"
    fi
    exit 0
else
    echo "OUT-OF-SYNC: origin/main ($(git rev-parse --short origin/main)) is NOT an ancestor of $BRANCH ($(git rev-parse --short "$BRANCH")); repair: git push origin $BRANCH:main"
    exit 1
fi
