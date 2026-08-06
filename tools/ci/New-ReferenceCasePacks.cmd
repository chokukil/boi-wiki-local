@echo off
setlocal
set "SCRIPT=%~dp0New-ReferenceCasePacks.ps1"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$code=Get-Content -LiteralPath '%SCRIPT%' -Raw -Encoding UTF8; & ([scriptblock]::Create($code)) -Root (Resolve-Path '%~dp0..\..').Path"
exit /b %ERRORLEVEL%
