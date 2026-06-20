param(
  [string]$Root = (Get-Location).Path
)

$dirs = @(
  "data/boi/private/me/notes",
  "data/boi/private/me/sop-drafts",
  "data/boi/private/me/action-drafts",
  "data/boi/private/me/event-drafts",
  "data/boi/private/me/diagrams",
  "data/boi/private/me/context-packs",
  "data/boi/private/me/workflow-simulations",
  "data/boi/private/me/langflow-plans",
  "data/boi/private/me/usage-examples",
  "data/boi/private/me/reports",
  "data/boi/private/me/promotion-drafts",
  "data/boi/private/me/_archive",
  "assets/diagrams",
  ("data/boi/private/me/_archive/" + (Get-Date -Format "yyyy/MM"))
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
Write-Host "Tell your agent: 이 폴더를 BoI Wiki Local로 써줘"
