$caseRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $caseRoot '..\..\..'))
& (Join-Path $repoRoot 'scripts\global_insight_case_baseline_check.ps1') -CaseRoot $caseRoot -CaseId 'scientific-foundation-model-knowledge' -FixtureId 'PUB-SFM-001-v1' -SourceCount 5
if (!$?) { exit 1 }
exit $LASTEXITCODE
