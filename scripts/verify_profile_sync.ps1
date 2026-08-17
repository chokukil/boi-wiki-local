# verify_profile_sync.ps1 — detect drift between the canonical harness repo and a
# Local Private profile repo. VERIFICATION ONLY: this script never rewrites files.
#
# Compared surfaces (files present in BOTH repos):
#   - scripts/*.py and scripts/*.ps1
#   - .agents/skills/boi-second-brain/** and .claude/skills/boi-second-brain/**
#     (the .agents and .claude copies are compared by path suffix, so each dot-root
#      is also verified against the other one)
#
# Exit codes: 0 = no drift, 2 = drift reported, 1 = usage/environment error.
#
# Examples:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/verify_profile_sync.ps1
#   powershell -NoProfile -File scripts/verify_profile_sync.ps1 -ProfileRoot C:\AI\second-brain-2055186
#   powershell -NoProfile -File scripts/verify_profile_sync.ps1 -Json

param(
  [string]$HarnessRoot,
  [string]$ProfileRoot,
  [switch]$Json
)

$ErrorActionPreference = "Stop"

if (-not $HarnessRoot) {
  $HarnessRoot = Split-Path -Parent $PSScriptRoot
}
$HarnessRoot = (Resolve-Path -LiteralPath $HarnessRoot).Path

function Get-FileSha256([string]$Path) {
  return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Get-SkillMap([string]$Root, [string]$Dot) {
  $base = Join-Path $Root "$Dot\skills\boi-second-brain"
  $map = @{}
  if (Test-Path -LiteralPath $base) {
    foreach ($file in Get-ChildItem -LiteralPath $base -Recurse -File) {
      $suffix = $file.FullName.Substring($base.Length + 1)
      $map[$suffix] = Get-FileSha256 $file.FullName
    }
  }
  return $map
}

function Compare-Maps([hashtable]$A, [hashtable]$B, [string]$Label) {
  $result = @{
    surface = $Label
    inSync = @()
    drift = @()
    onlyHarness = @()
    onlyProfile = @()
  }
  foreach ($key in ($A.Keys | Sort-Object)) {
    if (-not $B.Contains($key)) { $result.onlyHarness += $key; continue }
    if ($A[$key] -eq $B[$key]) { $result.inSync += $key } else {
      $result.drift += @{ file = $key; harnessSha = $A[$key]; profileSha = $B[$key] }
    }
  }
  foreach ($key in ($B.Keys | Sort-Object)) {
    if (-not $A.Contains($key)) { $result.onlyProfile += $key }
  }
  return $result
}

if (-not $ProfileRoot) {
  $parent = Split-Path -Parent $HarnessRoot
  $candidates = @(Get-ChildItem -LiteralPath $parent -Directory |
    Where-Object { $_.Name -like 'second-brain-*' -and (Test-Path -LiteralPath (Join-Path $_.FullName 'data\boi\private')) })
  if ($candidates.Count -eq 0) {
    Write-Host "ERROR no profile repo found next to harness ($parent); pass -ProfileRoot."
    exit 1
  }
  if ($candidates.Count -gt 1) {
    Write-Host "ERROR multiple profile repos found; pass -ProfileRoot explicitly:"
    foreach ($c in $candidates) { Write-Host "  $($c.FullName)" }
    exit 1
  }
  $ProfileRoot = $candidates[0].FullName
}
$ProfileRoot = (Resolve-Path -LiteralPath $ProfileRoot).Path

$scriptSurfaces = @("py", "ps1")
$report = @{
  harnessRoot = $HarnessRoot
  profileRoot = $ProfileRoot
  generatedAt = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
  mode = "verify-only"
  surfaces = @()
}

# scripts: compare per extension group so the surface label is meaningful
foreach ($ext in $scriptSurfaces) {
  $a = @{}
  $hScripts = Join-Path $HarnessRoot "scripts"
  if (Test-Path -LiteralPath $hScripts) {
    foreach ($file in Get-ChildItem -LiteralPath $hScripts -File -Filter "*.$ext") {
      $a[$file.Name] = Get-FileSha256 $file.FullName
    }
  }
  $b = @{}
  $pScripts = Join-Path $ProfileRoot "scripts"
  if (Test-Path -LiteralPath $pScripts) {
    foreach ($file in Get-ChildItem -LiteralPath $pScripts -File -Filter "*.$ext") {
      $b[$file.Name] = Get-FileSha256 $file.FullName
    }
  }
  $report.surfaces += Compare-Maps $a $b "scripts/*.$ext"
}

# skill dot-roots: harness .agents vs profile .agents, .claude vs .claude,
# plus intra-repo .agents vs .claude parity for both repos.
$skillPairs = @(
  @{ Name = "skills/boi-second-brain (.agents)"; A = (Get-SkillMap $HarnessRoot ".agents"); B = (Get-SkillMap $ProfileRoot ".agents") }
  @{ Name = "skills/boi-second-brain (.claude)"; A = (Get-SkillMap $HarnessRoot ".claude"); B = (Get-SkillMap $ProfileRoot ".claude") }
  @{ Name = "harness .agents vs .claude"; A = (Get-SkillMap $HarnessRoot ".agents"); B = (Get-SkillMap $HarnessRoot ".claude") }
  @{ Name = "profile .agents vs .claude"; A = (Get-SkillMap $ProfileRoot ".agents"); B = (Get-SkillMap $ProfileRoot ".claude") }
)
foreach ($pair in $skillPairs) {
  $report.surfaces += Compare-Maps $pair.A $pair.B $pair.Name
}

$report.driftCount = @($report.surfaces | ForEach-Object { @($_.drift).Count } | Measure-Object -Sum).Sum
$report.missingCount = @($report.surfaces | ForEach-Object { @($_.onlyHarness).Count + @($_.onlyProfile).Count } | Measure-Object -Sum).Sum
$report.ok = ($report.driftCount -eq 0 -and $report.missingCount -eq 0)

if ($Json) {
  $report | ConvertTo-Json -Depth 10
  exit $(if ($report.ok) { 0 } else { 2 })
}

Write-Host "harness: $HarnessRoot"
Write-Host "profile: $ProfileRoot"
Write-Host ""
foreach ($surface in $report.surfaces) {
  Write-Host ("{0} — inSync {1}, drift {2}, harness-only {3}, profile-only {4}" -f `
    $surface.surface, @($surface.inSync).Count, @($surface.drift).Count, @($surface.onlyHarness).Count, @($surface.onlyProfile).Count)
  foreach ($d in $surface.drift) {
    Write-Host ("  DRIFT {0}" -f $d.file)
    Write-Host ("    harness: {0}" -f $d.harnessSha)
    Write-Host ("    profile: {0}" -f $d.profileSha)
  }
  foreach ($f in $surface.onlyHarness) { Write-Host ("  harness-only  {0}" -f $f) }
  foreach ($f in $surface.onlyProfile) { Write-Host ("  profile-only  {0}" -f $f) }
}
Write-Host ""
if ($report.ok) {
  Write-Host "RESULT: in sync (drift 0)"
  exit 0
}
Write-Host ("RESULT: DRIFT — {0} drifted file(s), {1} missing on one side. Verification only; sync manually (harness is canonical)." -f $report.driftCount, $report.missingCount)
exit 2
