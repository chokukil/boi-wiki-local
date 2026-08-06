@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0scripts\setup-native.ps1" %*
exit /b %ERRORLEVEL%
