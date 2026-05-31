@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   BRAINROT - TEST PODPISU (wysyla 0.01 TON do siebie)
echo ============================================================
echo.
echo To sprawdza, czy seed steruje portfelem DEV i czy wysylka dziala,
echo ZANIM zrobisz pierwsza prawdziwa wyplate. Wysle tylko 0.01 TON
echo z powrotem na Twoj wlasny adres DEV.
echo.
echo Instaluje biblioteke TON (jednorazowo, chwile to trwa)...
python -m pip install -q pytoniq
echo.
python scripts\rewards_payout.py --test-self
echo.
pause
