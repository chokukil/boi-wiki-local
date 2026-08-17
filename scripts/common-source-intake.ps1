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
$resolvedProgress = ""
$checkpointOverlap = $false
if ($ProgressPath) {
  $resolvedProgress = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($ProgressPath)
  if (Test-Path -LiteralPath $resolvedProgress -PathType Leaf) {
    $progress = Get-Content -LiteralPath $resolvedProgress -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach ($digest in @($progress.completed_sha256)) { $completed[[string]$digest.ToLowerInvariant()] = $true }
    foreach ($digest in @($progress.already_reflected_sha256)) { $reflected[[string]$digest.ToLowerInvariant()] = $true }
    $overlap = @($completed.Keys | Where-Object { $reflected.ContainsKey($_) })
    $checkpointOverlap = $overlap.Count -gt 0
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
$currentManifestRows = @()
foreach ($item in $allItems) {
  foreach ($observation in @($item.observations)) {
    # This is the approved resume identity. Modification time and inferred kind
    # remain useful inventory observations, but are deliberately not approval inputs.
    $currentManifestRows += [ordered]@{
      bytes = [int64]$observation.size
      path = [string]$observation.path
      sha256 = [string]$item.sha256
    }
  }
}
$currentManifestRows = @($currentManifestRows | Sort-Object { [string]$_.path })
$sourceManifestHash = Get-TextHash (ConvertTo-Json -InputObject @($currentManifestRows) -Depth 5 -Compress)
$scope = [ordered]@{
  source_folder = [IO.Path]::GetFullPath($resolvedSource)
  requested_source_kind = $SourceKind.Trim().ToLowerInvariant()
  preserve_originals = $true
  remote_auto_upload = $false
}
$scopeHash = Get-TextHash ($scope | ConvertTo-Json -Depth 5 -Compress)
$resumeValid = $true
$resumeReason = ""

if ($null -ne $progress) {
  if ([string]$progress.schema -cne "boi-local-source-folder-progress/v1") {
    $resumeValid = $false
    $resumeReason = "progress-schema-invalid"
  } elseif ($checkpointOverlap) {
    $resumeValid = $false
    $resumeReason = "checkpoint-hash-overlap"
  }

  $plan = $null
  $planPath = Join-Path (Split-Path -Parent $resolvedProgress) "source-folder-plan.json"
  if ($resumeValid -and -not (Test-Path -LiteralPath $planPath -PathType Leaf)) {
    $resumeValid = $false
    $resumeReason = "approved-plan-missing"
  }
  if ($resumeValid) {
    $actualPlanHash = (Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if (-not [string]$progress.approved_plan_hash -or
        [string]$progress.approved_plan_hash.ToLowerInvariant() -cne $actualPlanHash) {
      $resumeValid = $false
      $resumeReason = "approved-plan-hash-mismatch"
    }
  }
  if ($resumeValid) {
    try {
      $plan = Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 | ConvertFrom-Json
    } catch {
      $resumeValid = $false
      $resumeReason = "approved-plan-invalid"
    }
  }
  if ($resumeValid -and (
      [string]$plan.schema -cne "boi-local-source-folder-plan/v1" -or
      [string]$plan.scope -cne "local-private" -or
      -not [bool]$plan.preserve_originals -or
      [bool]$plan.remote_auto_upload -or
      -not [bool]$plan.user_confirmed)) {
    $resumeValid = $false
    $resumeReason = "approved-plan-boundary-invalid"
  }
  if ($resumeValid -and [string]$plan.source_folder) {
    $plannedSource = [IO.Path]::GetFullPath([string]$plan.source_folder).TrimEnd('\')
    $currentSource = [IO.Path]::GetFullPath($resolvedSource).TrimEnd('\')
    if (-not $plannedSource.Equals($currentSource, [StringComparison]::OrdinalIgnoreCase)) {
      $resumeValid = $false
      $resumeReason = "source-folder-changed"
    }
  }

  $planManifestRows = @()
  if ($resumeValid) {
    foreach ($row in @($plan.source_manifest)) {
      $planManifestRows += [ordered]@{
        bytes = [int64]$row.bytes
        path = [string]$row.path
        sha256 = ([string]$row.sha256).ToLowerInvariant()
      }
    }
    $planManifestHash = Get-TextHash (ConvertTo-Json -InputObject @($planManifestRows) -Depth 5 -Compress)
    if (-not [string]$plan.source_manifest_hash -or
        [string]$plan.source_manifest_hash.ToLowerInvariant() -cne $planManifestHash -or
        -not [string]$progress.source_manifest_hash -or
        [string]$progress.source_manifest_hash.ToLowerInvariant() -cne $planManifestHash) {
      $resumeValid = $false
      $resumeReason = "approved-manifest-hash-mismatch"
    }
  }

  if ($resumeValid) {
    $currentByPath = @{}
    foreach ($row in $currentManifestRows) { $currentByPath[[string]$row.path] = $row }
    if ($planManifestRows.Count -ne $currentManifestRows.Count) {
      $resumeValid = $false
      $resumeReason = "source-manifest-changed"
    } else {
      foreach ($row in $planManifestRows) {
        $path = [string]$row.path
        if (-not $currentByPath.ContainsKey($path)) {
          $resumeValid = $false
          $resumeReason = "source-manifest-changed"
          break
        }
        $current = $currentByPath[$path]
        if ([int64]$current.bytes -ne [int64]$row.bytes -or
            [string]$current.sha256 -cne [string]$row.sha256) {
          $resumeValid = $false
          $resumeReason = "source-manifest-changed"
          break
        }
      }
    }
    if ($resumeValid) { $sourceManifestHash = $planManifestHash }
  }

  if ($resumeValid) {
    $remainingRefs = @()
    foreach ($ref in @($progress.remaining_source_refs)) {
      if ($null -ne $ref -and [string]$ref) { $remainingRefs += [string]$ref }
    }
    $nextRefs = @()
    foreach ($ref in @($progress.next_batch.source_refs)) {
      if ($null -ne $ref -and [string]$ref) { $nextRefs += [string]$ref }
    }
    if ($remainingRefs.Count -eq 0) {
      if ($nextRefs.Count -ne 0) {
        $resumeValid = $false
        $resumeReason = "next-batch-invalid"
      }
    } elseif ($nextRefs.Count -eq 0 -or $nextRefs.Count -gt $remainingRefs.Count) {
      $resumeValid = $false
      $resumeReason = "next-batch-invalid"
    } else {
      for ($index = 0; $index -lt $nextRefs.Count; $index++) {
        if ($nextRefs[$index] -cne $remainingRefs[$index]) {
          $resumeValid = $false
          $resumeReason = "next-batch-invalid"
          break
        }
      }
      if ($resumeValid) {
        $batchId = [string]$progress.next_batch.batch_id
        $plannedBatch = @($plan.ordered_batches | Where-Object { [string]$_.batch_id -ceq $batchId })
        if (-not $batchId -or $plannedBatch.Count -ne 1) {
          $resumeValid = $false
          $resumeReason = "next-batch-invalid"
        } else {
          $plannedRefs = @($plannedBatch[0].source_refs | ForEach-Object { [string]$_ })
          if ($plannedRefs.Count -ne $nextRefs.Count) {
            $resumeValid = $false
            $resumeReason = "next-batch-invalid"
          } else {
            for ($index = 0; $index -lt $nextRefs.Count; $index++) {
              if ($plannedRefs[$index] -cne $nextRefs[$index]) {
                $resumeValid = $false
                $resumeReason = "next-batch-invalid"
                break
              }
            }
          }
        }
      }
    }
  }

  if ($resumeValid -and [string]$progress.source_manifest_hash -cne $sourceManifestHash) {
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
$outputRemainingRefs = [object[]]@()
$outputNextBatch = [ordered]@{}
if ($null -ne $progress) {
  $outputRemainingRefs = [object[]]@(
    foreach ($ref in @($progress.remaining_source_refs)) {
      if ($null -ne $ref -and [string]$ref) { [string]$ref }
    }
  )
  if ($null -ne $progress.next_batch) { $outputNextBatch = $progress.next_batch }
}

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
  remaining_source_refs = $outputRemainingRefs
  next_batch = $outputNextBatch
  items = $selected
  writes_performed = $false
  source_bytes_changed = $false
  watcher_started = $false
  remote_submitted = $false
})
