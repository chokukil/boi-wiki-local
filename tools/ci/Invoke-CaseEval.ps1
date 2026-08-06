[CmdletBinding()]
param(
    [ValidateSet('Doctor', 'Run')]
    [string]$Action = 'Doctor',
    [ValidateSet('codex', 'claude')]
    [string]$Runtime = 'codex',
    [ValidateSet('with-harness', 'baseline')]
    [string]$Configuration = 'with-harness',
    [ValidatePattern('^p0[1-8]$')]
    [string]$PromptId = 'p01',
    [ValidateRange(1, 3)]
    [int]$Repetition = 1,
    [string]$ModelId = '',
    [ValidateSet('low', 'medium', 'high', 'xhigh', 'max', 'ultra')]
    [string]$ReasoningSetting = 'high',
    [ValidateRange(30, 1800)]
    [int]$TurnTimeoutSeconds = 300,
    [ValidateSet('workspace-write', 'danger-full-access')]
    [string]$CodexSandboxMode = 'workspace-write',
    [string]$CaseRoot = '',
    [string]$RunRoot = '',
    [switch]$ConfirmSyntheticRun,
    [switch]$ConfirmUnsandboxedSyntheticPilot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Utf8Json {
    param([Parameter(Mandatory)]$Value, [Parameter(Mandatory)][string]$Path)
    $json = $Value | ConvertTo-Json -Depth 100
    [IO.File]::WriteAllText($Path, $json + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}

function Get-Sha256 {
    param([Parameter(Mandatory)][string]$Path)
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-TextSha256 {
    param([Parameter(Mandatory)][string]$Text)
    $sha = [Security.Cryptography.SHA256]::Create()
    try {
        return ([BitConverter]::ToString($sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Text)))).Replace('-', '').ToLowerInvariant()
    }
    finally { $sha.Dispose() }
}

function ConvertTo-CanonicalValue {
    param($Value)
    if ($null -eq $Value) { return $null }
    if ($Value -is [System.Collections.IDictionary]) {
        $ordered = [ordered]@{}
        foreach ($key in @($Value.Keys | Sort-Object)) { $ordered[$key] = ConvertTo-CanonicalValue $Value[$key] }
        return $ordered
    }
    if ($Value -is [pscustomobject]) {
        $ordered = [ordered]@{}
        foreach ($property in @($Value.PSObject.Properties.Name | Sort-Object)) {
            $ordered[$property] = ConvertTo-CanonicalValue $Value.$property
        }
        return $ordered
    }
    if ($Value -is [System.Collections.IEnumerable] -and $Value -isnot [string]) {
        # Prevent PowerShell from unrolling a one-item JSON array into an
        # object.  The frozen Python oracle hashes JSON arrays as arrays even
        # when they contain a single scripted turn.
        $items = @($Value | ForEach-Object { ConvertTo-CanonicalValue $_ })
        return ,$items
    }
    return $Value
}

function Get-CanonicalJsonSha256 {
    param([Parameter(Mandatory)]$Value)
    $canonical = ConvertTo-CanonicalValue $Value
    $json = $canonical | ConvertTo-Json -Depth 100 -Compress
    # Windows PowerShell 5.1 HTML-escapes these printable characters while
    # the frozen cross-runtime JSON contract does not. Normalize them before
    # hashing so Codex/Claude/CI agree on the same interaction bytes.
    $json = $json.Replace('\u0027', "'").Replace('\u003c', '<').Replace('\u003e', '>').Replace('\u0026', '&')
    return Get-TextSha256 $json
}

function Get-BundleSha256 {
    param([Parameter(Mandatory)][array]$Rows)
    $payload = ''
    foreach ($row in @($Rows | Sort-Object path)) {
        $payload += "{0}`0{1}`0{2}`n" -f $row.path, $row.sha256, $row.bytes
    }
    return Get-TextSha256 $payload
}

function Resolve-Runtime {
    param([Parameter(Mandatory)][string]$Name)
    if ($Name -eq 'codex') {
        $preferred = Join-Path $env:USERPROFILE '.codex\packages\standalone\releases\0.146.0-x86_64-pc-windows-msvc\bin\codex.exe'
        if (Test-Path -LiteralPath $preferred) { return (Resolve-Path -LiteralPath $preferred).Path }
    }
    if ($Name -eq 'claude') {
        $wingetRoot = Join-Path $env:LOCALAPPDATA 'Microsoft\WinGet\Packages'
        if (Test-Path -LiteralPath $wingetRoot) {
            $wingetClaude = Get-ChildItem -LiteralPath $wingetRoot -Filter 'claude.exe' -File -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($wingetClaude) { return $wingetClaude.FullName }
        }
    }
    $command = Get-Command $Name -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    return $null
}

function Invoke-LoggedProcess {
    param(
        [Parameter(Mandatory)][string]$Executable,
        [Parameter(Mandatory)][string[]]$Arguments,
        [Parameter(Mandatory)][string]$StdoutPath,
        [Parameter(Mandatory)][string]$StderrPath,
        [Parameter(Mandatory)][string]$WorkingDirectory,
        [Parameter(Mandatory)][int]$TimeoutSeconds
    )
    function Quote-WindowsArgument([string]$Value) {
        if ($Value -notmatch '[\s"]') { return $Value }
        $escaped = [regex]::Replace($Value, '(\\*)"', '$1$1\"')
        $escaped = [regex]::Replace($escaped, '(\\+)$', '$1$1')
        return '"' + $escaped + '"'
    }
    $argumentLine = (($Arguments | ForEach-Object { Quote-WindowsArgument ([string]$_) }) -join ' ')
    $stdinPath = Join-Path (Split-Path -Parent $StdoutPath) 'empty-stdin.txt'
    if (-not (Test-Path -LiteralPath $stdinPath)) {
        [IO.File]::WriteAllText($stdinPath, '', [Text.UTF8Encoding]::new($false))
    }
    $process = Start-Process -FilePath $Executable -ArgumentList $argumentLine `
        -WorkingDirectory $WorkingDirectory -NoNewWindow -PassThru `
        -RedirectStandardInput $stdinPath -RedirectStandardOutput $StdoutPath -RedirectStandardError $StderrPath
    $timedOut = $false
    $exitCode = 1
    try {
        if (-not $process.WaitForExit($TimeoutSeconds * 1000)) {
            try { $process.Kill() } catch {}
            $process.WaitForExit()
            $timedOut = $true
        }
        else {
            $process.WaitForExit()
            $process.Refresh()
            $exitCode = [int]$process.ExitCode
        }
    }
    finally { $process.Dispose() }
    if ($timedOut) {
        # Start-Process can release redirected file handles just after the
        # process handle is disposed on Windows. Retry the audit marker rather
        # than turning a controlled model timeout into an evaluator crash.
        $written = $false
        for ($attempt = 1; $attempt -le 20 -and -not $written; $attempt++) {
            try {
                [IO.File]::AppendAllText($StderrPath, "`nTIMEOUT after $TimeoutSeconds seconds`n", [Text.UTF8Encoding]::new($false))
                $written = $true
            }
            catch [IO.IOException] { Start-Sleep -Milliseconds 50 }
        }
        if (-not $written) { throw "Timed-out process released without a writable stderr audit file: $StderrPath" }
        return 124
    }
    return $exitCode
}

function Get-CodexThreadId {
    param([Parameter(Mandatory)][string]$EventsPath)
    foreach ($line in Get-Content -LiteralPath $EventsPath -Encoding utf8) {
        if (-not $line.Trim()) { continue }
        try { $row = $line | ConvertFrom-Json } catch { continue }
        foreach ($name in @('thread_id', 'threadId', 'session_id', 'sessionId')) {
            if ($row.PSObject.Properties.Name -contains $name -and $row.$name) { return [string]$row.$name }
        }
    }
    return $null
}

function Get-CodexEffectiveSandbox {
    param(
        [Parameter(Mandatory)][string]$ThreadId,
        [Parameter(Mandatory)][string]$ExpectedWorkspace
    )
    $sessionsRoot = Join-Path $env:USERPROFILE '.codex\sessions'
    $rollout = Get-ChildItem -LiteralPath $sessionsRoot -Recurse -File -Filter ("*{0}*.jsonl" -f $ThreadId) -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $rollout) { throw "Codex effective sandbox evidence was not found for thread $ThreadId." }
    $contexts = @()
    foreach ($line in Get-Content -LiteralPath $rollout.FullName -Encoding utf8) {
        if (-not $line.Trim()) { continue }
        try { $row = $line | ConvertFrom-Json } catch { continue }
        if ($row.type -eq 'turn_context') { $contexts += $row.payload }
    }
    if ($contexts.Count -eq 0) { throw "Codex rollout has no turn_context evidence for thread $ThreadId." }
    $expected = [IO.Path]::GetFullPath($ExpectedWorkspace).TrimEnd('\')
    $summaries = @()
    foreach ($context in $contexts) {
        $writes = @($context.permission_profile.file_system.entries | Where-Object access -eq 'write' | ForEach-Object {
            if ($_.path.type -eq 'path') { [IO.Path]::GetFullPath([string]$_.path.path).TrimEnd('\') }
        } | Where-Object { $_ })
        $summaries += [ordered]@{
            sandbox_type = [string]$context.sandbox_policy.type
            sandbox_network_access = [bool]$context.sandbox_policy.network_access
            permission_profile_type = [string]$context.permission_profile.type
            permission_network = [string]$context.permission_profile.network
            workspace_write = @($writes | Where-Object { $_.Equals($expected, [StringComparison]::OrdinalIgnoreCase) }).Count -gt 0
            cwd_matches_workspace = ([IO.Path]::GetFullPath([string]$context.cwd).TrimEnd('\')).Equals($expected, [StringComparison]::OrdinalIgnoreCase)
            approval_policy = [string]$context.approval_policy
        }
    }
    $distinct = @($summaries | ForEach-Object { $_ | ConvertTo-Json -Compress } | Sort-Object -Unique)
    if ($distinct.Count -ne 1) { throw "Codex effective sandbox changed during thread $ThreadId." }
    $summary = $summaries[0]
    return [ordered]@{
        sandbox_type = $summary.sandbox_type
        sandbox_network_access = $summary.sandbox_network_access
        permission_profile_type = $summary.permission_profile_type
        permission_network = $summary.permission_network
        workspace_write = $summary.workspace_write
        cwd_matches_workspace = $summary.cwd_matches_workspace
        approval_policy = $summary.approval_policy
        turn_context_count = $contexts.Count
        turn_context_sha256 = Get-CanonicalJsonSha256 $summaries
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $CaseRoot) { $CaseRoot = Join-Path $repoRoot 'cases\flagship\second-brain' }
$CaseRoot = (Resolve-Path -LiteralPath $CaseRoot).Path
if (-not $RunRoot) { $RunRoot = Join-Path $env:LOCALAPPDATA 'BoI-Wiki-Local-Evals' }
$runtimePath = Resolve-Runtime $Runtime
$runtimeReady = $null -ne $runtimePath
$authReady = $false
$runtimeVersion = ''
$codexWindowsSandboxWriteReady = $null
$codexWindowsSandboxProbeError = ''
if ($runtimeReady) {
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $runtimeVersion = (& $runtimePath --version 2>&1 | Select-Object -First 1).ToString().Trim()
    if ($Runtime -eq 'codex') {
        $authReady = ((& $runtimePath login status 2>&1 | Out-String) -match 'Logged in')
    }
    else {
        try {
            $status = (& $runtimePath auth status --json 2>$null | ConvertFrom-Json)
            $authReady = $status.loggedIn -eq $true
        }
        catch { $authReady = $false }
    }
    $ErrorActionPreference = $previousPreference
}

if ($Runtime -eq 'codex' -and $runtimeReady -and $env:OS -eq 'Windows_NT') {
    New-Item -ItemType Directory -Path $RunRoot -Force | Out-Null
    $probeDir = Join-Path $RunRoot ('sandbox-doctor-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $probeDir -Force | Out-Null
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $probeOutput = (& $runtimePath sandbox -P ':workspace' -C $probeDir -c 'windows.sandbox="unelevated"' powershell.exe -NoProfile -Command 'Set-Content -LiteralPath doctor.txt -Value OK -Encoding UTF8' 2>&1 | Out-String).Trim()
    $probeExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    $codexWindowsSandboxWriteReady = $probeExitCode -eq 0 -and (Test-Path -LiteralPath (Join-Path $probeDir 'doctor.txt'))
    if (-not $codexWindowsSandboxWriteReady) { $codexWindowsSandboxProbeError = $probeOutput }
    $resolvedRunRoot = [IO.Path]::GetFullPath($RunRoot).TrimEnd('\') + '\'
    $resolvedProbe = [IO.Path]::GetFullPath($probeDir).TrimEnd('\') + '\'
    if ($resolvedProbe.StartsWith($resolvedRunRoot, [StringComparison]::OrdinalIgnoreCase)) {
        Remove-Item -LiteralPath $probeDir -Recurse -Force
    }
}

$doctor = [ordered]@{
    schema = 'boi-local-case-eval-doctor/v1'
    windows_native = $env:OS -eq 'Windows_NT'
    runtime = $Runtime
    runtime_ready = $runtimeReady
    runtime_path = $runtimePath
    runtime_version = $runtimeVersion
    authenticated = $authReady
    codex_windows_sandbox_write_ready = $codexWindowsSandboxWriteReady
    codex_windows_sandbox_probe_error = $codexWindowsSandboxProbeError
    case_root = $CaseRoot
    synthetic_only = $true
    internal_bitbucket_required = $false
    production_evidence_created = $false
}
if ($Action -eq 'Doctor') {
    $doctor | ConvertTo-Json -Depth 20
    if (-not $doctor.windows_native -or -not $runtimeReady -or -not $authReady -or ($Runtime -eq 'codex' -and $codexWindowsSandboxWriteReady -ne $true)) { exit 2 }
    exit 0
}

if (-not $ConfirmSyntheticRun) { throw 'Run requires -ConfirmSyntheticRun. Only packaged synthetic fixtures are allowed.' }
if (-not $doctor.windows_native) { throw 'Reference evaluation requires Windows native PowerShell.' }
if (-not $runtimeReady) { throw "$Runtime runtime was not found." }
if (-not $authReady) { throw "$Runtime is not authenticated. Authenticate manually; this runner never opens or automates login UI." }
if (-not $ModelId) { throw 'Run requires an explicit -ModelId so the evidence does not guess the model.' }
if ($Runtime -eq 'codex' -and $CodexSandboxMode -eq 'danger-full-access' -and -not $ConfirmUnsandboxedSyntheticPilot) {
    throw 'danger-full-access is allowed only for a non-production synthetic pilot with -ConfirmUnsandboxedSyntheticPilot.'
}
if ($Runtime -eq 'codex' -and $CodexSandboxMode -eq 'workspace-write' -and $codexWindowsSandboxWriteReady -ne $true) {
    throw "Codex Windows workspace-write sandbox failed its write probe: $codexWindowsSandboxProbeError"
}

$catalogPath = Join-Path $CaseRoot 'evals\prompts\prompt-catalog.json'
$fixtureManifestPath = Join-Path $CaseRoot 'fixtures\manifest.json'
$seedCatalogPath = Join-Path $CaseRoot 'evals\seeds\seed-catalog.json'
$baselinePath = Join-Path $CaseRoot 'evals\baseline.md'
$catalog = Get-Content -Raw -Encoding utf8 $catalogPath | ConvertFrom-Json
$fixtureManifest = Get-Content -Raw -Encoding utf8 $fixtureManifestPath | ConvertFrom-Json
$seedCatalog = Get-Content -Raw -Encoding utf8 $seedCatalogPath | ConvertFrom-Json
$prompt = @($catalog.prompts | Where-Object prompt_id -eq $PromptId)
if ($prompt.Count -ne 1) { throw "Prompt not found or duplicated: $PromptId" }
$prompt = $prompt[0]
if ($fixtureManifest.synthetic -ne $true) { throw 'Fixture manifest is not synthetic.' }
$seed = @($seedCatalog.seeds | Where-Object seed_id -eq $prompt.seed_id)
if ($seed.Count -ne 1) { throw "Seed not found or duplicated: $($prompt.seed_id)" }
$seed = $seed[0]

# This execution envelope is identical for with-Harness and baseline arms. It
# describes the neutral Windows test environment, not a BoI capability.
$runtimeEnvelope = @'

[합성 평가 실행 환경]
- 셸 명령은 읽기, 검색, 해시, Git 상태 확인에만 사용하세요.
- PowerShell 텍스트는 `-Encoding UTF8`로 읽고, 셸 호출 하나에는 단순한 읽기 명령 하나만 사용하세요.
- 파일을 만들거나 고칠 때는 현재 AI 런타임의 기본 파일 편집 도구를 사용하세요.
- 작업은 현재 합성 평가 작업공간 안에서만 수행하세요.
'@
if ($Runtime -eq 'codex' -and $CodexSandboxMode -eq 'workspace-write') {
    $runtimeEnvelope += "`n- 기본 편집 도구가 Windows sandbox에서 거부될 때만 상대 경로와 `New-Item -ItemType Directory`, `Set-Content -Encoding UTF8`을 사용하세요. 삭제·이동·복사·절대 경로 쓰기는 금지합니다."
}
else {
    $runtimeEnvelope += "`n- PowerShell로 파일 쓰기, 이동, 삭제를 하지 마세요."
}
$effectiveTurns = @()
foreach ($turn in @($prompt.interaction.turns)) {
    $effectiveTurns += [pscustomobject][ordered]@{
        turn = [int]$turn.turn
        role = [string]$turn.role
        text = ([string]$turn.text + $runtimeEnvelope)
    }
}
$effectiveInteraction = [ordered]@{
    mode = [string]$prompt.interaction.mode
    turns = $effectiveTurns
}

$selected = @()
foreach ($row in $fixtureManifest.files) {
    $matched = $false
    foreach ($selector in $prompt.inputs) { if ([string]$row.path -like [string]$selector) { $matched = $true; break } }
    if ($matched) { $selected += $row }
}
if ($selected.Count -eq 0) { throw 'Prompt selected no fixture input.' }

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$runId = '{0}-{1}-{2}-r{3}-{4}' -f $Runtime, $Configuration, $PromptId, $Repetition, $stamp
$runDir = Join-Path $RunRoot $runId
if (Test-Path -LiteralPath $runDir) { throw "Run directory already exists: $runDir" }
$workspace = Join-Path $runDir 'workspace'
$control = Join-Path $runDir 'control'
New-Item -ItemType Directory -Path $workspace, $control -Force | Out-Null

$selectedRows = @()
foreach ($row in $selected) {
    $source = Join-Path (Join-Path $CaseRoot 'fixtures') ([string]$row.path -replace '/', '\')
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Fixture missing: $source" }
    $actual = Get-Sha256 $source
    if ($actual -ne [string]$row.sha256) { throw "Fixture hash mismatch: $($row.path)" }
    $destination = Join-Path $workspace ([string]$row.path -replace '/', '\')
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination
    $selectedRows += [pscustomobject][ordered]@{ path = [string]$row.path; sha256 = $actual; bytes = [int64](Get-Item -LiteralPath $source).Length }
}
$selectedBundleHash = Get-BundleSha256 $selectedRows
$selectedBytes = [int64](($selectedRows | Measure-Object -Property bytes -Sum).Sum)

$seedDir = Join-Path $CaseRoot ('evals\seeds\' + [string]$prompt.seed_id)
$seedManifestPath = Join-Path $seedDir 'manifest.json'
$seedManifest = Get-Content -Raw -Encoding utf8 $seedManifestPath | ConvertFrom-Json
$profileRoot = Join-Path $workspace 'data\boi\private\0000000'
foreach ($row in $seedManifest.files) {
    $source = Join-Path $seedDir ([string]$row.path -replace '/', '\')
    if ((Get-Sha256 $source) -ne [string]$row.sha256) { throw "Seed hash mismatch: $($row.path)" }
    $destination = Join-Path $profileRoot ([string]$row.path -replace '/', '\')
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Copy-Item -LiteralPath $source -Destination $destination
}

# Both comparison arms receive the same narrow read-only Windows runtime
# policy. File creation remains constrained to native edit tools inside the
# workspace-write sandbox; this policy grants no network, MCP, submit, or
# sandbox escape capability.
$ruleDir = Join-Path $workspace '.codex\rules'
New-Item -ItemType Directory -Path $ruleDir -Force | Out-Null
$evalRulePath = Join-Path $ruleDir 'synthetic-eval.rules'
$evalRuleFile = if ($Runtime -eq 'codex' -and $CodexSandboxMode -eq 'workspace-write') { 'codex-workspace-eval.rules' } else { 'codex-readonly-eval.rules' }
$evalRuleSource = Join-Path $repoRoot ('tools\ci\' + $evalRuleFile)
if (-not (Test-Path -LiteralPath $evalRuleSource -PathType Leaf)) { throw "Evaluation rule missing: $evalRuleSource" }
Copy-Item -LiteralPath $evalRuleSource -Destination $evalRulePath

if ($Configuration -eq 'with-harness') {
    New-Item -ItemType Directory -Path (Join-Path $workspace '.boi-harness'), (Join-Path $workspace 'data\boi'), (Join-Path $workspace 'templates') -Force | Out-Null
    Copy-Item -LiteralPath (Join-Path $repoRoot 'harness.lock') -Destination (Join-Path $workspace 'harness.lock')
    Copy-Item -LiteralPath (Join-Path $repoRoot '.boi-harness\package.json') -Destination (Join-Path $workspace '.boi-harness\package.json')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'data\boi\index.md') -Destination (Join-Path $workspace 'data\boi\index.md')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'templates\second-brain-preferences.example.json') -Destination (Join-Path $workspace 'templates\second-brain-preferences.example.json')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'templates\agent-memory-template.md') -Destination (Join-Path $workspace 'templates\agent-memory-template.md')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'templates\source-record-template.md') -Destination (Join-Path $workspace 'templates\source-record-template.md')
    Copy-Item -LiteralPath (Join-Path $repoRoot 'templates\source-folder-progress.example.json') -Destination (Join-Path $workspace 'templates\source-folder-progress.example.json')
    if ($Runtime -eq 'codex') {
        New-Item -ItemType Directory -Path (Join-Path $workspace '.agents\skills') -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $repoRoot 'AGENTS.md') -Destination (Join-Path $workspace 'AGENTS.md')
        Copy-Item -Recurse -LiteralPath (Join-Path $repoRoot '.agents\skills\boi-wiki-local') -Destination (Join-Path $workspace '.agents\skills')
        Copy-Item -Recurse -LiteralPath (Join-Path $repoRoot '.agents\skills\boi-second-brain') -Destination (Join-Path $workspace '.agents\skills')
    }
    else {
        New-Item -ItemType Directory -Path (Join-Path $workspace '.claude\skills') -Force | Out-Null
        Copy-Item -LiteralPath (Join-Path $repoRoot 'CLAUDE.md') -Destination (Join-Path $workspace 'CLAUDE.md')
        Copy-Item -Recurse -LiteralPath (Join-Path $repoRoot '.claude\skills\boi-wiki-local') -Destination (Join-Path $workspace '.claude\skills')
        Copy-Item -Recurse -LiteralPath (Join-Path $repoRoot '.claude\skills\boi-second-brain') -Destination (Join-Path $workspace '.claude\skills')
    }
}

Push-Location $workspace
try {
    & git init -q
    & git config user.email 'case-eval@example.invalid'
    & git config user.name 'BoI Case Eval'
    & git add .
    & git commit -qm 'synthetic evaluation seed'
    $workspaceCommit = (& git rev-parse HEAD).Trim()
}
finally { Pop-Location }

$started = (Get-Date).ToUniversalTime()
$threadId = $null
$turnEvidence = @()
$exitCode = 0
$turns = @($effectiveInteraction.turns)
$userRuleDir = Join-Path $env:USERPROFILE '.codex\rules'
New-Item -ItemType Directory -Path $userRuleDir -Force | Out-Null
foreach ($stale in Get-ChildItem -LiteralPath $userRuleDir -Filter 'boi-synthetic-eval-*.rules' -File -ErrorAction SilentlyContinue) {
    if ($stale.LastWriteTimeUtc -lt (Get-Date).ToUniversalTime().AddMinutes(-15)) {
        $pidMatch = [regex]::Match($stale.BaseName, '^boi-synthetic-eval-(\d+)-')
        $ownerAlive = $pidMatch.Success -and $null -ne (Get-Process -Id ([int]$pidMatch.Groups[1].Value) -ErrorAction SilentlyContinue)
        if (-not $ownerAlive) { Remove-Item -LiteralPath $stale.FullName -Force }
    }
}
$userRulePath = Join-Path $userRuleDir ('boi-synthetic-eval-{0}-{1}.rules' -f $PID, [guid]::NewGuid().ToString('N'))
Copy-Item -LiteralPath $evalRulePath -Destination $userRulePath
try {
for ($index = 0; $index -lt $turns.Count; $index++) {
    $turnNumber = $index + 1
    $stdout = Join-Path $control ("turn-{0:D2}-events.jsonl" -f $turnNumber)
    $stderr = Join-Path $control ("turn-{0:D2}-stderr.txt" -f $turnNumber)
    $lastMessage = Join-Path $control ("turn-{0:D2}-last-message.txt" -f $turnNumber)
    if ($Runtime -eq 'codex') {
        if ($turnNumber -eq 1) {
            $arguments = @('exec', '--cd', $workspace, '--sandbox', $CodexSandboxMode, '--ignore-user-config', '--skip-git-repo-check', '--json', '-o', $lastMessage, '--model', $ModelId, '-c', ('model_reasoning_effort="{0}"' -f $ReasoningSetting), '-c', 'approval_policy="never"')
            if ($CodexSandboxMode -eq 'workspace-write') { $arguments += @('-c', 'windows.sandbox="unelevated"') }
            $arguments += [string]$turns[$index].text
        }
        else {
            if (-not $threadId) { throw 'Codex did not emit a resumable thread id.' }
            $arguments = @('exec', 'resume', $threadId, '--ignore-user-config', '--skip-git-repo-check', '--json', '-o', $lastMessage, '--model', $ModelId, '-c', ('model_reasoning_effort="{0}"' -f $ReasoningSetting), '-c', 'approval_policy="never"', '-c', ('sandbox_mode="{0}"' -f $CodexSandboxMode))
            if ($CodexSandboxMode -eq 'workspace-write') { $arguments += @('-c', 'windows.sandbox="unelevated"') }
            $arguments += [string]$turns[$index].text
        }
        $exitCode = Invoke-LoggedProcess -Executable $runtimePath -Arguments $arguments -StdoutPath $stdout -StderrPath $stderr -WorkingDirectory $workspace -TimeoutSeconds $TurnTimeoutSeconds
        if ($turnNumber -eq 1) { $threadId = Get-CodexThreadId $stdout }
    }
    else {
        if ($turnNumber -eq 1) { $threadId = [guid]::NewGuid().ToString() }
        $arguments = @('--print', '--output-format', 'json', '--permission-mode', 'acceptEdits', '--tools', 'Read,Write,Edit,Glob,Grep', '--model', $ModelId, '--effort', $ReasoningSetting)
        if ($turnNumber -eq 1) { $arguments += @('--session-id', $threadId) } else { $arguments += @('--resume', $threadId) }
        $arguments += [string]$turns[$index].text
        $exitCode = Invoke-LoggedProcess -Executable $runtimePath -Arguments $arguments -StdoutPath $stdout -StderrPath $stderr -WorkingDirectory $workspace -TimeoutSeconds $TurnTimeoutSeconds
        if (Test-Path -LiteralPath $stdout) {
            try {
                $result = Get-Content -Raw -Encoding utf8 $stdout | ConvertFrom-Json
                [IO.File]::WriteAllText($lastMessage, [string]$result.result + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
            }
            catch { [IO.File]::WriteAllText($lastMessage, '', [Text.UTF8Encoding]::new($false)) }
        }
    }
    $turnChangedSources = @()
    foreach ($row in $selectedRows) {
        $turnSourcePath = Join-Path $workspace ($row.path -replace '/', '\')
        if (-not (Test-Path -LiteralPath $turnSourcePath) -or (Get-Sha256 $turnSourcePath) -ne $row.sha256) {
            $turnChangedSources += $row.path
        }
    }
    Push-Location $workspace
    try { $turnGitStatus = @(& git status --short) } finally { Pop-Location }
    $turnEvidence += [ordered]@{
        turn = $turnNumber
        exit_code = $exitCode
        events = Split-Path -Leaf $stdout
        stderr = Split-Path -Leaf $stderr
        last_message = Split-Path -Leaf $lastMessage
        workspace_status = $turnGitStatus
        changed_source_files = $turnChangedSources
        selected_input_manifest_unchanged = ($turnChangedSources.Count -eq 0)
    }
    if ($exitCode -ne 0) { break }
}
}
finally {
    if (Test-Path -LiteralPath $userRulePath) { Remove-Item -LiteralPath $userRulePath -Force }
}
$finished = (Get-Date).ToUniversalTime()
$effectiveSandbox = if ($Runtime -eq 'codex') { Get-CodexEffectiveSandbox -ThreadId $threadId -ExpectedWorkspace $workspace } else { $null }

$changedSources = @()
foreach ($row in $selectedRows) {
    $path = Join-Path $workspace ($row.path -replace '/', '\')
    if (-not (Test-Path -LiteralPath $path) -or (Get-Sha256 $path) -ne $row.sha256) { $changedSources += $row.path }
}
Push-Location $workspace
try { $gitStatus = @(& git status --short) } finally { Pop-Location }

$metadata = [ordered]@{
    schema = 'boi-local-case-execution-capture/v1'
    production_evidence = $false
    case_id = [string]$catalog.case_id
    protocol_revision = [string]$catalog.protocol_revision
    prompt_id = $PromptId
    runtime = $Runtime
    runtime_path = $runtimePath
    runtime_version = $runtimeVersion
    runtime_sha256 = Get-Sha256 $runtimePath
    model_id = $ModelId
    reasoning_setting = $ReasoningSetting
    configuration = $Configuration
    repetition = $Repetition
    started_at = $started.ToString('o')
    finished_at = $finished.ToString('o')
    duration_seconds = [math]::Round(($finished - $started).TotalSeconds, 3)
    workspace = $workspace
    workspace_commit = $workspaceCommit
    fixture_manifest_sha256 = Get-Sha256 $fixtureManifestPath
    seed_manifest_sha256 = Get-Sha256 $seedManifestPath
    user_prompt_sha256 = Get-TextSha256 ([string]$prompt.user_prompt)
    interaction_script_sha256 = Get-CanonicalJsonSha256 $prompt.interaction
    runtime_envelope_sha256 = Get-TextSha256 $runtimeEnvelope
    evaluated_interaction_sha256 = Get-CanonicalJsonSha256 $effectiveInteraction
    selected_input_manifest_sha256_before = $selectedBundleHash
    selected_input_manifest_sha256_after = if ($changedSources.Count -eq 0) { $selectedBundleHash } else { '' }
    selected_input_count = $selectedRows.Count
    selected_input_bytes = $selectedBytes
    changed_source_files = $changedSources
    model_context = [ordered]@{ provider = if ($Runtime -eq 'codex') { 'openai' } else { 'anthropic' }; runtime = $Runtime; synthetic_evaluation = $true; selected_input_bytes = $selectedBytes; data_classification = 'synthetic'; user_authorized_runtime_processing = $true }
    boi_remote_activity = [ordered]@{ mcp_tools_exposed = $false; submit_tools_exposed = $false; mcp_writes = 0; remote_submits = 0; boi_remote_source_bytes = 0 }
    runtime_policy_sha256 = Get-Sha256 $evalRulePath
    configured_sandbox_mode = if ($Runtime -eq 'codex') { $CodexSandboxMode } else { 'claude-acceptEdits' }
    effective_sandbox = $effectiveSandbox
    unsandboxed_synthetic_pilot = $Runtime -eq 'codex' -and $CodexSandboxMode -eq 'danger-full-access'
    temporary_user_rule_removed = -not (Test-Path -LiteralPath $userRulePath)
    turns = $turnEvidence
    thread_id = $threadId
    exit_code = $exitCode
    git_status = $gitStatus
}
Write-Utf8Json $metadata (Join-Path $control 'execution-capture.json')
$metadata | ConvertTo-Json -Depth 100
if ($exitCode -ne 0 -or $changedSources.Count -ne 0) { exit 1 }
