@echo off
setlocal
cd /d "%~dp0"

rem Backward-compatible automation path. Interactive users are delegated to
rem setup.cmd so every entry point uses the same three questions and preview.
if defined BOI_CONFIRM_INSTALL (
  if /i not "%BOI_CONFIRM_INSTALL%"=="INSTALL" exit /b 2
  if defined BOI_LOCAL_EMPLOYEE_ID (
    call "%~dp0setup.cmd" -EmployeeId "%BOI_LOCAL_EMPLOYEE_ID%" -Mode auto-curate -Approve
  ) else (
    call "%~dp0setup.cmd" -Mode auto-curate -Approve
  )
) else (
  call "%~dp0setup.cmd" %*
)
exit /b %ERRORLEVEL%
