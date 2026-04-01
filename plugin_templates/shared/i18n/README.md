## Tłumaczenia

Stringi w wtyczce są opakowane w `tr()` poprzez `TranslationUtils.tr()` z `utils.py`.

## Jak dodać tłumaczenie

1. Wygeneruj plik `.ts`:
```
pylupdate5 *.py ui/*.ui -ts i18n/<nazwa_wtyczki>_<jezyk>.ts
```
Przykład:
```
pylupdate5 *.py ui/*.ui -ts i18n/moja_wtyczka_pl.ts
```

2. Przetłumacz w Qt Linguist:
- Otwórz `i18n/<nazwa_wtyczki>_<jezyk>.ts`
- Dla każdego stringa wpisz tłumaczenie
- Oznacz jako przetłumaczone (zielony ptaszek)
- Zapisz

3. Skompiluj `.ts` do `.qm`:
```
lrelease i18n/<nazwa_wtyczki>_<jezyk>.ts
```

Lub bezpośrednio w narzędziu `qt linguist`


4. Plik `.qm` musi znajdować się w folderze `i18n/` przy dystrybucji wtyczki.

## Uwagi
- `pylupdate5` i `lrelease` znajdują się w folderze instalacji QGIS, np.:
  `C:\Program Files\QGIS 3.x\bin\`
- Wtyczka automatycznie ładuje tłumaczenie na podstawie ustawień językowych QGIS