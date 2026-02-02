# git.sh - Git commands

cmd_status() {
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git status -sb"
}

cmd_add() {
  local files="${1:-.}"
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git add $files; echo '[add] done'; git status -sb"
}

cmd_commit() {
  local msg="${1:-}"
  [[ -n "$msg" ]] || die "commit requires <message>" 2
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git commit -m '$msg'; echo '[commit] done'"
}

cmd_commit_all() {
  local msg="${1:-}"
  [[ -n "$msg" ]] || die "commit-all requires <message>" 2
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git add -A; git commit -m '$msg'; echo '[commit-all] done'"
}

cmd_pull() {
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git pull"
}

cmd_clone() {
  local url="${1:-$REMOTE_GIT_URL}"
  local branch="${REMOTE_GIT_BRANCH:-}"

  [[ -n "$url" ]] || die "clone requires URL (set REMOTE_GIT_URL or pass as argument)" 2

  local branch_opt=""
  if [[ -n "$branch" ]]; then
    branch_opt="-b $branch"
  fi

  local cmd="set -e; cd $REMOTE_BASE; "
  cmd+="if [[ -d $REMOTE_PROJECT ]]; then echo '[clone] directory already exists: $REMOTE_PROJECT' >&2; exit 3; fi; "
  cmd+="git clone $branch_opt '$url' '$REMOTE_PROJECT'; "
  cmd+="echo '[clone] done: $REMOTE_BASE/$REMOTE_PROJECT'"

  ssh_remote "bash -lc \"$cmd\""
}

cmd_diff() {
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git diff"
}

cmd_log() {
  local n="${1:-10}"
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git log --oneline -n $n"
}

cmd_sync() {
  echo "[sync] Pushing local changes..."
  git push || die "git push failed" 3

  echo "[sync] Pulling on remote..."
  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git pull"
  echo "[sync] done"
}

cmd_push() {
  ensure_remote_repo
  echo "[push] Pushing from remote to origin..."
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git push"
}

cmd_git_config() {
  local name="${1:-$REMOTE_GIT_USER_NAME}"
  local email="${2:-$REMOTE_GIT_USER_EMAIL}"

  [[ -n "$name" ]] || die "git-config requires name (set REMOTE_GIT_USER_NAME or pass as argument)" 2
  [[ -n "$email" ]] || die "git-config requires email (set REMOTE_GIT_USER_EMAIL or pass as argument)" 2

  ensure_remote_repo
  remote_shq "set -e; cd $(printf "%q" "$REMOTE_DIR"); git config user.name '$name'; git config user.email '$email'; echo '[git-config] user.name: $name'; echo '[git-config] user.email: $email'"
}
