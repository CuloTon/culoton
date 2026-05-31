BRAINROT — system nagród $BRT (TON dla holderów)
=================================================

ZASADA
------
- Bank nagród = adres DEV: UQBzaZXIwj3mDY8HdYDkTO1lkn4OV8sfx2tsf-lChQex70NP
  (tam wpływają opłaty z launchpada + tax z $BRT).
- Jedna runda rozdaje 25% salda banku w momencie wypłaty.
- Dzielone pro-rata wg ilości $BRT (wykluczeni: LP DeDust, DEV, burn, kontrakty).
- Wypłata rusza TYLKO gdy bank >= 4 TON (pula >= 1 TON).
- Holder ze udziałem < 0,05 TON jest pomijany i ROLUJE się do następnej rundy
  (nic nie przepada — kumuluje się, aż przekroczy 0,05 TON).
- Holder dostaje pełny udział; gaz sieciowy płaci projekt.
- Ty wybierasz moment wypłaty (gdy uznasz, że saldo jest OK).

PLIKI DO KLIKNIĘCIA (w tym folderze)
------------------------------------
1) sprawdz-nagrody.bat   — PODGLĄD (bez klucza). Pokazuje bank, pulę 25%,
                           kto ile dostanie, kto rolowany. Klikaj kiedy chcesz.

2) test-podpisu.bat      — JEDNORAZOWY TEST przed pierwszą wypłatą. Wyśle 0,01 TON
                           z DEV z powrotem na DEV, żeby sprawdzić, że seed steruje
                           portfelem i wysyłka działa. Bezpieczne.

3) wyplata-nagrod.bat    — WYPŁATA. Klikasz gdy bank >= 4 TON. Pokaże plan,
                           zapyta "TAK", poprosi o seed (wpisujesz lokalnie,
                           ukryty, nigdzie się nie zapisuje), wyśle TON i wrzuci
                           podsumowanie na Telegram (kto dostał / kto rolowany).

BEZPIECZEŃSTWO
--------------
- Seed (24 słowa) wpisujesz TYLKO w czarne okno tych plików, na swoim kompie.
- NIGDY nie wpisuj seeda w czacie z Claude ani nigdzie online.
- Podgląd (sprawdz-nagrody) możesz też zlecić Claude — wypłaty NIGDY.

PIERWSZE UŻYCIE
---------------
1. Poczekaj aż bank (widoczny na https://brainrot-ton.fun/rewards) przebije 4 TON.
2. Kliknij test-podpisu.bat — potwierdź, że 0,01 TON wróciło.
3. Kliknij wyplata-nagrod.bat — zrób pierwszą realną rundę.

(Pod spodem: Python + biblioteka pytoniq, instalowana automatycznie przy
pierwszym uruchomieniu wypłaty. Skrypty: scripts/rewards_snapshot.py,
scripts/rewards_payout.py.)
