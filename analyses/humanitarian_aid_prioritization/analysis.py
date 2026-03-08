"""
Analiza: Regiony i typy konfliktów najbardziej dotknięte ubóstwem i brakiem bezpieczeństwa żywnościowego.
Pytanie: Które typy konfliktów i regiony w danych łączą się z najwyższym wskaźnikiem
skrajnego ubóstwa i braku bezpieczeństwa żywnościowego?
"""
from pathlib import Path

from core.data_loader import load_war_economic_data
from analyses.humanitarian_aid_prioritization.charts import build_all_charts
from analyses.humanitarian_aid_prioritization.constants import (
    COL_EXTREME_POVERTY,
    COL_FOOD_INSECURITY,
    COL_REGION,
    COL_CONFLICT_TYPE,
)


def run(csv_path: Path | None = None) -> list[Path]:
    df = load_war_economic_data(csv_path)
    n = len(df)
    n_pov = df[COL_EXTREME_POVERTY].notna().sum() if COL_EXTREME_POVERTY in df.columns else 0
    n_food = df[COL_FOOD_INSECURITY].notna().sum() if COL_FOOD_INSECURITY in df.columns else 0
    print(f"\nDane (pomoc humanitarna): załadowano {n:,} wierszy (ubóstwo skrajne: {n_pov:,}, brak bezpieczeństwa żywnościowego: {n_food:,}).\n")

    paths = build_all_charts(df)

    if COL_EXTREME_POVERTY in df.columns and COL_FOOD_INSECURITY in df.columns and COL_REGION in df.columns and COL_CONFLICT_TYPE in df.columns:
        by_region = df.groupby(COL_REGION)[[COL_EXTREME_POVERTY, COL_FOOD_INSECURITY]].mean().round(2).sort_values(COL_FOOD_INSECURITY, ascending=False)
        by_type = df.groupby(COL_CONFLICT_TYPE)[[COL_EXTREME_POVERTY, COL_FOOD_INSECURITY]].mean().round(2).sort_values(COL_FOOD_INSECURITY, ascending=False)
        print("\n" + "=" * 60)
        print("ANALIZA: Regiony i typy konfliktów najbardziej dotknięte ubóstwem i brakiem bezpieczeństwa żywnościowego")
        print("=" * 60)
        print("\nPytanie: Które regiony i typy konfliktów w danych są najbardziej dotknięte ubóstwem i brakiem bezpieczeństwa żywnościowego?")
        print("\nŚrednie wg regionu (skrajne ubóstwo %, brak bezpieczeństwa żywnościowego %):")
        print(by_region.to_string())
        print("\nŚrednie wg typu konfliktu:")
        print(by_type.to_string())
        print("\nWygenerowane wykresy:")
        for p in paths:
            print("  -", p)
        print("=" * 60 + "\n")

    return paths
