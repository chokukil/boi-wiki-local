param(
  [string]$Root = (Split-Path -Parent $PSScriptRoot),
  [string[]]$ArtifactPath = @()
)

$ErrorActionPreference = "Stop"
$Root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)
$script:Failures = [System.Collections.Generic.List[string]]::new()

function Add-Failure([string]$Message) {
  $script:Failures.Add($Message)
  Write-Host "ERROR $Message"
}

function Require-File([string]$Relative) {
  $path = Join-Path $Root $Relative
  if (!(Test-Path -LiteralPath $path -PathType Leaf)) {
    Add-Failure "missing Global Insight contract file: $Relative"
    return $null
  }
  return $path
}

function Require-Literals([string]$Relative, [string[]]$Literals) {
  $path = Require-File $Relative
  if (!$path) { return }
  $body = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)
  foreach ($literal in $Literals) {
    if (!$body.Contains($literal)) {
      Add-Failure "$Relative is missing contract literal: $literal"
    }
  }
}

function Test-Placeholder([string]$Path, [string]$Body) {
  if ($Path.EndsWith("harness-card-template.md")) { return }
  if ($Body -match '\{\{[^}]+\}\}|<replace-me>|TODO|TBD') {
    Add-Failure "unresolved placeholder: $Path"
  }
}

function Test-Sha256([object]$Value) {
  return ([string]$Value -cmatch '^[0-9a-f]{64}$')
}

function Require-JsonFields([object]$Value, [string[]]$Fields, [string]$Context) {
  foreach ($field in $Fields) {
    $property = $Value.PSObject.Properties[$field]
    if ($null -eq $property -or $null -eq $property.Value) {
      Add-Failure "$Context missing required field: $field"
      continue
    }
    if ($property.Value -is [string] -and [string]::IsNullOrWhiteSpace([string]$property.Value)) {
      Add-Failure "$Context has empty required field: $field"
    }
  }
}

function Resolve-ArtifactReference([string]$ArtifactPath, [string]$Reference) {
  if ([System.IO.Path]::IsPathRooted($Reference)) {
    return [System.IO.Path]::GetFullPath($Reference)
  }
  $nearArtifact = [System.IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $ArtifactPath) $Reference))
  if (Test-Path -LiteralPath $nearArtifact) { return $nearArtifact }
  return [System.IO.Path]::GetFullPath((Join-Path $Root $Reference))
}

