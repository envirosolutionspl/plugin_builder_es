# Plugin Builder EnviroSolutions

Generator szkieletów wtyczek QGIS z wyglądem zgodnym z pozostałymi wtyczkami EnviroSolutions
(nagłówek z ikoną, tytułem i wersją, karty z treścią, stopka z linkami i logo, motyw jasny i ciemny).

## Który szablon wybrać

**Tool button with dock widget (zalecany)** – domyślny wybór dla każdej nowej wtyczki.
Wtyczka otwiera się jako panel dokowany, tak jak ULDK, NMT, PhotoViewer360 i Pobieracz Danych GUGiK.
Nagłówek wtyczki jest paskiem tytułu panelu, przewija się tylko treść, nagłówek i stopka zostają na miejscu.
Stronę, po której pojawia się panel, wybiera się w kreatorze.

**Tool button with dialog** – tylko w szczególnych przypadkach. Wtyczka otwiera się jako osobne okno nad QGIS, które
wygląda jak wyjęty panel dokowany: bez systemowego paska tytułu, przesuwa się je za nagłówek wtyczki,
rozmiar zmienia za cienką ramkę dookoła. Różnica wobec panelu: nie da się go zadokować.

## Co dostaje wygenerowana wtyczka

- `ui/<modul>_dockwidget_base.ui` albo `ui/<modul>_dialog_base.ui` – formularz z arkuszem stylów
  dla obu motywów (selektory `[theme="light"]` / `[theme="dark"]`); kod tylko ustawia właściwość `theme`.
- Przykładowa karta „Parametry” (`QFrame` z `role="card"`) z polami i przyciskami
  „Wyczyść” / „Uruchom” (`role="primary"`) – do zastąpienia własną treścią.
- `utils.ThemeUtils` – wykrywanie motywu QGIS, logo i kolor linków w stopce, adres pomocy z `metadata.txt`.
- `images/` – wspólne ikony nagłówka (`help`, `close` + wersje `_dark`), strzałka list, logo ES (jasne i białe).
- `ui/qgis_feed.ui` – okno wyboru branży (QGIS Feed) w tym samym stylu.

Prefiks obrazków dla `url(...)` w arkuszach stylów (`QSS_IMAGES_PREFIX` w `__init__.py`) jest
tworzony z nazwy modułu, bo `QDir.addSearchPath` działa globalnie dla całego QGIS.

## Role w arkuszu stylów

| Właściwość | Element | Wygląd |
|---|---|---|
| `role="card"` | `QFrame` | ramka karty |
| `role="card-title"` | `QLabel` | pasek tytułu karty |
| `role="field-title"` | `QLabel` | pogrubiona etykieta pola |
| `role="hint"` | `QLabel` | mały szary opis |
| `role="primary"` | `QPushButton` | zielony przycisk głównej akcji (jeden na widok) |
