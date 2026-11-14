# Modelka mesiaca – spustenie hlasovania (cca 5 minút)

1. Na drive.google.com (účet, ktorý chceš používať pre HOTFOLK) daj **Nový → Google Tabuľky**. Pomenuj ju „HOTFOLK hlasovanie“.
2. V tabuľke otvor **Rozšírenia → Apps Script**. Zmaž, čo tam je, vlož celý obsah súboru `hlasovanie.gs` a ulož (ikona diskety).
3. Vpravo hore **Nasadiť → Nové nasadenie** → ozubené koliesko → **Webová aplikácia**.
   - Spustiť ako: **Ja**
   - Kto má prístup: **Ktokoľvek**
   - **Nasadiť** → povoľ prístup (ak Google napíše „aplikácia nie je overená“: Rozšírené → Prejsť na … (nebezpečné) – je to tvoj vlastný skript).
4. Skopíruj **URL webovej aplikácie** (končí na `/exec`) a pošli ju Claudovi – vloží ju do webu.

Hlasy sa zapisujú do hárka **Hlasy** (čas, kolo, modelka, meno, e-mail). Tabuľku nikomu nezdieľaj – sú v nej e-maily.

## Žrebovanie
V Apps Scripte vyber hore funkciu **vyzrebuj**, v kóde uprav `round` na aktuálne kolo (napr. `2026-11`) a klikni **Spustiť**. Výhercu uvidíš v **Záznam o vykonaní**.

## Nové kolo
Pošli Claudovi 3 fotky, mená a dátum konca kola. Skript ani tabuľku meniť netreba.
