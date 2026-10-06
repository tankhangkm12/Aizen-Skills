#!/usr/bin/env bash
# aizen-upgrade.sh — upgrade Aizen in a running project, safely (Linux, macOS, Git Bash, WSL).
# Same steps as aizen-upgrade.bat. Run from the project (any sub-folder); keep this file OUTSIDE the project.
#
#   aizen-upgrade.sh check       [base]   inspect only, change nothing — run this first
#   aizen-upgrade.sh upgrade     [base]   back up, untrack agent files, update skills, install hooks
#   aizen-upgrade.sh finish      [base]   continue with steps 4–6 when upgrade stopped after the skill update
#   aizen-upgrade.sh after-merge [base]   after the "untrack" PR is merged: back to base, pull, restore skills
#   aizen-upgrade.sh restore              copy the installed skills back (a checkout of an old branch overwrote them)
#   aizen-upgrade.sh rollback             put skills and .aizen back as they were before the upgrade
# base defaults to develop. Never force-pushes, never rewrites history, never deletes remote branches.
set -euo pipefail

MODE=${1:-check}
BASE=${2:-develop}
BRANCH=chore/untrack-agent-files
AI_FILES=(.agents .claude .cursor .gemini .windsurf .codex .kiro AGENTS.md CLAUDE.md GEMINI.md .mcp.json skills-lock.json graphify-out)
ASSUME_YES=${AIZEN_UPGRADE_YES:-}   # tests / CI: answer yes to every question

die() { echo "[X] $*" >&2; exit 1; }
ask() { [ -n "$ASSUME_YES" ] && return 0; read -r -p "$1 [y/N] " a; [[ $a =~ ^[Yy] ]]; }

for t in git uv npx; do command -v "$t" >/dev/null || die "$t not found on PATH"; done
ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || die "not a git repository"
cd "$ROOT"
GITDIR=$(git rev-parse --absolute-git-dir)
REPO=$(basename "$ROOT")
BKFILE="$GITDIR/aizen-upgrade-backup.txt"

