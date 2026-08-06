[CmdletBinding()]
param(
    [string]$EmployeeId = "",
    [ValidateSet("auto-curate", "suggest", "explicit-only", "")]
    [string]$Mode = "",
    [string]$Inbox = "",
    [switch]$Approve,
    [switch]$PreviewOnly,
    [string]$ConfirmPlanHash = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
if ($repoRoot -match '^(?i)\\\\wsl(?:\$|\.localhost)\\') {
    throw "Windows 네이티브 설치는 WSL 경로에서 실행할 수 없습니다. C:\\Users\\<계정>\\Projects\\boi-wiki-local clone을 AI 작업 폴더로 열어 다시 실행하세요. 개인 설정을 만들지 않았습니다."
}

$lockPath = Join-Path $repoRoot "harness.lock"
$snapshotPath = Join-Path $repoRoot ".boi-harness\package.json"
if (!(Test-Path -LiteralPath $lockPath) -or !(Test-Path -LiteralPath $snapshotPath)) {
    throw "고정 BoI Harness 잠금 파일 또는 오프라인 스냅샷이 없습니다. 개인 설정을 만들지 않았습니다."
}
try {
    $harnessLock = Get-Content -LiteralPath $lockPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $harnessPackage = Get-Content -LiteralPath $snapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    throw "고정 BoI Harness 정보를 읽을 수 없습니다. 개인 설정을 만들지 않았습니다."
}
$requiredHarnessFields = @("release", "checksum", "signature", "signature_algorithm")
foreach ($field in $requiredHarnessFields) {
    if ([string]::IsNullOrWhiteSpace([string]$harnessLock.$field) -or
        [string]::IsNullOrWhiteSpace([string]$harnessPackage.$field)) {
        throw "고정 BoI Harness의 $field 값이 없습니다. 개인 설정을 만들지 않았습니다."
    }
    if ([string]$harnessLock.$field -cne [string]$harnessPackage.$field) {
        throw "고정 BoI Harness의 $field 값이 일치하지 않습니다. 개인 설정을 만들지 않았습니다."
    }
}
if ([string]$harnessLock.checksum -notmatch '^[0-9a-f]{64}$' -or
    [string]$harnessLock.signature -notmatch '^[0-9a-f]{64}$' -or
    [string]$harnessLock.signature_algorithm -cne "hmac-sha256") {
    throw "고정 BoI Harness의 checksum 또는 signature 형식이 올바르지 않습니다. 개인 설정을 만들지 않았습니다."
}

$requiredProjectFiles = @(
    "AGENTS.md",
    "CLAUDE.md",
    ".agents\skills\boi-harness-builder\SKILL.md",
    ".agents\skills\boi-second-brain\SKILL.md",
    ".agents\skills\boi-wiki-local\SKILL.md",
    ".claude\skills\boi-harness-builder\SKILL.md",
    ".claude\skills\boi-second-brain\SKILL.md",
    ".claude\skills\boi-wiki-local\SKILL.md",
    ".boi-harness\core-runtime-manifest.json",
    "templates\second-brain-guide\00-start-here.md",
    "templates\second-brain-guide\02-build-your-harness.md",
    "templates\second-brain-guide\12-ai-assisted-setup.md",
    "templates\second-brain-guide\50-mcp-and-promotion.md",
    "templates\second-brain-guide\60-troubleshooting.md"
)
foreach ($relative in $requiredProjectFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoRoot $relative) -PathType Leaf)) {
        throw "현재 폴더는 완전한 BoI Wiki Local Windows clone이 아닙니다($relative 누락). 개인 설정을 만들지 않았습니다."
    }
}

$coreRuntimeManifestPath = Join-Path $repoRoot ".boi-harness\core-runtime-manifest.json"
try {
    $coreRuntimeManifest = Get-Content -LiteralPath $coreRuntimeManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    throw "Core runtime manifest를 읽을 수 없습니다. 개인 설정을 만들지 않았습니다."
}
$expectedCoreSkills = @("boi-harness-builder", "boi-second-brain", "boi-wiki-local")
$manifestCoreSkills = @($coreRuntimeManifest.skills.PSObject.Properties.Name | Sort-Object)
if ([string]$coreRuntimeManifest.schema -cne "boi-local-core-runtime-manifest/v1" -or
    ($manifestCoreSkills -join "`n") -cne (($expectedCoreSkills | Sort-Object) -join "`n")) {
    throw "Core runtime manifest의 schema 또는 Skill 목록이 올바르지 않습니다. 개인 설정을 만들지 않았습니다."
}

