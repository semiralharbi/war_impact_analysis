"""
Analiza: Czarny rynek i gospodarka nieformalna.
Pytanie: Jak wojna zwiększa nieformalność i czarny rynek?
Czy większy spadek PKB = większy wzrost nieformalności?
"""
from pathlib import Path

from core.data_loader import load_war_economic_data
from analyses.black_market_informal_economy.charts import build_all_charts
from analyses.black_market_informal_economy.constants import (
    COL_GDP,
    COL_INFORMAL_PRE,
    COL_INFORMAL_DURING,
    COL_CURRENCY_GAP,
    COL_CONFLICT_TYPE,
    COL_WAR_PROFITEERING,
    COL_REGION,
    COL_START_YEAR,
    COL_END_YEAR,
)


def run(csv_path: Path | None = None) -> list[Path]:
    df = load_war_economic_data(csv_path)
    if COL_INFORMAL_DURING in df.columns and COL_INFORMAL_PRE in df.columns:
        df = df.copy()
        df["informality_growth_pp"] = df[COL_INFORMAL_DURING] - df[COL_INFORMAL_PRE]
        if COL_START_YEAR in df.columns and COL_END_YEAR in df.columns:
            sy = df[COL_START_YEAR]
            ey = df[COL_END_YEAR]
            dur = ey - sy + 1
            df["war_duration_years"] = dur.where((dur >= 1) & sy.notna() & ey.notna())
    n = len(df)
    n_ok = df[["informality_growth_pp", COL_GDP]].dropna(how="any").shape[0] if "informality_growth_pp" in df.columns else 0
    print(f"\nDane (czarny rynek / nieformalność): załadowano {n:,} wierszy (z pełnymi danymi do analizy: {n_ok:,}).\n")

    paths = build_all_charts(df)

    print("\n" + "=" * 60)
    print("ANALIZA: Czarny rynek i gospodarka nieformalna")
    print("=" * 60)
    print("\nPytanie: Czy większy spadek PKB = większy wzrost nieformalności?")
    plot_df = df[["informality_growth_pp", COL_GDP]].dropna(how="any") if "informality_growth_pp" in df.columns else None
    if plot_df is not None and len(plot_df) > 1:
        corr = plot_df["informality_growth_pp"].corr(plot_df[COL_GDP])
        print(f"Korelacja (wzrost nieformalności vs zmiana PKB): {corr:.3f}")
    if COL_INFORMAL_PRE in df.columns and COL_INFORMAL_DURING in df.columns:
        pre_m = df[COL_INFORMAL_PRE].mean()
        dur_m = df[COL_INFORMAL_DURING].mean()
        print(f"\nŚrednio w całym zbiorze: nieformalność przed wojną {pre_m:.2f}%, w trakcie {dur_m:.2f}% (zbiór nie zawiera osobnej kolumny „po wojnie”).")
    if COL_REGION in df.columns and "informality_growth_pp" in df.columns:
        gr = df[[COL_REGION, "informality_growth_pp"]].dropna(how="any")
        if len(gr) > 0:
            by_reg = gr.groupby(COL_REGION)["informality_growth_pp"].mean().sort_values(ascending=False)
            print("\nŚredni wzrost nieformalności (p.p.) - top 5 regionów:")
            print(by_reg.head(5).round(2).to_string())
    if "war_duration_years" in df.columns and "informality_growth_pp" in df.columns:
        dd = df[["war_duration_years", "informality_growth_pp"]].dropna(how="any")
        if len(dd) > 1:
            c_dur = dd["informality_growth_pp"].corr(dd["war_duration_years"])
            print(f"\nKorelacja (wzrost nieformalności vs długość konfliktu w latach): {c_dur:.3f}")
    if COL_CURRENCY_GAP in df.columns and COL_CONFLICT_TYPE in df.columns:
        by_type = df.groupby(COL_CONFLICT_TYPE)[COL_CURRENCY_GAP].mean().round(2)
        print("\nŚrednia luka kursu czarnorynkowego (%) wg typu konfliktu:")
        print(by_type.to_string())
    if COL_WAR_PROFITEERING in df.columns and COL_CONFLICT_TYPE in df.columns:
        pct_yes = df.groupby(COL_CONFLICT_TYPE)[COL_WAR_PROFITEERING].apply(lambda x: (x == "Yes").mean() * 100).round(1)
        print("\nOdsetek obserwacji z War_Profiteering_Documented = Yes (%) wg typu konfliktu:")
        print(pct_yes.to_string())
    print("\nWygenerowane wykresy:")
    for p in paths:
        print("  -", p)
    print("=" * 60 + "\n")

    return paths
