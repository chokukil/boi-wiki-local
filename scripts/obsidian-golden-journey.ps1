[CmdletBinding()]
param(
  [ValidateSet("Detect", "Preview", "Apply", "Verify", "Recover")]
  [string]$Action = "Detect",
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string]$VaultPath = "",
  [string]$ConfirmPlanHash = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
$managedBase = Join-Path $env:LOCALAPPDATA "BoI\demo-vaults"
if (-not $VaultPath) { $VaultPath = Join-Path $managedBase "agentic-ai-change-radar-community" }
$resolvedVault = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($VaultPath)
$demoRoot = Join-Path $repoRoot "cases\research\agentic-ai-change-radar\golden-journey"
$walkthrough = Join-Path $demoRoot "obsidian-demo"
$receiptName = ".boi-demo-vault.json"
if ($repoRoot.StartsWith('\\') -or $resolvedVault.StartsWith('\\')) {
  throw "Golden Journey demo requires Windows-local paths; UNC paths are not supported"
}

function Get-Hash([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-TextHash([string]$Text) {
  $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
  $algorithm = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($algorithm.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant() }
  finally { $algorithm.Dispose() }
}

function Get-Plan {
  $mappings = @(
    @{ source = "obsidian-demo/00-Golden-Journey.md"; target = "obsidian-demo/00-Golden-Journey.md" },
    @{ source = "obsidian-demo/01-T0-Baseline.md"; target = "obsidian-demo/01-T0-Baseline.md" },
    @{ source = "obsidian-demo/02-T1-Update.md"; target = "obsidian-demo/02-T1-Update.md" },
    @{ source = "obsidian-demo/03-Same-Query-Diff.md"; target = "obsidian-demo/03-Same-Query-Diff.md" },
    @{ source = "obsidian-demo/04-Review-Queue.md"; target = "obsidian-demo/04-Review-Queue.md" },
    @{ source = "obsidian-demo/05-Common-Raw-Source-Intake.md"; target = "obsidian-demo/05-Common-Raw-Source-Intake.md" },
    @{ source = "obsidian-demo/06-Optional-Capture-Tools.md"; target = "obsidian-demo/06-Optional-Capture-Tools.md" },
    @{ source = "obsidian-demo/07-Public-Web-Clip-Raw.md"; target = "obsidian-demo/07-Public-Web-Clip-Raw.md" },
    @{ source = "obsidian-demo/08-Web-Clip-Knowledge-Candidate.md"; target = "obsidian-demo/08-Web-Clip-Knowledge-Candidate.md" },
    @{ source = "obsidian-demo/Golden-Journey-Review.base"; target = "obsidian-demo/Golden-Journey-Review.base" },
    @{ source = "obsidian-demo/Agentic-AI-Knowledge-Growth.canvas"; target = "obsidian-demo/Agentic-AI-Knowledge-Growth.canvas" },
    @{ source = "fixed-query.txt"; target = "fixed-query.txt" },
    @{ source = "runs/2026-08-06/t0/claim-snapshot.md"; target = "runs/2026-08-06/t0/claim-snapshot.md" },
    @{ source = "runs/2026-08-06/t0/query-answer.md"; target = "runs/2026-08-06/t0/query-answer.md" },
    @{ source = "runs/2026-08-06/t1/query-answer.md"; target = "runs/2026-08-06/t1/query-answer.md" },
    @{ source = "runs/2026-08-06/query-diff.md"; target = "runs/2026-08-06/query-diff.md" },
    @{ source = "runs/2026-08-06/t1/review-queue.md"; target = "runs/2026-08-06/t1/review-queue.md" }
  )
  $files = @()
  foreach ($mapping in $mappings) {
    $sourcePath = Join-Path $demoRoot $mapping.source
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) { throw "missing demo source: $($mapping.source)" }
    $files += [ordered]@{ source = $mapping.source; target = $mapping.target; sha256 = Get-Hash $sourcePath }
  }
  $planCore = [ordered]@{
    schema = "boi-obsidian-golden-journey-plan/v1"
    vault = $resolvedVault
    public_case = "agentic-ai-change-radar"
    community_only = $true
    local_private_included = $false
    files = $files
  }
  $canonical = $planCore | ConvertTo-Json -Depth 8 -Compress
  $planCore.plan_hash = Get-TextHash $canonical
  return $planCore
}

function Get-ObsidianPath {
  $candidates = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Obsidian\Obsidian.exe"),
    (Join-Path $env:LOCALAPPDATA "Obsidian\Obsidian.exe")
  )
  return @($candidates | Where-Object { Test-Path -LiteralPath $_ -PathType Leaf } | Select-Object -First 1)
}

