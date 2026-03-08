# Python War Economics Analysis

Analysis of the economic impact of war: economic resilience, poverty and food insecurity in conflict, black market and informality, and war costs vs reconstruction costs. Uses a Kaggle dataset and generates charts and summaries for each analysis.

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
.venv/bin/python main.py
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
│   ├── poverty_and_food_insecurity/
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

  ![GDP vs inflation](output/economic_resilience_hyperinflation/chart_scatter_gdp_vs_inflation.png)

  - **chart_hexbin_gdp_vs_inflation.png** — Density of observations (GDP vs inflation), hexbin.

  ![GDP vs inflation density](output/economic_resilience_hyperinflation/chart_hexbin_gdp_vs_inflation.png)

  - **chart_bar_inflation_threshold_by_gdp_bin.png** — GDP change bins vs share of observations with inflation >50%.

  ![Inflation threshold by GDP bin](output/economic_resilience_hyperinflation/chart_bar_inflation_threshold_by_gdp_bin.png)

- **Results:** Show the link between GDP decline and the frequency of high inflation; the steeper the GDP drop, the higher the share of cases above the inflation threshold.

---

### 2. Poverty and food insecurity in conflict  
*(poverty_and_food_insecurity)*

- **What we do:** We analyse which regions and conflict types show the highest extreme poverty and food insecurity (composite vulnerability: poverty rate, food insecurity, households falling into poverty). This identifies the most affected areas and conflict types in the data, not aid allocation.
- **Question:** Which regions and conflict types are associated with the highest extreme poverty and food insecurity?
- **Charts (in `output/poverty_and_food_insecurity/`):**
  1. **chart_food_insecurity_by_region.png** — Food insecurity by region.  
     Thesis: Which regions have the highest level of food insecurity?  
     **Result:** The highest level of food insecurity is in the Middle East; other regions show similar values.

  ![Food insecurity by region](output/poverty_and_food_insecurity/chart_food_insecurity_by_region.png)

  2. **chart_extreme_poverty_by_conflict_type.png** — Extreme poverty by conflict type.  
     Thesis: Which conflict type is associated with the highest extreme poverty?  
     **Result:** Extreme poverty is highest for Asymmetric war, followed by Civil war; other conflict types differ only slightly. A possible interpretation: asymmetric and civil wars often follow major armed conflicts, when the population is already severely depleted.

  ![Extreme poverty by conflict type](output/poverty_and_food_insecurity/chart_extreme_poverty_by_conflict_type.png)

  3. **chart_region_vulnerability_ranking.png** — Ranking of regions most affected by poverty and food insecurity (composite vulnerability index).  
     Thesis: Which regions are most affected (composite index: poverty, hunger, households in poverty)?  
     **Result:** The Middle East has a somewhat higher composite value; other regions are close. Poverty and hunger affect all regions to some degree during war.

  ![Region vulnerability ranking](output/poverty_and_food_insecurity/chart_region_vulnerability_ranking.png)

---

### 3. Black market and informal economy  
*(black_market_informal_economy)*

- **Question:** How does war affect informality and the black market? Is a larger GDP decline associated with a larger rise in informality?
- **Charts (in `output/black_market_informal_economy/`):**
  - **chart_scatter_gdp_vs_informality_growth.png** — Mean informality growth and mean GDP change by black market level.

  ![GDP vs informality growth](output/black_market_informal_economy/chart_scatter_gdp_vs_informality_growth.png)

  - **chart_bar_currency_gap_by_conflict_type.png** — Mean black-market currency gap (%) by conflict type.

  ![Currency gap by conflict type](output/black_market_informal_economy/chart_bar_currency_gap_by_conflict_type.png)

  - **chart_bar_informal_during_by_conflict_type.png** — Mean informal economy size during war (%) by conflict type.

  ![Informal economy by conflict type](output/black_market_informal_economy/chart_bar_informal_during_by_conflict_type.png)

  - **chart_black_market_level_by_region_and_period.png** — Black market level by region (older vs from 2010).

  ![Black market level by region and period](output/black_market_informal_economy/chart_black_market_level_by_region_and_period.png)

  - **chart_black_market_goods_and_inflation.png** — Frequency of goods on the black market and mean inflation.

  ![Black market goods and inflation](output/black_market_informal_economy/chart_black_market_goods_and_inflation.png)

- **Results:** Link between GDP decline and informality growth; differences across conflict types and regions; typical black-market goods and their relation to inflation (“Black Market Research”, war profiteering).

---

### 4. War costs vs reconstruction costs  
*(war_reconstruction_costs)*

- **Question:** When does reconstruction cost exceed war cost? How does the reconstruction-to-war ratio vary by conflict type? Are costs (war and reconstruction) higher in contemporary (from 2010) or older conflicts?
- **Charts (in `output/war_reconstruction_costs/`):**
  - **chart_bar_ratio_by_conflict_type.png** — Mean ratio (reconstruction cost / war cost) by conflict type (100% line = reconstruction equals war cost).

  ![Reconstruction-to-war cost ratio by conflict type](output/war_reconstruction_costs/chart_bar_ratio_by_conflict_type.png)

  - **chart_reconstruction_and_war_cost_contemporary_vs_old.png** — Mean reconstruction and war cost: contemporary (from 2010) vs older conflicts.

  ![Reconstruction and war cost: contemporary vs old](output/war_reconstruction_costs/chart_reconstruction_and_war_cost_contemporary_vs_old.png)

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
