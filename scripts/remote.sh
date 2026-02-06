#!/usr/bin/env bash
set -euo pipefail

# remote.sh - SSH remote runner with policy enforcement (Saliuitl_dev)
#
# Goal:
# - One entry point for remote operations
# - Enforce safe constraints (fixed remote dir, whitelisted subcommands, exp path validation)
# - Make long runs robust (tmux if available, else nohup)
#
# Setup (recommended):
#   Edit scripts/.env_remote with your settings
#
# Usage:
#   ./scripts/remote.sh <command> [args...]
#
# Commands:
#   File System:
#     ls                          List REMOTE_DIR (or REMOTE_BASE if no project)
#
#   Git:
#     status                      Show git status (short)
#     pull                        Git pull in REMOTE_DIR
#
#   Tmux:
#     tmux-ls                     List all tmux sessions
#     tmux-new <name>             Create new tmux session
#     tmux-attach <name>          Print attach command
#     tmux-kill <name>            Kill tmux session
#
#   Apptainer:
#     apptainer-shell             Print command to enter apptainer shell
#     apptainer-exec <cmd>        Execute command inside apptainer
#     apptainer-info              Show apptainer/GPU info
#
#   Experiments:
#     run <exp_dir> [--cpu]       Run experiment in tmux/nohup
#     diag <exp_dir>              Collect diagnostics
#     tail <exp_dir> [N]          Tail latest log (default 200 lines)
#     attach <exp_dir>            Print tmux attach command for experiment
#
# Policy knobs (via .env_remote or environment):
#   REMOTE_HOST, REMOTE_BASE, REMOTE_PROJECT
#   REMOTE_REQUIRE_TMUX=0/1, REMOTE_LOCK=0/1, REMOTE_SSH_OPTS="..."
#   APPTAINER_SIF=saliuitl.sif
#
# Exit codes:
#   2: usage / validation error
#   3: remote policy violation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env_remote if exists
if [[ -f "$SCRIPT_DIR/.env_remote" ]]; then
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.env_remote"
fi

# Defaults (can be overridden by .env_remote or environment)
REMOTE_HOST="${REMOTE_HOST:-ohki_highgarden}"
REMOTE_BASE="${REMOTE_BASE:-hsdisk}"
REMOTE_PROJECT="${REMOTE_PROJECT:-Saliuitl_dev}"
REMOTE_DIR_OVERRIDE="${REMOTE_DIR_OVERRIDE:-}"
REMOTE_REQUIRE_TMUX="${REMOTE_REQUIRE_TMUX:-0}"
REMOTE_LOCK="${REMOTE_LOCK:-1}"
REMOTE_SSH_OPTS="${REMOTE_SSH_OPTS:-}"
APPTAINER_SIF="${APPTAINER_SIF:-saliuitl.sif}"
REMOTE_GIT_URL="${REMOTE_GIT_URL:-}"
REMOTE_GIT_BRANCH="${REMOTE_GIT_BRANCH:-}"

if [[ -n "$REMOTE_DIR_OVERRIDE" ]]; then
  REMOTE_DIR="$REMOTE_DIR_OVERRIDE"
else
  if [[ -n "$REMOTE_PROJECT" ]]; then
    REMOTE_DIR="${REMOTE_BASE}/${REMOTE_PROJECT}"
  else
    REMOTE_DIR="${REMOTE_BASE}"
  fi
fi

# Export for submodules
export REMOTE_HOST REMOTE_BASE REMOTE_PROJECT REMOTE_DIR REMOTE_DIR_OVERRIDE
export REMOTE_REQUIRE_TMUX REMOTE_LOCK REMOTE_SSH_OPTS APPTAINER_SIF
export REMOTE_GIT_URL REMOTE_GIT_BRANCH
export REMOTE_GIT_USER_NAME="${REMOTE_GIT_USER_NAME:-}"
export REMOTE_GIT_USER_EMAIL="${REMOTE_GIT_USER_EMAIL:-}"
export REMOTE_SIF_DIR="${REMOTE_SIF_DIR:-}"
export APPTAINER_BIND="${APPTAINER_BIND:-}"
export APPTAINER_OPTS="${APPTAINER_OPTS:-}"

