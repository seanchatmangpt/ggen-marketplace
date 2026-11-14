#!/usr/bin/env bash
# courts/lib.sh — shim-court protocol for ash-a2a-app-pack (lane L32).
# Protocol source: /Users/sac/smalt/scripts/shim_court/lib.sh (header :1-22 protocol,
# shim_court_sha :63, shim_court_self_check :65-87, with_shim phases 1-5 :98-143).
# Phases: BASELINE(sha256) -> BEFORE -> SHIM(marked SHIM-COURT) -> AFTER -> RESTORE(byte-exact,
# fail-closed). Typed lines: [FAIL:BASELINE|BEFORE|SHIM|AFTER|RESTORE|SELF-CHECK], [SKIP], [PASS].
# Contract: caller defines `apply_shim` (edits $SHIM_FILE in place, marks edits SHIM-COURT)
# before calling with_shim. Witnesses run under `bash -uc` (unbound var fails loud).

SHIM_COURT_NAME="${SHIM_COURT_NAME:-$(basename "${0:-shim_court}" .sh)}"
SHIM_FILE=""; SHIM_BACKUP=""; SHIM_BASELINE_SHA=""; SHIM_PHASE="INIT"

shim_court_log()  { printf '[%s] %s\n' "$1" "$2"; }
shim_court_fail() { printf '[FAIL:%s] %s: %s\n' "$1" "$SHIM_COURT_NAME" "$2" >&2; exit 1; }
shim_court_skip() { printf '[SKIP] %s: %s\n' "$SHIM_COURT_NAME" "$1"; exit 3; }
shim_court_sha()  { shasum -a 256 "$1" 2>/dev/null | awk '{print $1}'; }

shim_court_self_check() {
    # Real temp-copy exercise: a clean restore must match baseline, a corrupted restore must NOT.
    # Optional $1 = real file used as subject (copied into a temp dir, never touched in place).
    local dir subject backup base good corrupt
    dir="$(mktemp -d)" || return 1
    subject="$dir/subject"; backup="$dir/backup"
    if [ -n "${1:-}" ] && [ -f "$1" ]; then cp "$1" "$subject"; else printf 'subject-body\n' > "$subject"; fi
    cp "$subject" "$backup"; base="$(shim_court_sha "$subject")"
    printf 'raise "SHIM-COURT"\n' >> "$subject"
    cp "$backup" "$subject"; good="$(shim_court_sha "$subject")"
    cp "$backup" "$subject"; printf 'x' | dd of="$subject" bs=1 seek=2 conv=notrunc status=none 2>/dev/null
    corrupt="$(shim_court_sha "$subject")"
    rm -r -f "$dir"
    if [ -n "$base" ] && [ "$good" = "$base" ] && [ "$corrupt" != "$base" ]; then
        printf '[self-check] sha256 restore-detection verified (clean==baseline, corrupt!=baseline)\n'; return 0
    fi
    printf '[FAIL:SELF-CHECK] restore-detection is vacuous\n' >&2; return 1
}

shim_court_trap() {
    if [ -n "${SHIM_BACKUP:-}" ] && [ -f "${SHIM_BACKUP:-}" ] && [ -n "${SHIM_FILE:-}" ] \
       && { [ "$SHIM_PHASE" = "SHIM" ] || [ "$SHIM_PHASE" = "AFTER" ]; }; then
        cp "$SHIM_BACKUP" "$SHIM_FILE"
        [ "$(shim_court_sha "$SHIM_FILE")" = "$SHIM_BASELINE_SHA" ] || \
            printf '[FAIL:RESTORE] interrupt path: restore did not verify\n' >&2
    fi
}

with_shim() {
    # with_shim <file> <before-cmd> <after-cmd>
    local file="$1" before_cmd="$2" after_cmd="$3"
    SHIM_PHASE="BASELINE"
    [ -f "$file" ] || shim_court_fail BASELINE "subject file not found: $file"
    SHIM_FILE="$file"; SHIM_BASELINE_SHA="$(shim_court_sha "$file")"
    [ -n "$SHIM_BASELINE_SHA" ] || shim_court_fail BASELINE "could not sha256 $file"
    shim_court_log SHIM "baseline sha256($file) = $SHIM_BASELINE_SHA"

    SHIM_PHASE="BEFORE"
    bash -uc "$before_cmd" || shim_court_fail BEFORE "before-witness failed on UNMODIFIED file (old signature does not hold)"
    shim_court_log SHIM "BEFORE witness passed (old signature holds)"

    SHIM_BACKUP="$(mktemp)"; cp "$file" "$SHIM_BACKUP"
    trap shim_court_trap EXIT INT TERM
    SHIM_PHASE="SHIM"
    apply_shim
    grep -q 'SHIM-COURT' "$file" || shim_court_fail SHIM "apply_shim left no SHIM-COURT marker"
    [ "$(shim_court_sha "$file")" != "$SHIM_BASELINE_SHA" ] || shim_court_fail SHIM "shim did not change the file"

    SHIM_PHASE="AFTER"
    if ! bash -uc "$after_cmd"; then
        cp "$SHIM_BACKUP" "$file"
        [ "$(shim_court_sha "$file")" = "$SHIM_BASELINE_SHA" ] || \
            shim_court_fail RESTORE "restore after AFTER failure did NOT verify byte-exact"
        shim_court_fail AFTER "after-witness failed: court cannot flip (gate vacuous or shim inert); file restored+verified"
    fi
    shim_court_log SHIM "AFTER witness passed (flip observed under shim)"

    SHIM_PHASE="RESTORE"
    cp "$SHIM_BACKUP" "$file"
    local actual; actual="$(shim_court_sha "$file")"
    rm -f "$SHIM_BACKUP"; SHIM_BACKUP=""; trap - EXIT INT TERM
    [ "$actual" = "$SHIM_BASELINE_SHA" ] || \
        shim_court_fail RESTORE "sha256 mismatch after restore: got $actual, baseline $SHIM_BASELINE_SHA"
    shim_court_log SHIM "RESTORE verified byte-exact (sha256 match)"
    printf '[PASS] %s: non-vacuous (BEFORE green, AFTER red, restore verified)\n' "$SHIM_COURT_NAME"
}
