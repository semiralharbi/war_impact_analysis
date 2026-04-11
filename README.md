# Python War Economics Analysis

Analysis of the economic impact of war: **economic resilience / hyperinflation risk** and the **black market and informal economy**, using a Kaggle-style conflict dataset. The project generates charts and console summaries, and includes a **Streamlit GUI** to browse and refresh figures.

**→ [Polish version (README_PL.md)](README_PL.md)**

---

## Dataset

The project uses the **War Economic & Livelihood Impact Dataset** (Likitha Gedipudi) from Kaggle:

- **Source:** [https://www.kaggle.com/datasets/likithagedipudi/war-economic-and-livelihood-impact-dataset](https://www.kaggle.com/datasets/likithagedipudi/war-economic-and-livelihood-impact-dataset)
- **Description:** Conflict-level dataset (~100,000 rows), from World War II to recent conflicts. Includes GDP change, inflation, currency devaluation, unemployment spike, informal economy, black market activity, war costs, conflict type, and region.
- **In this project:** After downloading from Kaggle, save the CSV as `dataset/war_economic_impact_dataset.csv` (column names must match those used in the code, e.g. `Conflict_Type`, `GDP_Change_%`, `Inflation_Rate_%`, `Cost_of_War_USD`).

---

## Running the project (.venv)

### 1. Create and activate a virtual environment

In the project directory:

```bash
python3 -m venv .venv
```

Activate:

- **macOS/Linux:** `source .venv/bin/activate`
- **Windows (cmd):** `.venv\Scripts\activate.bat`
- **Windows (PowerShell):** `.venv\Scripts\Activate.ps1`

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the data file

Download the dataset from Kaggle and place the CSV in the `dataset/` folder as:

```
dataset/war_economic_impact_dataset.csv
```

### 4. Run the analyses

```bash
.venv/bin/python main.py
```

The script loads the data, runs **two** analysis modules (`economic_resilience_hyperinflation`, `black_market_informal_economy`), and saves charts under `output/<analysis_name>/`. The console prints short summaries.

### 5. Chart browser GUI (Streamlit)

From the **project root** (the folder that contains `main.py` and `gui/`):

```bash
streamlit run gui/app.py
```

In the browser you can:

- Pick an analysis subfolder under `output/` and preview each **PNG** chart.
- **Download** the current chart.
- **Regenerate** charts for one or all registered analyses (optional custom CSV path in the sidebar).
- **Delete** a chart file from the **Zarządzanie plikami** tab (with confirmation).

Registered analyses for regeneration are defined in `gui/services.py` (`ANALYSIS_MODULES`). Folders that exist only under `output/` can still be browsed even if they are not in that map.

---

## Project structure

```
war_impact_analysis/
├── config/           # paths, CSV filename
├── core/             # data loading and normalization (data_loader.py)
├── utils/            # helpers (e.g. saving figures)
├── gui/              # Streamlit app (app.py, services.py)
├── analyses/         # analysis modules (constants, charts, analysis, __init__)
│   ├── economic_resilience_hyperinflation/
│   └── black_market_informal_economy/
├── dataset/          # place war_economic_impact_dataset.csv here
├── output/           # generated charts (subfolder per analysis)
├── main.py
├── requirements.txt
├── README.md         # this file (English)
└── README_PL.md      # Polish version
```

---

## Analyses, charts, and results

### 1. Economic resilience and hyperinflation  
*(economic_resilience_hyperinflation)*

- **Focus:** Risk of high inflation vs GDP decline; line chart breaks out **shares by region**; bar chart aggregates over the full sample.
- **Charts (in `output/economic_resilience_hyperinflation/`):**
  - **chart_scatter_gdp_vs_inflation.png** - For each GDP-change bin, share of observations with inflation above the configured threshold; **one line per region** (filename kept for compatibility).
  - **chart_bar_inflation_threshold_by_gdp_bin.png** - Same bins, overall share with inflation > threshold; dotted line = dataset-wide average share.

  ![Inflation risk by GDP bin](output/economic_resilience_hyperinflation/chart_bar_inflation_threshold_by_gdp_bin.png)

---

### 2. Black market and informal economy  
*(black_market_informal_economy)*

- **Focus:** Informality and black-market patterns by region, war duration, conflict context, and goods vs inflation (including regional breakdowns in a 2×2 figure).
- **Charts (in `output/black_market_informal_economy/`):**
  - **chart_scatter_gdp_vs_informality_growth.png** - Informality growth and GDP vs black-market activity level.
  - **chart_informal_pre_vs_during_by_region.png** - Informal economy share: pre-war vs during war, by region (min/max bars).
  - **chart_informality_growth_by_region.png** - Growth in informality (during − pre) by region (min / max / mean).
  - **chart_informality_growth_by_war_duration.png** - Same growth metric by conflict-duration buckets.
  - **chart_black_market_level_by_region_and_period.png** - Black market level by region and period (pre/post 2010 split).
  - **chart_black_market_goods_and_inflation.png** - Global and **by-region** bar panels for goods frequency and mean inflation.

  ![Black market goods and inflation](output/black_market_informal_economy/chart_black_market_goods_and_inflation.png)

---

## Dependencies (requirements.txt)

- pandas ≥ 2.0  
- matplotlib ≥ 3.7  
- seaborn ≥ 0.12  
- numpy ≥ 1.24  
- streamlit ≥ 1.28 (for the GUI)

---

## Data licence

The Kaggle dataset is released under **CC0: Public Domain**. Use in this project is consistent with Kaggle terms and the dataset licence.
