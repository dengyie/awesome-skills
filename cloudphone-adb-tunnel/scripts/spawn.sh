#!/data/data/com.termux/files/usr/bin/bash
# 经 termux-chroot 拉起 frpc: chroot 内 /etc/resolv.conf = $PREFIX/etc/resolv.conf
cd "$HOME/frp" || exit 1
if ! command -v termux-chroot >/dev/null 2>&1; then
  echo "[$(date '+%F %T')] termux-chroot 缺失 (pkg install proot)，本轮跳过"
  exit 1
fi
[ -f frpc.pid ] && kill "$(cat frpc.pid 2>/dev/null)" 2>/dev/null
command -v pkill >/dev/null 2>&1 && pkill -f "frp/frpc" 2>/dev/null
sleep 1
: > logs/frpc.log
termux-chroot "$HOME/frp/frpc" -c "$HOME/frp/frpc.toml" >> logs/frpc.log 2>&1 &
echo $! > frpc.pid
echo "[$(date '+%F %T')] frpc 已拉起 (termux-chroot)"
