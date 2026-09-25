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
LOCKDIR="${LOCKDIR:-$STATE_DIR/.keepalive.lockdir}"
PIDFILE="$STATE_DIR/keepalive.pid"

# Single instance: atomic mkdir lock. A directory cannot be inherited by child
# processes, so unlike flock the lock can never be held forever by an orphaned
# ssh child after the supervisor is killed (observed in production: a flock fd
# inherited by the foreground ssh kept every later supervisor instance from
# starting).
#
# Protocol (every step is atomic or verified after the fact; there is NO
# separate reclaim mutex):
#
#   * The lock is the directory $LOCKDIR. Creating it uses mkdir(2), which is
#     atomic: exactly one contender can create it.
#   * Claiming uses link(2): the creator writes its pid to claim.<pid> and
#     hard-links it to "info". link(2) fails if "info" already exists, so a
#     late claim can never overwrite a new owner's claim. Ownership is only
#     accepted when the pid read back from "info" equals $$.
#   * A lock is stale ONLY when its owner is verifiably gone: the claim is
#     unreadable, the recorded PID is dead, or that PID's cmdline is no longer
#     this keepalive. There is deliberately NO "older than N seconds" rule:
#     this supervisor is meant to run for weeks, so a healthy holder's
#     timestamp is always old - an age rule would let any second instance
#     steal the lock from a healthy first one, leaving two supervisors
#     fighting over the VPS port (tunnel flapping). Manual takeover stays
#     kill-and-restart via the pidfile: verify /proc/<pid>/cmdline, kill,
#     then start the replacement; the dead-PID branch below reclaims the lock.
#   * Reclaiming a stale lock uses an atomic rename(2):
#     mv "$LOCKDIR" "$LOCKDIR.stale.$$". Rename is atomic, so exactly one
#     contender takes the old lock aside and the rest back off and retry. The
#     winner then RE-VERIFIES the moved-aside state, because its pre-rename
#     "stale" verdict may be older than the rename itself: the owner may have
#     completed its claim in between (this exact check-then-act race produced
#     three simultaneous holders in a concurrency test when the code did
#     "decide stale, then rm -rf"). If the moved-aside lock turns out to be
#     alive, it is moved back and the contender yields. If the move-back itself
#     fails - a new contender claimed the fresh path in the microsecond gap -
#     the original owner is now a ghost (alive, but its directory is gone) and
#     is terminated: it cannot be relied on to step down, because it spends
#     nearly all its time blocked in foreground ssh and may never reach its
#     ownership re-validation. Its orphaned ssh child, if any, is reaped by
#     the new holder's stale-tunnel cleanup. If it is genuinely
#     stale, it is discarded and the contender loops back to create+claim a
#     fresh lock. (An earlier design serialized reclaim through a second
#     mkdir "mutex", but that mutex had its own torn-claim race - "empty
#     claim means dead holder" misfires while a holder is between mkdir and
#     its claim write - letting two reclaimers run concurrently and delete a
#     live holder's lockdir. The atomic rename IS the mutual exclusion, so no
#     second lock is needed.)
#   * On exit the lock directory is removed only if "info" still names our
#     own pid (compared via BASHPID, so an explicit subshell can never match),
#     so a late exit can never delete a successor's lock.
#   * The main loop re-validates ownership every iteration; if our claim ever
#     disappears from under us we step down, so at most one instance keeps
#     running even in a pathological race.
#
# OWNER_CMDLINE identifies this keepalive's own command line for the is-live
# check. It defaults to this file's basename, so renaming the file keeps
# working as long as it is started under its own name.
OWNER_CMDLINE="$(basename "$0")"
lock_pid=""  # set by lock_is_live
# lock_is_live <dir>: return 0 iff <dir>/info names a live, verified owner.
# A lockdir with no (readable) claim is NOT live: it is either an acquire in
# progress (microseconds between mkdir and claim) or a crashed acquire. The
# reclaim path re-verifies after the atomic rename, and the link-claim in the
# acquire branch guarantees a late writer can never clobber a new holder's
# claim - it yields instead.
lock_is_live() {
  local dir="$1" pid
  pid=$(cut -d' ' -f1 < "$dir/info" 2>/dev/null || true)
  case "$pid" in ''|*[!0-9]*) pid="" ;; esac
  # A claim naming our own pid is never "a live other holder": this function
  # only runs on the contender path (a holder returns from lock_acquire and
  # never comes back), so our own pid here means our own earlier claim attempt
  # was swept aside mid-claim - a reclaimer moved our directory away and moved
  # it back after we had already given up on it. We must reclaim it, not
  # yield to it: yielding to our own pid deadlocks the lock, because every
  # other contender yields to us too and nobody ever holds it (proven by a
  # concurrency test: 16 contenders, 0 winners).
  [ -n "$pid" ] && [ "$pid" != "$$" ] && kill -0 "$pid" 2>/dev/null \
    && tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -qF -- "$OWNER_CMDLINE" \
    && lock_pid="$pid"
}
# try_claim: we just created $LOCKDIR; publish our claim atomically.
# Returns 0 iff $LOCKDIR/info now names $$.
try_claim() {
  local owner=""
  if echo "$$ $(date +%s)" > "$LOCKDIR/claim.$$" 2>/dev/null \
     && ln "$LOCKDIR/claim.$$" "$LOCKDIR/info" 2>/dev/null; then
    owner=$(cut -d' ' -f1 < "$LOCKDIR/info" 2>/dev/null || true)
  fi
  rm -f "$LOCKDIR/claim.$$"
  [ "${owner:-}" = "$$" ]
}
lock_release_on_exit() {
  local o
  o=$(cut -d' ' -f1 < "$LOCKDIR/info" 2>/dev/null || true)
  # BASHPID (falling back to $$): an explicit subshell must never match.
  if [ "${o:-}" = "${BASHPID:-$$}" ]; then
    rm -rf "$LOCKDIR"
  fi
}
# The moved-aside lock turned out to be live, but moving it back failed because
# a new contender claimed the fresh path in the microsecond gap. There are now
# two would-be holders: the new claimant, and the original owner, which is
# still alive but whose directory is gone - a ghost. The ghost does NOT
# reliably step down on its own: its main-loop ownership check only runs
# between ssh runs, and it spends nearly all its time blocked in foreground
# ssh. Leaving it produces two supervisors fighting over the VPS port.
# Re-verify its cmdline (pid reuse) and terminate it; its EXIT trap is safe
# (it checks the pid inside $LOCKDIR/info, which is now the new claimant's,
# so it will not delete the new lock). Its orphaned ssh child, if any, is
# reaped by the new holder's stale-tunnel cleanup. Then drop the orphaned
# claim dir.
lock_displace_ghost() {
  local stale="$1"
  if lock_is_live "$stale"; then
    echo "ghost holder $lock_pid displaced by a new claimant, terminating it" >&2
    kill "$lock_pid" 2>/dev/null || true
  fi
  rm -rf "$stale" 2>/dev/null || true
}

