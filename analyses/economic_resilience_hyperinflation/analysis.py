"""
Analiza: Economic resilience - punkt przełamania (tipping point): przy jakiej intensywności
konfliktu rośnie ryzyko hiperinflacji lub skrajnej dewaluacji; powiązanie ze spadkiem PKB.
"""
from pathlib import Path

from core.data_loader import load_war_economic_data
from analyses.economic_resilience_hyperinflation.charts import build_all_charts

from analyses.economic_resilience_hyperinflation.constants import (
    COL_GDP,
    COL_INFLATION,
    COL_DEVAL,
    INFLATION_HIGH_THRESHOLD_PCT,
    HYPERINFLATION_THRESHOLD_PCT,
    SEVERE_DEVALUATION_THRESHOLD_PCT,
)


def run(csv_path: Path | None = None) -> list[Path]:
    df = load_war_economic_data(csv_path)
    n_total = len(df)
    n_with_inflation = df[COL_INFLATION].notna().sum() if COL_INFLATION in df.columns else 0
    n_with_gdp = df[COL_GDP].notna().sum() if COL_GDP in df.columns else 0
    print(f"\nDane: załadowano {n_total:,} wierszy (PKB: {n_with_gdp:,}, Inflacja: {n_with_inflation:,}).\n")

    paths = build_all_charts(df)

    plot_df = df[[COL_GDP, COL_INFLATION]].dropna(how="any")
    if not plot_df.empty:
        corr = plot_df[COL_GDP].corr(plot_df[COL_INFLATION])
        pct_high = (plot_df[COL_INFLATION] > INFLATION_HIGH_THRESHOLD_PCT).mean() * 100
        print("\n" + "=" * 60)
        print("ANALIZA: Odporność gospodarcza / ryzyko hiperinflacji")
        print("=" * 60)
        print(
            "\nPytanie (tipping point): przy jakiej intensywności konfliktu rośnie udział "
            "hiperinflacji lub skrajnej dewaluacji?"
        )
        print(f"\nKorelacja (zmiana PKB vs inflacja): {corr:.3f}")
        print(f"Odsetek obserwacji z inflacją > {INFLATION_HIGH_THRESHOLD_PCT}%: {pct_high:.1f}%")
        if COL_INFLATION in df.columns:
            p_hyp = (df[COL_INFLATION] > HYPERINFLATION_THRESHOLD_PCT).mean() * 100
            print(f"Odsetek z inflacją > {HYPERINFLATION_THRESHOLD_PCT}% (hiperinflacja): {p_hyp:.1f}%")
        if COL_DEVAL in df.columns:
            p_dev = (df[COL_DEVAL] > SEVERE_DEVALUATION_THRESHOLD_PCT).mean() * 100
            print(
                f"Odsetek z dewaluacją > {SEVERE_DEVALUATION_THRESHOLD_PCT}%: {p_dev:.1f}%"
            )
        print("\nWygenerowane wykresy:")
        for p in paths:
            print("  -", p)
        print("=" * 60 + "\n")

    return paths