foreach ($skillName in $expectedCoreSkills) {
    $codexRoot = Join-Path $repoRoot ".agents\skills\$skillName"
    $claudeRoot = Join-Path $repoRoot ".claude\skills\$skillName"
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
    $requiredFiles = @($coreRuntimeManifest.skills.$skillName | ForEach-Object { [string]$_ } | Sort-Object)
    $requiredFileList = $requiredFiles -join "`n"
    $codexFileList = @($codexFiles | Sort-Object) -join "`n"
    $claudeFileList = @($claudeFiles | Sort-Object) -join "`n"
    if ($codexFileList -cne $requiredFileList -or $claudeFileList -cne $requiredFileList) {
        throw "Core runtime manifest와 실제 Skill 파일 구성이 일치하지 않습니다($skillName). 개인 설정을 만들지 않았습니다."
    }
    $relativeFiles = $requiredFiles
    foreach ($relative in $relativeFiles) {
        $codexFile = Join-Path $codexRoot $relative
        $claudeFile = Join-Path $claudeRoot $relative
        if (!(Test-Path -LiteralPath $codexFile -PathType Leaf) -or
            !(Test-Path -LiteralPath $claudeFile -PathType Leaf)) {
            throw "Codex와 Claude의 Core Skill 파일 구성이 일치하지 않습니다($skillName/$relative). 개인 설정을 만들지 않았습니다."
        }
        if ((Get-Item -LiteralPath $codexFile).Length -eq 0 -or
            (Get-Item -LiteralPath $claudeFile).Length -eq 0) {
            throw "Core Skill 파일 내용이 비어 있습니다($skillName/$relative). 개인 설정을 만들지 않았습니다."
        }
        $codexHash = (Get-FileHash -LiteralPath $codexFile -Algorithm SHA256).Hash
        $claudeHash = (Get-FileHash -LiteralPath $claudeFile -Algorithm SHA256).Hash
        if ($codexHash -cne $claudeHash) {
            throw "Codex와 Claude의 Core Skill 내용이 일치하지 않습니다($skillName/$relative). 개인 설정을 만들지 않았습니다."
        }
    }
}

if (-not $EmployeeId) {
    $EmployeeId = $env:BOI_LOCAL_EMPLOYEE_ID
}
if (-not $EmployeeId) {
    $EmployeeId = Read-Host "사번 또는 7자리 Local Profile 식별자"
}
if ($EmployeeId -notmatch '^[0-9]{7}$' -or $EmployeeId -eq '0000000') {
    throw "실제 사용에는 0000000이 아닌 7자리 Local Profile 식별자가 필요합니다."
}

# Resolve an existing Profile binding before asking the remaining questions or
# creating any Local directory. A conflicting .env must be a true no-write
# failure, not a partially applied second Profile.
$envPath = Join-Path $repoRoot ".env"
$envContent = $null
if (Test-Path -LiteralPath $envPath) {
    $envContent = [System.IO.File]::ReadAllText($envPath)
    if ($envContent -match '(?m)^BOI_LOCAL_EMPLOYEE_ID=([0-9]{7})\s*$') {
        $configuredId = $Matches[1]
        if ($configuredId -notin @("0000000", $EmployeeId)) {
            throw ".env가 다른 Local Profile을 가리킵니다. 기존 설정을 보존하고 관리자에게 문의하세요."
        }
        $envContent = [regex]::Replace(
            $envContent,
            '(?m)^BOI_LOCAL_EMPLOYEE_ID=[0-9]{7}\s*$',
            "BOI_LOCAL_EMPLOYEE_ID=$EmployeeId"
        )
    } else {
        $envContent = $envContent.TrimEnd() + "`nBOI_LOCAL_EMPLOYEE_ID=$EmployeeId`n"
    }
}

