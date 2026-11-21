#!/usr/bin/env bash
# Atomic lock for ONE shared browser connection (daemon) that several Claude sessions might want.
# Why: "check, then create the file" lets two sessions win at the same time. noclobber makes the create atomic.
# Usage:
#   scripts/browser_lock.sh acquire <name> <session>   waits (polling) until it owns the lock, then prints "mine"
#   scripts/browser_lock.sh release <name> <session>   removes the lock, only if <session> owns it
#   scripts/browser_lock.sh owner <name>               prints the owner or "free"
# Run `acquire` in the background if you do not want to block; start work only after it printed "mine".
# Locks live in ~/.claude/state/bh_<name>.lock (outside git). Always release at the end, also on error.
set -u
D="${HOME}/.claude/state"; mkdir -p "$D"
cmd="${1:-}"; name="${2:-}"; who="${3:-}"; f="$D/bh_${name}.lock"
[ -n "$cmd" ] && [ -n "$name" ] || { sed -n 2,10p "$0"; exit 2; }
case "$cmd" in
  acquire)
    [ -n "$who" ] || { echo "session name missing"; exit 2; }
    until ( set -o noclobber; echo "$who" > "$f" ) 2>/dev/null; do sleep "${LOCK_POLL:-20}"; done
    echo mine ;;
  release)
    if [ -f "$f" ] && [ "$(cat "$f")" = "$who" ]; then rm -f "$f"; echo released; else echo "not the owner ($(cat "$f" 2>/dev/null || echo free))"; exit 1; fi ;;
  owner) cat "$f" 2>/dev/null || echo free ;;
  *) exit 2 ;;
esac