# Load modules
source "$SCRIPT_DIR/remote/common.sh"
source "$SCRIPT_DIR/remote/fs.sh"
source "$SCRIPT_DIR/remote/git.sh"
source "$SCRIPT_DIR/remote/tmux.sh"
source "$SCRIPT_DIR/remote/apptainer.sh"
source "$SCRIPT_DIR/remote/experiment.sh"

usage() {
  cat <<'EOF'
Usage: remote.sh <command> [args...]

File System:
  ls                          List REMOTE_DIR (or REMOTE_BASE if no project)

Git:
  status                      Show git status (short)
  add [files]                 Git add (default: all)
  commit <msg>                Git commit with message
  commit-all <msg>            Git add -A && commit
  pull                        Git pull in REMOTE_DIR
  push                        Push from remote to origin
  sync                        Push local, then pull on remote
  clone [url]                 Clone repo to REMOTE_DIR
  diff                        Show git diff
  log [N]                     Show last N commits (default 10)
  git-config [name] [email]   Set git user.name and user.email on remote

Tmux:
  tmux-ls                     List all tmux sessions
  tmux-new <name>             Create new tmux session
  tmux-attach <name>          Print attach command
  tmux-kill <name>            Kill tmux session

Apptainer:
  apptainer-shell             Print command to enter apptainer shell
  apptainer-exec <cmd> [args] Execute command inside apptainer
  apptainer-info              Show apptainer/GPU info

Experiments:
  run <exp_dir> [--cpu]       Run experiment in tmux/nohup
  diag <exp_dir>              Collect diagnostics
  tail <exp_dir> [N]          Tail latest log (default 200 lines)
  attach <exp_dir>            Print tmux attach command for experiment

Environment (set in .env_remote):
  REMOTE_HOST       Remote SSH host
  REMOTE_BASE       Base directory on remote
  REMOTE_PROJECT    Project subdirectory (empty = use REMOTE_BASE)
  APPTAINER_SIF     SIF container file name

Examples:
  ./scripts/remote.sh ls
  ./scripts/remote.sh tmux-ls
  ./scripts/remote.sh tmux-new dev
  ./scripts/remote.sh apptainer-shell
  ./scripts/remote.sh run experiments/exp_20260202_test
EOF
}

cmd="${1:-}"
shift || true

case "$cmd" in
  ""|-h|--help|help)
    usage; exit 0;;

  # File System
  ls)
    cmd_ls;;

  # Git
  status)
    cmd_status;;
  add)
    cmd_add "${1:-.}";;
  commit)
    [[ $# -ge 1 ]] || die "commit requires <message>" 2
    cmd_commit "$1";;
  commit-all)
    [[ $# -ge 1 ]] || die "commit-all requires <message>" 2
    cmd_commit_all "$1";;
  pull)
    cmd_pull;;
  push)
    cmd_push;;
  sync)
    cmd_sync;;
  clone)
    cmd_clone "${1:-}";;
  diff)
    cmd_diff;;
  log)
    cmd_log "${1:-10}";;
  git-config)
    cmd_git_config "${1:-}" "${2:-}";;

  # Tmux
  tmux-ls|sessions)
    cmd_tmux_ls;;
  tmux-new)
    [[ $# -ge 1 ]] || die "tmux-new requires <session_name>" 2
    cmd_tmux_new "$1";;
  tmux-attach)
    [[ $# -ge 1 ]] || die "tmux-attach requires <session_name>" 2
    cmd_tmux_attach "$1";;
  tmux-kill)
    [[ $# -ge 1 ]] || die "tmux-kill requires <session_name>" 2
    cmd_tmux_kill "$1";;

  # Apptainer
  apptainer-shell|shell)
    cmd_apptainer_shell;;
  apptainer-exec|exec)
    [[ $# -ge 1 ]] || die "apptainer-exec requires <command>" 2
    cmd_apptainer_exec "$@";;
  apptainer-info|info)
    cmd_apptainer_info;;

  # Experiments
  run)
    [[ $# -ge 1 ]] || die "run requires <experiment_dir>" 2
    cmd_run "$@";;
  diag)
    [[ $# -eq 1 ]] || die "diag requires <experiment_dir>" 2
    cmd_diag "$1";;
  tail)
    [[ $# -ge 1 ]] || die "tail requires <experiment_dir> [N]" 2
    cmd_tail "$@";;
  attach)
    [[ $# -eq 1 ]] || die "attach requires <experiment_dir>" 2
    cmd_exp_attach "$1";;

  *)
    die "unknown command: $cmd" 2;;
esac
