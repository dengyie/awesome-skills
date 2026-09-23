#!/bin/bash
# Persistent reverse SSH tunnel: inner machine -> VPS.
# The VPS listens on REMOTE_PORT (public) and forwards to this machine's sshd (port 22).
#
# Setup:
#   1. Copy this file somewhere durable, e.g. ~/.reverse-ssh/reverse-ssh-keepalive.sh
#   2. Replace every ALL_CAPS placeholder below.
#   3. chmod +x, then run:  nohup ./reverse-ssh-keepalive.sh >/dev/null 2>&1 &
#
# Takeover: kill the running keepalive (its lock is released on death),
# then start a new one. Never run two instances; flock guards that.
set -u

VPS_IP="203.0.113.10"                 # <-- your VPS public IP (example: documentation range)
VPS_USER="tunnel"                     # <-- user on the VPS that owns the tunnel
REMOTE_PORT="2222"                    # <-- public port on the VPS
TUNNEL_KEY="$HOME/.ssh/tunnel-key"    # <-- tunnel private key, mode 600
INNER_USER="operator"                 # <-- login user on THIS machine (used in the endpoint hint)

STATE_DIR="$HOME/.reverse-ssh"
mkdir -p "$STATE_DIR"
LOG="$STATE_DIR/reverse-ssh-tunnel.log"
LOCK="$STATE_DIR/reverse-ssh-keepalive.lock"
ENDPOINT_FILE="$STATE_DIR/current-endpoint.txt"

# Single instance: only the supervisor holds the lock. The ssh child is
# started with 9>&- so it never inherits the lock fd; killing the
# supervisor always releases the lock, even if an ssh child is orphaned.
exec 9>"$LOCK" || exit 1
flock -n 9 || { echo "another instance running"; exit 0; }

echo "ssh -p $REMOTE_PORT -i access-key.pem $INNER_USER@$VPS_IP" > "$ENDPOINT_FILE"
echo "endpoint: $(cat "$ENDPOINT_FILE")"

while true; do
  ssh -i "$TUNNEL_KEY" \
      -o BatchMode=yes -o ConnectTimeout=20 \
      -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
      -o ServerAliveInterval=20 -o ServerAliveCountMax=3 \
      -o ExitOnForwardFailure=yes \
      -N -R "$REMOTE_PORT:localhost:22" "$VPS_USER@$VPS_IP" 9>&- >> "$LOG" 2>&1
  echo "$(date -u): tunnel dropped, reconnecting in 5s" >> "$LOG"
  sleep 5
done
