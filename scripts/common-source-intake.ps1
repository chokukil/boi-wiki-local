[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)]
  [string]$SourceFolder,
  [ValidateSet("auto-curate", "suggest", "explicit-only")]
  [string]$ConversationMode = "suggest",
  [switch]$ExplicitRequest,
  [string]$SourceKind = "",
  [string]$ProgressPath = ""
)

$ErrorActionPreference = "Stop"
$resolvedSource = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($SourceFolder)

function Write-Result([hashtable]$Payload) {
  $Payload | ConvertTo-Json -Depth 12
}

function Get-TextHash([string]$Text) {
  $bytes = [Text.UTF8Encoding]::new($false).GetBytes($Text)
  $algorithm = [Security.Cryptography.SHA256]::Create()
  try { return ([BitConverter]::ToString($algorithm.ComputeHash($bytes))).Replace("-", "").ToLowerInvariant() }
  finally { $algorithm.Dispose() }
}

if ($ConversationMode -eq "explicit-only" -and -not $ExplicitRequest) {
  Write-Result ([ordered]@{
    schema = "boi-local-common-source-inventory/v1"
    ok = $true
    status = "explicit-request-required"
    inspection_performed = $false
    conversation_mode = $ConversationMode
    no_change = $true
    unique_source_count = 0
    new_unique_count = 0
    items = @()
    remote_submitted = $false
  })
  exit 0
}

if (-not (Test-Path -LiteralPath $resolvedSource -PathType Container)) {
  throw "common source folder is missing: $resolvedSource"
}

function Get-DeclaredSourceKind([string]$Path) {
  if ([IO.Path]::GetExtension($Path).ToLowerInvariant() -ne ".md") { return "" }
  $lines = @(Get-Content -LiteralPath $Path -Encoding UTF8 -TotalCount 80)
  if ($lines.Count -eq 0 -or $lines[0].Trim() -ne "---") { return "" }
  for ($index = 1; $index -lt $lines.Count; $index++) {
    $line = [string]$lines[$index]
    if ($line.Trim() -eq "---") { break }
    if ($line -match '^\s*source_kind\s*:\s*["'']?([^"''#]+)') {
      return $Matches[1].Trim().ToLowerInvariant()
    }
  }
  return ""
}

function Get-SourceKind([string]$Path) {
  $declared = Get-DeclaredSourceKind $Path
  $declaredMap = @{
    "web-clip" = "web-clip"
    "email" = "email"
    "meeting-note" = "meeting-note"
    "tabular-data" = "tabular-data"
    "document" = "document"
    "markdown" = "document"
    "text" = "document"
    "image" = "image"
    "analysis-export" = "analysis-export"
  }
  if ($declared -and $declaredMap.ContainsKey($declared)) { return $declaredMap[$declared] }

  switch ([IO.Path]::GetExtension($Path).ToLowerInvariant()) {
    ".eml" { return "email" }
    ".msg" { return "email" }
    ".md" { return "document" }
    ".txt" { return "meeting-note" }
    ".csv" { return "tabular-data" }
    ".tsv" { return "tabular-data" }
    ".xlsx" { return "tabular-data" }
    ".pdf" { return "document" }
    ".docx" { return "document" }
    ".rtf" { return "document" }
    ".png" { return "image" }
    ".jpg" { return "image" }
    ".jpeg" { return "image" }
    ".webp" { return "image" }
    default { return "unsupported" }
  }
}

function Test-TemporarySource([IO.FileInfo]$File) {
  $extension = $File.Extension.ToLowerInvariant()
  return $File.Name.StartsWith("~$") -or $extension -in @(".tmp", ".part", ".crdownload", ".download")
}

function Get-RelativeSourcePath([string]$BasePath, [string]$FilePath) {
  $baseFull = [IO.Path]::GetFullPath($BasePath).TrimEnd('\') + '\'
  $fileFull = [IO.Path]::GetFullPath($FilePath)
  $baseUri = [Uri]::new($baseFull)
  $fileUri = [Uri]::new($fileFull)
  return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($fileUri).ToString()).Replace("\", "/")
}

$completed = @{}
$reflected = @{}
$progress = $null
if ($ProgressPath) {
  $resolvedProgress = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ProgressPath)
  if (Test-Path -LiteralPath $resolvedProgress -PathType Leaf) {
    $progress = Get-Content -LiteralPath $resolvedProgress -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($digest in @($progress.completed_sha256)) { $completed[[string]$digest.ToLowerInvariant()] = $true }
    foreach ($digest in @($progress.already_reflected_sha256)) { $reflected[[string]$digest.ToLowerInvariant()] = $true }
    $overlap = @($completed.Keys | Where-Object { $reflected.ContainsKey($_) })
    if ($overlap.Count -gt 0) { throw "completed_sha256 and already_reflected_sha256 overlap" }
  }
}

