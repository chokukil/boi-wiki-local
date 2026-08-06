param(
  [string]$Root = ""
)

$ErrorActionPreference = "Stop"
if ([string]::IsNullOrWhiteSpace($Root)) {
  $Root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\..\.."))
} else {
  $Root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
}
$CaseRoot = Join-Path $Root "cases\research\agentic-ai-change-radar"
$JourneyRoot = Join-Path $CaseRoot "golden-journey"
$RunRoot = Join-Path $JourneyRoot "runs\2026-08-06"
$script:Failures = [System.Collections.Generic.List[string]]::new()

function Fail([string]$Message) {
  $script:Failures.Add($Message)
  Write-Host "ERROR $Message"
}

function Read-Json([string]$Path) {
  if (!(Test-Path -LiteralPath $Path -PathType Leaf)) {
    Fail "missing JSON: $Path"
    return $null
  }
  try { return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
  catch { Fail "invalid JSON: $Path"; return $null }
}

function Is-Sha256([object]$Value) {
  return [string]$Value -cmatch '^[0-9a-f]{64}$'
}

function Resolve-Binding([string]$OwnerPath, [string]$RelativePath) {
  if ([System.IO.Path]::IsPathRooted($RelativePath)) {
    return [System.IO.Path]::GetFullPath($RelativePath)
  }
  return [System.IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $OwnerPath) $RelativePath))
}

function Test-Binding([string]$OwnerPath, [object]$Row, [string]$Context) {
  foreach ($field in @('path', 'sha256', 'bytes')) {
    if ($null -eq $Row.PSObject.Properties[$field]) { Fail "$Context missing $field"; return }
  }
  if (!(Is-Sha256 $Row.sha256)) { Fail "$Context invalid SHA256"; return }
  $bound = Resolve-Binding $OwnerPath ([string]$Row.path)
  if (!(Test-Path -LiteralPath $bound -PathType Leaf)) { Fail "$Context missing file: $($Row.path)"; return }
  $actualHash = (Get-FileHash -LiteralPath $bound -Algorithm SHA256).Hash.ToLowerInvariant()
  $actualBytes = (Get-Item -LiteralPath $bound).Length
  if ($actualHash -cne [string]$Row.sha256 -or $actualBytes -ne [long]$Row.bytes) {
    Fail "$Context hash or bytes drift: $($Row.path)"
  }
}

$hashPath = Join-Path $JourneyRoot "hashes.json"
$hashes = Read-Json $hashPath
if ($hashes) {
  if ($hashes.schema -cne 'boi-global-insight-golden-journey-hashes/v1' -or
      $hashes.case_id -cne 'agentic-ai-change-radar' -or
      $hashes.fixture_id -cne 'PUB-AAI-RADAR-002-v1' -or
      [long]$hashes.source_count -ne 14 -or [long]$hashes.t0_source_count -ne 3 -or
      [long]$hashes.t1_source_count -ne 11 -or $hashes.local_only -ne $true -or
      $hashes.remote_submitted -ne $false) {
    Fail "golden journey hash contract is invalid"
  }
  if (@($hashes.files).Count -ne 17) { Fail "golden journey must bind exactly 17 execution files" }
  foreach ($row in @($hashes.files)) { Test-Binding $hashPath $row "golden journey file" }
}