if (-not $Mode) {
    Write-Host "`n자동 정리 방식을 고르세요."
    Write-Host "  1. 알아서 정리 (권장)"
    Write-Host "  2. 정리 전 확인"
    Write-Host "  3. 요청할 때만"
    $choice = Read-Host "선택 [1]"
    $Mode = switch ($choice) {
        "2" { "suggest" }
        "3" { "explicit-only" }
        default { "auto-curate" }
    }
}

if (-not $Inbox) {
    $defaultInbox = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "BoI-Second-Brain-Inbox"
    $enteredInbox = Read-Host "자료를 넣을 폴더 (Enter: $defaultInbox)"
    $Inbox = if ($enteredInbox) { $enteredInbox } else { $defaultInbox }
}
$Inbox = [System.IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($Inbox))
$profileRoot = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "data\boi\private\$EmployeeId"))
if ($Inbox -eq [System.IO.Path]::GetPathRoot($Inbox) -or $Inbox -eq [Environment]::GetFolderPath("UserProfile")) {
    throw "드라이브 전체나 사용자 폴더 전체는 자료 폴더로 지정할 수 없습니다."
}
if ($Inbox.StartsWith($profileRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "BoI Wiki Local 출력 폴더를 다시 자료 폴더로 지정할 수 없습니다."
}

$modeLabel = switch ($Mode) {
    "auto-curate" { "가치 있는 내용만 알아서 반영" }
    "suggest" { "변경 요약을 확인한 뒤 반영" }
    "explicit-only" { "요청할 때만 반영" }
}
$authorizationSummary = switch ($Mode) {
    "auto-curate" { "가치 있는 대화와 지정 자료 폴더를 Local Private 지식에 알아서 반영" }
    "suggest" { "가치 있는 대화와 지정 자료 폴더의 변경 요약을 확인한 뒤 Local Private 지식에 반영" }
    "explicit-only" { "명시적으로 요청한 대화와 자료 폴더 작업만 Local Private 지식에 반영" }
}

$setupPlan = [ordered]@{
    schema = "boi-local-setup-plan/v1"
    employee_id = $EmployeeId
    conversation_mode = $Mode
    source_folders = @($Inbox)
    preserve_originals = $true
    copy_raw_transcripts = $false
    remote_auto_upload = $false
    agent_session_check = ($Mode -ne "explicit-only")
    harness_release = [string]$harnessPackage.release
    harness_checksum = [string]$harnessPackage.checksum
}
$setupPlanJson = $setupPlan | ConvertTo-Json -Depth 5 -Compress
$setupPlanBytes = [System.Text.UTF8Encoding]::new($false).GetBytes($setupPlanJson)
$sha256 = [System.Security.Cryptography.SHA256]::Create()
try {
    $setupPlanHash = -join ($sha256.ComputeHash($setupPlanBytes) | ForEach-Object { $_.ToString("x2") })
} finally {
    $sha256.Dispose()
}

if ($PreviewOnly) {
    [ordered]@{
        schema = "boi-local-setup-preview/v1"
        plan_hash = $setupPlanHash
        plan = $setupPlan
        mutation_performed = $false
    } | ConvertTo-Json -Depth 7
    exit 0
}

Write-Host "`n설정 미리보기`n"
Write-Host "- 대화 관리: $modeLabel"
Write-Host "- 자료 폴더: $Inbox"
Write-Host "- 원본 보존: 켜짐"
Write-Host "- 원격 자동 업로드: 꺼짐"
Write-Host "- Obsidian/MCP: 없어도 정상 동작"

if ($ConfirmPlanHash) {
    if ($ConfirmPlanHash -notmatch '^[0-9a-f]{64}$' -or $ConfirmPlanHash -cne $setupPlanHash) {
        throw "승인한 설정과 현재 설정 계획이 일치하지 않습니다. 새 미리보기를 확인하세요. 파일을 변경하지 않았습니다."
    }
} elseif ($Approve) {
    Write-Host "INFO 기존 관리 자동화 호환 모드로 적용합니다. AI 설정은 preview hash 확인 경로를 사용해야 합니다."
}

if (-not $Approve) {
    $confirmation = Read-Host "이대로 설정할까요? [Y/N]"
    if ($confirmation -notin @("Y", "y", "예", "네")) {
        Write-Host "취소했습니다. 파일을 변경하지 않았습니다."
        exit 2
    }
}

$folders = @(
    "notes\capture-inbox", "notes\knowledge", "notes\memory", "notes\guide", "notes\harnesses",
    "evidence\inbox", "cases", "sop-drafts", "promotion-drafts", "action-drafts",
    "event-drafts", "dictionary", "diagrams", "context-packs", "workflow-simulations",
    "langflow-plans", "usage-examples", "reports", "_archive\config", ".boi-local"
)
foreach ($relative in $folders) {
    [System.IO.Directory]::CreateDirectory((Join-Path $profileRoot $relative)) | Out-Null
}
[System.IO.Directory]::CreateDirectory($Inbox) | Out-Null

$profileIndex = Join-Path $profileRoot "index.md"
if (-not (Test-Path -LiteralPath $profileIndex)) {
    $indexContent = @"
# 내 BoI Wiki Local

개인 Meta Harness와 Local Private 지식 공간입니다. 명시적인 promotion 승인 없이 원격으로 전송하지 않습니다.

## 먼저 할 일

1. [내 업무용 BoI Harness 만들기](notes/guide/02-build-your-harness.md)
2. [Flagship Second Brain 설정](notes/guide/12-ai-assisted-setup.md)
3. [처음 시작하기](notes/guide/00-start-here.md)
4. [승인된 개인 Harness](notes/harnesses/index.md)

## 내 작업 공간

- [Inbox](inbox.md)
- [Notes](notes/)
- [SOP Drafts](sop-drafts/)
- [Action Drafts](action-drafts/)
- [Event Drafts](event-drafts/)
- [Dictionary](dictionary/)
- [Diagrams](diagrams/)
- [Context Packs](context-packs/)
- [Workflow Simulations](workflow-simulations/)
- [Langflow Plans](langflow-plans/)
- [Reports](reports/)
- [Promotion Drafts](promotion-drafts/)
- [Usage Examples](usage-examples/)
- [Archive](_archive/)
"@
    [System.IO.File]::WriteAllText($profileIndex, $indexContent.Replace("`r`n", "`n"), [System.Text.UTF8Encoding]::new($false))
}

$profileInbox = Join-Path $profileRoot "inbox.md"
if (-not (Test-Path -LiteralPath $profileInbox)) {
    [System.IO.File]::WriteAllText(
        $profileInbox,
        "# Inbox`n`n아직 분류되지 않은 메모를 둡니다. AI가 원본을 보존하고 적절한 Local Private 지식으로 정리합니다.`n",
        [System.Text.UTF8Encoding]::new($false)
    )
}

$harnessIndex = Join-Path $profileRoot "notes\harnesses\index.md"
if (-not (Test-Path -LiteralPath $harnessIndex)) {
    $harnessIndexContent = @"
# 승인된 개인 Harness

이곳은 AI가 업무 설명에서 구성하고 사용자가 승인한 재사용 실행 계약을 찾는 시작 페이지입니다. Harness 카드는 Local Private로 유지되며 그 자체를 Team/Public으로 직접 공유하지 않습니다.

## 새 Harness 만들기

> 내가 반복하는 업무를 설명할게. 기존 BoI Skills를 먼저 확인하고 역할, 작업 흐름, 산출물, 검토 기준이 있는 Harness 미리보기를 만들어줘. 내가 승인하면 이 폴더에 저장해줘.

## 저장된 Harness 다시 사용하기

> 저장된 Harness 이름으로 이번 자료를 처리해줘. 먼저 필요한 입력과 변경 범위를 확인하고 기존 역할·DAG·검토 계약을 그대로 사용해줘.

## 기존 Harness 개선하기

> 저장된 Harness 이름에서 실제로 막힌 부분을 분석하고, 기존 파일과 실패 evidence를 보존하는 변경 미리보기를 먼저 보여줘.

## 저장된 Harness

승인된 카드가 생기면 AI가 이 아래에 표준 Markdown 링크를 추가합니다. 카드가 아직 없어도 오류가 아닙니다.

## 공유 경계

개인 Harness 카드에는 Local 경로와 실행 설정이 있으므로 직접 promotion할 수 없습니다. 조직에 공유하려면 개인 설정을 제거한 일반 가이드나 검토된 Community Case로 별도 정제합니다.
"@
    [System.IO.File]::WriteAllText($harnessIndex, $harnessIndexContent.Replace("`r`n", "`n"), [System.Text.UTF8Encoding]::new($false))
}

$preferencesPath = Join-Path $profileRoot ".boi-local\second-brain-preferences.json"
if (Test-Path -LiteralPath $preferencesPath) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss"
    Copy-Item -LiteralPath $preferencesPath -Destination (Join-Path $profileRoot "_archive\config\second-brain-preferences-$stamp.json")
}

