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
- **Procházet** – volné učení po okruzích, popořadě podle PDF nebo náhodně.
- **Chyby** – otázky po chybě, dokud nejsou jednou jistě správně.

## Zdroj otázek

`build/data.js` a obrázky v `build/img/` jsou vygenerované z oficiálního souboru
testových otázek Ministerstva vnitra ČR (verze 15. 12. 2025), zveřejněného na
<https://mv.gov.cz/zbrojni-opravneni>. Správná odpověď je v PDF označena
kurzívou a šedým podbarvením; obě značky parser čte a u nesouladu hlásí
problém. Čísla otázek a stran odpovídají PDF, takže lze každou otázku dohledat.

Aplikace není oficiálním materiálem MV ČR ani Policie ČR. Při změně souboru
otázek data přegenerujte, viz níže.

## Spuštění

Otevřete `build/index.html` v prohlížeči, nebo složku `build/` nahrajte na
GitHub Pages (Settings → Pages → složka `/build` na větvi `main`). Na telefonu
pak Sdílet → Přidat na plochu.

## Přegenerování dat z nového PDF

```
pip install pdfplumber
python3 parse_pdf.py otazky.pdf questions.json build/img
python3 make_data.py questions.json build/data.js
```

Parser vypíše počty otázek po oddílech, počet obrázkových otázek a seznam
otázek, u kterých si označením správné odpovědi není jistý. Ty zkontrolujte
ručně v PDF.

## Licence

Kód: MIT. Texty otázek a obrázky pocházejí z dokumentu Ministerstva vnitra ČR a
jsou zde pouze pro účely přípravy na zkoušku.
