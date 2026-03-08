# Python War Economics Analysis

Analysis of the economic impact of war: economic resilience, humanitarian aid prioritization, black market and informality, and war costs vs reconstruction costs. Uses a Kaggle dataset and generates charts and summaries for each analysis.

**→ [Polska wersja (README.md)](README.md)**

---

## Dataset

The project uses the **War Economic & Livelihood Impact Dataset** (Likitha Gedipudi) from Kaggle:

- **Source:** [https://www.kaggle.com/datasets/likithagedipudi/war-economic-and-livelihood-impact-dataset](https://www.kaggle.com/datasets/likithagedipudi/war-economic-and-livelihood-impact-dataset)
- **Description:** Conflict-level dataset (~100,000 rows), from World War II to recent conflicts. Includes GDP change, inflation, extreme poverty, food insecurity, informal economy size, black market activity, war costs and estimated reconstruction costs, conflict type, and region.
- **In this project:** After downloading from Kaggle, save the CSV as `dataset/war_economic_impact_dataset.csv` (column names must match those used in the code, e.g. `Conflict_Type`, `GDP_Change_%`, `Inflation_Rate_%`, `Cost_of_War_USD`, `Estimated_Reconstruction_Cost_USD`).

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
python main.py
```

The script loads the data, runs all four analysis modules in sequence, and saves charts under `output/<analysis_name>/`. The console prints short summaries (observation counts, generated files, selected statistics).

---

## Project structure

```
Python_War_Economics_Analysis/
├── config/           # paths, CSV filename
├── core/             # data loading and normalization (data_loader.py)
├── utils/            # helpers (e.g. saving figures)
├── analyses/        # analysis modules (each: constants, charts, analysis, __init__)
│   ├── economic_resilience_hyperinflation/
│   ├── humanitarian_aid_prioritization/
│   ├── black_market_informal_economy/
│   └── war_reconstruction_costs/
├── dataset/         # place war_economic_impact_dataset.csv here
├── output/          # generated charts (subfolder per analysis)
├── main.py
├── requirements.txt
├── README.md          # Polish version
└── README_EN.md       # English version
```

---

## Analyses, charts, and results

### 1. Economic resilience and hyperinflation  
*(economic_resilience_hyperinflation)*

- **Question:** At what level of GDP decline does the risk of high inflation (e.g. >50%) increase?
- **Charts (in `output/economic_resilience_hyperinflation/`):**
  - **chart_scatter_gdp_vs_inflation.png** — GDP change vs inflation, coloured by conflict type; 50% threshold line.
  - **chart_hexbin_gdp_vs_inflation.png** — Density of observations (GDP vs inflation), hexbin.
  - **chart_bar_inflation_threshold_by_gdp_bin.png** — GDP change bins vs share of observations with inflation >50%.
- **Results:** Show the link between GDP decline and the frequency of high inflation; the steeper the GDP drop, the higher the share of cases above the inflation threshold.

---

### 2. Humanitarian aid prioritization  
*(humanitarian_aid_prioritization)*

- **Question:** Which regions and conflict types are associated with the highest extreme poverty and food insecurity?
- **Charts (in `output/humanitarian_aid_prioritization/`):**
  1. **chart_boxplot_food_insecurity_by_region.png**  
     **Food insecurity by region.**  
     Thesis: Which regions have the highest level of food insecurity?  
     **Result:** The highest level of food insecurity is in the Middle East; other regions show similar values.
  2. **chart_boxplot_extreme_poverty_by_conflict_type.png**  
     **Extreme poverty by conflict type.**  
     Thesis: Which conflict type is associated with the highest extreme poverty?  
     **Result:** Extreme poverty is highest for Asymmetric war, followed by Civil war; other conflict types differ only slightly. A possible interpretation: asymmetric and civil wars often follow major armed conflicts, when the population is already severely depleted.
  3. **chart_bar_region_ranking.png**  
     **Ranking of regions most affected by poverty and food insecurity.**  
     Thesis: Which regions are most affected (composite index: poverty, hunger, households in poverty)?  
     **Result:** The Middle East has a somewhat higher composite value; other regions are close. Poverty and hunger affect all regions to some degree during war.

---

### 3. Black market and informal economy  
*(black_market_informal_economy)*

- **Question:** How does war affect informality and the black market? Is a larger GDP decline associated with a larger rise in informality?
- **Charts (in `output/black_market_informal_economy/`):**
  - **chart_scatter_gdp_vs_informality_growth.png** — Two bar charts: mean informality growth (During − Pre) and mean GDP change by black market level (Low/Moderate/High/Dominant).
  - **chart_bar_currency_gap_by_conflict_type.png** — Mean black-market currency gap (%) by conflict type.
  - **chart_bar_informal_during_by_conflict_type.png** — Mean informal economy size during war (%) by conflict type.
  - **chart_black_market_level_by_region_and_period.png** — (1) Distribution of black market level by region (stacked bars); (2) Mean black market level by region: older conflicts (pre-2010) vs from 2010.
  - **chart_black_market_goods_and_inflation.png** — (1) Frequency of goods on the black market (%); (2) Mean inflation when trading a given good.
- **Results:** Link between GDP decline and informality growth; differences across conflict types and regions; typical black-market goods and their relation to inflation (“Black Market Research”, war profiteering).

---

### 4. War costs vs reconstruction costs  
*(war_reconstruction_costs)*

- **Question:** When does reconstruction cost exceed war cost? How does the reconstruction-to-war ratio vary by conflict type? Are costs (war and reconstruction) higher in contemporary (from 2010) or older conflicts?
- **Charts (in `output/war_reconstruction_costs/`):**
  - **chart_bar_ratio_by_conflict_type.png** — Mean ratio (reconstruction cost / war cost) by conflict type (100% line = reconstruction equals war cost).
  - **chart_reconstruction_and_war_cost_contemporary_vs_old.png** — Two bar charts: (1) Mean reconstruction cost as % of older wars (older = 100%); (2) Mean war cost as % of older wars (older = 100%). Comparison of conflicts from 2010 vs before 2010.
- **Results:** Which conflict types have ratio > 1 (reconstruction more expensive than war); whether contemporary conflicts (from 2010) show higher or lower relative costs (“reconstruction costs”, long-term fiscal burden).

---

## Dependencies (requirements.txt)

- pandas ≥ 2.0
- matplotlib ≥ 3.7
- seaborn ≥ 0.12
- numpy ≥ 1.24

---

## Data licence

The Kaggle dataset is released under **CC0: Public Domain**. Use in this project is consistent with Kaggle terms and the dataset licence.
