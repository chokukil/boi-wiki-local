[CmdletBinding()]
param([string]$Root = $PSScriptRoot)

$ErrorActionPreference = "Stop"
$repoRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
if ((Split-Path -Leaf $repoRoot) -eq "scripts") { $repoRoot = Split-Path -Parent $repoRoot }
$tool = Join-Path $repoRoot "scripts\obsidian-golden-journey.ps1"
$vaultPath = Join-Path $env:LOCALAPPDATA ("BoI\demo-vaults\native-check-" + [guid]::NewGuid().ToString("N"))

try {
  $detected = & $tool -Action Detect -Root $repoRoot -VaultPath $vaultPath | ConvertFrom-Json
  if (-not $detected.ok -or -not $detected.windows_local_path -or $detected.unc_path -or $detected.personal_vault_touched) {
    throw "demo Detect did not enforce a Windows-local sanitized target"
  }
  $preview = & $tool -Action Preview -Root $repoRoot -VaultPath $vaultPath | ConvertFrom-Json
  if ([string]$preview.schema -cne "boi-obsidian-golden-journey-plan/v1" -or
      [string]$preview.plan_hash -notmatch '^[0-9a-f]{64}$' -or
      $preview.local_private_included) {
    throw "invalid sanitized demo preview"
  }
  & $tool -Action Apply -Root $repoRoot -VaultPath $vaultPath -ConfirmPlanHash ([string]$preview.plan_hash) | Out-Null
  $verified = & $tool -Action Verify -Root $repoRoot -VaultPath $vaultPath | ConvertFrom-Json
  if (-not $verified.ok -or $verified.local_private_included -or $verified.git_metadata_included -or
      -not $verified.windows_local_path -or $verified.unc_path) {
    throw "sanitized demo verification failed"
  }
  $trackedLeaks = @(Get-ChildItem -LiteralPath $vaultPath -Recurse -File | Where-Object {
    $_.FullName -match '\\data\\boi\\private\\' -or $_.Name -eq '.env' -or $_.Name -eq '.git'
  })
  if ($trackedLeaks.Count -ne 0) { throw "private or repository metadata leaked into the demo Vault" }
  & $tool -Action Recover -Root $repoRoot -VaultPath $vaultPath | Out-Null
  if (Test-Path -LiteralPath $vaultPath) { throw "Recover did not remove the managed demo Vault" }
  Write-Host "OK Obsidian Golden Journey native preview/apply/verify/recover check passed"
  exit 0
} catch {
  Write-Host "ERROR Obsidian Golden Journey native check failed: $($_.Exception.Message)"
  exit 1
} finally {
  if (Test-Path -LiteralPath $vaultPath -PathType Container) {
    $receipt = Join-Path $vaultPath ".boi-demo-vault.json"
    if (Test-Path -LiteralPath $receipt -PathType Leaf) {
      & $tool -Action Recover -Root $repoRoot -VaultPath $vaultPath | Out-Null
    }
  }
}
