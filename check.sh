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
BASE="$ROOT/$BASE_REL"
SCAFFOLD="$ROOT/data/boi/private/0000000"

if [ "$EMPLOYEE_ID" != "0000000" ] && [ ! -d "$BASE" ] && [ -d "$SCAFFOLD" ]; then
  if [ -f "$ROOT/install.sh" ]; then
    sh "$ROOT/install.sh" "$ROOT" >/dev/null
  else
    cp -R "$SCAFFOLD" "$BASE"
    find "$BASE" -type f -name '*.md' -exec sed -i \
      -e "s/employee_id: \"0000000\"/employee_id: \"$EMPLOYEE_ID\"/g" \
      -e "s/local_owner_ref: local-private:0000000/local_owner_ref: local-private:$EMPLOYEE_ID/g" \
      -e "s#data/boi/private/0000000#data/boi/private/$EMPLOYEE_ID#g" \
      {} +
  fi
fi

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
check_dir "$BASE_REL/dictionary"
check_dir "$BASE_REL/diagrams"
check_dir "$BASE_REL/context-packs"
check_dir "$BASE_REL/workflow-simulations"
check_dir "$BASE_REL/langflow-plans"
check_dir "$BASE_REL/usage-examples"
check_file ".agents/skills/boi-sop-flow-visualizer/SKILL.md"
check_file ".agents/skills/boi-event-workflow-planner/SKILL.md"
check_file ".agents/skills/boi-action-author/SKILL.md"
check_file ".agents/skills/boi-dictionary-author/SKILL.md"
check_file ".agents/skills/boi-context-pack-builder/SKILL.md"
check_file ".agents/skills/boi-workflow-simulator/SKILL.md"
check_file ".agents/skills/boi-langflow-connector-planner/SKILL.md"
check_file "scripts/local_capture.py"
check_file "scripts/local_review.py"
check_file "scripts/promotion_preflight.py"

if command -v git >/dev/null 2>&1; then
  printf '%s\n' "OK git is available"
else
  printf '%s\n' "WARN git is not available; plain folder mode is OK"
fi

if command -v python3 >/dev/null 2>&1; then
  python3 "$ROOT/scripts/local_capture.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" --check >/dev/null || status=1
  python3 "$ROOT/scripts/local_review.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" --check >/dev/null || status=1
  python3 "$ROOT/scripts/promotion_preflight.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" --check >/dev/null || status=1
else
  printf '%s\n' "WARN python3 is not available; local lifecycle helper checks skipped"
fi

if [ "$status" -eq 0 ]; then
  printf '%s\n' "BoI Wiki Local check passed"
fi
exit "$status"
