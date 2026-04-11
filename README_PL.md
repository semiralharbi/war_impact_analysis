# Python War Economics Analysis

Projekt analizy ekonomicznego wpływu wojen: **odporność gospodarcza / ryzyko hiperinflacji** oraz **czarny rynek i gospodarka nieformalna**, na bazie zbioru danych w stylu Kaggle. Generuje wykresy i podsumowania w konsoli oraz udostępnia **graficzny interfejs Streamlit** do przeglądania i odświeżania wykresów.

**→ [English version (README.md)](README.md)**

---

## Dataset

Wykorzystywany jest zbiór **War Economic & Livelihood Impact Dataset** (Likitha Gedipudi) z serwisu Kaggle:

- **Źródło:** [https://www.kaggle.com/datasets/likithagedipudi/war-economic-and-livelihood-impact-dataset](https://www.kaggle.com/datasets/likithagedipudi/war-economic-and-livelihood-impact-dataset)
- **Opis:** Zbiór na poziomie konfliktów (ok. 100 000 wierszy), od II wojny światowej po konflikty współczesne. Zawiera m.in. zmianę PKB, inflację, dewaluację waluty, skok bezrobocia, rozmiar gospodarki nieformalnej, aktywność czarnego rynku, koszty wojny, typ konfliktu i region.
- **Plik w projekcie:** Po pobraniu z Kaggle zapisz plik CSV jako `dataset/war_economic_impact_dataset.csv` (nazwy kolumn muszą odpowiadać tym używanym w kodzie, np. `Conflict_Type`, `GDP_Change_%`, `Inflation_Rate_%`, `Cost_of_War_USD`).

---

## Uruchomienie projektu (środowisko .venv)

### 1. Utworzenie i aktywacja wirtualnego środowiska

W katalogu projektu:

```bash
python3 -m venv .venv
```

Aktywacja:

- **macOS/Linux:** `source .venv/bin/activate`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

### 2. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 3. Umieszczenie danych

Pobierz dataset z Kaggle i umieść plik CSV w katalogu `dataset/` jako:

```
dataset/war_economic_impact_dataset.csv
```

### 4. Uruchomienie analiz

```bash
.venv/bin/python main.py
```

Skrypt ładuje dane, uruchamia **dwa** moduły analiz (`economic_resilience_hyperinflation`, `black_market_informal_economy`) i zapisuje wykresy w `output/<nazwa_analizy>/`. W konsoli pojawiają się krótkie podsumowania.

### 5. Przeglądarka wykresów (GUI, Streamlit)

Z **katalogu głównego projektu** (folder z `main.py` i `gui/`):

```bash
streamlit run gui/app.py
```

W przeglądarce możesz:

- wybrać podkatalog analizy w `output/` i podejrzeć każdy plik **PNG**;
- **pobrać** bieżący wykres;
- **wygenerować ponownie** wykresy dla jednej lub wszystkich zarejestrowanych analiz (opcjonalna ścieżka do CSV w panelu bocznym);
- **usunąć** plik wykresu w zakładce **Zarządzanie plikami** (po zaznaczeniu potwierdzenia).

Lista analiz dostępnych do regeneracji jest w `gui/services.py` (`ANALYSIS_MODULES`). Podkatalogi w `output/` bez wpisu w mapie nadal da się **przeglądać**, ale bez przycisku regeneracji z poziomu GUI.

---

## Struktura projektu

```
war_impact_analysis/
├── config/           # ścieżki, nazwa pliku CSV
├── core/             # ładowanie i normalizacja danych (data_loader.py)
├── utils/            # pomocnicze (np. zapis wykresów)
├── gui/              # aplikacja Streamlit (app.py, services.py)
├── analyses/         # moduły analiz (constants, charts, analysis, __init__)
│   ├── economic_resilience_hyperinflation/
│   └── black_market_informal_economy/
├── dataset/          # tu: war_economic_impact_dataset.csv
├── output/           # wygenerowane wykresy (podkatalogi per analiza)
├── main.py
├── requirements.txt
├── README.md         # wersja angielska
└── README_PL.md      # niniejszy plik (polski)
```

---

## Przeprowadzone analizy, wykresy i wyniki

### 1. Odporność gospodarcza i hiperinflacja  
*(economic_resilience_hyperinflation)*

- **Zakres:** Ryzyko wysokiej inflacji w zależności od spadku PKB; wykres liniowy pokazuje **udziały wg regionu**; wykres słupkowy agreguje cały zbiór.
- **Wykresy (w `output/economic_resilience_hyperinflation/`):**
  - **chart_scatter_gdp_vs_inflation.png** - Dla przedziałów zmiany PKB: odsetek obserwacji z inflacją powyżej ustawionego progu; **osobna linia na region** (nazwa pliku historyczna).
  - **chart_bar_inflation_threshold_by_gdp_bin.png** - Te same przedziały PKB, ogólny odsetek z inflacją > próg; linia kropkowana = średni udział w całym zbiorze.

  ![Ryzyko inflacji wg przedziału PKB](output/economic_resilience_hyperinflation/chart_bar_inflation_threshold_by_gdp_bin.png)

---

### 2. Czarny rynek i gospodarka nieformalna  
*(black_market_informal_economy)*

- **Zakres:** Nieformalność i czarny rynek wg regionu, długości konfliktu, kontekstu oraz towary vs inflacja (w tym panel z podziałem **wg regionu** w układzie 2×2).
- **Wykresy (w `output/black_market_informal_economy/`):**
  - **chart_scatter_gdp_vs_informality_growth.png** - Wzrost nieformalności i PKB wg poziomu aktywności czarnego rynku.
  - **chart_informal_pre_vs_during_by_region.png** - Udział nieformalności: przed wojną vs w trakcie, wg regionu (słupki min/max).
  - **chart_informality_growth_by_region.png** - Wzrost nieformalności (w trakcie − przed) wg regionu (min / max / średnia).
  - **chart_informality_growth_by_war_duration.png** - Ten sam wzrost w koszykach długości konfliktu.
  - **chart_black_market_level_by_region_and_period.png** - Poziom czarnego rynku wg regionu i okresu (podział przed / od 2010).
  - **chart_black_market_goods_and_inflation.png** - Częstość towarów i średnia inflacja: widoki globalne oraz **wg regionu** (słupki grupowane).

  ![Towary na czarnym rynku a inflacja](output/black_market_informal_economy/chart_black_market_goods_and_inflation.png)

---

## Zależności (requirements.txt)

- pandas ≥ 2.0  
- matplotlib ≥ 3.7  
- seaborn ≥ 0.12  
- numpy ≥ 1.24  
- streamlit ≥ 1.28 (GUI)

---

## Licencja danych

Dataset na Kaggle jest udostępniony na licencji **CC0: Public Domain**. Zastosowanie w tym projekcie jest zgodne z warunkami Kaggle i licencją zbioru.
