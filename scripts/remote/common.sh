# common.sh - Shared functions for remote.sh modules

die() { echo "ERROR: $*" >&2; exit "${2:-2}"; }

ssh_remote() {
  # shellcheck disable=SC2086
  ssh $REMOTE_SSH_OPTS "$REMOTE_HOST" "$@"
}

remote_shq() {
  local payload="$1"
  ssh_remote "bash -lc $(printf "%q" "$payload")"
}

ensure_remote_repo() {
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR") >/dev/null 2>&1 || { echo '[policy] missing repo dir: $REMOTE_DIR' >&2; exit 3; }; echo '[remote] repo ok: '"$REMOTE_DIR""
}

# Strict validation for experiment directories
validate_exp_dir() {
  local exp="$1"
  [[ "$exp" =~ ^experiments/exp_[A-Za-z0-9._-]+/?$ ]] || die "exp_dir must match experiments/exp_<slug> (got: $exp)" 2
}

# Generate tmux session name from experiment path
session_name_for_exp() {
  local exp="$1"
  local s="${exp//\//_}"
  echo "exp_${s}"
}

# Lock block for GPU runs
remote_lock_block() {
  cat <<'EOF'
LOCK_DIR=".locks/gpu_run.lock"
mkdir -p .locks
if [[ "${REMOTE_LOCK}" == "1" ]]; then
  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "[lock] acquired: $LOCK_DIR"
    cleanup_lock() { rmdir "$LOCK_DIR" >/dev/null 2>&1 || true; }
    trap cleanup_lock EXIT INT TERM
  else
    echo "[lock] busy: another run is active (lock exists: $LOCK_DIR)" >&2
    exit 3
  fi
else
  echo "[lock] disabled"
fi
EOF
}
