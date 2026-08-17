[CmdletBinding()]
param([string]$Root = $PSScriptRoot)

$ErrorActionPreference = "Stop"
$repoRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
if ((Split-Path -Leaf $repoRoot) -eq "scripts") { $repoRoot = Split-Path -Parent $repoRoot }
$tool = Join-Path $repoRoot "scripts\common-source-intake.ps1"
$tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("boi-common-intake-" + [guid]::NewGuid().ToString("N"))
$source = Join-Path $tempRoot "common-source"

try {
  New-Item -ItemType Directory -Path $source -Force | Out-Null
  $clip = Join-Path $source "clip.md"
  $duplicate = Join-Path $source "same-bytes.txt"
  $csv = Join-Path $source "table.csv"
  $body = "---`nsource_kind: web-clip`nsource_url: https://example.com/source`ncaptured_at: 2026-08-07T00:00:00Z`n---`n`nPublic fixture.`n"
  [IO.File]::WriteAllText($clip, $body, [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllBytes($duplicate, [IO.File]::ReadAllBytes($clip))
  [IO.File]::WriteAllText($csv, "claim,status`nA,new`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $source "note.md"), "# Ordinary Markdown`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $source "meeting.txt"), "Meeting note`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllText((Join-Path $source "message.eml"), "From: source@example.com`r`nSubject: Public fixture`r`n`r`nBody`r`n", [Text.UTF8Encoding]::new($false))
  [IO.File]::WriteAllBytes((Join-Path $source "document.pdf"), [Text.UTF8Encoding]::new($false).GetBytes("%PDF-1.4 public fixture"))
  [IO.File]::WriteAllBytes((Join-Path $source "image.png"), [byte[]](1,2,3,4))
  [IO.File]::WriteAllBytes((Join-Path $source "photo.jpg"), [byte[]](5,6,7,8))
  [IO.File]::WriteAllBytes((Join-Path $source "diagram.webp"), [byte[]](9,10,11,12))
  [IO.File]::WriteAllBytes((Join-Path $source "document.docx"), [byte[]](13,14,15,16))
  [IO.File]::WriteAllBytes((Join-Path $source "unsupported.bin"), [byte[]](17,18,19,20))
  [IO.File]::WriteAllBytes((Join-Path $source "incomplete.part"), [byte[]](21,22))
  $before = (Get-FileHash -LiteralPath $clip -Algorithm SHA256).Hash.ToLowerInvariant()

  $inventory = & $tool -SourceFolder $source -ConversationMode auto-curate -ExplicitRequest | ConvertFrom-Json
  if (-not $inventory.inspection_performed -or $inventory.unique_source_count -ne 11 -or $inventory.new_unique_count -ne 11) {
    throw "common inventory did not deduplicate identical bytes"
  }
  $kinds = @($inventory.items | ForEach-Object { $_.source_kinds } | Sort-Object -Unique)
  foreach ($requiredKind in @("web-clip", "document", "meeting-note", "email", "tabular-data", "image", "unsupported")) {
    if ($kinds -notcontains $requiredKind) { throw "missing source kind: $requiredKind" }
  }
  $unsupported = @($inventory.items | Where-Object { $_.source_kinds -contains "unsupported" })
  if ($unsupported.Count -ne 1 -or -not $unsupported[0].review_required) {
    throw "unsupported input was not held for content review"
  }
  if ($inventory.skipped_temporary_count -ne 1) { throw "incomplete download was not skipped" }
  $duplicateGroup = @($inventory.items | Where-Object { $_.sha256 -eq $before })
  if ($duplicateGroup.Count -ne 1 -or @($duplicateGroup[0].observations).Count -ne 2 -or $duplicateGroup[0].source_kinds -notcontains "web-clip") {
    throw "web-clip provenance or cross-type observations were not retained"
  }

  $filtered = & $tool -SourceFolder $source -ConversationMode auto-curate -ExplicitRequest -SourceKind web-clip | ConvertFrom-Json
  if ($filtered.unique_source_count -ne 1 -or $filtered.new_unique_count -ne 1 -or $filtered.pending_outside_filter -ne 10) {
    throw "web-clip-only scope did not preserve other new sources as pending"
  }

  $explicitOnly = & $tool -SourceFolder $source -ConversationMode explicit-only | ConvertFrom-Json
  if ($explicitOnly.inspection_performed -or $explicitOnly.status -ne "explicit-request-required") {
    throw "explicit-only mode inspected the common source folder without a request"
  }

  $manifestRows = @()
  foreach ($item in @($inventory.items)) {
    foreach ($observation in @($item.observations)) {
      $manifestRows += [ordered]@{
        bytes = [int64]$observation.size
        path = [string]$observation.path
        sha256 = [string]$item.sha256
      }
    }
  }
  $manifestRows = @($manifestRows | Sort-Object { [string]$_.path })
  $planPath = Join-Path $tempRoot "source-folder-plan.json"
  $plan = [ordered]@{
    schema = "boi-local-source-folder-plan/v1"
    employee_id = "0000000"
    scope = "local-private"
    preserve_originals = $true
    remote_auto_upload = $false
    user_confirmed = $true
    source_folder = [IO.Path]::GetFullPath($source)
    source_manifest_hash = [string]$inventory.source_manifest_hash
    source_manifest = @($manifestRows)
    ordered_batches = @(
      [ordered]@{ batch_id = "batch-01"; source_refs = @("clip.md", "same-bytes.txt") },
      [ordered]@{ batch_id = "batch-02"; source_refs = @("table.csv") }
    )
  }
  [IO.File]::WriteAllText(
    $planPath,
    ($plan | ConvertTo-Json -Depth 8),
    [Text.UTF8Encoding]::new($false)
  )
  $approvedPlanHash = (Get-FileHash -LiteralPath $planPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $progressPath = Join-Path $tempRoot "source-folder-progress.json"
  [IO.File]::WriteAllText(
    $progressPath,
    (@{
      schema = "boi-local-source-folder-progress/v1"
      approved_plan_hash = $approvedPlanHash
      source_manifest_hash = [string]$inventory.source_manifest_hash
      completed_sha256 = @($before)
      already_reflected_sha256 = @()
      remaining_source_refs = @("table.csv")
      next_batch = @{ batch_id = "batch-02"; source_refs = @("table.csv") }
      status = "in_progress"
    } | ConvertTo-Json -Depth 5),
    [Text.UTF8Encoding]::new($false)
  )
  $noChange = & $tool -SourceFolder $source -ConversationMode auto-curate -ExplicitRequest -SourceKind web-clip -ProgressPath $progressPath | ConvertFrom-Json
  if (-not $noChange.no_change -or $noChange.status -ne "no-change" -or $noChange.writes_performed) {
    throw "existing hash did not produce a read-only no-change result"
  }
  if (-not $noChange.resume_contract_checked -or -not $noChange.resume_contract_valid -or
      $noChange.next_batch.batch_id -ne "batch-02") {
    throw "unchanged progress did not resume from the saved checkpoint"
  }
  $after = (Get-FileHash -LiteralPath $clip -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($before -ne $after) { throw "source bytes changed during inventory" }

  [IO.File]::WriteAllText((Join-Path $source "document.pdf"), "%PDF-1.4 changed public fixture", [Text.UTF8Encoding]::new($false))
  $invalidated = & $tool -SourceFolder $source -ConversationMode auto-curate -ExplicitRequest -ProgressPath $progressPath | ConvertFrom-Json
  if ($invalidated.resume_contract_valid -or $invalidated.status -ne "preview-required" -or
      $invalidated.resume_invalidation_reason -ne "source-manifest-changed") {
    throw "changed source did not invalidate the saved checkpoint before writes"
  }

  Write-Host "OK common Raw Source Intake native check passed"
  exit 0
} catch {
  Write-Host "ERROR common Raw Source Intake native check failed: $($_.Exception.Message)"
  exit 1
} finally {
  if (Test-Path -LiteralPath $tempRoot -PathType Container) {
    $resolvedTemp = [IO.Path]::GetFullPath($tempRoot).TrimEnd('\')
    $allowedTemp = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
    if (-not $resolvedTemp.StartsWith($allowedTemp + '\', [StringComparison]::OrdinalIgnoreCase)) {
      throw "refusing to remove a non-temporary intake check directory"
    }
    [IO.Directory]::Delete($resolvedTemp, $true)
  }
}