$preferences = [ordered]@{
    schema = "boi-local-second-brain-preferences/v1"
    employee_id = $EmployeeId
    conversation_mode = $Mode
    source_folders = @($Inbox)
    preserve_originals = $true
    copy_raw_transcripts = $false
    remote_auto_upload = $false
    agent_session_check = ($Mode -ne "explicit-only")
    obsidian_optional = $true
    mcp_optional = $true
    configured_at = (Get-Date).ToString("o")
    authorization = [ordered]@{
        approved_summary = $authorizationSummary
        requires_preview_for_scope_change = $true
    }
}
$temporaryPreferences = "$preferencesPath.tmp"
$preferences | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $temporaryPreferences -Encoding UTF8
Move-Item -LiteralPath $temporaryPreferences -Destination $preferencesPath -Force

if ($null -eq $envContent) {
    [System.IO.File]::WriteAllText(
        $envPath,
        "BOI_LOCAL_ROOT=.`nBOI_LOCAL_EMPLOYEE_ID=$EmployeeId`n",
        [System.Text.UTF8Encoding]::new($false)
    )
} else {
    [System.IO.File]::WriteAllText($envPath, $envContent, [System.Text.UTF8Encoding]::new($false))
}

$guideSource = Join-Path $repoRoot "templates\second-brain-guide"
$guideTarget = Join-Path $profileRoot "notes\guide"
if (Test-Path -LiteralPath $guideSource) {
    Get-ChildItem -LiteralPath $guideSource -Recurse -File | ForEach-Object {
        $relative = $_.FullName.Substring($guideSource.Length).TrimStart('\')
        $target = Join-Path $guideTarget $relative
        [System.IO.Directory]::CreateDirectory((Split-Path -Parent $target)) | Out-Null
        if (-not (Test-Path -LiteralPath $target)) {
            if ($_.Extension -eq ".md") {
                $content = [System.IO.File]::ReadAllText($_.FullName)
                $content = $content.Replace("{{employee_id}}", $EmployeeId)
                $content = $content.Replace("{{timestamp}}", (Get-Date).ToString("o"))
                $content = $content.Replace("{{review_after}}", (Get-Date).AddMonths(6).ToString("yyyy-MM-dd"))
                $content = $content.Replace("{{repository_url}}", "<현재 Git origin>")
                [System.IO.File]::WriteAllText($target, $content, [System.Text.UTF8Encoding]::new($false))
            } else {
                Copy-Item -LiteralPath $_.FullName -Destination $target
            }
        }
    }
}

# Employee setup must remain runtime-independent, but it must still prove that
# the promised Profile, preferences, and connected Wiki were applied correctly
# before printing a success result.
$requiredInstalledFiles = @(
    $profileIndex,
    $profileInbox,
    $harnessIndex,
    $preferencesPath,
    $envPath,
    (Join-Path $guideTarget "00-start-here.md"),
    (Join-Path $guideTarget "02-build-your-harness.md"),
    (Join-Path $guideTarget "12-ai-assisted-setup.md"),
    (Join-Path $guideTarget "50-mcp-and-promotion.md"),
    (Join-Path $guideTarget "60-troubleshooting.md")
)
foreach ($requiredPath in $requiredInstalledFiles) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "설치 결과 확인에 실패했습니다: 필수 파일이 없습니다($requiredPath). 설정 완료로 표시하지 않습니다."
    }
}
if (-not (Test-Path -LiteralPath (Join-Path $profileRoot "notes\harnesses") -PathType Container)) {
    throw "설치 결과 확인에 실패했습니다: 개인 Harness 폴더가 없습니다. 설정 완료로 표시하지 않습니다."
}

