param(
  [string]$Root = $PSScriptRoot,
  [switch]$NativeOnly
)

$Root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)

$EnvironmentId = ([string]$env:BOI_LOCAL_EMPLOYEE_ID).Trim()
$DotenvId = ""
$dotenv = Join-Path $Root ".env"
if (Test-Path -LiteralPath $dotenv) {
  $line = Get-Content -LiteralPath $dotenv -Encoding UTF8 | Where-Object { $_ -match '^\s*BOI_LOCAL_EMPLOYEE_ID\s*=' } | Select-Object -First 1
  if ($line) { $DotenvId = (($line -split '=', 2)[1]).Trim().Trim('"').Trim("'") }
}

foreach ($candidate in @($EnvironmentId, $DotenvId)) {
  if ($candidate -and $candidate -notmatch '^[0-9]{7}$') {
    Write-Host "ERROR BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID."
    exit 1
  }
}
if ($EnvironmentId -notin @("", "0000000") -and
    $DotenvId -notin @("", "0000000") -and
    $EnvironmentId -cne $DotenvId) {
  Write-Host "ERROR environment and .env select different Local Private profiles; choose one explicitly."
  exit 1
}

if ($EnvironmentId -and $EnvironmentId -ne "0000000") {
  $EmployeeId = $EnvironmentId
  $EmployeeSource = "environment"
} elseif ($DotenvId -and $DotenvId -ne "0000000") {
  $EmployeeId = $DotenvId
  $EmployeeSource = "dotenv"
} else {
  $privateRoot = Join-Path $Root "data/boi/private"
  $profiles = @()
  if (Test-Path -LiteralPath $privateRoot) {
    $profiles = @(Get-ChildItem -LiteralPath $privateRoot -Directory | Where-Object { $_.Name -match '^[0-9]{7}$' -and $_.Name -ne '0000000' })
  }
  if ($profiles.Count -gt 1) {
    Write-Host "ERROR multiple Local Private profiles found; set BOI_LOCAL_EMPLOYEE_ID explicitly."
    exit 1
  }
  if ($profiles.Count -eq 1) {
    $EmployeeId = $profiles[0].Name
    $EmployeeSource = "profile-directory"
  } else {
    $EmployeeId = "0000000"
    $EmployeeSource = if ($DotenvId) { "dotenv-template" } elseif ($EnvironmentId) { "environment-template" } else { "template-default" }
  }
}
$status = 0

if ($EmployeeId -notmatch '^[0-9]{7}$') {
  Write-Host "ERROR BOI_LOCAL_EMPLOYEE_ID must be a numeric 7-digit employee ID."
  $status = 1
}

$legacyId = "m" + "e"
if (Test-Path (Join-Path $Root "data/boi/private/$legacyId")) {
  Write-Host "ERROR legacy non-numeric private folder is not allowed."
  $status = 1
}

if ($status -ne 0) {
  exit $status
}

$baseRel = "data/boi/private/$EmployeeId"
$basePath = Join-Path $Root $baseRel
$scaffoldPath = Join-Path $Root "data/boi/private/0000000"
function Check-File($Path) {
  if (!(Test-Path (Join-Path $Root $Path))) {
    Write-Host "ERROR missing file: $Path"
    $script:status = 1
  }
}

function Check-Dir($Path) {
  if (!(Test-Path (Join-Path $Root $Path))) {
    Write-Host "ERROR missing directory: $Path"
    $script:status = 1
  }
}

