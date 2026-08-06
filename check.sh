#!/usr/bin/env sh
set -eu

ROOT="${1:-$(pwd)}"
EMPLOYEE_ID="${BOI_LOCAL_EMPLOYEE_ID:-}"
EMPLOYEE_SOURCE=""
if [ -n "$EMPLOYEE_ID" ]; then
  EMPLOYEE_SOURCE="environment"
elif [ -f "$ROOT/.env" ]; then
  EMPLOYEE_ID="$(sed -n 's/^[[:space:]]*BOI_LOCAL_EMPLOYEE_ID[[:space:]]*=[[:space:]]*//p' "$ROOT/.env" | head -n 1 | sed 's/^["'\'']//;s/["'\'']$//')"
  EMPLOYEE_SOURCE="dotenv"
fi
if [ -z "$EMPLOYEE_ID" ] || { [ "$EMPLOYEE_SOURCE" = "dotenv" ] && [ "$EMPLOYEE_ID" = "0000000" ]; }; then
  profile_count=0
  discovered_profile=""
  for profile_path in "$ROOT"/data/boi/private/[0-9][0-9][0-9][0-9][0-9][0-9][0-9]; do
    [ -d "$profile_path" ] || continue
    profile_name="${profile_path##*/}"
    [ "$profile_name" = "0000000" ] && continue
    profile_count=$((profile_count + 1))
    discovered_profile="$profile_name"
  done
  if [ "$profile_count" -gt 1 ]; then
    printf '%s\n' "ERROR multiple Local Private profiles found; set BOI_LOCAL_EMPLOYEE_ID explicitly."
    exit 1
  fi
  if [ "$profile_count" -eq 1 ]; then EMPLOYEE_ID="$discovered_profile"; else EMPLOYEE_ID="0000000"; fi
fi
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
check_file "scripts/boi_compatibility.py"
check_file "scripts/contribution_check.py"
check_file "scripts/boi_update.py"
check_file "scripts/ux_acceptance.py"
check_file "scripts/obsidian_plugin_check.py"
check_file "scripts/release_evidence.py"
check_file "scripts/pilot_acceptance.py"
check_file "scripts/release_clone_acceptance.py"
check_file "scripts/release_gate.py"
check_file "CONTRIBUTING.md"
check_file "install.cmd"
check_file "update.cmd"
check_file "check.cmd"
check_file "pilot-acceptance.cmd"
check_file "scripts/harness_sync.py"
check_file "scripts/boi_local_common.py"
check_file "scripts/boi_setup.py"
check_file "scripts/local_distill.py"
check_file "scripts/local_search.py"
check_file "scripts/local_lint.py"
check_file "scripts/local_wiki.py"
check_file "scripts/query_quality.py"
check_file "scripts/migrate_local_profile.py"
check_file "scripts/migration_audit.py"
check_file "scripts/wiki_check.py"
check_file ".agents/skills/boi-second-brain/SKILL.md"
check_file ".agents/skills/boi-harness-builder/SKILL.md"
check_file "cases/catalog.json"
check_file "scripts/case_harness_check.py"
check_file "scripts/meta_harness_check.py"
check_file "scripts/case_benchmark.py"
check_file "scripts/build_second_brain_fixture.py"
check_file "scripts/build_reference_case_fixtures.py"
check_file "scripts/build_reference_case_docs.py"
check_file "scripts/build_reference_case_evals.py"
check_file "scripts/build_case_runtime_cards.py"
check_file "templates/global-insight/README.md"
check_file "templates/global-insight/artifact-contract.md"
check_file "cases/research/agentic-ai-change-radar/CASE.md"
check_file "cases/strategy/fab-logistics-digital-twin/CASE.md"
check_file "cases/strategy/scientific-foundation-model-knowledge/CASE.md"
check_file "cases/_schema/handoff.schema.json"
check_file "cases/flagship/second-brain/evals/PROTOCOL.md"
check_file "cases/flagship/second-brain/evals/run-artifact.schema.json"
check_file "cases/flagship/second-brain/fixtures/sources/20-promotion-candidate.md"
check_file "templates/second-brain-guide/00-start-here.md"
check_file "templates/second-brain-guide/30-obsidian-install-and-vault.md"
check_file "templates/second-brain-guide/41-quickadd.md"
check_file "templates/second-brain-guide/42-omnisearch.md"