try {
    $installedPreferences = Get-Content -LiteralPath $preferencesPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    throw "설치 결과 확인에 실패했습니다: Second Brain 설정을 읽을 수 없습니다. 설정 완료로 표시하지 않습니다."
}
if ([string]$installedPreferences.schema -cne "boi-local-second-brain-preferences/v1" -or
    [string]$installedPreferences.employee_id -cne $EmployeeId -or
    [string]$installedPreferences.conversation_mode -cne $Mode -or
    $installedPreferences.preserve_originals -ne $true -or
    $installedPreferences.copy_raw_transcripts -ne $false -or
    $installedPreferences.remote_auto_upload -ne $false -or
    $installedPreferences.agent_session_check -ne ($Mode -ne "explicit-only") -or
    [string]$installedPreferences.authorization.approved_summary -cne $authorizationSummary -or
    $installedPreferences.authorization.requires_preview_for_scope_change -ne $true) {
    throw "설치 결과 확인에 실패했습니다: Local Private 또는 승인 경계 설정이 예상값과 다릅니다. 설정 완료로 표시하지 않습니다."
}
if (@($installedPreferences.source_folders).Count -ne 1 -or
    [System.IO.Path]::GetFullPath([string]$installedPreferences.source_folders[0]) -cne $Inbox) {
    throw "설치 결과 확인에 실패했습니다: 자료 폴더 설정이 승인한 경로와 다릅니다. 설정 완료로 표시하지 않습니다."
}

