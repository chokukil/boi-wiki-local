@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (
  echo ERROR Python 3 is required for administrator validation.
  exit /b 1
)
if not defined BOI_LOCAL_EMPLOYEE_ID set /p BOI_LOCAL_EMPLOYEE_ID=Enter your numeric 7-digit employee ID:
python scripts\harness_sync.py verify --root . || exit /b 1
python scripts\boi_setup.py doctor --root . || exit /b 1
python scripts\boi_setup.py preview --root . || exit /b 1
set /p BOI_CONFIRM=Review the preview. Type INSTALL to create missing Local files:
if /i not "%BOI_CONFIRM%"=="INSTALL" exit /b 2
python scripts\boi_setup.py apply --root . || exit /b 1
python scripts\boi_setup.py verify --root . || exit /b 1
python scripts\boi_setup.py next-steps --root . || exit /b 1