# Returns: 0 = we hold the lock; 1 = a live instance is already running;
# 2 = the lock directory is unusable (cannot create or write inside it).
lock_acquire() {
  local stale
  # Create the parent once up front, so a later mkdir failure means "held or
  # lost a race", never "missing parent".
  mkdir -p "$(dirname "$LOCKDIR")" 2>/dev/null || {
    echo "cannot create lock parent directory, aborting" >&2
    return 2
  }
  while true; do
    if mkdir "$LOCKDIR" 2>/dev/null; then
      if try_claim; then
        trap lock_release_on_exit EXIT
        return 0
      fi
      # Claim failed: either a reclaimer swept our not-yet-claimed directory
      # (its claim is in place; just retry and yield to it), or we cannot
      # write at all (disk full / read-only). Probe writability to tell them
      # apart instead of looping forever on a dead disk.
      if [ -e "$LOCKDIR" ]; then
        if touch "$LOCKDIR/.writetest.$$" 2>/dev/null; then
          rm -f "$LOCKDIR/.writetest.$$"
        else
          echo "cannot write inside $LOCKDIR, aborting" >&2
          rmdir "$LOCKDIR" 2>/dev/null || true
          return 2
        fi
      fi
      sleep 1
      continue
    fi
    if [ ! -e "$LOCKDIR" ]; then
      # Vanished between our mkdir and this test: a reclaimer's atomic rename
      # won the race. Retry; the fast path above will create it fresh.
      sleep 1
      continue
    fi
    if lock_is_live "$LOCKDIR"; then
      echo "another keepalive instance running (pid $lock_pid), exiting"
      return 1
    fi
    # Stale. Take it over with an atomic rename; exactly one contender wins.
    stale="$LOCKDIR.stale.$$"
    rm -rf "$stale" 2>/dev/null || true
    if ! mv -T "$LOCKDIR" "$stale" 2>/dev/null; then
      sleep 1   # lost the rename race; retry and let the winner decide
      continue
    fi
    # Re-verify AFTER the rename: our "stale" verdict may predate it, and the
    # owner may have completed its claim in between. Checking before the
    # rename and acting after it is the race that used to delete live locks.
    if lock_is_live "$stale"; then
      # It was alive after all: move it back and yield to the owner.
      if ! mv -T "$stale" "$LOCKDIR" 2>/dev/null; then
        lock_displace_ghost "$stale"
      fi
      sleep 1
      continue
    fi
    # Genuinely stale: discard it and loop back to create+claim a fresh lock.
    rm -rf "$stale" 2>/dev/null || true
  done
}
# --- end single-instance lock ---

