#!/usr/bin/env bash
# freestyle-sandbox 快捷管理辅助脚本
set -euo pipefail

CURRENT_RUNNING_SLUG=""
PAUSED_DONE=0

cleanup_on_exit() {
  local sig="${1:-EXIT}"
  if [ "${PAUSED_DONE:-0}" -eq 1 ] || [ -z "${CURRENT_RUNNING_SLUG:-}" ]; then
    return
  fi
  PAUSED_DONE=1
  echo -e "\n[freestyle-sandbox] 触发 $sig 信号，正在自动暂停 VM '$CURRENT_RUNNING_SLUG' 保护免费算力额度..." >&2
  freestyle vm pause "$CURRENT_RUNNING_SLUG" >/dev/null 2>&1 || true
}

trap 'cleanup_on_exit INT; trap - INT; kill -s INT "$$"' INT
trap 'cleanup_on_exit TERM; trap - TERM; kill -s TERM "$$"' TERM
trap 'cleanup_on_exit EXIT' EXIT

usage() {
  cat << 'EOF'
用法:
  manage.sh list                           列出当前所有 VM 状态与规格
  manage.sh run <slug> <tier> <cmd...>     智能运行：若 VM 存在则唤醒并执行，若不存在则创建对应 tier 后执行，执行后自动 pause（带异常/中断安全陷阱）
  manage.sh ensure <slug> <tier>           确保 VM 存在并处于 running 状态（不自动暂停）
  manage.sh pause <slug>                   手动暂停指定 VM（停止扣除算力）
  manage.sh start <slug>                   手动唤醒指定 VM
  manage.sh destroy <slug>                 删除指定 VM

参数说明:
  tier:
    sm    - 2 vCPU / 4 GiB 内存 (freestyle/ubuntu-sm)，推荐日常/脚本/测试，每月可跑 ~50h
    std   - 4 vCPU / 8 GiB 内存 (freestyle/ubuntu)，重型编译/Docker打包，每月可跑 ~25h
EOF
  exit 1
}

SNAPSHOT_FOR_TIER() {
  case "$1" in
    sm)  echo "freestyle/ubuntu-sm" ;;
    std) echo "freestyle/ubuntu" ;;
    *)   echo "freestyle/ubuntu-sm" ;;
  esac
}

IDLE_TIMEOUT_FOR_TIER() {
  case "$1" in
    sm)  echo "600" ;; # 10 分钟
    std) echo "300" ;; # 5 分钟
  esac
}

get_vm_state() {
  local slug="$1"
  local vms_json
  if ! vms_json="$(freestyle --output json vm list 2>&1)"; then
    echo "[freestyle-sandbox] 错误: 获取 VM 列表失败: $vms_json" >&2
    return 1
  fi

  echo "$vms_json" | python3 -c '
import sys, json
slug = sys.argv[1]
try:
    data = json.load(sys.stdin)
    vms = data.get("vms", [])
    target = next((v for v in vms if v.get("slug") == slug or v.get("id") == slug), None)
    if target:
        print(target.get("state", "unknown"))
    else:
        print("none")
except Exception as e:
    sys.stderr.write(f"JSON 解析失败: {e}\n")
    sys.exit(2)
' "$slug"
}

wait_for_state() {
  local slug="$1"
  local target="$2"
  local timeout="${3:-30}"
  local elapsed=0
  while [ "$elapsed" -lt "$timeout" ]; do
    local cur
    cur="$(get_vm_state "$slug")" || return 1
    if [ "$cur" = "$target" ]; then
      return 0
    fi
    sleep 1
    elapsed=$((elapsed + 1))
  done
  echo "[freestyle-sandbox] 等待 VM '$slug' 进入 '$target' 状态超时 (${timeout}s)" >&2
  return 1
}

ensure_vm() {
  local slug="${1:-}"
  local tier="${2:-sm}"
  [ -z "$slug" ] && usage

  local snapshot
  local idle
  snapshot="$(SNAPSHOT_FOR_TIER "$tier")"
  idle="$(IDLE_TIMEOUT_FOR_TIER "$tier")"

  local state
  state="$(get_vm_state "$slug")" || return 1

  case "$state" in
    none)
      echo "[freestyle-sandbox] VM '$slug' 不存在，正在按规格 '$tier' ($snapshot) 创建..."
      freestyle vm create --snapshot-id "$snapshot" --slug "$slug" --idle-timeout-seconds "$idle" --no-ssh
      wait_for_state "$slug" "running" 30
      ;;
    paused|stopped)
      echo "[freestyle-sandbox] VM '$slug' 处于 $state 状态，正在唤醒..."
      freestyle vm start "$slug"
      wait_for_state "$slug" "running" 30
      ;;
    pausing)
      echo "[freestyle-sandbox] VM '$slug' 处于 pausing 状态，等待其暂停后重新唤醒..."
      wait_for_state "$slug" "paused" 20
      freestyle vm start "$slug"
      wait_for_state "$slug" "running" 30
      ;;
    starting)
      echo "[freestyle-sandbox] VM '$slug' 正在启动中，等待就绪..."
      wait_for_state "$slug" "running" 30
      ;;
    running)
      echo "[freestyle-sandbox] VM '$slug' 已处于运行状态 (running)。"
      ;;
    *)
      echo "[freestyle-sandbox] 警告: VM '$slug' 处于未知状态: $state" >&2
      ;;
  esac
}

run_task() {
  local slug="${1:-}"
  local tier="${2:-sm}"
  [ -z "$slug" ] && usage
  shift 2 || usage

  if [ $# -eq 0 ]; then
    echo "[freestyle-sandbox] 错误: 未指定要执行的命令" >&2
    usage
  fi

  ensure_vm "$slug" "$tier"

  # 激活全局退出守护钩子
  CURRENT_RUNNING_SLUG="$slug"
  PAUSED_DONE=0

  # 参数处理：若仅单参数且含复合语法，使用 bash -lc 包装；多参数直接数组透传
  local exec_args=()
  if [ $# -eq 1 ]; then
    if [[ "$1" =~ [[:space:]] || "$1" =~ [\&\|\;\<\>] ]]; then
      exec_args=(bash -lc "$1")
    else
      exec_args=("$1")
    fi
  else
    exec_args=("$@")
  fi

  echo "[freestyle-sandbox] 正在 VM '$slug' 中执行任务: ${exec_args[*]}"
  local exit_code=0
  set +e
  freestyle vm exec "$slug" -- "${exec_args[@]}"
  exit_code=$?
  set -e

  exit $exit_code
}

CMD="${1:-}"
[ -z "$CMD" ] && usage

case "$CMD" in
  list)
    freestyle vm list
    ;;

  ensure)
    shift 1
    ensure_vm "$@"
    ;;

  run)
    shift 1
    run_task "$@"
    ;;

  pause)
    SLUG="${2:-}"
    [ -z "$SLUG" ] && usage
    freestyle vm pause "$SLUG"
    ;;

  start)
    SLUG="${2:-}"
    [ -z "$SLUG" ] && usage
    freestyle vm start "$SLUG"
    ;;

  destroy)
    SLUG="${2:-}"
    [ -z "$SLUG" ] && usage
    freestyle vm delete "$SLUG"
    ;;

  *)
    usage
    ;;
esac
