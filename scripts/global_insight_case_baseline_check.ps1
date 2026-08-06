param(
  [Parameter(Mandatory = $true)][string]$CaseRoot,
  [Parameter(Mandatory = $true)][string]$CaseId,
  [Parameter(Mandatory = $true)][string]$FixtureId,
  [Parameter(Mandatory = $true)][int]$SourceCount
)

$ErrorActionPreference = "Stop"
$ResolvedCaseRoot = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($CaseRoot)
$ValidationRoot = Join-Path $ResolvedCaseRoot "contract-validation"
$RunRoot = Join-Path $ValidationRoot "runs\2026-08-06"
$script:Failures = [System.Collections.Generic.List[string]]::new()

function Fail([string]$Message) {
  $script:Failures.Add($Message)
  Write-Host "ERROR $Message"
}

function Read-Json([string]$Path) {
  if (!(Test-Path -LiteralPath $Path -PathType Leaf)) { Fail "missing JSON: $Path"; return $null }
  try { return Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json }
  catch { Fail "invalid JSON: $Path"; return $null }
}

function Is-Sha256([object]$Value) {
  return [string]$Value -cmatch '^[0-9a-f]{64}$'
}

function Resolve-Binding([string]$OwnerPath, [string]$RelativePath) {
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

$fixturePath = Join-Path $ResolvedCaseRoot 'fixtures\manifest.json'
$fixture = Read-Json $fixturePath
$fixtureHash = (Get-FileHash -LiteralPath $fixturePath -Algorithm SHA256).Hash.ToLowerInvariant()
if ($fixture -and ($fixture.case_id -cne $CaseId -or $fixture.fixture_id -cne $FixtureId -or
    [long]$fixture.source_count -ne $SourceCount -or $fixture.fixture_policy -cne 'public-only')) {
  Fail 'fixture identity, count, or public-only policy is invalid'
}
foreach ($row in @($fixture.files)) { Test-Binding $fixturePath $row 'fixture source' }

$hashPath = Join-Path $ValidationRoot 'hashes.json'
$hashes = Read-Json $hashPath
if ($hashes) {
  if ($hashes.schema -cne 'boi-global-insight-case-validation-hashes/v1' -or
      $hashes.case_id -cne $CaseId -or $hashes.fixture_id -cne $FixtureId -or
      [long]$hashes.source_count -ne $SourceCount -or $hashes.local_only -ne $true -or
      $hashes.remote_submitted -ne $false) { Fail 'validation hash contract is invalid' }
  foreach ($row in @($hashes.files)) { Test-Binding $hashPath $row 'validation artifact' }
}

$manifestPath = Join-Path $RunRoot 'source-manifest.json'
$manifest = Read-Json $manifestPath
if ($manifest) {
  if ($manifest.artifact_kind -cne 'source-manifest' -or $manifest.case_id -cne $CaseId -or
      $manifest.local_only -ne $true -or @($manifest.sources).Count -ne $SourceCount) {
    Fail 'source manifest identity, scope, or count is invalid'
  }
  foreach ($row in @($manifest.sources)) {
    Test-Binding $manifestPath $row 'source manifest row'
    if ([string]::IsNullOrWhiteSpace([string]$row.verified_scope) -or $row.access_status -cne 'accessed') {
      Fail "source row lacks checked scope: $($row.source_ref)"
    }
  }
  if ([string]@($manifest.generated_from)[0].sha256 -cne $fixtureHash) {
    Fail 'source manifest is not bound to fixture manifest'
  }
}

$queryPath = Join-Path $ValidationRoot 'fixed-query.txt'
$queryHash = (Get-FileHash -LiteralPath $queryPath -Algorithm SHA256).Hash.ToLowerInvariant()
$queryAnswerPath = Join-Path $RunRoot 'query-answer.md'
$queryBody = [System.IO.File]::ReadAllText($queryAnswerPath, [System.Text.Encoding]::UTF8)
if (!$queryBody.Contains($queryHash)) { Fail 'Query answer is not bound to fixed Query bytes' }
foreach ($section in @('Answer', 'Evidence', 'Counterevidence', 'Unknowns', 'Next checks', 'Confidence')) {
  if (!$queryBody.Contains("## $section")) { Fail "Query answer missing section: $section" }
}

$evidencePath = Join-Path $RunRoot 'evidence.json'
$evidence = Read-Json $evidencePath
if ($evidence) {
  if ($evidence.artifact_kind -cne 'evidence' -or $evidence.case_id -cne $CaseId -or
      $evidence.local_only -ne $true -or @($evidence.claims).Count -lt 3) {
    Fail 'evidence identity, scope, or claim count is invalid'
  }
  foreach ($claim in @($evidence.claims)) {
    foreach ($field in @('claim_ref', 'claim', 'supporting_evidence', 'counterevidence', 'verification_level', 'uncertainty', 'access_limitation', 'unknown')) {
      if ($null -eq $claim.PSObject.Properties[$field]) { Fail "claim missing ${field}: $($claim.claim_ref)" }
    }
  }
}

$reviewPath = Join-Path $RunRoot 'reviewer-report.json'
$review = Read-Json $reviewPath
if ($review) {
  if ($review.decision -cne 'partial' -or $review.human_review_required -ne $true -or
      $review.semantic_changes_approved -ne $false -or $review.release_scope -cne 'community-local-contract-evidence' -or
      [long]$review.remote_activity.mcp_writes -ne 0 -or [long]$review.remote_activity.remote_submits -ne 0 -or
      [long]$review.remote_activity.boi_remote_source_bytes -ne 0) {
    Fail 'review report overclaims approval or records remote activity'
  }
}

$handoffPath = Join-Path $RunRoot 'handoff.json'
$handoff = Read-Json $handoffPath
$handoffFields = @('artifact_kind', 'schema', 'case_id', 'run_id', 'phase', 'from_role', 'to_role', 'local_only', 'source_refs', 'generated_from', 'input_refs', 'output_files', 'supported_claims', 'counterevidence', 'unknowns', 'contradictions', 'blockers', 'review_questions', 'phase_exit', 'source_integrity')
if ($handoff) {
  foreach ($field in $handoffFields) {
    if ($null -eq $handoff.PSObject.Properties[$field]) { Fail "handoff missing canonical field $field" }
  }
  foreach ($row in @($handoff.input_refs)) { Test-Binding $handoffPath $row 'handoff input' }
  foreach ($row in @($handoff.output_files)) { Test-Binding $handoffPath $row 'handoff output' }
  if ($handoff.local_only -ne $true -or
      [string]$handoff.source_integrity.before_manifest_sha256 -cne [string]$handoff.source_integrity.after_manifest_sha256 -or
      @($handoff.source_integrity.changed_source_files).Count -ne 0) { Fail 'handoff scope or source integrity is invalid' }
}

$caseManifest = Read-Json (Join-Path $ResolvedCaseRoot 'case.yaml')
if ($caseManifest -and ($caseManifest.status -cne 'community' -or $caseManifest.domain_validation -ne $false)) {
  Fail 'Case must remain Community without domain validation'
}

$privateId = '123' + '4567'
$privacyPattern = "(?i)$privateId|data[\\/]boi[\\/]private[\\/]|[A-Z]:[\\/]Users[\\/]|local_owner_ref|boi:private:|BOI_LOCAL_EMPLOYEE_ID|(?:^|[\\/])\.env(?:$|[\\/])"
$secretPattern = '(?i)github_pat_[A-Za-z0-9_]+|ghp_[A-Za-z0-9]+|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}'
foreach ($file in Get-ChildItem -LiteralPath $ValidationRoot -Recurse -File) {
  $body = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
  if ($body -match $privacyPattern) { Fail "privacy identifier or Local path in validation: $($file.FullName)" }
  if ($body -match $secretPattern) { Fail "secret-like token in validation: $($file.FullName)" }
}

if ($script:Failures.Count -gt 0) {
  Write-Host "$CaseId baseline contract verification failed ($($script:Failures.Count) issue(s))"
  exit 1
}

Write-Host "$CaseId baseline contract verification passed"
Write-Host "INFO $SourceCount public source records, fixed Query, evidence, review, handoff, privacy and zero remote submit verified"
exit 0
