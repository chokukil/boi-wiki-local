param(
  [string]$Root = (Get-Location).Path
)

$EmployeeId = if ($env:BOI_LOCAL_EMPLOYEE_ID) { $env:BOI_LOCAL_EMPLOYEE_ID } else { "0000000" }
$status = 0

if ($EmployeeId -notmatch '^[0-9]{7}$') {
  Write-Host "ERROR BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID."
  $status = 1
}

$legacyId = "m" + "e"
if (Test-Path (Join-Path $Root "data/boi/private/$legacyId")) {
  Write-Host "ERROR legacy non-numeric private folder is not allowed."
  $status = 1
}

if ($status -ne 0) {
  exit $status
}

$baseRel = "data/boi/private/$EmployeeId"
$basePath = Join-Path $Root $baseRel
$scaffoldPath = Join-Path $Root "data/boi/private/0000000"
if ($EmployeeId -ne "0000000" -and !(Test-Path $basePath) -and (Test-Path $scaffoldPath)) {
  $installPath = Join-Path $Root "install.ps1"
  if (Test-Path $installPath) {
    & $installPath -Root $Root | Out-Null
  } else {
    Copy-Item -Recurse -Path $scaffoldPath -Destination $basePath
    Get-ChildItem -Path $basePath -Recurse -Filter "*.md" | ForEach-Object {
      $content = Get-Content $_.FullName -Raw
      $content = $content.Replace('employee_id: "0000000"', "employee_id: `"$EmployeeId`"")
      $content = $content.Replace('local_owner_ref: local-private:0000000', "local_owner_ref: local-private:$EmployeeId")
      $content = $content.Replace('data/boi/private/0000000', "data/boi/private/$EmployeeId")
      Set-Content -Path $_.FullName -Value $content -NoNewline
    }
  }
}

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
Check-File "$baseRel/index.md"
Check-File "$baseRel/inbox.md"
Check-Dir "$baseRel/notes"
Check-Dir "$baseRel/sop-drafts"
Check-Dir "$baseRel/promotion-drafts"
Check-Dir "$baseRel/action-drafts"
Check-Dir "$baseRel/event-drafts"
Check-Dir "$baseRel/dictionary"
Check-Dir "$baseRel/diagrams"
Check-Dir "$baseRel/context-packs"
Check-Dir "$baseRel/workflow-simulations"
Check-Dir "$baseRel/langflow-plans"
Check-Dir "$baseRel/usage-examples"
Check-File ".agents/skills/boi-sop-flow-visualizer/SKILL.md"
Check-File ".agents/skills/boi-event-workflow-planner/SKILL.md"
Check-File ".agents/skills/boi-action-author/SKILL.md"
Check-File ".agents/skills/boi-dictionary-author/SKILL.md"
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
