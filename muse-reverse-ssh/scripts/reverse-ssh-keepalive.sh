#!/bin/bash
# Persistent reverse SSH tunnel: inner machine -> VPS.
# The VPS listens on REMOTE_PORT (public) and forwards to this machine's sshd (port 22).
#
# Setup:
#   1. Copy this file somewhere durable, e.g. ~/.reverse-ssh/reverse-ssh-keepalive.sh
#   2. Replace every ALL_CAPS placeholder below.
#   3. chmod +x, then run:  nohup ./reverse-ssh-keepalive.sh >/dev/null 2>&1 &
#
# Takeover: read the pid from $STATE_DIR/keepalive.pid, verify
# /proc/<pid>/cmdline really is this script, kill it, then start a new one.
# The mkdir lock below guarantees a single instance.
set -u

VPS_IP="203.0.113.10"                 # <-- your VPS public IP (example: documentation range)
VPS_USER="tunnel"                     # <-- user on the VPS that owns the tunnel
REMOTE_PORT="2222"                    # <-- public port on the VPS
TUNNEL_KEY="$HOME/.ssh/tunnel-key"    # <-- tunnel private key, mode 600
INNER_USER="operator"                 # <-- login user on THIS machine (used in the endpoint hint)

STATE_DIR="$HOME/.reverse-ssh"
mkdir -p "$STATE_DIR"
LOG="$STATE_DIR/reverse-ssh-tunnel.log"
LOCKDIR="$STATE_DIR/.keepalive.lockdir"
LOCK_MAX_AGE=900                      # stale lock older than this is reclaimed
PIDFILE="$STATE_DIR/keepalive.pid"

# Single instance: atomic mkdir lock. A directory cannot be inherited by child
# processes, so unlike flock the lock can never be held forever by an orphaned
# ssh child after the supervisor is killed (observed in production: a flock fd
# inherited by the foreground ssh kept every later supervisor instance from
# starting). Stale locks (dead pid / too old) are reclaimed.
lock_acquire() {
  local lock_pid lock_ts now
  if mkdir "$LOCKDIR" 2>/dev/null; then
    echo "$$ $(date +%s)" > "$LOCKDIR/info"
    trap 'rm -rf "$LOCKDIR"' EXIT
    return 0
  fi
  read -r lock_pid lock_ts < "$LOCKDIR/info" 2>/dev/null || lock_pid=""
  case "$lock_ts" in ''|*[!0-9]*) lock_ts=0 ;; esac
  now=$(date +%s)
  if [ -z "$lock_pid" ] || ! kill -0 "$lock_pid" 2>/dev/null \
     || ! tr '\0' ' ' < "/proc/$lock_pid/cmdline" 2>/dev/null | grep -q "reverse-ssh-keepalive" \
     || [ $(( now - lock_ts )) -gt "$LOCK_MAX_AGE" ]; then
    echo "stale lock (pid ${lock_pid:-unknown}), reclaiming" >&2
    rm -rf "$LOCKDIR"
    lock_acquire
    return $?
  fi
  echo "another keepalive instance running (pid $lock_pid), exiting"
  exit 0
}
lock_acquire

echo $$ > "$PIDFILE"

echo "ssh -p $REMOTE_PORT -i access-key.pem $INNER_USER@$VPS_IP" > "$STATE_DIR/current-endpoint.txt"
echo "endpoint: $(cat "$STATE_DIR/current-endpoint.txt")"

# Stale tunnel cleanup: a previous supervisor killed without its ssh child leaves
# an orphan holding the VPS port, and a new ssh would then fail forever on
# ExitOnForwardFailure. Anchor the pattern strictly (^...) to avoid killing
# unrelated ssh sessions. The pattern lives in a variable so pgrep never
# matches this script's own command line.
TUN_PATTERN="^ssh -i $TUNNEL_KEY .* -R $REMOTE_PORT:localhost:22 $VPS_USER@"

while true; do
  stale=$(pgrep -f "$TUN_PATTERN" || true)
  if [ -n "$stale" ]; then
    echo "$(date -u): killing stale tunnel ssh (pid $stale)" >> "$LOG"
    # shellcheck disable=SC2086
    kill $stale 2>/dev/null || true
    sleep 2
  fi
  ssh -i "$TUNNEL_KEY" \
      -o BatchMode=yes -o ConnectTimeout=20 \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o ServerAliveInterval=20 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes \
      -N -R "$REMOTE_PORT:localhost:22" "$VPS_USER@$VPS_IP" >> "$LOG" 2>&1
  echo "$(date -u): tunnel dropped, reconnecting in 5s" >> "$LOG"
  sleep 5
done
