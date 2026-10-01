@echo off
setlocal
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0..\Start-FaceVision.ps1" %*
if errorlevel 1 (
    echo.
    echo [ERROR] FaceVision failed to start.
    pause
)
