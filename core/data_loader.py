"""Load and validate war economic impact dataset.
Used to standardize column names and ensure numeric data types."""
import pandas as pd
from pathlib import Path

from config.settings import WAR_ECONOMIC_CSV


def load_war_economic_data(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Load the war economic impact CSV into a DataFrame.
    Uses consistent column naming for GDP and conflict metadata.
    """
    path = csv_path or WAR_ECONOMIC_CSV
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)

    rename = {
        "GDP_Change_%": "gdp_change_pct",
        "Inflation_Rate_%": "inflation_rate_pct",
        "Currency_Devaluation_%": "currency_devaluation_pct",
        "Unemployment_Spike_Percentage_Points": "unemployment_spike_pp",
        "Extreme_Poverty_Rate_%": "extreme_poverty_rate_pct",
        "Food_Insecurity_Rate_%": "food_insecurity_rate_pct",
        "Households_Fallen_Into_Poverty_Estimate": "households_fallen_into_poverty",
        "Informal_Economy_Size_Pre_War_%": "informal_economy_pre_pct",
        "Informal_Economy_Size_During_War_%": "informal_economy_during_pct",
        "Currency_Black_Market_Rate_Gap_%": "currency_black_market_gap_pct",
    }
    rename = {k: v for k, v in rename.items() if k in df.columns}
    df = df.rename(columns=rename)

    numeric_cols = [
        "gdp_change_pct", "Start_Year", "End_Year",
        "inflation_rate_pct", "currency_devaluation_pct", "unemployment_spike_pp",
        "extreme_poverty_rate_pct", "food_insecurity_rate_pct", "households_fallen_into_poverty",
        "informal_economy_pre_pct", "informal_economy_during_pct", "currency_black_market_gap_pct",
        "Cost_of_War_USD", "Estimated_Reconstruction_Cost_USD",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
