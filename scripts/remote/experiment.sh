# experiment.sh - Experiment execution commands

cmd_run() {
  local exp="$1"; shift || true
  local cpu_flag=""
  if [[ "${1:-}" == "--cpu" ]]; then
    cpu_flag="--cpu"
    shift || true
  fi

  validate_exp_dir "$exp"
  local sess
  sess="$(session_name_for_exp "$exp")"

  ensure_remote_repo

  local payload
  payload="$(cat <<EOF
set -euo pipefail
cd $(printf "%q" "$REMOTE_DIR")

if [[ ! -x "./scripts/run_apptainer.sh" ]]; then
  echo "[policy] missing ./scripts/run_apptainer.sh (not executable)" >&2
  exit 3
fi

if [[ ! -d "$(printf "%q" "$exp")" ]]; then
  echo "[policy] experiment dir not found: $(printf "%q" "$exp")" >&2
  exit 3
fi

mkdir -p "$(printf "%q" "$exp")/logs" "$(printf "%q" "$exp")/results"

git rev-parse HEAD > "$(printf "%q" "$exp")/logs/git_commit.txt" 2>/dev/null || true
command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi > "$(printf "%q" "$exp")/logs/nvidia_smi.txt" 2>&1 || true
date > "$(printf "%q" "$exp")/logs/run_started_at.txt"

$(remote_lock_block)

RUN_CMD="./scripts/run_apptainer.sh $(printf "%q" "$exp") $cpu_flag"
LOG_MAIN="$(printf "%q" "$exp")/logs/run_remote.log"
LOG_TS="$(printf "%q" "$exp")/logs/run_remote_\$(date +%Y%m%d_%H%M%S).log"

echo "[remote] session: $sess"
echo "[remote] run: \$RUN_CMD"
echo "[remote] logs: \$LOG_MAIN, \$LOG_TS"

if command -v tmux >/dev/null 2>&1; then
  tmux has-session -t "$sess" 2>/dev/null && { echo "[tmux] session exists, not overwriting: $sess" >&2; exit 3; }
  tmux new-session -d -s "$sess" "bash -lc '\$RUN_CMD |& tee "\$LOG_MAIN" | tee "\$LOG_TS"'"
  echo "[tmux] started: $sess"
  echo "Attach with: tmux attach -t $sess"
else
  if [[ "${REMOTE_REQUIRE_TMUX}" == "1" ]]; then
    echo "[policy] tmux required but not available on remote" >&2
    exit 3
  fi
  nohup bash -lc "\$RUN_CMD |& tee "\$LOG_MAIN" | tee "\$LOG_TS"" >/dev/null 2>&1 &
  echo "[nohup] started in background (no tmux). Tail: tail -f "\$LOG_MAIN""
fi
EOF
)"
  remote_shq "$payload"
}

cmd_diag() {
  local exp="$1"
  validate_exp_dir "$exp"
  ensure_remote_repo

  local payload
  payload="$(cat <<EOF
set -euo pipefail
cd $(printf "%q" "$REMOTE_DIR")

if [[ ! -d "$(printf "%q" "$exp")" ]]; then
  echo "[policy] experiment dir not found: $(printf "%q" "$exp")" >&2
  exit 3
fi
mkdir -p "$(printf "%q" "$exp")/logs"

TS="\$(date +%Y%m%d_%H%M%S)"
PACK_DIR="$(printf "%q" "$exp")/logs/diagnostics_\$TS"
mkdir -p "\$PACK_DIR"

uname -a > "\$PACK_DIR/uname.txt" 2>&1 || true
hostname > "\$PACK_DIR/hostname.txt" 2>&1 || true
whoami > "\$PACK_DIR/whoami.txt" 2>&1 || true
date > "\$PACK_DIR/date.txt" 2>&1 || true

git rev-parse HEAD > "\$PACK_DIR/git_commit.txt" 2>&1 || true
git status --porcelain > "\$PACK_DIR/git_status.txt" 2>&1 || true

command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi > "\$PACK_DIR/nvidia_smi.txt" 2>&1 || echo "no nvidia-smi" > "\$PACK_DIR/nvidia_smi.txt"
command -v apptainer >/dev/null 2>&1 && apptainer --version > "\$PACK_DIR/apptainer_version.txt" 2>&1 || echo "no apptainer" > "\$PACK_DIR/apptainer_version.txt"

df -h > "\$PACK_DIR/df.txt" 2>&1 || true
free -h > "\$PACK_DIR/free.txt" 2>&1 || true

ls -la "$(printf "%q" "$exp")" > "\$PACK_DIR/exp_ls.txt" 2>&1 || true

shopt -s nullglob
for f in $(printf "%q" "$exp")/logs/*.log $(printf "%q" "$exp")/logs/*.out; do
  tail -n 200 "\$f" > "\$PACK_DIR/\$(basename "\$f").tail200.txt" 2>&1 || true
done

tar -czf "$(printf "%q" "$exp")/logs/diagnostics_\$TS.tar.gz" -C "\$PACK_DIR" .
echo "Saved: $(printf "%q" "$exp")/logs/diagnostics_\$TS.tar.gz"
EOF
)"
  remote_shq "$payload"
}

cmd_tail() {
  local exp="$1"; shift || true
  validate_exp_dir "$exp"
  local n="${1:-200}"
  [[ "$n" =~ ^[0-9]+$ ]] || die "N must be a number" 2
  ensure_remote_repo

  local payload
  payload="$(cat <<EOF
set -euo pipefail
cd $(printf "%q" "$REMOTE_DIR")
LOG_DIR="$(printf "%q" "$exp")/logs"
if [[ ! -d "\$LOG_DIR" ]]; then
  echo "[policy] missing log dir: \$LOG_DIR" >&2
  exit 3
fi
latest=\$(ls -1t "\$LOG_DIR"/*.log 2>/dev/null | head -n 1 || true)
if [[ -z "\$latest" ]]; then
  echo "[info] no .log files found in \$LOG_DIR" >&2
  exit 0
fi
echo "[tail] \$latest"
tail -n "$n" "\$latest"
EOF
)"
  remote_shq "$payload"
}

cmd_exp_attach() {
  local exp="$1"
  validate_exp_dir "$exp"
  local sess
  sess="$(session_name_for_exp "$exp")"
  echo "Run this command to attach:"
  echo "  ssh $REMOTE_HOST \"tmux attach -t $sess\""
}
