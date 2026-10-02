#!/bin/bash
# health-watch-loop.sh — zero-cost resident loop for a health-watch check script.
#
# Runs the check script (~/.health-watch/health-watch.sh) about once a minute
# and lets it self-heal. This loop does the minute-level checking so an
# external supervisor (Layer 3) only has to verify THIS process lives, instead
# of paying for a poll that re-runs every check.
#
# Setup:
#   1. Copy this file somewhere durable, e.g. ~/.health-watch/health-watch-loop.sh
#      (on an ephemeral machine: on the persistent data disk, next to the
#      check script itself).
#   2. Replace every ALL_CAPS placeholder below.
#   3. chmod +x, then run:  setsid nohup ./health-watch-loop.sh >/dev/null 2>&1 < /dev/null &
#
# Stop: kill "$(cat ~/.health-watch/health-watch-loop.pid)" — but verify
# /proc/<pid>/cmdline really is this script first (PIDs get reused).
#
# Hard rules baked in here (each one is a production lesson):
#   - NO `set -e`: the check script exits 1 exactly when it finds degraded
#     state. Under `set -e` the first degraded run would kill this loop.
#   - `timeout 300` per run: a hung check must never serialize the loop.
#   - Check stdout is discarded: the status JSON file is the source of truth.
#   - stderr is trimmed to the last 200 lines every cycle: logs stay bounded.
set -u

STATE_DIR="$HOME/.health-watch"        # <-- state dir (persistent disk on ephemeral machines)
WATCH="$STATE_DIR/health-watch.sh"     # <-- your check script (writes the status JSON)
INTERVAL=60                            # seconds between the END of one run and the next

PIDFILE="$STATE_DIR/health-watch-loop.pid"
ERRLOG="$STATE_DIR/health-watch-loop.err.log"

mkdir -p "$STATE_DIR"
echo $$ > "$PIDFILE"

while true; do
  HOME="$HOME" timeout 300 bash "$WATCH" >/dev/null 2>>"$ERRLOG" || true
  tail -n 200 "$ERRLOG" > "$ERRLOG.tmp" 2>/dev/null && mv "$ERRLOG.tmp" "$ERRLOG"
  sleep "$INTERVAL"
done
