@echo off
cd /d "%~dp0"
echo Starting PowerShell script...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-FaceVision.ps1"
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The script failed to run.
    pause
)