lock_acquire
case $? in
  0) : ;;          # we hold the lock; fall through to the main loop
  1) exit 0 ;;     # a live instance is already running; not an error
  *) exit 1 ;;     # lock directory unusable
esac

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
  # Ownership re-validation (see the lock protocol above): if our claim ever
  # disappears from under us - e.g. a reclaimer won the atomic rename during
  # our microsecond claim window - step down at once so that at most one
  # instance keeps running. A healthy holder's claim is never touched, so a
  # mismatch always means we lost the lock.
  cur_owner=$(cut -d' ' -f1 < "$LOCKDIR/info" 2>/dev/null || true)
  if [ "${cur_owner:-}" != "$$" ]; then
    echo "[$(date '+%F %T')] lock ownership lost (info now '${cur_owner:-missing}'), stepping down" >> "$LOG"
    exit 0
  fi
  # Log rotation: this log only grows on tunnel events, but over months even
  # that is unbounded. Keep the last 5000 lines.
  if [ "$(wc -l < "$LOG" 2>/dev/null || echo 0)" -gt 6000 ]; then
    tail -n 5000 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"
  fi
  stale=$(pgrep -f "$TUN_PATTERN" || true)
  if [ -n "$stale" ]; then
    # shellcheck disable=SC2086
    for p in $stale; do
      # Re-verify each PID against the pattern before killing: pgrep output is
      # only a snapshot, and a PID can be recycled between the pgrep and the
      # kill. Never kill on a bare PID.
      if tr '\0' ' ' < "/proc/$p/cmdline" 2>/dev/null | grep -Eq "$TUN_PATTERN"; then
        echo "$(date -u): killing stale tunnel ssh (pid $p)" >> "$LOG"
        kill "$p" 2>/dev/null || true
      fi
    done
    sleep 2
  fi
  # NOTE on the next two options: StrictHostKeyChecking=no +
  # UserKnownHostsFile=/dev/null disables man-in-the-middle protection on the
  # *tunnel* leg. This is a deliberate trade-off for VPSes that get reimaged
  # often (a changed host key would otherwise wedge the tunnel forever). For a
  # stable VPS, drop both options and pre-seed the VPS host key into
  # ~/.ssh/known_hosts instead. Never use these options for the operator access
  # leg (the ssh -p $REMOTE_PORT ... command in current-endpoint.txt).
  ssh -i "$TUNNEL_KEY" \
      -o BatchMode=yes -o ConnectTimeout=20 \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o ServerAliveInterval=20 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes \
      -N -R "$REMOTE_PORT:localhost:22" "$VPS_USER@$VPS_IP" >> "$LOG" 2>&1
  # Never silence repair diagnostics: if this ssh keeps failing, its stderr
  # above is the only record of why. Check the log before retrying blindly.
  echo "$(date -u): tunnel dropped, reconnecting in 5s" >> "$LOG"
  sleep 5
done
