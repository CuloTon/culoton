@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo   BRAINROT - WYPLATA nagrod $BRT holderom
echo ============================================================
echo.
echo Co sie stanie:
echo   1. Pokaze plan (kto ile dostaje, kto rolowany).
echo   2. Zapyta o potwierdzenie (wpisz TAK).
echo   3. Poprosi o seed portfela DEV - wpisujesz go TUTAJ, lokalnie,
echo      input jest ukryty i NIGDZIE sie nie zapisuje.
echo   4. Wysle TON i wrzuci podsumowanie na Telegram.
echo.
echo Wyplata ruszy tylko jesli bank DEV ma min. 4 TON.
echo.
echo Instaluje biblioteke TON (jednorazowo, chwile to trwa)...
python -m pip install -q pytoniq
echo.
python scripts\rewards_payout.py --send
echo.
echo ------------------------------------------------------------
pause