$installedEnv = [System.IO.File]::ReadAllText($envPath)
if ($installedEnv -notmatch "(?m)^BOI_LOCAL_EMPLOYEE_ID=$EmployeeId\s*$") {
    throw "설치 결과 확인에 실패했습니다: Local Profile 연결이 적용되지 않았습니다. 설정 완료로 표시하지 않습니다."
}

$profileMarkers = @(
    'okf_version: "0.1"',
    'boi_profile_version: "0.1-local"',
    'visibility: local-private',
    "owner: `"$EmployeeId`"",
    'local_only: true'
)
foreach ($guideName in @("00-start-here.md", "02-build-your-harness.md", "12-ai-assisted-setup.md", "50-mcp-and-promotion.md")) {
    $installedGuidePath = Join-Path $guideTarget $guideName
    $installedGuide = [System.IO.File]::ReadAllText($installedGuidePath)
    foreach ($marker in $profileMarkers) {
        if (-not $installedGuide.Contains($marker)) {
            throw "설치 결과 확인에 실패했습니다: $guideName 문서의 OKF·BoI Local Profile 계약이 불완전합니다. 설정 완료로 표시하지 않습니다."
        }
    }
}

$unresolvedTemplate = Get-ChildItem -LiteralPath $guideTarget -Recurse -File -Filter "*.md" |
    Select-String -Pattern '\{\{(employee_id|timestamp|review_after|repository_url)\}\}' |
    Select-Object -First 1
if ($unresolvedTemplate) {
    throw "설치 결과 확인에 실패했습니다: Wiki에 치환되지 않은 설치 값이 남았습니다($($unresolvedTemplate.Path)). 설정 완료로 표시하지 않습니다."
}

Write-Host "`n설치 결과 확인: 통과 (Windows 기본 검사)"

Write-Host "`n설정 완료`n"
Write-Host "- 대화 관리: $modeLabel"
Write-Host "- 자료 폴더: $Inbox"
Write-Host "- 원본 보존: 켜짐"
Write-Host "- 원격 자동 업로드: 꺼짐"
Write-Host "- Obsidian/MCP: 없어도 정상 동작"
Write-Host "`n첫 사용: 오늘 논의한 결정 중 오래 쓸 내용은 Second Brain에 반영해줘."
