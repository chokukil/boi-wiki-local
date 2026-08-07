param(
  [string]$Root = $PSScriptRoot,
  [switch]$Apply,
  [string]$ConfirmGuideRelease = "",
  [string]$ConfirmSourcePlanHash = ""
)

$ErrorActionPreference = "Stop"
$Root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)

function Fail([string]$Message) {
  Write-Error $Message
  exit 1
}

function Safe-Remote([string]$Value) {
  if ($Value -match '^[A-Za-z][A-Za-z0-9+.-]*://') {
    try {
      $uri = [Uri]$Value
      $authority = $uri.Host
      if (!$uri.IsDefaultPort) { $authority = "$authority`:$($uri.Port)" }
      if ($uri.Scheme -eq 'ssh' -and $uri.UserInfo -eq 'git') { $authority = "git@$authority" }
      return "$($uri.Scheme)://$authority$($uri.PathAndQuery)"
    } catch { return "<configured origin>" }
  }
  return $Value
}

function Resolve-LocalProfile([string]$RepoRoot) {
  $environmentId = ([string]$env:BOI_LOCAL_EMPLOYEE_ID).Trim()
  $dotenvId = ""
  $dotenv = Join-Path $RepoRoot ".env"
  if (Test-Path -LiteralPath $dotenv) {
    $line = Get-Content -LiteralPath $dotenv -Encoding UTF8 | Where-Object { $_ -match '^\s*BOI_LOCAL_EMPLOYEE_ID\s*=' } | Select-Object -First 1
    if ($line) { $dotenvId = (($line -split '=', 2)[1]).Trim().Trim('"').Trim("'") }
  }

  foreach ($candidate in @($environmentId, $dotenvId)) {
    if ($candidate -and $candidate -notmatch '^[0-9]{7}$') {
      Fail "BOI_LOCAL_EMPLOYEE_ID는 숫자 7자리여야 합니다."
    }
  }
  if ($environmentId -notin @("", "0000000") -and
      $dotenvId -notin @("", "0000000") -and
      $environmentId -cne $dotenvId) {
    Fail "환경 변수와 .env가 서로 다른 Local Private Profile을 가리킵니다. 하나를 명시적으로 선택하세요."
  }

  if ($environmentId -and $environmentId -ne "0000000") {
    $employeeId = $environmentId
    $source = "environment"
  } elseif ($dotenvId -and $dotenvId -ne "0000000") {
    $employeeId = $dotenvId
    $source = "dotenv"
  } else {
    $employeeId = ""
    $source = ""
    $privateRoot = Join-Path $RepoRoot "data\boi\private"
    $profiles = @()
    if (Test-Path -LiteralPath $privateRoot) {
      $profiles = @(Get-ChildItem -LiteralPath $privateRoot -Directory | Where-Object { $_.Name -match '^[0-9]{7}$' -and $_.Name -ne '0000000' })
    }
    if ($profiles.Count -gt 1) { Fail "여러 Local Private Profile이 있습니다. BOI_LOCAL_EMPLOYEE_ID를 명시하세요." }
    if ($profiles.Count -eq 1) {
      $employeeId = $profiles[0].Name
      $source = "profile-directory"
    } else {
      $employeeId = "0000000"
      $source = if ($dotenvId) { "dotenv-template" } elseif ($environmentId) { "environment-template" } else { "template-default" }
    }
  }
  return @{ Id = $employeeId; Source = $source }
}