if ($Action -eq "Detect") {
  $obsidian = @(Get-ObsidianPath)
  [ordered]@{
    schema = "boi-obsidian-golden-journey-detect/v1"
    ok = $true
    obsidian_installed = $obsidian.Count -eq 1
    obsidian_path = if ($obsidian.Count -eq 1) { $obsidian[0] } else { "" }
    cli_available = [bool](Get-Command obsidian -ErrorAction SilentlyContinue)
    vault_exists = Test-Path -LiteralPath $resolvedVault -PathType Container
    windows_local_path = $true
    unc_path = $false
    personal_vault_touched = $false
  } | ConvertTo-Json -Depth 6
  exit 0
}

$plan = Get-Plan
if ($Action -eq "Preview") {
  $plan | ConvertTo-Json -Depth 8
  exit 0
}

if ($Action -eq "Apply") {
  if ($ConfirmPlanHash -cne $plan.plan_hash) { throw "Apply requires the exact current plan hash" }
  if (Test-Path -LiteralPath $resolvedVault) { throw "target demo Vault already exists; Verify or Recover it first" }
  New-Item -ItemType Directory -Path $resolvedVault -Force | Out-Null
  foreach ($file in $plan.files) {
    $sourcePath = Join-Path $demoRoot $file.source
    $targetPath = Join-Path $resolvedVault $file.target
    New-Item -ItemType Directory -Path (Split-Path -Parent $targetPath) -Force | Out-Null
    Copy-Item -LiteralPath $sourcePath -Destination $targetPath
  }
  $obsidianDir = Join-Path $resolvedVault ".obsidian"
  New-Item -ItemType Directory -Path $obsidianDir -Force | Out-Null
  [IO.File]::WriteAllText((Join-Path $obsidianDir "app.json"), "{`n  `"showUnsupportedFiles`": true`n}`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $obsidianDir "appearance.json"), "{`n  `"baseFontSize`": 19`n}`n", [Text.UTF8Encoding]::new($false))
  $receipt = [ordered]@{
    schema = "boi-obsidian-golden-journey-receipt/v1"
    plan_hash = $plan.plan_hash
    created_utc = [DateTime]::UtcNow.ToString("o")
    repo_root_hash = Get-TextHash $repoRoot
    files = $plan.files
    generated_files = @(
      @{ target = ".obsidian/app.json"; sha256 = Get-Hash (Join-Path $obsidianDir "app.json") },
      @{ target = ".obsidian/appearance.json"; sha256 = Get-Hash (Join-Path $obsidianDir "appearance.json") }
    )
    local_private_included = $false
  }
  [IO.File]::WriteAllText((Join-Path $resolvedVault $receiptName), ($receipt | ConvertTo-Json -Depth 8), [Text.UTF8Encoding]::new($false))
  Write-Host "Applied sanitized Community demo Vault: $resolvedVault"
  Write-Host "Plan hash: $($plan.plan_hash)"
  exit 0
}

$receiptPath = Join-Path $resolvedVault $receiptName
if (-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)) { throw "managed demo Vault receipt is missing" }
$receipt = Get-Content -LiteralPath $receiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$receipt.schema -cne "boi-obsidian-golden-journey-receipt/v1") { throw "invalid managed demo Vault receipt" }
if ([string]$receipt.repo_root_hash -cne (Get-TextHash $repoRoot)) { throw "managed demo Vault belongs to a different repository root" }

if ($Action -eq "Verify") {
  if ([string]$receipt.plan_hash -cne $plan.plan_hash) { throw "demo Vault plan hash is stale" }
  foreach ($file in $plan.files) {
    $targetPath = Join-Path $resolvedVault $file.target
    if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf) -or (Get-Hash $targetPath) -cne $file.sha256) {
      throw "demo Vault file mismatch: $($file.target)"
    }
  }
  foreach ($file in @($receipt.generated_files)) {
    $targetPath = Join-Path $resolvedVault ([string]$file.target)
    if (-not (Test-Path -LiteralPath $targetPath -PathType Leaf) -or (Get-Hash $targetPath) -cne [string]$file.sha256) {
      throw "generated demo Vault file mismatch: $($file.target)"
    }
  }
  [ordered]@{
    schema = "boi-obsidian-golden-journey-verify/v1"
    ok = $true
    plan_hash = $plan.plan_hash
    verified_file_count = @($plan.files).Count + @($receipt.generated_files).Count
    local_private_included = $false
    git_metadata_included = Test-Path -LiteralPath (Join-Path $resolvedVault ".git")
    windows_local_path = $true
    unc_path = $false
  } | ConvertTo-Json -Depth 5
  exit 0
}

if ($Action -eq "Recover") {
  $vaultFull = [IO.Path]::GetFullPath($resolvedVault).TrimEnd('\')
  $baseFull = [IO.Path]::GetFullPath($managedBase).TrimEnd('\')
  if (-not $vaultFull.StartsWith($baseFull + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "Recover only removes demo Vaults under the managed demo-vaults directory"
  }
  Remove-Item -LiteralPath $vaultFull -Recurse -Force
  Write-Host "Recovered by removing the managed demo Vault only: $vaultFull"
  exit 0
}
