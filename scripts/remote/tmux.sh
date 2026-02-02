# tmux.sh - Tmux session management commands

cmd_tmux_ls() {
  remote_shq "tmux list-sessions 2>/dev/null || echo 'No tmux sessions found.'"
}

cmd_tmux_new() {
  local name="${1:-}"
  [[ -n "$name" ]] || die "tmux-new requires <session_name>" 2

  local payload
  payload="$(cat <<EOF
set -e
cd $(printf "%q" "$REMOTE_DIR")
if tmux has-session -t $(printf "%q" "$name") 2>/dev/null; then
  echo "[tmux] session already exists: $name" >&2
  exit 3
fi
tmux new-session -d -s $(printf "%q" "$name")
echo "[tmux] created session: $name"
echo "Attach with: ssh $REMOTE_HOST \"tmux attach -t $name\""
EOF
)"
  ensure_remote_repo
  remote_shq "$payload"
}

cmd_tmux_attach() {
  local name="${1:-}"
  [[ -n "$name" ]] || die "tmux-attach requires <session_name>" 2
  echo "Run this command to attach:"
  echo "  ssh $REMOTE_HOST \"tmux attach -t $name\""
}

cmd_tmux_kill() {
  local name="${1:-}"
  [[ -n "$name" ]] || die "tmux-kill requires <session_name>" 2

  remote_shq "tmux kill-session -t $(printf "%q" "$name") && echo '[tmux] killed session: $name'"
}
