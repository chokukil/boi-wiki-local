param(
  [string]$Root = $PSScriptRoot,
  [string]$EmployeeId = "",
  [ValidateSet("auto-curate", "suggest", "explicit-only", "")]
  [string]$Mode = "",
  [string]$Inbox = "",
  [string]$ConfirmInstall = ""
)

$Root = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Root)

$nativeSetup = Join-Path $Root "scripts/setup-native.ps1"
if (!(Test-Path -LiteralPath $nativeSetup)) {
  Write-Error "Windows 기본 설정 파일이 없습니다: scripts/setup-native.ps1"
  exit 1
}

$setupParameters = @{}
if ($EmployeeId) { $setupParameters.EmployeeId = $EmployeeId }
if ($Mode) { $setupParameters.Mode = $Mode }
if ($Inbox) { $setupParameters.Inbox = $Inbox }

# ConfirmInstall is retained only for existing managed automation. A normal
# interactive launch asks the canonical setup preview confirmation instead.
if ($ConfirmInstall) {
  if ($ConfirmInstall -cne "INSTALL") {
    Write-Host "설치를 취소했습니다. 설정 파일을 변경하지 않았습니다."
    exit 2
  }
  $setupParameters.Approve = $true
}

& $nativeSetup @setupParameters
exit $LASTEXITCODE
