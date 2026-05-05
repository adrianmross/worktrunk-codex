codex_has_explicit_profile() {
  local arg
  for arg in "$@"; do
    case "$arg" in
      -p|--profile|--profile=*)
        return 0
        ;;
    esac
  done

  return 1
}

codex_is_linked_worktree() {
  command -v git >/dev/null 2>&1 || return 1
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || return 1

  local -a git_paths
  git_paths=("${(@f)$(git rev-parse --path-format=absolute --git-dir --git-common-dir 2>/dev/null)}")

  [[ ${#git_paths[@]} -ge 2 ]] || return 1
  [[ -n "${git_paths[1]}" && -n "${git_paths[2]}" ]] || return 1
  [[ "${git_paths[1]}" != "${git_paths[2]}" ]]
}

codex() {
  local profile="${CODEX_LINKED_WORKTREE_PROFILE:-worktree-git}"

  if [[ -n "${CODEX_DISABLE_LINKED_WORKTREE_PROFILE:-}" ]]; then
    command codex "$@"
    return $?
  fi

  if codex_has_explicit_profile "$@"; then
    command codex "$@"
    return $?
  fi

  if codex_is_linked_worktree; then
    command codex -p "$profile" "$@"
    return $?
  fi

  command codex "$@"
}

wtcodex() {
  local -a switch_args exec_args
  local saw_separator=0

  while (( $# > 0 )); do
    if [[ "$1" == "--" ]]; then
      saw_separator=1
      shift
      break
    fi

    switch_args+=("$1")
    shift
  done

  if (( saw_separator )); then
    exec_args=("$@")
    wt switch "${switch_args[@]}" -x codex -- "${exec_args[@]}"
    return $?
  fi

  wt switch "${switch_args[@]}" -x codex
}

wtreview() {
  command -v dev-handoff >/dev/null 2>&1 || {
    echo "dev-handoff is not available in PATH" >&2
    return 1
  }

  if (( $# == 0 )); then
    dev-handoff review-current @
    return $?
  fi

  dev-handoff review-current "$@"
}
