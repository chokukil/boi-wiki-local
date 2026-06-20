param(
  [string]$Root = (Get-Location).Path
)

$EmployeeId = if ($env:BOI_LOCAL_EMPLOYEE_ID) { $env:BOI_LOCAL_EMPLOYEE_ID } else { "0000000" }
if ($EmployeeId -notmatch '^[0-9]{7}$') {
  Write-Error "BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID."
  exit 1
}

$legacyId = "m" + "e"
$legacyPath = Join-Path $Root "data/boi/private/$legacyId"
if (Test-Path $legacyPath) {
  Write-Error "legacy non-numeric private folder is not allowed. Move it to data/boi/private/{7-digit employee_id} first."
  exit 1
}

$scaffoldPath = Join-Path $Root "data/boi/private/0000000"
$baseRel = "data/boi/private/$EmployeeId"
$basePath = Join-Path $Root $baseRel
if ($EmployeeId -ne "0000000" -and !(Test-Path $basePath) -and (Test-Path $scaffoldPath)) {
  Copy-Item -Recurse -Path $scaffoldPath -Destination $basePath
  Get-ChildItem -Path $basePath -Recurse -Filter "*.md" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $content = $content.Replace('employee_id: "0000000"', "employee_id: `"$EmployeeId`"")
    $content = $content.Replace('local_owner_ref: local-private:0000000', "local_owner_ref: local-private:$EmployeeId")
    $content = $content.Replace('data/boi/private/0000000', "data/boi/private/$EmployeeId")
    Set-Content -Path $_.FullName -Value $content -NoNewline
  }
}

$dirs = @(
  "$baseRel/notes",
  "$baseRel/sop-drafts",
  "$baseRel/action-drafts",
  "$baseRel/event-drafts",
  "$baseRel/diagrams",
  "$baseRel/context-packs",
  "$baseRel/workflow-simulations",
  "$baseRel/langflow-plans",
  "$baseRel/usage-examples",
  "$baseRel/reports",
  "$baseRel/promotion-drafts",
  "$baseRel/_archive",
  "assets/diagrams",
  ("$baseRel/_archive/" + (Get-Date -Format "yyyy/MM"))
)

foreach ($dir in $dirs) {
  New-Item -ItemType Directory -Force -Path (Join-Path $Root $dir) | Out-Null
}

$envPath = Join-Path $Root ".env"
$envExamplePath = Join-Path $Root ".env.example"
if (!(Test-Path $envPath) -and (Test-Path $envExamplePath)) {
  Copy-Item $envExamplePath $envPath
}

if (Get-Command git -ErrorAction SilentlyContinue) {
  if (!(Test-Path (Join-Path $Root ".git"))) {
    git -C $Root init | Out-Null
  }
}

Write-Host "BoI Wiki Local is ready at $Root"
Write-Host "Local Private employee_id: $EmployeeId"
Write-Host "Tell your agent: 이 폴더를 BoI Wiki Local로 써줘"
