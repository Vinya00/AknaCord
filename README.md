# Aknakereső Discord Bot

## Leírás
Ez a bot egy klasszikus **Aknakereső** játékot valósít meg Discordon.
A játék állását képként küldi a csatornára, és a parancsokat az **`!akna`** előtaggal kell kezdeni.

A bot képes:
- Új játék indítására előre definiált vagy egyedi mérettel
- Mezők ásására
- Zászlózásra / zászló levételére
- Játék befejezésére
- Segítség parancs megjelenítésére
- Üzenetek törlésére azonosító alapján

A játék közben a bot:
- Törli a parancsüzeneteket
- Törli a korábbi állásképet
- Csak az aktuális állásképet tartja meg
- A játékidőt nem méri
- A végső állás (nyerés vagy vereség) képe megmarad

---

## Követelmények

### Szoftver
- Python 3.10 vagy újabb
- Következő Python csomagok:
  - discord.py
  - Pillow
  - Flask

### Egyéb
- Discord bot token (lásd: https://discord.com/developers)
- Futtatási környezet: például Replit (https://replit.com/)
- Folyamatos működéshez UptimeRobot pingelés (https://uptimerobot.com/)

---

## Telepítés

1) Discord bot létrehozása
   - Nyisd meg a Discord Developer Portal-t: https://discord.com/developers/applications
   - Hozz létre egy App-ot, add hozzá a Bot-ot, másold ki a tokenjét
   - Engedélyezd a "MESSAGE CONTENT INTENT" opciót a botnál

2) Projekt importálása Replitbe
   - Hozz létre egy új Repl-t, vagy importáld a kódot GitHubból

3) Környezeti változó beállítása
   - Replit "Secrets" menüben add hozzá:
     DISCORD_TOKEN = a bot tokenje

4) Csomagok telepítése
   - Az ".replit" futtatáskor automatikusan kiadja: pip install -r requirements.txt
   - Ha szükséges, futtasd kézzel is a Shellben:
     pip install -r requirements.txt

5) Futtatás
   - A Replit a "Run" gombra indul
   - A keep_alive.py egy mini web szervert indít a pingekhez

6) UptimeRobot beállítása
   - Típus: HTTP(S) monitor
   - URL: a Replit által adott webcím (pl. https://sajat-repl.nev.repl.co/)
   - Intervallum: 5 perc

---

## Használat

Minden parancs " !akna " előtaggal indul.

### Új játék
```
!akna új könnyű
!akna új normális
!akna új nehéz
!akna új saját <x>x<y> <aknák>
```
Példa:
```
!akna új saját 10x12 20
```
(10 oszlop x 12 sor, 20 akna)

### Ásás
```
!akna ásás <x>x<y>
```
Példa:
```
!akna ásás 3x4
```
A koordináták 1-től indulnak (bal felső: 1x1).

### Jelölés (zászló)
```
!akna jelölés <x>x<y>
```
Megjelöli vagy leveszi a zászlót az adott mezőről.

### Befejezés
```
!akna befejezés
```
Felfedi a teljes táblát és lezárja a játékot. A kép megmarad.

### Segítség
```
!akna segítség
```
Kilistázza a parancsokat. Az üzenet rövid idő után törlődik.

### Üzenet törlése
```
!akna törlés <üzenetID>
```
Megpróbálja törölni a megadott üzenetet a csatornából (megfelelő jogosultság szükséges).

---

## Viselkedés és szabályok

- A koordináták 1-alapúak a felhasználónak (belsőleg 0-alapú).
- Üres mező ásásakor a kapcsolódó üres régiók automatikusan felfedődnek.
- Győzelem: minden nem aknás mező fel van fedve.
- Vereség: aknára lépsz (a felrobbant mező kiemelve jelenik meg).
- A bot törli a parancsüzeneteket és a korábbi állásképeket; a végső állás megmarad.
- Új játék indításakor a bot megpróbálja törölni a korábbi bot-üzeneteket, hogy csak az aktuális állás maradjon.

---

## Jogosultságok

- A botnak szüksége lehet ezekre a szerveren/csatornán:
  - Manage Messages (üzenetek törlése)
  - Attach Files (képek küldése)
  - Read Message History (opcionális, takarításhoz)

---

## Hibakeresés

- Ha a parancsokra nem reagál: ellenőrizd a MESSAGE CONTENT INTENT beállítást a Developer Portalon.
- Ha nem tud törölni üzenetet: ellenőrizd a bot jogosultságait és a csatorna beállításait.
- Ha nem jelenik meg kép: ellenőrizd, hogy a Pillow települt-e (requirements.txt).