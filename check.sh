#!/usr/bin/env sh
set -eu

ROOT="${1:-$(pwd)}"
status=0

check_file() {
  if [ ! -f "$ROOT/$1" ]; then
    printf '%s\n' "ERROR missing file: $1"
    status=1
  fi
}

check_dir() {
  if [ ! -d "$ROOT/$1" ]; then
    printf '%s\n' "ERROR missing directory: $1"
    status=1
  fi
}

check_file "README.md"
check_file "AGENTS.md"
check_file "data/boi/index.md"
check_file "data/boi/log.md"
check_file "data/boi/private/me/index.md"
check_file "data/boi/private/me/inbox.md"
check_dir "data/boi/private/me/notes"
check_dir "data/boi/private/me/sop-drafts"
check_dir "data/boi/private/me/promotion-drafts"
check_dir "data/boi/private/me/action-drafts"
check_dir "data/boi/private/me/event-drafts"
check_dir "data/boi/private/me/diagrams"
check_dir "data/boi/private/me/context-packs"
check_dir "data/boi/private/me/workflow-simulations"
check_dir "data/boi/private/me/langflow-plans"
check_dir "data/boi/private/me/usage-examples"
check_file ".agents/skills/boi-sop-flow-visualizer/SKILL.md"
check_file ".agents/skills/boi-event-workflow-planner/SKILL.md"
check_file ".agents/skills/boi-action-author/SKILL.md"
check_file ".agents/skills/boi-context-pack-builder/SKILL.md"
check_file ".agents/skills/boi-workflow-simulator/SKILL.md"
check_file ".agents/skills/boi-langflow-connector-planner/SKILL.md"

if command -v git >/dev/null 2>&1; then
  printf '%s\n' "OK git is available"
else
  printf '%s\n' "WARN git is not available; plain folder mode is OK"
fi

if [ "$status" -eq 0 ]; then
  printf '%s\n' "BoI Wiki Local check passed"
fi
exit "$status"
