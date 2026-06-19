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

if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Host "OK git is available"
} else {
  Write-Host "WARN git is not available; plain folder mode is OK"
}

if ($status -eq 0) {
  Write-Host "BoI Wiki Local check passed"
}
exit $status

