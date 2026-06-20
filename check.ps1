param(
  [string]$Root = (Get-Location).Path
)

$status = 0

function Check-File($Path) {
  if (!(Test-Path (Join-Path $Root $Path))) {
    Write-Host "ERROR missing file: $Path"
    $script:status = 1
  }
}

function Check-Dir($Path) {
  if (!(Test-Path (Join-Path $Root $Path))) {
    Write-Host "ERROR missing directory: $Path"
    $script:status = 1
  }
}

Check-File "README.md"
Check-File "AGENTS.md"
Check-File "data/boi/index.md"
Check-File "data/boi/log.md"
Check-File "data/boi/private/me/index.md"
Check-File "data/boi/private/me/inbox.md"
Check-Dir "data/boi/private/me/notes"
Check-Dir "data/boi/private/me/sop-drafts"
Check-Dir "data/boi/private/me/promotion-drafts"
Check-Dir "data/boi/private/me/action-drafts"
Check-Dir "data/boi/private/me/event-drafts"
Check-Dir "data/boi/private/me/diagrams"
Check-Dir "data/boi/private/me/context-packs"
Check-Dir "data/boi/private/me/workflow-simulations"
Check-Dir "data/boi/private/me/langflow-plans"
Check-Dir "data/boi/private/me/usage-examples"
Check-File ".agents/skills/boi-sop-flow-visualizer/SKILL.md"
Check-File ".agents/skills/boi-event-workflow-planner/SKILL.md"
Check-File ".agents/skills/boi-action-author/SKILL.md"
Check-File ".agents/skills/boi-context-pack-builder/SKILL.md"
Check-File ".agents/skills/boi-workflow-simulator/SKILL.md"
Check-File ".agents/skills/boi-langflow-connector-planner/SKILL.md"

if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Host "OK git is available"
} else {
  Write-Host "WARN git is not available; plain folder mode is OK"
}

if ($status -eq 0) {
  Write-Host "BoI Wiki Local check passed"
}
exit $status