function Test-FileBinding([string]$ArtifactPath, [object]$Row, [string]$Context) {
  Require-JsonFields $Row @('path', 'sha256', 'bytes') $Context
  if (!(Test-Sha256 $Row.sha256)) {
    Add-Failure "$Context has invalid SHA256"
    return
  }
  $boundPath = Resolve-ArtifactReference $ArtifactPath ([string]$Row.path)
  if (!(Test-Path -LiteralPath $boundPath -PathType Leaf)) {
    Add-Failure "$Context bound file is missing: $($Row.path)"
    return
  }
  $actualHash = (Get-FileHash -LiteralPath $boundPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $actualBytes = (Get-Item -LiteralPath $boundPath).Length
  if ($actualHash -cne [string]$Row.sha256 -or $actualBytes -ne [long]$Row.bytes) {
    Add-Failure "$Context bound file hash or bytes drift: $($Row.path)"
  }
}

function Test-MarkdownArtifact([string]$Path) {
  $body = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
  Test-Placeholder $Path $body
  if ($body.Trim().Length -eq 0) {
    Add-Failure "empty artifact: $Path"
    return
  }
  if ($body.StartsWith("---")) {
    $end = $body.IndexOf("`n---", 3)
    if ($end -lt 0) {
      Add-Failure "unterminated frontmatter: $Path"
      return
    }
    $front = $body.Substring(0, $end)
    $content = $body.Substring($end + 4).Trim()
    foreach ($literal in @(
      'okf_version: "0.1"',
      'boi_profile_version: "0.1-local"',
      'type:',
      'title:',
      'description:',
      'visibility: local-private',
      'classification: internal',
      'owner:',
      'employee_id:',
      'local_owner_ref:',
      'local_only: true',
      'promotion_status: local_only',
      'retention_class:',
      'archive_status: active',
      'artifact_visibility:',
      'lifecycle_state:',
      'memory_candidate:',
      'cleanup_policy:',
      'review_after:',
      'contains_sensitive:',
      'source_refs:',
      'generated_from:'
    )) {
      if (!$front.Contains($literal)) {
        Add-Failure "Profile artifact missing $literal in $Path"
      }
    }
    if ($content.Length -lt 40) {
      Add-Failure "metadata-only wrapper or empty body: $Path"
    }
    $frontLines = $front -split "`r?`n"
    $insideGenerated = $false
    $generatedRef = ""
    $generatedCount = 0
    foreach ($line in $frontLines) {
      if ($line -match '^generated_from:\s*$') { $insideGenerated = $true; continue }
      if ($insideGenerated -and $line -match '^\S') { break }
      if (!$insideGenerated) { continue }
      if ($line -match '^\s+ref:\s*["'']?(.+?)["'']?\s*$') {
        $generatedRef = $Matches[1]
        continue
      }
      if ($line -match '^\s+sha256:\s*["'']?([0-9a-f]{64})["'']?\s*$') {
        $generatedHash = $Matches[1]
        $generatedCount += 1
        if ([string]::IsNullOrWhiteSpace($generatedRef)) {
          Add-Failure "generated_from SHA256 has no ref in $Path"
          continue
        }
        $generatedPath = Resolve-ArtifactReference $Path $generatedRef
        if (!(Test-Path -LiteralPath $generatedPath -PathType Leaf)) {
          Add-Failure "generated_from file is missing in $Path`: $generatedRef"
          continue
        }
        $actualGeneratedHash = (Get-FileHash -LiteralPath $generatedPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualGeneratedHash -cne $generatedHash) {
          Add-Failure "generated_from hash drift in $Path`: $generatedRef"
        }
        $generatedRef = ""
      }
    }
    if ($generatedCount -eq 0) { Add-Failure "Profile artifact has no hash-bound generated_from item: $Path" }
    $blockedType = $front -match '(?m)^type:\s*(boi/local-evidence|boi/local-capture|boi/local-hypothesis|boi/local-analysis-log|boi/local-analysis-case)\s*$'
    $promotable = $front -match '(?m)^promotion_status:\s*(?!local_only)'
    if ($blockedType -and $promotable) {
      Add-Failure "direct promotion is forbidden for this Local type: $Path"
    }
  }
}

function Test-JsonArtifact([string]$Path) {
  try {
    $value = Get-Content -LiteralPath $Path -Raw -Encoding UTF8 | ConvertFrom-Json
  } catch {
    Add-Failure "invalid JSON artifact: $Path"
    return
  }
  $body = [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
  Test-Placeholder $Path $body
  if ($value.local_only -eq $false -and $value.approved -ne $true) {
    Add-Failure "non-local artifact lacks explicit approval: $Path"
  }
  $kind = [string]$value.artifact_kind
  if ($kind -in @('source-manifest', 'evidence', 'claim-delta', 'handoff', 'failure', 'scoped-lint')) {
    if (!$value.source_refs -or !$value.generated_from) {
      Add-Failure "provenance is incomplete: $Path"
    }
  }
  if ($kind -eq 'source-manifest') {
    if (@($value.sources).Count -eq 0) {
      Add-Failure "source manifest has no sources: $Path"
    }
    foreach ($row in @($value.sources)) {
      Require-JsonFields $row @('source_ref', 'path', 'url', 'sha256', 'bytes', 'source_class', 'published_at', 'checked_at', 'version', 'access_status', 'verified_scope', 'runtime', 'source_refs', 'generated_from') "source manifest row in $Path"
      if ([string]$row.source_class -notin @('primary', 'secondary', 'community-signal')) {
        Add-Failure "source manifest row has invalid source_class: $Path"
      }
      Test-FileBinding $Path $row "source manifest row in $Path"
    }
  }
  if ($kind -eq 'evidence') {
    if (@($value.claims).Count -eq 0) { Add-Failure "evidence artifact has no claims: $Path" }
    foreach ($claim in @($value.claims)) {
      Require-JsonFields $claim @('claim_ref', 'claim', 'supporting_evidence', 'counterevidence', 'verification_level', 'uncertainty', 'access_limitation', 'unknown', 'source_sha256') "evidence claim in $Path"
      if (!(Test-Sha256 $claim.source_sha256)) { Add-Failure "evidence claim has invalid source SHA256: $Path" }
    }
  }
  if ($kind -eq 'claim-delta') {
    $allowed = @('new', 'strengthened', 'revised', 'contradicted', 'stale', 'retirement-candidate', 'unknown')
    if ($value.PSObject.Properties['delta_type'] -and [string]$value.delta_type -notin $allowed) {
      Add-Failure "invalid delta_type in $Path"
    }
    if ($value.PSObject.Properties['deltas']) {
      foreach ($delta in @($value.deltas)) {
        if ([string]$delta.delta_type -notin $allowed) { Add-Failure "invalid delta_type in delta list: $Path" }
      }
    }
    if ($value.empty_change_set -eq $true) {
      if ([long]$value.source_change_count -ne 0 -or @($value.deltas).Count -ne 0 -or
          $value.report_created -ne $false -or $value.new_claims_created -ne $false) {
        Add-Failure "empty change set created a report, claim, source change, or delta: $Path"
      }
    }
    if ($value.input_hash_changed -eq $true) {
      if ($value.approval_valid -ne $false -or @($value.invalidated_dependent_artifacts).Count -eq 0 -or
          [string]$value.resume_from -cne 'capture') {
        Add-Failure "hash change did not invalidate dependents and approval or restart from Capture: $Path"
      }
    }
  }
  if ($kind -eq 'handoff') {
    Require-JsonFields $value @('schema', 'case_id', 'run_id', 'phase', 'from_role', 'to_role', 'input_artifacts', 'output_artifacts', 'supported_claims', 'counterevidence', 'unknown', 'contradiction', 'blocker', 'review_questions', 'phase_exit') "handoff artifact $Path"
    if ([string]$value.schema -cne 'boi-local-case-handoff/v1') { Add-Failure "handoff schema is invalid: $Path" }
    foreach ($row in @($value.input_artifacts)) { Test-FileBinding $Path $row "handoff input in $Path" }
  }
  if ($kind -eq 'failure') {
    Require-JsonFields $value @('status', 'failure_phase', 'verified_artifacts', 'invalidated_dependent_artifacts', 'retry_count', 'resume_checkpoint', 'resume_condition', 'blocker') "failure artifact $Path"
    if ([string]$value.status -notin @('partial', 'blocked')) { Add-Failure "failure artifact status is invalid: $Path" }
    if ([long]$value.retry_count -lt 0 -or [long]$value.retry_count -gt 1) { Add-Failure "failure artifact exceeds the one-retry source policy: $Path" }
    Require-JsonFields $value.resume_checkpoint @('phase', 'input_sha256') "resume checkpoint in $Path"
    if (!(Test-Sha256 $value.resume_checkpoint.input_sha256)) { Add-Failure "resume checkpoint input hash is invalid: $Path" }
  }
  if ($kind -eq 'scoped-lint') {
    Require-JsonFields $value @('status', 'scope', 'findings', 'semantic_mutations') "scoped lint artifact $Path"
    Require-JsonFields $value.scope @('changed_documents', 'linked_topics', 'affected_claims', 'navigation', 'new_contradictions', 'stale_downstream') "scoped lint scope in $Path"
    if (@($value.semantic_mutations).Count -ne 0) { Add-Failure "scoped lint must not mutate semantic conclusions: $Path" }
  }
  if ($kind -eq 'promotion-preview') {
    Require-JsonFields $value @('candidate_path', 'candidate_sha256', 'candidate_bytes', 'reviewer', 'target_visibility', 'target_scope', 'source_refs', 'blockers', 'approved', 'submitted', 'remote_submit_allowed', 'approval_invalidated_when') "promotion preview $Path"
    if (!(Test-Sha256 $value.candidate_sha256)) { Add-Failure "promotion preview has invalid candidate SHA256: $Path" }
    if ([string]$value.target_visibility -notin @('team', 'public')) { Add-Failure "promotion preview has invalid target visibility: $Path" }
    if ($value.approved -ne $false -or $value.submitted -ne $false -or $value.remote_submit_allowed -ne $false) {
      Add-Failure "native promotion preview must remain unapproved and unsubmitted: $Path"
    }
    $requiredInvalidators = @('candidate', 'source', 'reviewer', 'target_scope', 'candidate_sha256')
    foreach ($item in $requiredInvalidators) {
      if ($item -notin @($value.approval_invalidated_when)) { Add-Failure "promotion preview is missing approval invalidator $item in $Path" }
    }
    if ($value.candidate_path) {
      $candidatePath = Resolve-ArtifactReference $Path ([string]$value.candidate_path)
      if (!(Test-Path -LiteralPath $candidatePath -PathType Leaf)) {
        Add-Failure "promotion candidate file is missing: $Path"
      } else {
        $candidateHash = (Get-FileHash -LiteralPath $candidatePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $candidateBytes = (Get-Item -LiteralPath $candidatePath).Length
        if ($candidateHash -cne [string]$value.candidate_sha256 -or $candidateBytes -ne [long]$value.candidate_bytes) {
          Add-Failure "promotion candidate hash or bytes drift: $Path"
        }
        $candidateBody = [System.IO.File]::ReadAllText($candidatePath, [System.Text.Encoding]::UTF8)
        if ($candidateBody -match '(?i)data/boi/private/|local_owner_ref|boi:private:|[A-Z]:[\\/](?:Users|Documents)[\\/]|BOI_LOCAL_EMPLOYEE_ID') {
          Add-Failure "promotion candidate contains a Local path or Profile identifier: $Path"
        }
      }
    }
  }
}

function Test-RuntimeContract {
  $path = Require-File "templates/global-insight/runtime-contract.json"
  if (!$path) { return }
  try { $contract = Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json }
  catch { Add-Failure "Global Insight runtime contract is invalid JSON"; return }
  if ([string]$contract.schema -cne 'boi-global-insight-runtime/v1') { Add-Failure "Global Insight runtime contract schema is invalid" }
  $expected = @(
    @('Capture', 'capture'), @('Update', 'update'), @('Query', 'query'),
    @('DeepResearch', 'deep-research'), @('Health', 'health'), @('Review', 'review'), @('Promote', 'promote')
  )
  if (@($contract.tools).Count -ne $expected.Count) { Add-Failure "Global Insight runtime contract must define exactly seven tools" }
  for ($index = 0; $index -lt $expected.Count; $index++) {
    $tool = @($contract.tools)[$index]
    if ([string]$tool.name -cne $expected[$index][0] -or [string]$tool.id -cne $expected[$index][1]) {
      Add-Failure "Global Insight tool routing mismatch at position $index"
    }
    if ($tool.remote_submit -ne $false) { Add-Failure "Global Insight tool may not submit remotely by default: $($tool.name)" }
  }
  $query = @($contract.tools | Where-Object { $_.id -eq 'query' })[0]
  $deep = @($contract.tools | Where-Object { $_.id -eq 'deep-research' })[0]
  $health = @($contract.tools | Where-Object { $_.id -eq 'health' })[0]
  $promote = @($contract.tools | Where-Object { $_.id -eq 'promote' })[0]
  if ($query.knowledge_scope -cne 'current-local-only' -or $query.auto_deep_research -ne $false) { Add-Failure "Query must remain Local-only and must not auto-start DeepResearch" }
  if ('explicit-user-request' -notin @($deep.start_policy) -or 'approved-query-scope' -notin @($deep.start_policy)) { Add-Failure "DeepResearch start policy is incomplete" }
  if ($health.semantic_mutation -ne $false) { Add-Failure "Health must not mutate semantic conclusions" }
  if ($promote.requires_exact_preview_approval -ne $true) { Add-Failure "Promote must require exact preview approval" }
  $expectedDelta = @('new', 'strengthened', 'revised', 'contradicted', 'stale', 'retirement-candidate', 'unknown')
  if ((@($contract.delta_types) -join "`n") -cne ($expectedDelta -join "`n")) { Add-Failure "Global Insight delta enum is invalid" }
  if ($contract.safety.remote_auto_upload -ne $false -or $contract.safety.promotion_requires_user_approval -ne $true) { Add-Failure "Global Insight runtime safety boundary is invalid" }
}

Require-Literals "templates/global-insight/README.md" @(
  '| Capture | `capture` |',
  '| Update | `update` |',
  '| Query | `query` |',
  '| DeepResearch | `deep-research` |',
  '| Health | `health` |',
  '| Review | `review` |',
  '| Promote | `promote` |',
  'retirement-candidate',
  'No-team fallback',
  'Python'
)
Require-Literals "templates/global-insight/artifact-contract.md" @(
  'primary | secondary | community-signal',
  'source_refs',
  'generated_from',
  'boi-local-case-handoff/v1',
  'change set',
  'exact candidate SHA256'
)
Require-File "templates/global-insight/native-fast-gate.md" | Out-Null
Require-File "templates/global-insight/harness-card-template.md" | Out-Null
Test-RuntimeContract

$contractArtifacts = @(
  'templates/global-insight/examples/source-manifest.json',
  'templates/global-insight/examples/evidence.json',
  'templates/global-insight/examples/empty-change-set.json',
  'templates/global-insight/examples/hash-invalidation.json',
  'templates/global-insight/examples/handoff.json',
  'templates/global-insight/examples/failure-resume.json',
  'templates/global-insight/examples/scoped-lint.json',
  'templates/global-insight/examples/promotion-preview.json'
)
foreach ($relative in $contractArtifacts) {
  $artifact = Require-File $relative
  if ($artifact) { Test-JsonArtifact $artifact }
}

$caseRoots = @(
  "cases/research/agentic-ai-change-radar",
  "cases/strategy/fab-logistics-digital-twin",
  "cases/strategy/scientific-foundation-model-knowledge"
)
foreach ($caseRoot in $caseRoots) {
  foreach ($relative in @(
    'CASE.md', 'case.yaml', 'orchestrator.md', 'roles/roles.md',
    'runtime/runtime.yaml', 'runtime/dispatch.md', 'prompts/evals.md',
    'references/method.md', 'fixtures/fixture.md', 'fixtures/manifest.json',
    'expected/OUTPUT-CONTRACT.md', 'expected/local-output.md', 'walkthrough/01-run.md',
    'evals/eval-plan.yaml', 'evals/assertions.json', 'evals/benchmark.json',
    'evals/BENCHMARK.md', 'evals/run-artifact.schema.json',
    'evals/prompts/prompt-catalog.json', 'evals/seeds/seed-catalog.json',
    'evals/runs/run-index.json', 'evals/blind-comparison/comparisons.json',
    'evals/failures/failures.json'
  )) {
    Require-File "$caseRoot/$relative" | Out-Null
  }
  $resolvedCaseRoot = Join-Path $Root $caseRoot
  $caseManifestPath = Join-Path $resolvedCaseRoot 'case.yaml'
  $runtimeManifestPath = Join-Path $resolvedCaseRoot 'runtime/runtime.yaml'
  $dispatchPath = Join-Path $resolvedCaseRoot 'runtime/dispatch.md'
  $benchmarkPath = Join-Path $resolvedCaseRoot 'evals/benchmark.json'
  if (Test-Path -LiteralPath $caseManifestPath -PathType Leaf) {
    try {
      $caseManifest = Get-Content -LiteralPath $caseManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
      $expectedCaseId = Split-Path -Leaf $resolvedCaseRoot
      if ($caseManifest.schema -cne 'boi-local-case-harness/v1' -or $caseManifest.case_id -cne $expectedCaseId) {
        Add-Failure "Global Insight Case manifest identity is invalid: $expectedCaseId"
      }
      if ($caseManifest.status -cne 'community' -or $caseManifest.fixture_policy -cne 'public-only') {
        Add-Failure "Global Insight Case must remain public-only Community: $expectedCaseId"
      }
      if (@($caseManifest.logical_roles).Count -lt 4 -or @($caseManifest.logical_roles).Count -gt 5 -or
          [string]$caseManifest.reviewer_role -notin @($caseManifest.logical_roles)) {
        Add-Failure "Global Insight Case role or reviewer contract is invalid: $expectedCaseId"
      }
      $expectedModes = @('full', 'reduced', 'single-agent', 'no-team-fallback')
      if ((@($caseManifest.scale_modes) -join "`n") -cne ($expectedModes -join "`n")) {
        Add-Failure "Global Insight Case scale modes are invalid: $expectedCaseId"
      }
      foreach ($role in @($caseManifest.logical_roles)) {
        Require-File "$caseRoot/roles/$role.md" | Out-Null
      }
    } catch {
      Add-Failure "Global Insight Case manifest is not valid JSON: $caseRoot"
    }
  }
  if (Test-Path -LiteralPath $runtimeManifestPath -PathType Leaf) {
    try {
      $runtimeManifest = Get-Content -LiteralPath $runtimeManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
      if ($runtimeManifest.schema -cne 'boi-local-case-runtime/v1' -or
          $runtimeManifest.case_id -cne (Split-Path -Leaf $resolvedCaseRoot) -or
          $runtimeManifest.remote_mutation_default -ne $false) {
        Add-Failure "Global Insight runtime manifest is invalid: $caseRoot"
      }
      if (@($runtimeManifest.role_cards | Where-Object { $_.independent_reviewer -eq $true }).Count -ne 1) {
        Add-Failure "Global Insight runtime must have exactly one independent reviewer: $caseRoot"
      }
    } catch {
      Add-Failure "Global Insight runtime manifest is not valid JSON: $caseRoot"
    }
  }
  if (Test-Path -LiteralPath $dispatchPath -PathType Leaf) {
    $dispatchBody = [System.IO.File]::ReadAllText($dispatchPath, [System.Text.Encoding]::UTF8)
    foreach ($literal in @('Codex', 'Claude', 'Single-agent', 'No-team')) {
      if (!$dispatchBody.Contains($literal)) { Add-Failure "Global Insight runtime dispatch is missing $literal`: $caseRoot" }
    }
  }
  if (Test-Path -LiteralPath $benchmarkPath -PathType Leaf) {
    try {
      $benchmark = Get-Content -LiteralPath $benchmarkPath -Raw -Encoding UTF8 | ConvertFrom-Json
      if ([long]$benchmark.completed_executions -ne 0 -or $benchmark.production_quality_gate_passed -ne $false -or
          $benchmark.reference_eligible -ne $false -or $benchmark.codex_validated -ne $false -or
          $benchmark.claude_validated -ne $false -or $benchmark.actual_boi_validator -ne $false) {
        Add-Failure "Global Insight Community benchmark contains unsupported status evidence: $caseRoot"
      }
    } catch {
      Add-Failure "Global Insight benchmark is not valid JSON: $caseRoot"
    }
  }
  $expectedLocalOutput = Join-Path $resolvedCaseRoot 'expected/local-output.md'
  if (Test-Path -LiteralPath $expectedLocalOutput -PathType Leaf) { Test-MarkdownArtifact $expectedLocalOutput }
  $manifestPath = Join-Path $resolvedCaseRoot "fixtures/manifest.json"
  if (Test-Path -LiteralPath $manifestPath -PathType Leaf) {
    try {
      $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
      $expectedCaseId = Split-Path -Leaf $resolvedCaseRoot
      if ($manifest.schema -cne 'boi-local-case-fixture-manifest/v2' -or $manifest.case_id -cne $expectedCaseId) {
        Add-Failure "Global Insight fixture manifest identity is invalid: $expectedCaseId"
      }
      if ($manifest.fixture_policy -cne 'public-only' -or $manifest.synthetic -ne $false) {
        Add-Failure "Global Insight fixture must be deterministic public-only: $expectedCaseId"
      }
      if ($manifest.source_count -ne @($manifest.files).Count -or $manifest.source_count -lt 5) {
        Add-Failure "Global Insight source_count is invalid: $expectedCaseId"
      }
      foreach ($row in @($manifest.files)) {
        $sourcePath = Join-Path (Join-Path $resolvedCaseRoot 'fixtures') ([string]$row.path)
        if (!(Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
          Add-Failure "missing Global Insight source: $expectedCaseId/$($row.path)"
          continue
        }
        $hash = (Get-FileHash -LiteralPath $sourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
        $bytes = (Get-Item -LiteralPath $sourcePath).Length
        if ($hash -cne [string]$row.sha256 -or $bytes -ne [long]$row.bytes) {
          Add-Failure "Global Insight source hash or bytes drift: $expectedCaseId/$($row.path)"
        }
      }
    } catch {
      Add-Failure "Global Insight fixture manifest is not valid JSON: $caseRoot"
    }
  }
}

foreach ($requested in $ArtifactPath) {
  $path = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($requested)
  if (!(Test-Path -LiteralPath $path -PathType Leaf)) {
    Add-Failure "artifact does not exist: $requested"
    continue
  }
  switch ([System.IO.Path]::GetExtension($path).ToLowerInvariant()) {
    '.md' { Test-MarkdownArtifact $path }
    '.json' { Test-JsonArtifact $path }
    default { Add-Failure "unsupported fast-gate artifact format: $path" }
  }
}

if ($script:Failures.Count -gt 0) {
  Write-Host "Global Insight native check failed ($($script:Failures.Count) issue(s))"
  exit 1
}

Write-Host "Global Insight native check passed"
Write-Host "INFO semantic conclusions were not modified; Review remains human-controlled"
exit 0
