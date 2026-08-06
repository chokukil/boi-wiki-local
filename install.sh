#!/usr/bin/env sh
set -eu

ROOT="${1:-$(pwd)}"
EMPLOYEE_ID="${BOI_LOCAL_EMPLOYEE_ID:-}"

case "$EMPLOYEE_ID" in
  [0-9][0-9][0-9][0-9][0-9][0-9][0-9]) ;;
  *)
    printf '%s\n' "ERROR Set BOI_LOCAL_EMPLOYEE_ID to your numeric 7-digit employee ID."
    exit 1
    ;;
esac

if [ "$EMPLOYEE_ID" = "0000000" ]; then
  printf '%s\n' "ERROR 0000000 is the template ID. Set your real employee ID."
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf '%s\n' "ERROR Python 3 is required for setup and local Second Brain commands."
  exit 1
fi

python3 "$ROOT/scripts/boi_setup.py" doctor --root "$ROOT" --employee-id "$EMPLOYEE_ID"
python3 "$ROOT/scripts/boi_setup.py" preview --root "$ROOT" --employee-id "$EMPLOYEE_ID"
python3 "$ROOT/scripts/boi_setup.py" apply --root "$ROOT" --employee-id "$EMPLOYEE_ID"
python3 "$ROOT/scripts/boi_setup.py" verify --root "$ROOT" --employee-id "$EMPLOYEE_ID"
python3 "$ROOT/scripts/boi_setup.py" next-steps --root "$ROOT" --employee-id "$EMPLOYEE_ID"
