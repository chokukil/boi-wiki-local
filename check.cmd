@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0check.ps1" -NativeOnly
exit /b %ERRORLEVEL%
