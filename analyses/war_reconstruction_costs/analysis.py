"""
Analiza: Koszty wojny vs koszty odbudowy — kiedy odbudowa przewyższa koszt wojny.
Pytanie: Jak stosunek Estimated_Reconstruction_Cost_USD do Cost_of_War_USD zależy od typu konfliktu,
czasu trwania i zniszczeń (np. spadku PKB)?
"""
from pathlib import Path

from core.data_loader import load_war_economic_data
from analyses.war_reconstruction_costs.charts import build_all_charts
from analyses.war_reconstruction_costs.constants import (
    COL_COST_OF_WAR,
    COL_RECONSTRUCTION_COST,
    COL_CONFLICT_TYPE,
)


def run(csv_path: Path | None = None) -> list[Path]:
    df = load_war_economic_data(csv_path)
    n = len(df)
    n_war = df[COL_COST_OF_WAR].notna().sum() if COL_COST_OF_WAR in df.columns else 0
    n_rec = df[COL_RECONSTRUCTION_COST].notna().sum() if COL_RECONSTRUCTION_COST in df.columns else 0
    print(f"\nDane (koszty wojny vs odbudowa): załadowano {n:,} wierszy (Cost_of_War: {n_war:,}, Reconstruction_Cost: {n_rec:,}).\n")

    paths = build_all_charts(df)

    if COL_COST_OF_WAR in df.columns and COL_RECONSTRUCTION_COST in df.columns and COL_CONFLICT_TYPE in df.columns:
        valid = df[(df[COL_COST_OF_WAR] > 0) & (df[COL_RECONSTRUCTION_COST] > 0)].copy()
        valid["ratio"] = valid[COL_RECONSTRUCTION_COST] / valid[COL_COST_OF_WAR]
        if not valid.empty:
            by_type = valid.groupby(COL_CONFLICT_TYPE)["ratio"].agg(["mean", "median", "count"]).round(3)
            by_type = by_type.sort_values("median", ascending=False)
            print("\n" + "=" * 60)
            print("ANALIZA: Koszty wojny vs koszty odbudowy")
            print("=" * 60)
            print("\nPytanie: Kiedy odbudowa przewyższa koszt wojny (ratio > 1)?")
            print("\nStosunek odbudowa/wojna wg typu konfliktu (średnia, mediana, N):")
            print(by_type.to_string())
            print("\nWygenerowane wykresy:")
            for p in paths:
                print("  -", p)
            print("=" * 60 + "\n")

    return paths
