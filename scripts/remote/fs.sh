# fs.sh - File system commands

cmd_ls() {
  if [[ -n "$REMOTE_PROJECT" ]]; then
    remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); ls -la"
  else
    remote_shq "set -e; cd $(printf "%q" "$REMOTE_BASE"); ls -la"
  fi
}