core_dir() {
  local b
  for b in .agents/skills .claude/skills; do
    [ -f "$b/aizen-core/manifest.json" ] && { echo "$b/aizen-core"; return; }
  done
  echo ""
}
version() { sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$1/manifest.json" | head -1; }
tracked() { git ls-files -- "${AI_FILES[@]}"; }
dirty() { [ -n "$(git status --porcelain)" ]; }

report() {
  local core; core=$(core_dir)
  echo "Branch          : $(git branch --show-current)"
  if [ -n "$core" ]; then echo "Aizen installed : $(version "$core")  [$core]"; else echo "[!] no aizen-core in .agents/skills or .claude/skills"; fi
  git rev-parse --verify --quiet "refs/heads/$BASE" >/dev/null || echo "[!] no local branch $BASE — pass the right base as 2nd argument"
  if dirty; then echo "[!] uncommitted changes — commit or stash first"; else echo "[ok] working tree clean"; fi
  if [ -n "$(tracked)" ]; then
    echo "[!] agent files tracked by git — upgrade untracks them, the files stay on disk:"
    for p in "${AI_FILES[@]}"; do git ls-files --error-unmatch -- "$p" >/dev/null 2>&1 && echo "      $p"; done
  else
    echo "[ok] no agent files in git"
  fi
  echo "Unpushed commits with a task code (e.g. TET-12) or an AI co-author line — pre-push checks them again:"
  BAD=$(git log --branches --not --remotes -E --grep='[A-Z][A-Z0-9]+-[0-9]+' --grep='Co-Authored-By' --format='      %h %s')
  echo "${BAD:-      none}"
  echo "Aizen runs in progress — finish or stop them first:"
  RUNS=""
  if [ -d .aizen/runs ]; then
    for r in .aizen/runs/*/; do r=$(basename "$r"); [ "$r" = "*" ] || [ "$r" = init ] || RUNS="$RUNS      $r"$'\n'; done
  fi
  printf '%s' "${RUNS:-      none
}"
}

copyset() {  # src dst [noaizen]
  local src=$1 dst=$2 d
  mkdir -p "$dst"
  for d in .agents .claude; do [ -d "$src/$d" ] && cp -a "$src/$d" "$dst/"; done
  [ -f "$src/skills-lock.json" ] && cp -a "$src/skills-lock.json" "$dst/"
  if [ "${3:-}" != noaizen ] && [ -d "$src/.aizen" ]; then
    mkdir -p "$dst/.aizen"
    for e in "$src/.aizen"/* "$src/.aizen"/.[!.]*; do
      [ -e "$e" ] || continue
      case $(basename "$e") in worktrees|cache) ;; *) cp -a "$e" "$dst/.aizen/" ;; esac
    done
  fi
  return 0
}
copyback() {  # src
  local src=$1 d
  [ -d "$src" ] || die "backup not found: $src"
  for d in .agents .claude .aizen; do [ -d "$src/$d" ] && cp -a "$src/$d/." "$ROOT/$d/"; done
  [ -f "$src/skills-lock.json" ] && cp -a "$src/skills-lock.json" "$ROOT/"
  return 0
}
loadbk() { [ -f "$BKFILE" ] || die "upgrade was never run here — no backup"; BK=$(cat "$BKFILE"); }
install_guard() { uv run --quiet "$1/scripts/core/guard.py" install; }
exclude_ai() {
  local p e; mkdir -p "$GITDIR/info"; touch "$GITDIR/info/exclude"
  for p in "${AI_FILES[@]}"; do
    e=$p; [ -d "$p" ] && e="$p/"
    grep -qxF "$e" "$GITDIR/info/exclude" || echo "$e" >> "$GITDIR/info/exclude"
  done
}

steps_4_to_6() {
  local core=$1
  echo "[4/6] guard.py install"
  install_guard "$core"
  exclude_ai
  echo "[5/6] Saving the installed skills to $BK/installed"
  rm -rf "$BK/installed"; copyset "$ROOT" "$BK/installed" noaizen
  echo "[6/6] Checking the branch before push"
  [ -z "$(tracked)" ] || die "agent files are still in git"
  echo "      no agent files in git"
  if ask "Push $BRANCH to GitHub now?"; then
    git push -u origin "$BRANCH"
    if command -v gh >/dev/null && ask "Open a PR into $BASE with gh?"; then
      gh pr create --base "$BASE" --head "$BRANCH" --title "chore: stop tracking local agent tool files" \
        --body "Agent files stay on each machine; the repository keeps only the product." \
        || echo "[!] gh could not open the PR — open it on GitHub from the branch above"
    fi
  fi
  echo
  echo "DONE. Next:"
  echo "  1. Merge the $BRANCH PR into $BASE."
  echo "  2. Run: aizen-upgrade.sh after-merge $BASE"
  echo "  Backup: $BK   — back to the old version: aizen-upgrade.sh rollback"
}

case $MODE in
  check)
    echo "=== Project: $REPO   base: $BASE ==="
    report
    echo; echo "Fix every [!] first, then: aizen-upgrade.sh upgrade $BASE"
    ;;
  upgrade)
    echo "=== Upgrading Aizen — $REPO ==="
    report
    dirty && die "commit or stash first"
    CORE=$(core_dir); [ -n "$CORE" ] || die "Aizen is not installed in this project"
    git rev-parse --verify --quiet "refs/heads/$BASE" >/dev/null || die "no branch $BASE"
    [ -z "$BAD" ] || ask "Unpushed commits above may be refused at push. Continue?" || exit 1
    if [ -n "$RUNS" ]; then
      echo "Runs in progress continue after the upgrade, but their old branches still track .agents/.claude:"
      echo "checking one out overwrites the new skills — then run: aizen-upgrade.sh restore"
      ask "Agent sessions closed, continue?" || exit 1
    fi
    BK="$HOME/aizen-backups/$REPO-$(date +%Y%m%d-%H%M%S)"
    echo "[1/6] Backup → $BK/before"
    copyset "$ROOT" "$BK/before"
    echo "$BK" > "$BKFILE"
    echo "[2/6] Branch $BRANCH from $BASE, untrack agent files"
    git switch -q "$BASE"
    git pull -q --ff-only || die "cannot pull $BASE — check the network or conflicts, then run again"
    if git rev-parse --verify --quiet "refs/heads/$BRANCH" >/dev/null; then git switch -q "$BRANCH"; else git switch -q -c "$BRANCH"; fi
    git rm -r -q --cached --ignore-unmatch -- "${AI_FILES[@]}"
    if git diff --cached --quiet; then echo "      nothing to untrack"; else
      git commit -q -m "chore: stop tracking local agent tool files"; echo "      committed on $BRANCH"; fi
    [ -f "$CORE/manifest.json" ] || copyback "$BK/before"
    echo "[3/6] npx skills update -p"
    npx -y skills update -p || die "skills update failed — run: aizen-upgrade.sh rollback"
    echo "      aizen-core $(version "$CORE")"
    steps_4_to_6 "$CORE"
    ;;
  finish)
    echo "=== Continuing with steps 4–6 — $REPO ==="
    loadbk
    CORE=$(core_dir); [ -n "$CORE" ] || die "no aizen-core"
    steps_4_to_6 "$CORE"
    ;;
  after-merge|restore)
    loadbk
    if [ "$MODE" = after-merge ]; then
      echo "=== After the merge — $REPO ==="
      dirty && die "uncommitted changes"
      git switch -q "$BASE"
      git pull -q --ff-only
      if [ -n "$(tracked)" ]; then echo "[X] $BASE still tracks agent files — PR not merged yet? Merge, then run again."
      elif git branch -d "$BRANCH" >/dev/null 2>&1; then echo "      deleted local branch $BRANCH"; fi
    fi
    echo "Restoring the installed skills from $BK/installed"
    copyback "$BK/installed"
    CORE=$(core_dir); install_guard "$CORE"
    echo "Aizen installed: $(version "$CORE")"
    echo "DONE. Open a new agent session; new tasks: state.py init --task <ID> --goal \"…\" --slug <business-name>"
    ;;
  rollback)
    loadbk
    echo "Putting skills, rules and .aizen back from $BK/before"
    ask "Sure?" || exit 1
    copyback "$BK/before"
    CORE=$(core_dir); install_guard "$CORE" || true
    echo "DONE. Commits on $BRANCH (if any) are kept — delete with: git branch -D $BRANCH"
    ;;
  *) die "usage: aizen-upgrade.sh check|upgrade|finish|after-merge|restore|rollback [base]" ;;
esac
