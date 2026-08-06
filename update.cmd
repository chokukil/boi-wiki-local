@echo off
setlocal
cd /d "%~dp0"
set "APPLY_ARG="
set "GUIDE_ARG="

:parse
if "%~1"=="" goto run
if /i "%~1"=="--apply" (
  set "APPLY_ARG=-Apply"
  shift
  goto parse
)
if /i "%~1"=="--confirm-guide-release" (
  if "%~2"=="" (
    echo ERROR --confirm-guide-release requires a release value.
    exit /b 2
  )
  set "GUIDE_ARG=-ConfirmGuideRelease %~2"
  shift
  shift
  goto parse
)
echo ERROR unknown option: %~1
exit /b 2

:run
powershell.exe -NoLogo -NoProfile -ExecutionPolicy RemoteSigned -File "%~dp0update.ps1" -Root "%~dp0" %APPLY_ARG% %GUIDE_ARG%
exit /b %ERRORLEVEL%