function Private-Manifest([string]$RepoRoot, [string]$EmployeeId) {
  $private = Join-Path $RepoRoot "data\boi\private\$EmployeeId"
  $manifest = @{}
  if (!(Test-Path -LiteralPath $private)) { return $manifest }
  Get-ChildItem -LiteralPath $private -Recurse -File | ForEach-Object {
    $relative = $_.FullName.Substring($private.Length).TrimStart('\', '/').Replace('\', '/')
    if ($relative -like 'notes/guide/*' -or $relative -like '_archive/guides/*') { return }
    $manifest[$relative] = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
  }
  return $manifest
}

function Assert-SameManifest($Before, $After) {
  $beforeRows = @($Before.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" })
  $afterRows = @($After.GetEnumerator() | Sort-Object Name | ForEach-Object { "$($_.Name)=$($_.Value)" })
  if (($beforeRows -join "`n") -cne ($afterRows -join "`n")) {
    Fail "업데이트 중 Local Private 문서가 변경되었습니다. 재시도하지 말고 백업과 비교하세요."
  }
}

function Verify-HarnessSnapshot([string]$RepoRoot) {
  $lockPath = Join-Path $RepoRoot "harness.lock"
  $packagePath = Join-Path $RepoRoot ".boi-harness\package.json"
  if (!(Test-Path -LiteralPath $lockPath -PathType Leaf) -or !(Test-Path -LiteralPath $packagePath -PathType Leaf)) {
    Fail "고정 Harness lock 또는 offline snapshot이 없습니다."
  }
  try {
    $lock = Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $package = Get-Content -LiteralPath $packagePath -Raw -Encoding UTF8 | ConvertFrom-Json
  } catch {
    Fail "고정 Harness lock 또는 offline snapshot을 읽을 수 없습니다."
  }
  if ([string]$lock.schema -cne "boi-harness-lock/v1" -or [string]$package.package_schema -cne "boi-harness-package/v1") {
    Fail "고정 Harness schema가 올바르지 않습니다."
  }
  foreach ($field in @("release", "checksum", "signature", "signature_algorithm")) {
    if ([string]::IsNullOrWhiteSpace([string]$lock.$field) -or [string]::IsNullOrWhiteSpace([string]$package.$field)) {
      Fail "고정 Harness의 $field 값이 없습니다."
    }
    if ([string]$lock.$field -cne [string]$package.$field) {
      Fail "고정 Harness lock과 snapshot의 $field 값이 일치하지 않습니다."
    }
  }
  if ([string]$lock.checksum -notmatch '^[0-9a-f]{64}$' -or
      [string]$lock.signature -notmatch '^[0-9a-f]{64}$' -or
      [string]$lock.signature_algorithm -cne "hmac-sha256" -or
      [string]$package.signature_status -cne "signed") {
    Fail "고정 Harness checksum 또는 signature 상태가 올바르지 않습니다."
  }
  foreach ($field in @("capability_catalog", "ontology_schema_registry", "domain_catalogs", "policies")) {
    if ($null -eq $package.$field) { Fail "고정 Harness package에 $field 계약이 없습니다." }
  }
  Write-Host "Harness: $($package.release)"
  Write-Host "Harness checksum: $($package.checksum)"
  Write-Host "Harness verification: reduced offline lock/snapshot match (관리자 CI에서 canonical checksum 검증)"
}

function Verify-CoreRuntimeWorktree([string]$RepoRoot) {
  $manifestPath = Join-Path $RepoRoot ".boi-harness\core-runtime-manifest.json"
  if (!(Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Fail "CORE_RUNTIME_MANIFEST_MISSING: Core runtime manifest가 없습니다."
  }
  try {
    $manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
  } catch {
    Fail "CORE_RUNTIME_MANIFEST_INVALID: Core runtime manifest를 읽을 수 없습니다."
  }
  $expectedCoreSkills = @("boi-harness-builder", "boi-second-brain", "boi-wiki-local")
  $manifestCoreSkills = @($manifest.skills.PSObject.Properties.Name | Sort-Object)
  if ([string]$manifest.schema -cne "boi-local-core-runtime-manifest/v1" -or
      ($manifestCoreSkills -join "`n") -cne (($expectedCoreSkills | Sort-Object) -join "`n")) {
    Fail "CORE_RUNTIME_MANIFEST_INVALID: Core runtime manifest의 schema 또는 Skill 목록이 올바르지 않습니다."
  }
  foreach ($relative in @("AGENTS.md", "CLAUDE.md")) {
    $path = Join-Path $RepoRoot $relative
    if (!(Test-Path -LiteralPath $path -PathType Leaf) -or (Get-Item -LiteralPath $path).Length -eq 0) {
      Fail "CORE_RUNTIME_BOOTSTRAP_INVALID: Core runtime bootstrap이 없거나 비어 있습니다($relative)."
    }
  }
  foreach ($skillName in $expectedCoreSkills) {
    $codexRoot = Join-Path $RepoRoot ".agents\skills\$skillName"
    $claudeRoot = Join-Path $RepoRoot ".claude\skills\$skillName"
    foreach ($path in @($codexRoot, $claudeRoot)) {
      if (!(Test-Path -LiteralPath $path -PathType Container)) {
        Fail "CORE_SKILL_INVALID: Core Skill 폴더가 없습니다($skillName)."
      }
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
      Fail "CORE_SKILL_FILESET_MISMATCH: Core runtime manifest와 실제 Skill 파일 구성이 일치하지 않습니다($skillName)."
    }
    $relativeFiles = $requiredFiles
    foreach ($relative in $relativeFiles) {
      $codexFile = Join-Path $codexRoot $relative
      $claudeFile = Join-Path $claudeRoot $relative
      if (!(Test-Path -LiteralPath $codexFile -PathType Leaf) -or
          !(Test-Path -LiteralPath $claudeFile -PathType Leaf)) {
        Fail "CORE_SKILL_FILESET_MISMATCH: Codex와 Claude Core Skill 파일 구성이 일치하지 않습니다($skillName/$relative)."
      }
      if ((Get-Item -LiteralPath $codexFile).Length -eq 0 -or
          (Get-Item -LiteralPath $claudeFile).Length -eq 0) {
        Fail "CORE_SKILL_INVALID: Core Skill 파일이 비어 있습니다($skillName/$relative)."
      }
      if ((Get-FileHash -LiteralPath $codexFile -Algorithm SHA256).Hash -cne
          (Get-FileHash -LiteralPath $claudeFile -Algorithm SHA256).Hash) {
        Fail "CORE_SKILL_MIRROR_MISMATCH: Codex와 Claude Core Skill 내용이 일치하지 않습니다($skillName/$relative)."
      }
    }
  }
  Write-Host "Core runtime verification: worktree bootstrap and Skill mirrors match"
}

function Verify-CoreRuntimeRef([string]$RepoRoot, [string]$Ref) {
  $runtimePaths = @("AGENTS.md", "CLAUDE.md")
  foreach ($relative in $runtimePaths) {
    $spec = "${Ref}:$relative"
    & git -C $RepoRoot cat-file -e $spec 2>$null
    if ($LASTEXITCODE -ne 0) { Fail "UPDATE_CORE_RUNTIME_MISSING: 업데이트 후보에 Core runtime 파일이 없습니다($relative)." }
    $size = (& git -C $RepoRoot cat-file -s $spec 2>$null).Trim()
    if ($LASTEXITCODE -ne 0 -or [int64]$size -le 0) { Fail "UPDATE_CORE_RUNTIME_EMPTY: 업데이트 후보의 Core runtime 파일이 비어 있습니다($relative)." }
  }
  $manifestSpec = "${Ref}:.boi-harness/core-runtime-manifest.json"
  $manifestText = (& git -C $RepoRoot show $manifestSpec 2>$null) -join "`n"
  if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($manifestText)) {
    Fail "UPDATE_CORE_RUNTIME_MANIFEST_MISSING: 업데이트 후보에 Core runtime manifest가 없습니다."
  }
  try {
    $manifest = $manifestText | ConvertFrom-Json
  } catch {
    Fail "UPDATE_CORE_RUNTIME_MANIFEST_INVALID: 업데이트 후보의 Core runtime manifest를 읽을 수 없습니다."
  }
  $expectedCoreSkills = @("boi-harness-builder", "boi-second-brain", "boi-wiki-local")
  $manifestCoreSkills = @($manifest.skills.PSObject.Properties.Name | Sort-Object)
  if ([string]$manifest.schema -cne "boi-local-core-runtime-manifest/v1" -or
      ($manifestCoreSkills -join "`n") -cne (($expectedCoreSkills | Sort-Object) -join "`n")) {
    Fail "UPDATE_CORE_RUNTIME_MANIFEST_INVALID: 업데이트 후보의 Core runtime manifest 계약이 올바르지 않습니다."
  }
  foreach ($skillName in $expectedCoreSkills) {
    $codexPrefix = ".agents/skills/$skillName/"
    $claudePrefix = ".claude/skills/$skillName/"
    $codexPaths = @(& git -C $RepoRoot ls-tree -r --name-only $Ref -- $codexPrefix 2>$null)
    if ($LASTEXITCODE -ne 0) { Fail "UPDATE_CORE_RUNTIME_INVALID: 업데이트 후보의 Core Skill을 읽을 수 없습니다($skillName)." }
    $claudePaths = @(& git -C $RepoRoot ls-tree -r --name-only $Ref -- $claudePrefix 2>$null)
    if ($LASTEXITCODE -ne 0) { Fail "UPDATE_CORE_RUNTIME_INVALID: 업데이트 후보의 Core Skill을 읽을 수 없습니다($skillName)." }
    $codexRelative = @($codexPaths | ForEach-Object { $_.Substring($codexPrefix.Length) } | Sort-Object)
    $claudeRelative = @($claudePaths | ForEach-Object { $_.Substring($claudePrefix.Length) } | Sort-Object)
    $requiredFiles = @($manifest.skills.$skillName | ForEach-Object { [string]$_ } | Sort-Object)
    $requiredFileList = $requiredFiles -join "`n"
    if (($codexRelative -join "`n") -cne $requiredFileList -or
        ($claudeRelative -join "`n") -cne $requiredFileList -or
        $requiredFiles.Count -eq 0) {
      Fail "UPDATE_CORE_SKILL_FILESET_MISMATCH: 업데이트 후보의 manifest와 Codex·Claude Core Skill 파일 구성이 일치하지 않습니다($skillName)."
    }
    foreach ($relative in $requiredFiles) {
      $codexSpec = "${Ref}:$codexPrefix$relative"
      $claudeSpec = "${Ref}:$claudePrefix$relative"
      $codexSize = (& git -C $RepoRoot cat-file -s $codexSpec 2>$null).Trim()
      if ($LASTEXITCODE -ne 0 -or [int64]$codexSize -le 0) {
        Fail "UPDATE_CORE_RUNTIME_EMPTY: 업데이트 후보의 Core Skill 파일이 비어 있습니다($skillName/$relative)."
      }
      $claudeSize = (& git -C $RepoRoot cat-file -s $claudeSpec 2>$null).Trim()
      if ($LASTEXITCODE -ne 0 -or [int64]$claudeSize -le 0) {
        Fail "UPDATE_CORE_RUNTIME_EMPTY: 업데이트 후보의 Core Skill 파일이 비어 있습니다($skillName/$relative)."
      }
      $codexBlob = (& git -C $RepoRoot rev-parse $codexSpec 2>$null).Trim()
      $claudeBlob = (& git -C $RepoRoot rev-parse $claudeSpec 2>$null).Trim()
      if (!$codexBlob -or !$claudeBlob -or $codexBlob -cne $claudeBlob) {
        Fail "UPDATE_CORE_SKILL_MIRROR_MISMATCH: 업데이트 후보의 Codex와 Claude Core Skill 내용이 일치하지 않습니다($skillName/$relative)."
      }
    }
  }
  Write-Host "Core runtime verification: $Ref bootstrap and Skill mirrors match"
}

function Get-FrontmatterValue([string]$Content, [string]$Name) {
  $pattern = '(?m)^' + [regex]::Escape($Name) + ':\s*"?([^"\r\n]+)'
  $match = [regex]::Match($Content, $pattern)
  if ($match.Success) { return $match.Groups[1].Value.Trim() }
  return ""
}

function Get-GuideRelease([string]$GuideRoot) {
  $releases = @(
    Get-ChildItem -LiteralPath $GuideRoot -Recurse -Filter "*.md" -File | ForEach-Object {
      $value = Get-FrontmatterValue ([IO.File]::ReadAllText($_.FullName)) "guide_release"
      if ($value) { $value }
    } | Sort-Object -Unique
  )
  if ($releases.Count -ne 1) { Fail "가이드 release 값이 하나로 일치하지 않습니다." }
  return [string]$releases[0]
}

function Render-Guide([string]$TemplatePath, [string]$CurrentPath, [string]$EmployeeId, [string]$RepoUrl) {
  $template = [IO.File]::ReadAllText($TemplatePath)
  $current = if (Test-Path -LiteralPath $CurrentPath -PathType Leaf) { [IO.File]::ReadAllText($CurrentPath) } else { "" }
  $timestamp = Get-FrontmatterValue $current "timestamp"
  $reviewAfter = Get-FrontmatterValue $current "review_after"
  if (!$timestamp) { $timestamp = (Get-Date).ToString("o") }
  if (!$reviewAfter) { $reviewAfter = (Get-Date).AddMonths(6).ToString("yyyy-MM-dd") }
  $rendered = $template.Replace("{{employee_id}}", $EmployeeId)
  $rendered = $rendered.Replace("{{timestamp}}", $timestamp)
  $rendered = $rendered.Replace("{{review_after}}", $reviewAfter)
  $rendered = $rendered.Replace("{{repository_url}}", $RepoUrl)
  return $rendered.Replace("`r`n", "`n")
}

function Guide-Plan([string]$RepoRoot, [string]$EmployeeId, [string]$RepoUrl) {
  $sourceRoot = Join-Path $RepoRoot "templates\second-brain-guide"
  $targetRoot = Join-Path $RepoRoot "data\boi\private\$EmployeeId\notes\guide"
  $items = @()
  if (!(Test-Path -LiteralPath $sourceRoot -PathType Container)) { Fail "가이드 template 폴더가 없습니다." }
  Get-ChildItem -LiteralPath $sourceRoot -Recurse -File | ForEach-Object {
    $relative = $_.FullName.Substring($sourceRoot.Length).TrimStart('\', '/')
    $target = Join-Path $targetRoot $relative
    if ($_.Extension -ieq ".md") {
      $desiredText = Render-Guide $_.FullName $target $EmployeeId $RepoUrl
      $desiredBytes = [Text.UTF8Encoding]::new($false).GetBytes($desiredText)
    } else {
      $desiredBytes = [IO.File]::ReadAllBytes($_.FullName)
    }
    $same = $false
    if (Test-Path -LiteralPath $target -PathType Leaf) {
      $currentBytes = [IO.File]::ReadAllBytes($target)
      $same = [Linq.Enumerable]::SequenceEqual([byte[]]$currentBytes, [byte[]]$desiredBytes)
    }
    if (!$same) {
      $items += [pscustomobject]@{
        Relative = $relative
        Target = $target
        Exists = (Test-Path -LiteralPath $target -PathType Leaf)
        Bytes = $desiredBytes
      }
    }
  }
  return @($items)
}

function Show-GuidePlan($Plan, [string]$Release) {
  Write-Host "Guide release: $Release"
  Write-Host "Guide changes: $($Plan.Count)"
  foreach ($item in $Plan) {
    $action = if ($item.Exists) { "update" } else { "create" }
    Write-Host "  $action $($item.Relative)"
  }
}

function Apply-GuidePlan($Plan, [string]$RepoRoot, [string]$EmployeeId) {
  $guideRoot = Join-Path $RepoRoot "data\boi\private\$EmployeeId\notes\guide"
  $archive = Join-Path $RepoRoot ("data\boi\private\$EmployeeId\_archive\guides\" + (Get-Date -Format "yyyyMMdd-HHmmss"))
  foreach ($item in $Plan) {
    if ($item.Exists) {
      $backup = Join-Path $archive $item.Relative
      [IO.Directory]::CreateDirectory((Split-Path -Parent $backup)) | Out-Null
      Copy-Item -LiteralPath $item.Target -Destination $backup
    }
    [IO.Directory]::CreateDirectory((Split-Path -Parent $item.Target)) | Out-Null
    [IO.File]::WriteAllBytes($item.Target, [byte[]]$item.Bytes)
  }
  if ($Plan.Count -gt 0) { Write-Host "Guide backup: $archive" }
  Write-Host "Guide apply: $($Plan.Count) file(s)"
}

if (!(Test-Path -LiteralPath (Join-Path $Root ".git"))) { Fail "Git checkout이 아닙니다: $Root" }
if (!(Get-Command git -ErrorAction SilentlyContinue)) { Fail "Git for Windows가 필요합니다." }

Verify-HarnessSnapshot $Root
Verify-CoreRuntimeWorktree $Root

$sourceSelector = Join-Path $Root "scripts\select-repository-source.ps1"
if (Test-Path -LiteralPath $sourceSelector -PathType Leaf) {
  $sourcePreviewJson = & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $sourceSelector -Mode Preview -Root $Root -RepositoryId "boi-wiki-local"
  if ($LASTEXITCODE -ne 0) { Fail "저장소 위치 판정에 실패했습니다." }
  $sourcePreview = $sourcePreviewJson | ConvertFrom-Json
} else {
  $sourcePreview = [pscustomobject]@{
    state = "legacy-existing-origin"; selection_reason = "selector-arrives-with-update"
    action = "no-change"; plan_hash = "not-required"; blocker = ""
  }
}
Write-Host "Repository source state: $([string]$sourcePreview.state)"
Write-Host "Repository source reason: $([string]$sourcePreview.selection_reason)"
Write-Host "Repository source action: $([string]$sourcePreview.action)"
Write-Host "Repository source plan hash: $([string]$sourcePreview.plan_hash)"
Write-Host "External fallback is not push approval."
if ([string]$sourcePreview.action -eq "blocked") { Fail ([string]$sourcePreview.blocker) }
if ($Apply -and [string]$sourcePreview.action -eq "set-origin") {
  if (!$ConfirmSourcePlanHash -or $ConfirmSourcePlanHash -cne [string]$sourcePreview.plan_hash) {
    Fail "origin 변경 후보가 있습니다. 현재 source plan hash를 --confirm-source-plan으로 승인한 뒤 다시 실행하세요."
  }
  $sourceApplyJson = & powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File $sourceSelector -Mode Apply -Root $Root -RepositoryId "boi-wiki-local" -ConfirmPlanHash $ConfirmSourcePlanHash
  if ($LASTEXITCODE -ne 0) { Fail "승인된 origin 변경 또는 검증에 실패했습니다." }
  $sourceApply = $sourceApplyJson | ConvertFrom-Json
  if ($sourceApply.ok -ne $true) { Fail "origin 변경 후 검증에 실패했습니다." }
}

$origin = (& git -C $Root remote get-url origin 2>$null).Trim()
if ($LASTEXITCODE -ne 0 -or !$origin) { Fail "Git origin이 없습니다. GitHub 또는 사내 Bitbucket mirror 주소를 설정하세요." }
$safeOrigin = Safe-Remote $origin
$profile = Resolve-LocalProfile $Root
$employeeId = $profile.Id
$beforePrivate = Private-Manifest $Root $employeeId
$dirty = @(& git -C $Root status --porcelain=v1 --untracked-files=all)
$currentBranch = (& git -C $Root branch --show-current).Trim()
if (!$currentBranch) { Fail "detached HEAD는 지원하지 않습니다. stable branch로 전환하세요." }

Write-Host "Repository: $safeOrigin"
Write-Host "Current branch: $currentBranch"
Write-Host "Local profile source: $($profile.Source)"
Write-Host "Mode: $(if ($Apply) {'APPLY'} else {'PREVIEW'})"

& git -C $Root fetch --prune origin
if ($LASTEXITCODE -ne 0) { Fail "origin fetch에 실패했습니다. Local-only 사용은 계속 가능하며 네트워크 또는 인증을 확인하세요." }

$defaultRef = (& git -C $Root symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>$null).Trim()
if ($LASTEXITCODE -eq 0 -and $defaultRef -match '^origin/(.+)$') {
  $stableBranch = $Matches[1]
} else {
  & git -C $Root show-ref --verify --quiet refs/remotes/origin/main
  if ($LASTEXITCODE -eq 0) { $stableBranch = "main" } else { Fail "stable branch를 확인할 수 없습니다. origin/HEAD 또는 origin/main을 설정하세요." }
}

Verify-CoreRuntimeRef $Root "origin/$stableBranch"

$incoming = @(& git -C $Root log --oneline "$currentBranch..origin/$stableBranch")
$changed = @(& git -C $Root diff --name-status "$currentBranch...origin/$stableBranch")
Write-Host "Stable branch: $stableBranch"
Write-Host "Incoming commits: $($incoming.Count)"
if ($incoming.Count) { $incoming | ForEach-Object { Write-Host "  $_" } }
Write-Host "Incoming files: $($changed.Count)"
if ($changed.Count) { $changed | ForEach-Object { Write-Host "  $_" } }

if (!$Apply) {
  if ($dirty.Count) { Write-Warning "작업 폴더에 변경이 있습니다. Apply는 변경을 안전하게 보존하기 전까지 중단됩니다." }
  Write-Host "Preview complete. 목록 확인 후 .\update.cmd --apply를 실행하세요."
  Assert-SameManifest $beforePrivate (Private-Manifest $Root $employeeId)
  exit 0
}

if ($dirty.Count) { Fail "작업 폴더가 clean 상태가 아닙니다. 업데이트는 자동 stash 또는 reset을 하지 않습니다." }
if ($currentBranch -ne $stableBranch) { Fail "Apply는 stable branch '$stableBranch'에서만 가능합니다. 현재 branch: '$currentBranch'." }

$behindAhead = (& git -C $Root rev-list --left-right --count "$currentBranch...origin/$stableBranch").Trim() -split '\s+'
if ($behindAhead.Count -lt 2) { Fail "branch divergence를 확인할 수 없습니다." }
if ([int]$behindAhead[0] -gt 0) { Fail "Local stable branch에 origin에 없는 commit이 있습니다. push/review하거나 새 clone을 사용하세요." }

& git -C $Root pull --ff-only origin $stableBranch
if ($LASTEXITCODE -ne 0) { Fail "fast-forward update에 실패했습니다. reset 또는 stash는 수행하지 않았습니다." }

Verify-HarnessSnapshot $Root
Verify-CoreRuntimeWorktree $Root
$guideRoot = Join-Path $Root "templates\second-brain-guide"
$guideRelease = Get-GuideRelease $guideRoot
$repoUrl = if ($employeeId -eq "0000000") { "<배포 Git 저장소 주소>" } else { $safeOrigin }
$guidePlan = @(Guide-Plan $Root $employeeId $repoUrl)
Show-GuidePlan $guidePlan $guideRelease
if ($ConfirmGuideRelease) {
  if ($ConfirmGuideRelease -cne $guideRelease) { Fail "가이드 적용에는 --confirm-guide-release $guideRelease 값이 필요합니다." }
  Apply-GuidePlan $guidePlan $Root $employeeId
} elseif ($guidePlan.Count -gt 0) {
  Write-Host "가이드는 preview만 했습니다. 적용하려면 --confirm-guide-release $guideRelease를 추가하세요."
}

& (Join-Path $Root "check.ps1") -Root $Root -NativeOnly
if ($LASTEXITCODE -ne 0) { Fail "업데이트 후 저장소 check가 실패했습니다." }
Assert-SameManifest $beforePrivate (Private-Manifest $Root $employeeId)
Write-Host "Update completed. Local Private content hash is unchanged."