$groups = [ordered]@{}
$skippedTemporary = 0
foreach ($file in @(Get-ChildItem -LiteralPath $resolvedSource -Recurse -File | Sort-Object FullName)) {
  if (Test-TemporarySource $file) {
    $skippedTemporary += 1
    continue
  }
  $digest = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  $kind = Get-SourceKind $file.FullName
  $relative = Get-RelativeSourcePath $resolvedSource $file.FullName
  $observation = [ordered]@{
    path = $relative
    size = [int64]$file.Length
    modified_utc = $file.LastWriteTimeUtc.ToString("o")
    source_kind = $kind
    supported = $kind -ne "unsupported"
  }
  if (-not $groups.Contains($digest)) {
    $groups[$digest] = [ordered]@{
      sha256 = $digest
      source_kinds = @()
      observations = @()
      status = "new"
      review_required = $kind -eq "unsupported"
    }
  }
  $groups[$digest].observations += $observation
  $groups[$digest].source_kinds = @($groups[$digest].source_kinds + $kind | Sort-Object -Unique)
  if ($kind -eq "unsupported") { $groups[$digest].review_required = $true }
}

$allItems = @($groups.Values)
$sourceManifest = @($allItems | ForEach-Object {
  [ordered]@{
    sha256 = $_.sha256
    source_kinds = @($_.source_kinds)
    observations = @($_.observations | ForEach-Object {
      [ordered]@{
        path = $_.path
        size = $_.size
        modified_utc = $_.modified_utc
        source_kind = $_.source_kind
        supported = $_.supported
      }
    })
  }
})
$sourceManifestHash = Get-TextHash ($sourceManifest | ConvertTo-Json -Depth 10 -Compress)
$scope = [ordered]@{
  source_folder = [IO.Path]::GetFullPath($resolvedSource)
  requested_source_kind = $SourceKind.Trim().ToLowerInvariant()
  preserve_originals = $true
  remote_auto_upload = $false
}
$scopeHash = Get-TextHash ($scope | ConvertTo-Json -Depth 5 -Compress)
$resumeValid = $true
$resumeReason = ""
if ($null -ne $progress -and [string]$progress.source_manifest_hash) {
  if ([string]$progress.source_manifest_hash -cne $sourceManifestHash) {
    $resumeValid = $false
    $resumeReason = "source-manifest-changed"
  }
}
foreach ($item in $allItems) {
  if ($completed.ContainsKey($item.sha256)) { $item.status = "completed" }
  elseif ($reflected.ContainsKey($item.sha256)) { $item.status = "already-reflected" }
}

$selected = @($allItems)
if ($SourceKind.Trim()) {
  $requestedKind = $SourceKind.Trim().ToLowerInvariant()
  $selected = @($allItems | Where-Object { $_.source_kinds -contains $requestedKind })
}
$newItems = @($selected | Where-Object { $_.status -eq "new" })
$pendingOutsideFilter = if ($SourceKind.Trim()) {
  @($allItems | Where-Object { $_.sha256 -notin @($selected.sha256) -and $_.status -eq "new" }).Count
} else { 0 }

Write-Result ([ordered]@{
  schema = "boi-local-common-source-inventory/v1"
  ok = $true
  status = if (-not $resumeValid) { "preview-required" } elseif ($newItems.Count -eq 0) { "no-change" } elseif ($ConversationMode -eq "suggest" -and -not $ExplicitRequest) { "preview-required" } else { "ready-for-agent-processing" }
  inspection_performed = $true
  conversation_mode = $ConversationMode
  requested_source_kind = $SourceKind.Trim().ToLowerInvariant()
  no_change = $newItems.Count -eq 0
  observed_file_count = @($allItems | ForEach-Object { $_.observations } | ForEach-Object { $_ }).Count
  unique_source_count = $selected.Count
  new_unique_count = $newItems.Count
  pending_outside_filter = $pendingOutsideFilter
  skipped_temporary_count = $skippedTemporary
  source_manifest_hash = $sourceManifestHash
  source_scope_hash = $scopeHash
  resume_contract_checked = $null -ne $progress
  resume_contract_valid = $resumeValid
  resume_invalidation_reason = $resumeReason
  remaining_source_refs = if ($null -ne $progress) { @($progress.remaining_source_refs) } else { @() }
  next_batch = if ($null -ne $progress -and $null -ne $progress.next_batch) { $progress.next_batch } else { @{} }
  items = $selected
  writes_performed = $false
  source_bytes_changed = $false
  watcher_started = $false
  remote_submitted = $false
})