$fixturePath = Join-Path $CaseRoot "fixtures\manifest.json"
$fixture = Read-Json $fixturePath
$sourceManifestPath = Join-Path $RunRoot "source-manifest.json"
$sourceManifest = Read-Json $sourceManifestPath
if ($fixture -and $sourceManifest) {
  $fixtureHash = (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($fixture.fixture_id -cne 'PUB-AAI-RADAR-002-v1' -or [long]$fixture.source_count -ne 14) {
    Fail "fixture identity or source count is invalid"
  }
  if (@($sourceManifest.sources).Count -ne 14) { Fail "source manifest must contain 14 source records" }
  $t0 = @($sourceManifest.sources | Where-Object { $_.version -match 'T0 cutoff eligible|MCP 2025-03-26' })
  if ($t0.Count -ne 3) { Fail "T0 source partition must contain 3 records" }
  foreach ($row in @($sourceManifest.sources)) {
    Test-Binding $sourceManifestPath $row "source manifest row"
    if ($row.source_class -cne 'primary' -or $row.access_status -cne 'accessed' -or
        [string]::IsNullOrWhiteSpace([string]$row.verified_scope)) {
      Fail "source row is not accessed primary evidence with checked scope: $($row.source_ref)"
    }
  }
  $manifestProvenance = @($sourceManifest.generated_from)[0]
  if ([string]$manifestProvenance.sha256 -cne $fixtureHash) {
    Fail "source manifest is not bound to the fixture manifest"
  }
}

$requestPath = Join-Path $RunRoot "request-contract.json"
$request = Read-Json $requestPath
$queryPath = Join-Path $JourneyRoot "fixed-query.txt"
$queryHash = (Get-FileHash -LiteralPath $queryPath -Algorithm SHA256).Hash.ToLowerInvariant()
$queryBytes = (Get-Item -LiteralPath $queryPath).Length
if ($request) {
  if ($request.tool_id -cne 'deep-research' -or $request.execution_mode -cne 'single-agent' -or
      $request.local_only -ne $true -or $request.remote_submit -ne $false) {
    Fail "request contract routing or safety boundary is invalid"
  }
  if ([string]$request.fixed_query.sha256 -cne $queryHash -or [long]$request.fixed_query.bytes -ne $queryBytes) {
    Fail "request contract fixed Query drift"
  }
}

$t0SnapshotPath = Join-Path $RunRoot "t0\claim-snapshot.md"
$t0SnapshotHash = (Get-FileHash -LiteralPath $t0SnapshotPath -Algorithm SHA256).Hash.ToLowerInvariant()
$changePath = Join-Path $RunRoot "t1\change-set.json"
$change = Read-Json $changePath
if ($change) {
  if ([string]$change.previous_snapshot_sha256 -cne $t0SnapshotHash -or $change.empty_change_set -ne $false -or
      [long]$change.source_change_count -ne 11 -or $change.report_created -ne $false) {
    Fail "T1 change set baseline or no-report contract is invalid"
  }
  $expectedDelta = @('new', 'strengthened', 'revised', 'contradicted', 'stale', 'retirement-candidate', 'unknown')
  foreach ($kind in $expectedDelta) {
    if ($kind -notin @($change.deltas.delta_type)) { Fail "missing delta type: $kind" }
  }
  foreach ($delta in @($change.deltas)) {
    if ([string]$delta.previous.snapshot_sha256 -cne $t0SnapshotHash) {
      Fail "delta history is not bound to T0 snapshot: $($delta.claim_ref)/$($delta.delta_type)"
    }
    if ([string]::IsNullOrWhiteSpace([string]$delta.reason) -or
        [string]::IsNullOrWhiteSpace([string]$delta.next_review_at) -or
        @($delta.source_refs).Count -eq 0) {
      Fail "delta lacks reason, review date, or source: $($delta.claim_ref)/$($delta.delta_type)"
    }
  }
}

foreach ($relative in @('t0\query-answer.md', 't1\query-answer.md')) {
  $body = [System.IO.File]::ReadAllText((Join-Path $RunRoot $relative), [System.Text.Encoding]::UTF8)
  if (!$body.Contains($queryHash)) { Fail "$relative does not use the fixed Query hash" }
  foreach ($section in @('Answer', 'Evidence', 'Counterevidence', 'Unknowns', 'Next checks', 'Confidence')) {
    if (!$body.Contains("## $section")) { Fail "$relative missing section: $section" }
  }
}
$diffBody = [System.IO.File]::ReadAllText((Join-Path $RunRoot 'query-diff.md'), [System.Text.Encoding]::UTF8)
if (!$diffBody.Contains($queryHash) -or !$diffBody.Contains($t0SnapshotHash)) {
  Fail "same-Query diff is not bound to Query and T0 snapshot"
}

$reviewPath = Join-Path $RunRoot "review\reviewer-report.json"
$review = Read-Json $reviewPath
if ($review) {
  if ($review.decision -cne 'partial' -or $review.procedural_independence -ne $true -or
      $review.human_review_required -ne $true -or $review.semantic_changes_approved -ne $false -or
      $review.release_scope -cne 'community-local-authoring-evidence') {
    Fail "review decision overclaims independence or semantic approval"
  }
  if ([long]$review.remote_activity.mcp_writes -ne 0 -or [long]$review.remote_activity.remote_submits -ne 0 -or
      [long]$review.remote_activity.boi_remote_source_bytes -ne 0) {
    Fail "review report records unauthorized remote activity"
  }
  if (@($review.reviewed_source_sha256).Count -ne 14) { Fail "reviewer did not inspect all source hashes" }
  foreach ($row in @($review.reviewed_artifacts)) { Test-Binding $reviewPath $row "reviewed artifact" }
}

$handoffFields = @('artifact_kind', 'schema', 'case_id', 'run_id', 'phase', 'from_role', 'to_role', 'local_only', 'source_refs', 'generated_from', 'input_refs', 'output_files', 'supported_claims', 'counterevidence', 'unknowns', 'contradictions', 'blockers', 'review_questions', 'phase_exit', 'source_integrity')
$handoffs = Get-ChildItem -LiteralPath (Join-Path $RunRoot 'handoffs') -Filter '*.json' -File | Sort-Object Name
if ($handoffs.Count -ne 4) { Fail "expected four phase handoffs" }
foreach ($file in $handoffs) {
  $handoff = Read-Json $file.FullName
  if (!$handoff) { continue }
  foreach ($field in $handoffFields) {
    if ($null -eq $handoff.PSObject.Properties[$field]) { Fail "$($file.Name) missing canonical handoff field $field" }
  }
  if ($handoff.artifact_kind -cne 'handoff' -or $handoff.schema -cne 'boi-local-case-handoff/v1' -or
      $handoff.local_only -ne $true) { Fail "$($file.Name) handoff identity or scope is invalid" }
  foreach ($row in @($handoff.input_refs)) { Test-Binding $file.FullName $row "$($file.Name) input" }
  foreach ($row in @($handoff.output_files)) { Test-Binding $file.FullName $row "$($file.Name) output" }
  if ([string]$handoff.source_integrity.before_manifest_sha256 -cne [string]$handoff.source_integrity.after_manifest_sha256 -or
      @($handoff.source_integrity.changed_source_files).Count -ne 0) {
    Fail "$($file.Name) source integrity changed"
  }
}

$caseManifest = Read-Json (Join-Path $CaseRoot 'case.yaml')
if ($caseManifest -and ($caseManifest.status -cne 'community' -or $caseManifest.fixture_id -cne 'PUB-AAI-RADAR-002-v1')) {
  Fail "Case must remain Community and bind the executed fixture"
}

$privateId = '123' + '4567'
$privacyPattern = "(?i)$privateId|data[\\/]boi[\\/]private[\\/]|[A-Z]:[\\/]Users[\\/]|local_owner_ref|boi:private:|BOI_LOCAL_EMPLOYEE_ID|(?:^|[\\/])\.env(?:$|[\\/])"
$secretPattern = '(?i)github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}'
foreach ($file in Get-ChildItem -LiteralPath $JourneyRoot -Recurse -File) {
  if ($file.FullName -eq $PSCommandPath) { continue }
  $body = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
  if ($body -match $privacyPattern) { Fail "privacy identifier or Local path in Golden Journey: $($file.FullName)" }
  if ($body -match $secretPattern) { Fail "secret-like token in Golden Journey: $($file.FullName)" }
}

if ($script:Failures.Count -gt 0) {
  Write-Host "Agentic AI Golden Journey verification failed ($($script:Failures.Count) issue(s))"
  exit 1
}

Write-Host "Agentic AI Golden Journey verification passed"
Write-Host "INFO T0/T1 same-Query growth, 14 public sources, all delta types, handoffs, history, privacy and zero remote submit verified"
exit 0
