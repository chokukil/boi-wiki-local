@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul || (echo ERROR Python 3 is required. & exit /b 1)
python scripts\pilot_acceptance.py %*
