#!/usr/bin/env sh
set -eu

ROOT="${1:-$(pwd)}"
EMPLOYEE_ID="${BOI_LOCAL_EMPLOYEE_ID:-0000000}"
status=0

case "$EMPLOYEE_ID" in
  [0-9][0-9][0-9][0-9][0-9][0-9][0-9]) ;;
  *)
    printf '%s\n' "ERROR BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID."
    status=1
    ;;
esac

LEGACY_ID="m""e"
if [ -e "$ROOT/data/boi/private/$LEGACY_ID" ]; then
  printf '%s\n' "ERROR legacy non-numeric private folder is not allowed."
  status=1
fi

if [ "$status" -ne 0 ]; then
  exit "$status"
fi

BASE_REL="data/boi/private/$EMPLOYEE_ID"

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
check_file "$BASE_REL/index.md"
check_file "$BASE_REL/inbox.md"
check_dir "$BASE_REL/notes"
check_dir "$BASE_REL/sop-drafts"
check_dir "$BASE_REL/promotion-drafts"
check_dir "$BASE_REL/action-drafts"
check_dir "$BASE_REL/event-drafts"
check_dir "$BASE_REL/diagrams"
check_dir "$BASE_REL/context-packs"
check_dir "$BASE_REL/workflow-simulations"
check_dir "$BASE_REL/langflow-plans"
check_dir "$BASE_REL/usage-examples"
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
