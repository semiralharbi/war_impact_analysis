"""
Wykresy: Modelowanie odporności gospodarczej (hiperinflacja / tipping point).
- Scatter: GDP vs Inflacja (kolor = typ konfliktu)
- Hexbin / 2D histogram: gęstość (GDP vs Inflacja)
- Bar: przedziały spadku PKB → odsetek obserwacji z inflacją > 50%
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from config.settings import get_analysis_output_dir
from utils.plot_helpers import save_figure
from analyses.economic_resilience_hyperinflation.constants import (
    COL_GDP,
    COL_INFLATION,
    COL_DEVAL,
    COL_CONFLICT_TYPE,
    INFLATION_HIGH_THRESHOLD_PCT,
    GDP_BIN_EDGES,
    ANALYSIS_NAME,
)

OUTPUT_DIR = get_analysis_output_dir(ANALYSIS_NAME)


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ujednolicenie nazw kolumn (loader może zwrócić oryginalne nazwy)."""
    df = df.copy()
    if COL_INFLATION not in df.columns and "Inflation_Rate_%" in df.columns:
        df[COL_INFLATION] = pd.to_numeric(df["Inflation_Rate_%"], errors="coerce")
    if COL_DEVAL not in df.columns and "Currency_Devaluation_%" in df.columns:
        df[COL_DEVAL] = pd.to_numeric(df["Currency_Devaluation_%"], errors="coerce")
    if COL_GDP not in df.columns and "GDP_Change_%" in df.columns:
        df[COL_GDP] = pd.to_numeric(df["GDP_Change_%"], errors="coerce")
    return df


def chart_scatter_gdp_vs_inflation(df: pd.DataFrame) -> Path:
   
    df = _ensure_columns(df)
    plot_df = df[[COL_GDP, COL_INFLATION, COL_CONFLICT_TYPE]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title("Brak danych: GDP_Change_%, Inflation_Rate_%, Conflict_Type")
        out = OUTPUT_DIR / "chart_scatter_gdp_vs_inflation.png"
        save_figure(fig, out)
        return out

    fig, ax = plt.subplots(figsize=(10, 6))
    for ctype in plot_df[COL_CONFLICT_TYPE].unique():
        sub = plot_df[plot_df[COL_CONFLICT_TYPE] == ctype]
        ax.scatter(sub[COL_GDP], sub[COL_INFLATION], label=ctype, alpha=0.5, s=15)
    ax.axhline(INFLATION_HIGH_THRESHOLD_PCT, color="red", linestyle="--", linewidth=1.5, label=f"Próg inflacji {INFLATION_HIGH_THRESHOLD_PCT}%")
    ax.set_xlabel("Zmiana PKB (%)")
    ax.set_ylabel("Inflacja (%)")
    ax.set_title("PKB a inflacja (kolor = typ konfliktu)\nTeza: Przy jakim spadku PKB rośnie ryzyko wysokiej inflacji?")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout(rect=[0, 0, 0.82, 1])
    out = OUTPUT_DIR / "chart_scatter_gdp_vs_inflation.png"
    save_figure(fig, out)
    return out


def chart_hexbin_gdp_vs_inflation(df: pd.DataFrame) -> Path:
  
    df = _ensure_columns(df)
    plot_df = df[[COL_GDP, COL_INFLATION]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_hexbin_gdp_vs_inflation.png"
        save_figure(fig, out)
        return out

    fig, ax = plt.subplots(figsize=(10, 6))
    hb = ax.hexbin(
        plot_df[COL_GDP],
        plot_df[COL_INFLATION],
        gridsize=25,
        cmap="YlOrRd",
        mincnt=1,
        edgecolors="none",
    )
    ax.axhline(INFLATION_HIGH_THRESHOLD_PCT, color="darkred", linestyle="--", linewidth=1.5, label=f"Inflacja {INFLATION_HIGH_THRESHOLD_PCT}%")
    ax.set_xlabel("Zmiana PKB (%)")
    ax.set_ylabel("Inflacja (%)")
    ax.set_title("Gęstość obserwacji: PKB a inflacja (hexbin)\nTeza: Gdzie koncentrują się obserwacje PKB–inflacja (gęstość)?")
    plt.colorbar(hb, ax=ax, label="Liczba obserwacji")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_hexbin_gdp_vs_inflation.png"
    save_figure(fig, out)
    return out


def chart_bar_inflation_above_threshold_by_gdp_bin(df: pd.DataFrame) -> Path:
   
    df = _ensure_columns(df)
    plot_df = df[[COL_GDP, COL_INFLATION]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_bar_inflation_threshold_by_gdp_bin.png"
        save_figure(fig, out)
        return out

    edges = GDP_BIN_EDGES
    plot_df["gdp_bin"] = pd.cut(plot_df[COL_GDP], bins=edges, include_lowest=True)
    plot_df["high_inflation"] = plot_df[COL_INFLATION] > INFLATION_HIGH_THRESHOLD_PCT

    agg = plot_df.groupby("gdp_bin", observed=True).agg(
        total=("high_inflation", "count"),
        high_inf=("high_inflation", "sum"),
    )
    agg["pct_high_inflation"] = (agg["high_inf"] / agg["total"] * 100).round(1)
    agg = agg[agg["total"] > 0]
    x_pos = np.arange(len(agg))
    labels = [f"{int(i.left)} do {int(i.right)}%" for i in agg.index]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(x_pos, agg["pct_high_inflation"].values, color="steelblue", edgecolor="white")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_ylabel("Odsetek obserwacji z inflacją > 50% (%)")
    ax.set_xlabel("Przedział zmiany PKB (%)")
    ax.set_title(f"Ryzyko wysokiej inflacji (> {INFLATION_HIGH_THRESHOLD_PCT}%) w zależności od spadku PKB\nTeza: Odsetek obserwacji z wysoką inflacją rośnie ze spadkiem PKB.")
    ax.axhline(INFLATION_HIGH_THRESHOLD_PCT, color="red", linestyle="--", alpha=0.7, label="Próg 50%")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_bar_inflation_threshold_by_gdp_bin.png"
    save_figure(fig, out)
    return out


def build_all_charts(df: pd.DataFrame) -> list[Path]:
    paths = []
    paths.append(chart_scatter_gdp_vs_inflation(df))
    paths.append(chart_hexbin_gdp_vs_inflation(df))
    paths.append(chart_bar_inflation_above_threshold_by_gdp_bin(df))
    return paths