if command -v git >/dev/null 2>&1; then
  printf '%s\n' "OK git is available"
else
  printf '%s\n' "WARN git is not available; plain folder mode is OK"
fi

if command -v python3 >/dev/null 2>&1; then
  if [ -f "$ROOT/harness.lock" ]; then
    python3 "$ROOT/scripts/harness_sync.py" verify --root "$ROOT" >/dev/null || status=1
  fi
  python3 "$ROOT/scripts/local_capture.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" --check >/dev/null || status=1
  python3 "$ROOT/scripts/local_review.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" --check >/dev/null || status=1
  python3 "$ROOT/scripts/promotion_preflight.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" --check >/dev/null || status=1
  python3 "$ROOT/scripts/local_lint.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" >/dev/null || status=1
  python3 "$ROOT/scripts/local_wiki.py" --root "$ROOT" --employee-id "$EMPLOYEE_ID" wiki-lint >/dev/null || status=1
  python3 "$ROOT/scripts/wiki_check.py" --root "$ROOT" >/dev/null || status=1
  python3 "$ROOT/scripts/contribution_check.py" --root "$ROOT" --all >/dev/null || status=1
  python3 "$ROOT/scripts/obsidian_plugin_check.py" --root "$ROOT" >/dev/null || status=1
  python3 "$ROOT/scripts/case_harness_check.py" --root "$ROOT" >/dev/null || status=1
  python3 "$ROOT/scripts/meta_harness_check.py" --root "$ROOT" >/dev/null || status=1
  python3 "$ROOT/scripts/build_second_brain_fixture.py" --root "$ROOT" --check >/dev/null || status=1
  python3 "$ROOT/scripts/build_reference_case_fixtures.py" --root "$ROOT" --check >/dev/null || status=1
  python3 "$ROOT/scripts/build_reference_case_docs.py" --root "$ROOT" --check >/dev/null || status=1
  python3 "$ROOT/scripts/build_reference_case_evals.py" --check >/dev/null || status=1
  python3 "$ROOT/scripts/build_case_runtime_cards.py" --check >/dev/null || status=1
  python3 -m unittest discover -s "$ROOT/tests" -p 'test_*.py' >/dev/null || status=1
  python3 -m py_compile \
    "$ROOT/scripts/boi_local_common.py" \
    "$ROOT/scripts/boi_setup.py" \
    "$ROOT/scripts/build_guide_media.py" \
    "$ROOT/scripts/local_capture.py" \
    "$ROOT/scripts/local_distill.py" \
    "$ROOT/scripts/local_search.py" \
    "$ROOT/scripts/local_review.py" \
    "$ROOT/scripts/local_lint.py" \
    "$ROOT/scripts/local_wiki.py" \
    "$ROOT/scripts/query_quality.py" \
    "$ROOT/scripts/migrate_local_profile.py" \
    "$ROOT/scripts/migration_audit.py" \
    "$ROOT/scripts/wiki_check.py" \
    "$ROOT/scripts/boi_compatibility.py" \
    "$ROOT/scripts/contribution_check.py" \
    "$ROOT/scripts/boi_update.py" \
    "$ROOT/scripts/ux_acceptance.py" \
    "$ROOT/scripts/obsidian_plugin_check.py" \
    "$ROOT/scripts/release_evidence.py" \
    "$ROOT/scripts/pilot_acceptance.py" \
    "$ROOT/scripts/release_clone_acceptance.py" \
    "$ROOT/scripts/release_gate.py" \
    "$ROOT/scripts/promotion_preflight.py" \
    "$ROOT/scripts/case_harness_check.py" \
    "$ROOT/scripts/meta_harness_check.py" \
    "$ROOT/scripts/case_benchmark.py" \
    "$ROOT/scripts/build_second_brain_fixture.py" \
    "$ROOT/scripts/build_reference_case_fixtures.py" \
    "$ROOT/scripts/build_reference_case_docs.py" \
    "$ROOT/scripts/build_reference_case_evals.py" \
    "$ROOT/scripts/build_case_runtime_cards.py" || status=1
else
  printf '%s\n' "WARN python3 is not available; local lifecycle and Harness snapshot checks skipped"
fi

if [ "$status" -eq 0 ]; then
  printf '%s\n' "BoI Wiki Local check passed"
fi
exit "$status"
