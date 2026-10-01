#!/usr/bin/env bash
# Usage: verify/validate.sh [corpus [cases.ttl ...] | witnesses]
set -euo pipefail
exec python3 "$(cd "$(dirname "$0")" && pwd)/validate.py" "${@:-corpus}"
