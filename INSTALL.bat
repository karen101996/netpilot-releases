@echo off
setlocal
title NetPilot Installer
cd /d "%~dp0"
echo ====================================
echo    NetPilot - One-click Installer
echo ====================================
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if errorlevel 1 (
  echo.
  echo Installation failed. Read the error above.
  pause
  exit /b 1
)
echo.
echo Installation complete. Open a NEW CMD and run: np help
pause
