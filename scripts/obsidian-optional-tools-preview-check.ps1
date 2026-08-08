[CmdletBinding()]
param([string]$Root = $PSScriptRoot)

$ErrorActionPreference = "Stop"
$repoRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
if ((Split-Path -Leaf $repoRoot) -eq "scripts") { $repoRoot = Split-Path -Parent $repoRoot }
$demoTool = Join-Path $repoRoot "scripts\obsidian-golden-journey.ps1"
$previewTool = Join-Path $repoRoot "scripts\obsidian-optional-tools-preview.ps1"
$vaultPath = Join-Path $env:LOCALAPPDATA ("BoI\demo-vaults\optional-tool-check-" + [guid]::NewGuid().ToString("N"))
$sourcePath = Join-Path ([IO.Path]::GetTempPath()) ("boi-common-source-preview-" + [guid]::NewGuid().ToString("N"))

try {
  [IO.Directory]::CreateDirectory($sourcePath) | Out-Null
  $demoPreview = & $demoTool -Action Preview -Root $repoRoot -VaultPath $vaultPath | ConvertFrom-Json
  & $demoTool -Action Apply -Root $repoRoot -VaultPath $vaultPath -ConfirmPlanHash ([string]$demoPreview.plan_hash) | Out-Null

  $quickAdd = & $previewTool -Component QuickAdd -Root $repoRoot -VaultPath $vaultPath | ConvertFrom-Json
  if ($quickAdd.version -ne "2.21.0" -or $quickAdd.minimum_obsidian_version -ne "1.13.0" -or
      @($quickAdd.distribution_artifacts).Count -ne 3 -or -not $quickAdd.approval_required -or
      $quickAdd.apply_supported -or $quickAdd.personal_vault -or $quickAdd.remote_submitted) {
    throw "QuickAdd exact preview contract failed"
  }
  foreach ($artifact in @($quickAdd.distribution_artifacts)) {
    if ([string]$artifact.sha256 -notmatch '^[0-9a-f]{64}$') { throw "QuickAdd artifact hash is not pinned" }
  }
  if (Test-Path -LiteralPath (Join-Path $vaultPath ".obsidian\plugins\quickadd")) {
    throw "QuickAdd preview installed plugin files"
  }

  $clipper = & $previewTool -Component WebClipper -Root $repoRoot -CommonSourceFolder $sourcePath | ConvertFrom-Json
  $serialized = $clipper | ConvertTo-Json -Depth 10 -Compress
  if (-not $clipper.approval_required -or $clipper.apply_supported -or $clipper.remote_submitted -or
      $clipper.dedicated_folder_created -or $clipper.template.source_kind -ne "web-clip" -or
      [string]$clipper.template.sha256 -notmatch '^[0-9a-f]{64}$' -or
      $clipper.plan_hash -eq $quickAdd.plan_hash) {
    throw "Web Clipper separate exact preview contract failed"
  }
  foreach ($forbidden in @('web-clips/', '"interpreter_enabled":true', '"remote_endpoint_configured":true')) {
    if ($serialized.ToLowerInvariant().Contains($forbidden.ToLowerInvariant())) { throw "Web Clipper preview contains forbidden behavior: $forbidden" }
  }

  & $demoTool -Action Recover -Root $repoRoot -VaultPath $vaultPath | Out-Null
  Write-Host "OK optional Obsidian tools preview check passed"
  exit 0
} catch {
  Write-Host "ERROR optional Obsidian tools preview check failed: $($_.Exception.Message)"
  exit 1
} finally {
  if (Test-Path -LiteralPath $vaultPath -PathType Container) {
    $receipt = Join-Path $vaultPath ".boi-demo-vault.json"
    if (Test-Path -LiteralPath $receipt -PathType Leaf) {
      & $demoTool -Action Recover -Root $repoRoot -VaultPath $vaultPath | Out-Null
    }
  }
  if (Test-Path -LiteralPath $sourcePath -PathType Container) {
    $resolvedTemp = [IO.Path]::GetFullPath($sourcePath).TrimEnd('\')
    $allowedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
    if (-not $resolvedTemp.StartsWith($allowedTemp + '\', [StringComparison]::OrdinalIgnoreCase)) {
      throw "refusing to remove a non-temporary optional-tool check directory"
    }
    [IO.Directory]::Delete($resolvedTemp, $true)
  }
}
