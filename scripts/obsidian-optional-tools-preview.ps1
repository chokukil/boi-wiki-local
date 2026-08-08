[CmdletBinding()]
param(
  [ValidateSet("QuickAdd", "WebClipper")]
  [string]$Component,
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string]$VaultPath = "",
  [string]$CommonSourceFolder = "",
  [string]$Browser = "current-browser"
)

$ErrorActionPreference = "Stop"
$repoRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
$managedBase = Join-Path $env:LOCALAPPDATA "BoI\demo-vaults"
if (-not $VaultPath) { $VaultPath = Join-Path $managedBase "agentic-ai-change-radar-community" }
$resolvedVault = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($VaultPath)

function Get-TextHash([string]$Text) {
  $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
  $algorithm = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($algorithm.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant() }
  finally { $algorithm.Dispose() }
}

function Add-PlanHash([System.Collections.IDictionary]$Plan) {
  $canonical = $Plan | ConvertTo-Json -Depth 12 -Compress
  $Plan.plan_hash = Get-TextHash $canonical
  return $Plan
}

if ($Component -eq "QuickAdd") {
  $vaultFull = [IO.Path]::GetFullPath($resolvedVault).TrimEnd('\')
  $baseFull = [IO.Path]::GetFullPath($managedBase).TrimEnd('\')
  if (-not $vaultFull.StartsWith($baseFull + '\', [StringComparison]::OrdinalIgnoreCase)) {
    throw "QuickAdd preview is limited to a managed sanitized demo Vault"
  }
  $receiptPath = Join-Path $vaultFull ".boi-demo-vault.json"
  if (-not (Test-Path -LiteralPath $receiptPath -PathType Leaf)) {
    throw "managed sanitized demo Vault receipt is missing"
  }
  $receipt = Get-Content -LiteralPath $receiptPath -Raw -Encoding UTF8 | ConvertFrom-Json
  if ([string]$receipt.schema -cne "boi-obsidian-golden-journey-receipt/v1" -or $receipt.local_private_included) {
    throw "target is not a verified sanitized Community demo Vault"
  }
  $snapshotPath = Join-Path $repoRoot "research\obsidian-plugin-compatibility.json"
  $snapshot = Get-Content -LiteralPath $snapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
  $plugin = @($snapshot.plugins | Where-Object { $_.id -eq "quickadd" }) | Select-Object -First 1
  $candidate = @($plugin.candidates | Where-Object { $_.version -eq "2.21.0" }) | Select-Object -First 1
  if ($null -eq $candidate -or @($candidate.distribution_artifacts).Count -ne 3) {
    throw "pinned QuickAdd distribution artifacts are incomplete"
  }
  foreach ($artifact in @($candidate.distribution_artifacts)) {
    if ([string]$artifact.sha256 -notmatch '^[0-9a-f]{64}$' -or [int64]$artifact.bytes -le 0) {
      throw "invalid pinned QuickAdd distribution artifact"
    }
  }
  $plan = [ordered]@{
    schema = "boi-obsidian-optional-tool-preview/v1"
    component = "quickadd"
    target_vault = $vaultFull
    managed_sanitized_demo_vault = $true
    personal_vault = $false
    version = [string]$candidate.version
    minimum_obsidian_version = [string]$candidate.min_app_version
    distribution_artifacts = @($candidate.distribution_artifacts)
    changed_files_if_approved = @(
      ".obsidian/plugins/quickadd/main.js",
      ".obsidian/plugins/quickadd/manifest.json",
      ".obsidian/plugins/quickadd/styles.css",
      ".obsidian/community-plugins.json"
    )
    startup_macro_enabled = $false
    ai_provider_connected = $false
    external_api_connected = $false
    recovery = "Disable QuickAdd, remove its community-plugins entry, and remove only .obsidian/plugins/quickadd; preserve captured source files."
    approval_required = $true
    apply_supported = $false
    remote_submitted = $false
  }
  Add-PlanHash $plan | ConvertTo-Json -Depth 12
  exit 0
}

$templatePath = Join-Path $repoRoot "templates\obsidian\web-clipper\boi-common-source.json"
if (-not (Test-Path -LiteralPath $templatePath -PathType Leaf)) { throw "Web Clipper template is missing" }
$template = Get-Content -LiteralPath $templatePath -Raw -Encoding UTF8 | ConvertFrom-Json
if ([string]$template.path -ne "") { throw "Web Clipper template must not require a dedicated folder" }
$resolvedSource = if ($CommonSourceFolder) {
  $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CommonSourceFolder)
} else { "" }
$plan = [ordered]@{
  schema = "boi-web-clipper-install-preview/v1"
  component = "web-clipper"
  browser = $Browser
  extension_install = "manual-official-store"
  site_permissions = "user-reviewed-separate-approval"
  common_source_folder = $resolvedSource
  dedicated_folder_created = $false
  template = [ordered]@{
    file = "templates/obsidian/web-clipper/boi-common-source.json"
    sha256 = (Get-FileHash -LiteralPath $templatePath -Algorithm SHA256).Hash.ToLowerInvariant()
    source_kind = "web-clip"
  }
  interpreter_enabled = $false
  llm_prompt_variables = $false
  remote_endpoint_configured = $false
  changed_repository_files = @()
  recovery = "Remove the browser extension or imported template only; preserve Markdown raw sources in the common source folder."
  approval_required = $true
  apply_supported = $false
  remote_submitted = $false
}
Add-PlanHash $plan | ConvertTo-Json -Depth 10
