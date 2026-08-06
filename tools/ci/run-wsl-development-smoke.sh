#!/usr/bin/env bash
# Development-only cross-runtime smoke. WSL output is never production evidence.
set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"

runtime="${1:-}"
configuration="${2:-}"
prompt_id="${3:-}"

if [[ "$runtime" != "codex" && "$runtime" != "claude" ]]; then
  echo "usage: $0 <codex|claude> <with-harness|baseline> <p01..p08>" >&2
  exit 2
fi
if [[ "$configuration" != "with-harness" && "$configuration" != "baseline" ]]; then
  echo "configuration must be with-harness or baseline" >&2
  exit 2
fi
if [[ ! "$prompt_id" =~ ^p0[1-8]$ ]]; then
  echo "prompt_id must be p01..p08" >&2
  exit 2
fi

repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
catalog="$repo/cases/flagship/second-brain/evals/prompts/prompt-catalog.json"
fixture_root="$repo/cases/flagship/second-brain"
work="$(mktemp -d "/tmp/boi-sb-${runtime}-${configuration}-${prompt_id}.XXXXXX")"
mkdir -p "$work/data/boi/private/0000000" "$work/fixtures/sources"

readarray -t prompt_fields < <(
  python3 - "$catalog" "$prompt_id" <<'PY'
import json
import sys

catalog, prompt_id = sys.argv[1:]
item = next(row for row in json.load(open(catalog, encoding="utf-8"))["prompts"] if row["prompt_id"] == prompt_id)
print(item["seed_id"])
print(item["user_prompt"])
for path in item["inputs"]:
    print("INPUT=" + path)
PY
)
seed_id="${prompt_fields[0]}"
prompt="${prompt_fields[1]}"

cp -R "$fixture_root/evals/seeds/$seed_id/." "$work/data/boi/private/0000000/"
for row in "${prompt_fields[@]:2}"; do
  input="${row#INPUT=fixtures/}"
  if [[ "$input" == "sources/*" ]]; then
    cp -R "$fixture_root/fixtures/sources/." "$work/fixtures/sources/"
  else
    cp "$fixture_root/fixtures/$input" "$work/fixtures/$input"
  fi
done

if [[ "$configuration" == "with-harness" ]]; then
  mkdir -p "$work/.boi-harness"
  cp "$repo/harness.lock" "$work/harness.lock"
  cp "$repo/.boi-harness/package.json" "$work/.boi-harness/package.json"
  mkdir -p "$work/data/boi"
  cp "$repo/data/boi/index.md" "$work/data/boi/index.md"
  if [[ "$runtime" == "codex" ]]; then
    mkdir -p "$work/.agents/skills"
    cp "$repo/AGENTS.md" "$work/AGENTS.md"
    cp -R "$repo/.agents/skills/boi-wiki-local" "$work/.agents/skills/"
    cp -R "$repo/.agents/skills/boi-second-brain" "$work/.agents/skills/"
  else
    mkdir -p "$work/.claude/skills"
    cp "$repo/CLAUDE.md" "$work/CLAUDE.md"
    cp -R "$repo/.claude/skills/boi-wiki-local" "$work/.claude/skills/"
    cp -R "$repo/.claude/skills/boi-second-brain" "$work/.claude/skills/"
  fi
fi

cd "$work"
git init -q
git config user.email smoke@example.invalid
git config user.name smoke
git add .
git commit -qm seed

set +e
if [[ "$runtime" == "codex" ]]; then
  timeout 180 codex exec \
    --cd "$work" \
    --sandbox workspace-write \
    --ephemeral \
    --ignore-user-config \
    --ignore-rules \
    --skip-git-repo-check \
    --json \
    -o "$work/last-message.txt" \
    "$prompt" > "$work/events.jsonl" 2> "$work/stderr.txt"
  exit_code=$?
else
  timeout 180 claude \
    --print \
    --no-session-persistence \
    --setting-sources project \
    --permission-mode acceptEdits \
    --tools Read,Write,Edit,Glob,Grep,Bash \
    --output-format json \
    --max-budget-usd 2 \
    "$prompt" > "$work/claude-result.json" 2> "$work/stderr.txt"
  exit_code=$?
  python3 - "$work/claude-result.json" "$work/last-message.txt" <<'PY'
import json
import sys

source, target = sys.argv[1:]
try:
    payload = json.load(open(source, encoding="utf-8"))
    result = payload.get("result", "") if isinstance(payload, dict) else ""
except Exception as exc:
    result = f"unable to parse Claude output: {exc}"
open(target, "w", encoding="utf-8").write(result + "\n")
PY
fi
set -e

echo "schema=boi-local-development-smoke/v1"
echo "production_evidence=false"
echo "environment=wsl"
echo "runtime=$runtime"
echo "configuration=$configuration"
echo "prompt_id=$prompt_id"
echo "exit_code=$exit_code"
echo "workspace=$work"
echo "changed_files_begin"
git status --short
echo "changed_files_end"
echo "last_message_begin"
sed -n '1,160p' "$work/last-message.txt" 2>/dev/null || true
echo "last_message_end"
echo "stderr_begin"
sed -n '1,80p' "$work/stderr.txt" 2>/dev/null || true
echo "stderr_end"
exit "$exit_code"