function Check-CoreRuntimeIntegrity {
  $manifestPath = Join-Path $Root ".boi-harness\core-runtime-manifest.json"
  if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Write-Host "ERROR missing Core runtime manifest: .boi-harness/core-runtime-manifest.json"
    $script:status = 1
    return
  }
  try {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
  } catch {
    Write-Host "ERROR invalid Core runtime manifest"
    $script:status = 1
    return
  }
  $expectedCoreSkills = @("boi-harness-builder", "boi-second-brain", "boi-wiki-local")
  $manifestCoreSkills = @($manifest.skills.PSObject.Properties.Name | Sort-Object)
  if ([string]$manifest.schema -cne "boi-local-core-runtime-manifest/v1" -or
      ($manifestCoreSkills -join "`n") -cne (($expectedCoreSkills | Sort-Object) -join "`n")) {
    Write-Host "ERROR invalid Core runtime manifest schema or Skill list"
    $script:status = 1
    return
  }
  foreach ($relative in @("AGENTS.md", "CLAUDE.md")) {
    $path = Join-Path $Root $relative
    if ((Test-Path -LiteralPath $path -PathType Leaf) -and (Get-Item -LiteralPath $path).Length -eq 0) {
      Write-Host "ERROR empty Core runtime bootstrap: $relative"
      $script:status = 1
    }
  }
  foreach ($skillName in $expectedCoreSkills) {
    $codexRoot = Join-Path $Root ".agents\skills\$skillName"
    $claudeRoot = Join-Path $Root ".claude\skills\$skillName"
    if (!(Test-Path -LiteralPath $codexRoot -PathType Container) -or
        !(Test-Path -LiteralPath $claudeRoot -PathType Container)) {
      continue
    }
    $codexFiles = @(
      Get-ChildItem -LiteralPath $codexRoot -Recurse -File | ForEach-Object {
        $_.FullName.Substring($codexRoot.Length + 1).Replace('\', '/')
      }
    )
    $claudeFiles = @(
      Get-ChildItem -LiteralPath $claudeRoot -Recurse -File | ForEach-Object {
        $_.FullName.Substring($claudeRoot.Length + 1).Replace('\', '/')
      }
    )
    $requiredFiles = @($manifest.skills.$skillName | ForEach-Object { [string]$_ } | Sort-Object)
    $requiredFileList = $requiredFiles -join "`n"
    $codexFileList = @($codexFiles | Sort-Object) -join "`n"
    $claudeFileList = @($claudeFiles | Sort-Object) -join "`n"
    if ($codexFileList -cne $requiredFileList -or $claudeFileList -cne $requiredFileList) {
      Write-Host "ERROR Core runtime manifest and actual Skill file sets differ: $skillName"
      $script:status = 1
    }
    $relativeFiles = @(($codexFiles + $claudeFiles + $requiredFiles) | Sort-Object -Unique)
    foreach ($relative in $relativeFiles) {
      $codexFile = Join-Path $codexRoot $relative
      $claudeFile = Join-Path $claudeRoot $relative
      if (!(Test-Path -LiteralPath $codexFile -PathType Leaf) -or
          !(Test-Path -LiteralPath $claudeFile -PathType Leaf)) {
        Write-Host "ERROR Codex and Claude Core Skill file sets differ: $skillName/$relative"
        $script:status = 1
        continue
      }
      if ((Get-Item -LiteralPath $codexFile).Length -eq 0 -or
          (Get-Item -LiteralPath $claudeFile).Length -eq 0) {
        Write-Host "ERROR empty Core Skill file: $skillName/$relative"
        $script:status = 1
        continue
      }
      if ((Get-FileHash -LiteralPath $codexFile -Algorithm SHA256).Hash -cne
          (Get-FileHash -LiteralPath $claudeFile -Algorithm SHA256).Hash) {
        Write-Host "ERROR Codex and Claude Core Skill mirrors differ: $skillName/$relative"
        $script:status = 1
      }
    }
  }
}

Check-File "README.md"
Check-File "README_KO.md"
Check-File "AGENTS.md"
Check-File "CLAUDE.md"
Check-File ".agents/skills/boi-harness-builder/SKILL.md"
Check-File ".agents/skills/boi-second-brain/SKILL.md"
Check-File ".agents/skills/boi-wiki-local/SKILL.md"
Check-File ".claude/skills/boi-harness-builder/SKILL.md"
Check-File ".claude/skills/boi-second-brain/SKILL.md"
Check-File ".claude/skills/boi-wiki-local/SKILL.md"
Check-File ".boi-harness/core-runtime-manifest.json"
Check-CoreRuntimeIntegrity
Check-File "data/boi/index.md"
Check-File "data/boi/log.md"
Check-File "$baseRel/index.md"
Check-File "$baseRel/inbox.md"
Check-Dir "$baseRel/notes"
Check-Dir "$baseRel/sop-drafts"
Check-Dir "$baseRel/promotion-drafts"
Check-Dir "$baseRel/action-drafts"
Check-Dir "$baseRel/event-drafts"
Check-Dir "$baseRel/dictionary"
Check-Dir "$baseRel/diagrams"
Check-Dir "$baseRel/context-packs"
Check-Dir "$baseRel/workflow-simulations"
Check-Dir "$baseRel/langflow-plans"
Check-Dir "$baseRel/usage-examples"
Check-File ".agents/skills/boi-sop-flow-visualizer/SKILL.md"
Check-File ".agents/skills/boi-event-workflow-planner/SKILL.md"
Check-File ".agents/skills/boi-action-author/SKILL.md"
Check-File ".agents/skills/boi-dictionary-author/SKILL.md"
Check-File ".agents/skills/boi-context-pack-builder/SKILL.md"
Check-File ".agents/skills/boi-workflow-simulator/SKILL.md"
Check-File ".agents/skills/boi-langflow-connector-planner/SKILL.md"

# Native employee distribution: Harness, Skills, connected Wiki, and Windows entrypoints only.
Check-File "harness.lock"
Check-File ".boi-harness/package.json"
Check-File ".boi-harness/bootstrap/codex.json"
Check-File ".boi-harness/bootstrap/claude.json"
Check-File ".boi-harness/bootstrap/custom.json"
Check-File "install.cmd"
Check-File "install.ps1"
Check-File "setup.cmd"
Check-File "update.cmd"
Check-File "check.cmd"
Check-File "update.ps1"
Check-File "scripts/setup-native.ps1"
Check-File "repository-sources.json"
Check-File "scripts/select-repository-source.ps1"
Check-File "scripts/connect-boi-wiki-mcp.ps1"
Check-File "scripts/check-repository-source-contract.ps1"
Check-File "templates/mcp/boi-wiki-mcp-connection.json"
Check-File "templates/agent-memory-template.md"
Check-File "templates/source-knowledge-template.md"
Check-File "templates/source-record-template.md"
Check-File "templates/second-brain-preferences.example.json"
  Check-File "templates/global-insight/README.md"
  Check-File "templates/global-insight/runtime-contract.json"
  Check-File "templates/global-insight/artifact-contract.md"
Check-File "templates/global-insight/native-fast-gate.md"
Check-File "templates/global-insight/harness-card-template.md"
Check-File "scripts/global_insight_native_check.ps1"
Check-File "cases/catalog.json"
Check-File "cases/flagship/second-brain/CASE.md"
Check-File "templates/second-brain-guide/00-start-here.md"
Check-File "templates/second-brain-guide/02-build-your-harness.md"
Check-File "templates/second-brain-guide/12-ai-assisted-setup.md"
Check-File "templates/second-brain-guide/30-obsidian-install-and-vault.md"
Check-File "templates/second-brain-guide/50-mcp-and-promotion.md"
Check-File "templates/second-brain-guide/60-troubleshooting.md"
Check-File "templates/second-brain-guide/70-update-and-rollback.md"
Check-File "templates/second-brain-guide/41-quickadd.md"
Check-File "templates/second-brain-guide/42-omnisearch.md"

if (Test-Path -LiteralPath (Join-Path $Root "scripts/check-repository-source-contract.ps1")) {
  try {
    & (Join-Path $Root "scripts/check-repository-source-contract.ps1") -Root $Root | Out-Null
  } catch {
    Write-Host "ERROR repository source contract check failed: $($_.Exception.Message)"
    $status = 1
  }
}

$python = Get-Command python -ErrorAction SilentlyContinue

# Admin and CI only: these files are not part of the employee Native contract.
if (!$NativeOnly -and $python) {
  foreach ($adminFile in @(
    "CONTRIBUTING.md", "pilot-acceptance.cmd",
    "scripts/local_capture.py", "scripts/local_intake.py", "scripts/local_case.py", "scripts/local_review.py",
    "scripts/promotion_preflight.py", "scripts/boi_compatibility.py", "scripts/contribution_check.py",
    "scripts/boi_update.py", "scripts/ux_acceptance.py", "scripts/obsidian_plugin_check.py",
    "scripts/release_evidence.py", "scripts/pilot_acceptance.py", "scripts/release_clone_acceptance.py",
    "scripts/release_gate.py", "scripts/harness_sync.py", "scripts/boi_local_common.py", "scripts/boi_setup.py",
    "scripts/local_distill.py", "scripts/local_search.py", "scripts/local_lint.py", "scripts/local_wiki.py",
    "scripts/migrate_local_profile.py", "scripts/migration_audit.py", "scripts/wiki_check.py",
    "cases/_schema/case-harness.schema.json", "cases/_schema/handoff.schema.json",
    "scripts/case_harness_check.py", "scripts/meta_harness_check.py", "scripts/case_benchmark.py",
    "scripts/build_second_brain_fixture.py", "scripts/build_reference_case_fixtures.py",
    "scripts/build_reference_case_docs.py", "scripts/build_reference_case_evals.py",
    "scripts/build_case_runtime_cards.py", "cases/flagship/second-brain/evals/PROTOCOL.md",
    "cases/flagship/second-brain/evals/run-artifact.schema.json",
    "cases/flagship/second-brain/fixtures/sources/20-promotion-candidate.md"
  )) { Check-File $adminFile }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
  Write-Host "OK git is available"
} else {
  Write-Host "WARN git is not available; plain folder mode is OK"
}

if (Test-Path -LiteralPath (Join-Path $Root "scripts/global_insight_native_check.ps1")) {
  & (Join-Path $Root "scripts/global_insight_native_check.ps1") -Root $Root
  if ($LASTEXITCODE -ne 0) { $status = 1 }
}

if ($NativeOnly) {
  Write-Host "OK native structure check passed"
  Write-Host "INFO administrator CI and contract-oracle checks were not requested"
} elseif ($python) {
  $env:PYTHONUTF8 = "1"
  if (Test-Path (Join-Path $Root "harness.lock")) {
    & $python.Source (Join-Path $Root "scripts/harness_sync.py") verify --root $Root | Out-Null
    if ($LASTEXITCODE -ne 0) { $status = 1 }
  }
  & $python.Source (Join-Path $Root "scripts/local_capture.py") --root $Root --employee-id $EmployeeId --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/local_review.py") --root $Root --employee-id $EmployeeId --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/promotion_preflight.py") --root $Root --employee-id $EmployeeId --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/local_lint.py") --root $Root --employee-id $EmployeeId | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/local_wiki.py") --root $Root --employee-id $EmployeeId wiki-lint | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/wiki_check.py") --root $Root | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/contribution_check.py") --root $Root --all | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/obsidian_plugin_check.py") --root $Root | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/case_harness_check.py") --root $Root | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/meta_harness_check.py") --root $Root | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/build_second_brain_fixture.py") --root $Root --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/build_reference_case_fixtures.py") --root $Root --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/build_reference_case_docs.py") --root $Root --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/build_reference_case_evals.py") --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source (Join-Path $Root "scripts/build_case_runtime_cards.py") --check | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  & $python.Source -m unittest discover -s (Join-Path $Root "tests") -p "test_*.py" | Out-Null
  if ($LASTEXITCODE -ne 0) { $status = 1 }
  $compileTargets = @(
    "scripts/boi_local_common.py", "scripts/boi_setup.py", "scripts/build_guide_media.py", "scripts/local_capture.py", "scripts/local_intake.py", "scripts/local_case.py",
    "scripts/local_distill.py", "scripts/local_search.py", "scripts/local_review.py",
    "scripts/local_lint.py", "scripts/local_wiki.py", "scripts/query_quality.py", "scripts/promotion_preflight.py", "scripts/boi_compatibility.py", "scripts/contribution_check.py", "scripts/boi_update.py", "scripts/ux_acceptance.py", "scripts/obsidian_plugin_check.py", "scripts/release_evidence.py", "scripts/pilot_acceptance.py", "scripts/release_clone_acceptance.py", "scripts/release_gate.py",
    "scripts/migrate_local_profile.py", "scripts/migration_audit.py", "scripts/wiki_check.py", "scripts/case_harness_check.py", "scripts/meta_harness_check.py", "scripts/case_benchmark.py", "scripts/build_second_brain_fixture.py", "scripts/build_reference_case_fixtures.py", "scripts/build_reference_case_docs.py", "scripts/build_reference_case_evals.py", "scripts/build_case_runtime_cards.py"
  ) | ForEach-Object { Join-Path $Root $_ }
  & $python.Source -m py_compile $compileTargets
  if ($LASTEXITCODE -ne 0) { $status = 1 }
} else {
  Write-Host "OK native structure check passed"
  Write-Host "INFO Python is not required for employee use; optional CI and contract-oracle checks were not evaluated"
}

if ($status -eq 0) {
  Write-Host "BoI Wiki Local check passed"
}
exit $status
