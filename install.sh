#!/usr/bin/env sh
set -eu

ROOT="${1:-$(pwd)}"
mkdir -p "$ROOT/data/boi/private/me/notes" \
  "$ROOT/data/boi/private/me/sop-drafts" \
  "$ROOT/data/boi/private/me/action-drafts" \
  "$ROOT/data/boi/private/me/event-drafts" \
  "$ROOT/data/boi/private/me/diagrams" \
  "$ROOT/data/boi/private/me/context-packs" \
  "$ROOT/data/boi/private/me/workflow-simulations" \
  "$ROOT/data/boi/private/me/langflow-plans" \
  "$ROOT/data/boi/private/me/usage-examples" \
  "$ROOT/data/boi/private/me/reports" \
  "$ROOT/data/boi/private/me/promotion-drafts" \
  "$ROOT/data/boi/private/me/_archive" \
  "$ROOT/assets/diagrams"

ARCHIVE_MONTH="$(date '+%Y/%m' 2>/dev/null || printf 'YYYY/MM')"
mkdir -p "$ROOT/data/boi/private/me/_archive/$ARCHIVE_MONTH"

if [ ! -f "$ROOT/.env" ] && [ -f "$ROOT/.env.example" ]; then
  cp "$ROOT/.env.example" "$ROOT/.env"
fi

if command -v git >/dev/null 2>&1 && [ ! -d "$ROOT/.git" ]; then
  git -C "$ROOT" init >/dev/null 2>&1 || true
fi

printf '%s\n' "BoI Wiki Local is ready at $ROOT"
printf '%s\n' "Tell your agent: 이 폴더를 BoI Wiki Local로 써줘"
