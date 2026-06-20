#!/usr/bin/env sh
set -eu

ROOT="${1:-$(pwd)}"
EMPLOYEE_ID="${BOI_LOCAL_EMPLOYEE_ID:-0000000}"

case "$EMPLOYEE_ID" in
  [0-9][0-9][0-9][0-9][0-9][0-9][0-9]) ;;
  *)
    printf '%s\n' "ERROR BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID."
    exit 1
    ;;
esac

LEGACY_ID="m""e"
if [ -e "$ROOT/data/boi/private/$LEGACY_ID" ]; then
  printf '%s\n' "ERROR legacy non-numeric private folder is not allowed. Move it to data/boi/private/{7-digit employee_id} first."
  exit 1
fi

SCAFFOLD="$ROOT/data/boi/private/0000000"
BASE="$ROOT/data/boi/private/$EMPLOYEE_ID"

if [ "$EMPLOYEE_ID" != "0000000" ] && [ ! -d "$BASE" ] && [ -d "$SCAFFOLD" ]; then
  cp -R "$SCAFFOLD" "$BASE"
  find "$BASE" -type f -name '*.md' -exec sed -i \
    -e "s/employee_id: \"0000000\"/employee_id: \"$EMPLOYEE_ID\"/g" \
    -e "s/local_owner_ref: local-private:0000000/local_owner_ref: local-private:$EMPLOYEE_ID/g" \
    -e "s#data/boi/private/0000000#data/boi/private/$EMPLOYEE_ID#g" \
    {} +
fi

mkdir -p "$BASE/notes" \
  "$BASE/sop-drafts" \
  "$BASE/action-drafts" \
  "$BASE/event-drafts" \
  "$BASE/diagrams" \
  "$BASE/context-packs" \
  "$BASE/workflow-simulations" \
  "$BASE/langflow-plans" \
  "$BASE/usage-examples" \
  "$BASE/reports" \
  "$BASE/promotion-drafts" \
  "$BASE/_archive" \
  "$ROOT/assets/diagrams"

ARCHIVE_MONTH="$(date '+%Y/%m' 2>/dev/null || printf 'YYYY/MM')"
mkdir -p "$BASE/_archive/$ARCHIVE_MONTH"

if [ ! -f "$ROOT/.env" ] && [ -f "$ROOT/.env.example" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

if command -v git >/dev/null 2>&1 && [ ! -d "$ROOT/.git" ]; then
  git -C "$ROOT" init >/dev/null 2>&1 || true
fi

printf '%s\n' "BoI Wiki Local is ready at $ROOT"
printf '%s\n' "Local Private employee_id: $EMPLOYEE_ID"
printf '%s\n' "Tell your agent: 이 폴더를 BoI Wiki Local로 써줘"
