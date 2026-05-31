@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   BRAINROT - stan nagrod $BRT (PODGLAD, bez klucza)
echo ============================================================
echo.
python scripts\rewards_snapshot.py
echo.
echo ------------------------------------------------------------
echo To byl tylko podglad - nic nie zostalo wyslane.
pause
