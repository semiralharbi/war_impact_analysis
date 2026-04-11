"""
Wykresy: Modelowanie odporności gospodarczej (hiperinflacja / tipping point).
- Linie: przedziały spadku PKB → odsetek wysokiej inflacji, osobna linia na region
- Słupki: przedziały spadku PKB → odsetek wysokiej inflacji (cały zbiór)
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
    COL_REGION,
    COL_UNEMPLOYMENT_SPIKE,
    COL_COST_OF_WAR_USD,
    INFLATION_HIGH_THRESHOLD_PCT,
    HYPERINFLATION_THRESHOLD_PCT,
    SEVERE_DEVALUATION_THRESHOLD_PCT,
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
    if COL_UNEMPLOYMENT_SPIKE not in df.columns and "Unemployment_Spike_Percentage_Points" in df.columns:
        df[COL_UNEMPLOYMENT_SPIKE] = pd.to_numeric(
            df["Unemployment_Spike_Percentage_Points"], errors="coerce"
        )
    if COL_COST_OF_WAR_USD in df.columns:
        df[COL_COST_OF_WAR_USD] = pd.to_numeric(df[COL_COST_OF_WAR_USD], errors="coerce")
    return df


def chart_scatter_gdp_vs_inflation(df: pd.DataFrame) -> Path:
    """
    Wykres liniowy: w przedziałach zmiany PKB - jaki % obserwacji ma inflację > próg,
    osobna linia dla każdego regionu (to samo cięcie PKB co wykres słupkowy).
    """
    df = _ensure_columns(df)
    out = OUTPUT_DIR / "chart_scatter_gdp_vs_inflation.png"
    if COL_REGION not in df.columns:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title("Brak kolumny Region")
        save_figure(fig, out)
        return out

    plot_df = df[[COL_GDP, COL_INFLATION, COL_REGION]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title("Brak danych: zmiana PKB, inflacja, region")
        save_figure(fig, out)
        return out

    plot_df = plot_df.copy()
    plot_df["gdp_bin"] = pd.cut(plot_df[COL_GDP], bins=GDP_BIN_EDGES, include_lowest=True)
    plot_df = plot_df.dropna(subset=["gdp_bin"])
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title("Brak danych po przypisaniu przedziałów PKB")
        save_figure(fig, out)
        return out

    plot_df["high_inflation"] = plot_df[COL_INFLATION] > INFLATION_HIGH_THRESHOLD_PCT
    agg = plot_df.groupby([COL_REGION, "gdp_bin"], observed=True).agg(
        total=("high_inflation", "count"),
        high_inf=("high_inflation", "sum"),
    )
    agg["pct_high"] = np.where(agg["total"] > 0, agg["high_inf"] / agg["total"] * 100, np.nan)
    piv = agg["pct_high"].unstack(fill_value=np.nan)
    bins_sorted = sorted(piv.columns.dropna().unique(), key=lambda iv: iv.left)
    piv = piv.reindex(columns=bins_sorted)
    region_order = plot_df.groupby(COL_REGION, observed=True).size().sort_values(ascending=False).index.tolist()
    piv = piv.reindex(index=[r for r in region_order if r in piv.index])
    if piv.empty:
        fig, ax = plt.subplots(figsize=(9, 6))
        ax.set_title("Brak zagregowanych danych (region × przedział PKB)")
        save_figure(fig, out)
        return out

    x_centers = np.array([(iv.left + iv.right) / 2 for iv in bins_sorted])
    x_labels = [f"{int(iv.left)} do {int(iv.right)}%" for iv in bins_sorted]

    fig, ax = plt.subplots(figsize=(11, 6))
    cmap = plt.get_cmap("tab10")
    for i, region in enumerate(piv.index):
        y = piv.loc[region].to_numpy(dtype=float)
        ax.plot(
            x_centers,
            y,
            marker="o",
            linewidth=2,
            markersize=6,
            label=str(region),
            color=cmap(i % 10),
        )

    ax.set_xticks(x_centers)
    ax.set_xticklabels(x_labels, rotation=35, ha="right", fontsize=8)
    ax.set_xlabel("Przedział zmiany PKB (%)")
    ax.set_ylabel(f"Odsetek obserwacji z inflacją > {INFLATION_HIGH_THRESHOLD_PCT:.0f}%")
    ax.set_title(
        "Ryzyko wysokiej inflacji vs spadek PKB - wg regionu (linie)\n"
        "Teza: Przy jakim spadku PKB rośnie odsetek przypadków z bardzo wysoką inflacją w danym regionie?"
    )
    vals = piv.to_numpy(dtype=float).ravel()
    vals = vals[np.isfinite(vals)]
    if vals.size == 0:
        y_lo, y_hi = 0.0, 100.0
    else:
        y_lo, y_hi = float(vals.min()), float(vals.max())
        if y_hi <= y_lo:
            y_lo, y_hi = y_lo - 0.5, y_hi + 0.5
        span = y_hi - y_lo
        pad = max(span * 0.08, 0.2)
        y_lo, y_hi = y_lo - pad, y_hi + pad
        y_lo = max(0.0, y_lo)
        y_hi = min(100.0, y_hi)
        if y_hi <= y_lo:
            y_lo, y_hi = max(0.0, y_lo - 0.5), min(100.0, y_hi + 0.5)
    ax.set_ylim(y_lo, y_hi)
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout(rect=[0, 0, 0.82, 1])
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
    baseline_pct = float(plot_df["high_inflation"].mean() * 100)
    ax.axhline(baseline_pct, color="gray", linestyle=":", linewidth=1.2, alpha=0.85, label=f"Średni udział w zbiorze ({baseline_pct:.1f}%)")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper left", fontsize=8)
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_bar_inflation_threshold_by_gdp_bin.png"
    save_figure(fig, out)
    return out


def build_all_charts(df: pd.DataFrame) -> list[Path]:
    paths = []
    paths.append(chart_scatter_gdp_vs_inflation(df))
    paths.append(chart_bar_inflation_above_threshold_by_gdp_bin(df))
    return paths
