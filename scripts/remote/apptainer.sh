# apptainer.sh - Apptainer container commands

# SIF file path: use REMOTE_SIF_DIR if set, otherwise look in REMOTE_DIR
get_sif_path() {
  if [[ -n "${REMOTE_SIF_DIR:-}" ]]; then
    echo "${REMOTE_SIF_DIR}/${APPTAINER_SIF}"
  else
    echo "${APPTAINER_SIF}"
  fi
}

# Build apptainer options string
get_apptainer_opts() {
  local opts="${APPTAINER_OPTS:---nv}"
  if [[ -n "${APPTAINER_BIND:-}" ]]; then
    opts="$opts --bind ${APPTAINER_BIND}"
  fi
  echo "$opts"
}

cmd_apptainer_shell() {
  ensure_remote_repo
  local sif_path opts
  sif_path="$(get_sif_path)"
  opts="$(get_apptainer_opts)"
  echo "Run this command to enter apptainer shell:"
  echo "  ssh -t $REMOTE_HOST \"cd $REMOTE_DIR && apptainer shell $opts $sif_path\""
}

cmd_apptainer_exec() {
  local cmd="${1:-}"
  [[ -n "$cmd" ]] || die "apptainer-exec requires <command>" 2
  shift || true
  local args="$*"

  ensure_remote_repo
  local sif_path opts
  sif_path="$(get_sif_path)"
  opts="$(get_apptainer_opts)"
  local payload
  payload="$(cat <<EOF
set -e
cd $(printf "%q" "$REMOTE_DIR")
if [[ ! -f $(printf "%q" "$sif_path") ]]; then
  echo "[policy] SIF file not found: $sif_path" >&2
  exit 3
fi
apptainer exec $opts $(printf "%q" "$sif_path") $cmd $args
EOF
)"
  remote_shq "$payload"
}

cmd_apptainer_info() {
  ensure_remote_repo
  local sif_path
  sif_path="$(get_sif_path)"
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); echo '=== Apptainer version ==='; apptainer --version 2>/dev/null || echo 'apptainer not found'; echo ''; echo '=== SIF file ==='; if [[ -f $(printf "%q" "$sif_path") ]]; then ls -lh $(printf "%q" "$sif_path"); else echo 'SIF not found: $sif_path'; fi; echo ''; echo '=== GPU (nvidia-smi) ==='; nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv 2>/dev/null || echo 'nvidia-smi not available'"
}
