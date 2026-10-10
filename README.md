# Zbroják 2026

Trenažér na teoretickou část zkoušky odborné způsobilosti pro zbrojní oprávnění
(zákon č. 90/2024 Sb., nařízení vlády č. 238/2025 Sb.). Jedna HTML stránka, bez
serveru, bez reklam, bez registrace. Funguje v telefonu i na počítači, pokrok se
ukládá v prohlížeči.

## Co umí

- **Dnešní dávka** – rozložené opakování. Otázka je naučená po jisté správné
  odpovědi ve třech různých dnech (successive relearning). Po správné odpovědi se
  vrací za 1, 2, 4 a 7 dní, po chybě za 10 minut a znovu zítra. Nové otázky se
  rozkládají do dnů zbývajících do zadaného data zkoušky, poslední dva dny
  zůstávají na opakování a testy.
- **Hádám** – odpověď označená jako hádání se nepočítá do naučených (confidence-
  based marking). Chyba s jistotou se zobrazí zvlášť (hypercorrection effect).
- **Skryté možnosti** – volitelně se nejdřív zobrazí jen otázka, možnosti až na
  klepnutí (vybavení před výběrem; snižuje učení chybných distraktorů).
- **Test nanečisto** – 30 otázek ve skladbě zkoušky (17 právo, 10 nauka vč.
  bezpečného nakládání, 3 zdravotnické minimum), odpočet 40 minut, vyhodnocení
  s hranicí 26 (obecné) a 28 (rozšířené) správných odpovědí.
- **Vysvětlení** – pod každou odhalenou odpovědí je, proč je správná, v čem
  jsou ostatní možnosti chybné, pramen (paragraf, nařízení) a pomůcka na
  zapamatování. Vysvětlení nejsou součástí souboru MV a kde si nejsou jistá
  číslem nebo paragrafem, upozorní na to.
- **Slovníček** – 119 pojmů z nauky, práva, střelnice a první pomoci, s
  anglickým ekvivalentem a u klíčových pojmů se schématem (náboj, zápal,
  vývrt, mířidla, části pistole, střelnice). Pojmy jsou podtržené přímo
  v otázkách, klepnutím se otevře vysvětlení.
- **Učení** – volné procházení po okruzích, popořadě podle PDF nebo náhodně;
  **Chyby** – otázky po chybě, dokud nejsou jednou jistě správně.
- **Praxe** – postupy praktické části podle přílohy č. 2 k NV č. 238/2025 Sb.
  (kontrola pistole, revolveru, samonabíjecí a opakovací pušky, selhač, slabá
  rána, zádržka, čištění, průběh střelby) a zásady, které platí pořád. Režim
  „seřadit kroky“: zamíchané kroky klepáte ve správném pořadí; postup je
  naučený po dvou bezchybných dnech.
- **Obecné / rozšířené oprávnění** – volba v nastavení přepíná hranice
  (26 nebo 28 z 30, 6 nebo 8 zásahů z 10) ve výsledcích i textech.
- **Tempo** – přehled ukazuje průměr nových otázek za posledních 7 dní a za
  kolik dní tímto tempem dojdou; denní cíl se přepočítává každý den.
- **Připomínka** – stažení souboru .ics s denní událostí a upozorněním až do
  dne zkoušky (stránka bez serveru sama upozornění poslat neumí).
- **Offline** – service worker uloží stránku, otázky i obrázky; po prvním
  otevření funguje bez připojení, nová verze se stáhne při dalším připojení.
- **Synchronizace** – pokrok se ukládá pod náhodným tajným klíčem do Firestore
  a mezi zařízeními se slučuje (u každé otázky vyhrává novější stav).

## Zdroj otázek

`docs/data.js` a obrázky v `docs/img/` jsou vygenerované z oficiálního souboru
testových otázek Ministerstva vnitra ČR (verze 15. 12. 2025), zveřejněného na
<https://mv.gov.cz/zbrojni-opravneni>. Správná odpověď je v PDF označena
kurzívou a šedým podbarvením; obě značky parser čte a u nesouladu hlásí
problém. Čísla otázek a stran odpovídají PDF, takže lze každou otázku dohledat.

Vysvětlení, slovníček a postupy praktické části vznikly jako doplněk a nejsou
součástí oficiálního souboru; správná odpověď je vždy ta z PDF.

Aplikace není oficiálním materiálem MV ČR ani Policie ČR. Při změně souboru
otázek data přegenerujte, viz níže.

## Spuštění

Aplikace běží na <https://zbrojak-2026.github.io/>.

Otevřete `docs/index.html` v prohlížeči, nebo složku `docs/` nahrajte na
GitHub Pages (Settings → Pages → složka `/docs` na větvi `main`). Na telefonu
pak Sdílet → Přidat na plochu.

## Když MV vydá nový soubor otázek

Workflow `.github/workflows/check-mv.yml` jednou týdně stáhne PDF z mv.gov.cz,
porovná jeho otisk s `tools/mv-pdf.sha256` a při změně založí issue (lze
spustit i ručně v záložce Actions). Pak:

```
pip install pdfplumber
python3 parse_pdf.py otazky.pdf data/questions_new.json docs/img
python3 compare_questions.py data/questions.json data/questions_new.json
```

`compare_questions.py` vypíše přidané, odebrané a změněné otázky (znění,
odpovědi, přehozená správná odpověď, obrázek) a kolik vysvětlení je potřeba
napsat nebo zkontrolovat. Doplňte je do `data/explanations.json` (klíč je
číslo otázky, hodnoty `why`, `ref`, `hint`, `verify`), přejmenujte
`questions_new.json` na `questions.json` a vygenerujte data:

```
python3 make_data.py data/questions.json docs/data.js \
  --expl data/explanations.json --glossary data/glossary.json --practical data/practical.json
```

Nakonec v `docs/sw.js` změňte `VERSION` na nový řetězec (aby se u uživatelů
obnovila offline paměť) a zapište nový otisk PDF do `tools/mv-pdf.sha256`
(`sha256sum otazky.pdf`).

Parser vypíše počty otázek po oddílech, počet obrázkových otázek a seznam
otázek, u kterých si označením správné odpovědi není jistý. Ty zkontrolujte
ručně v PDF.

## Soubory

- `docs/` – publikovaná stránka (GitHub Pages): `index.html`, `data.js`,
  `sw.js`, `img/`, ikony
- `data/` – zdrojová data: `questions.json` (z PDF), `explanations.json`,
  `glossary.json`, `practical.json`
- `parse_pdf.py`, `make_data.py`, `compare_questions.py` – nástroje
- `tools/mv-pdf.sha256` – otisk naposledy zpracovaného PDF

## Licence

Kód: MIT. Texty otázek a obrázky pocházejí z dokumentu Ministerstva vnitra ČR a
jsou zde pouze pro účely přípravy na zkoušku.
