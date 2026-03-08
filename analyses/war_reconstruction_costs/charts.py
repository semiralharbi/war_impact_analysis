"""
Wykresy: Koszty wojny vs koszty odbudowy — kiedy odbudowa przewyższa koszt wojny.
- Bar: stosunek Reconstruction_Cost / Cost_of_War wg Conflict_Type
- Porównanie współczesne vs stare: koszt odbudowy oraz koszt wojny (czy wyższy teraz czy kiedyś)
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from config.settings import get_analysis_output_dir
from utils.plot_helpers import save_figure
from analyses.war_reconstruction_costs.constants import (
    COL_COST_OF_WAR,
    COL_RECONSTRUCTION_COST,
    COL_GDP_CHANGE,
    COL_CONFLICT_TYPE,
    COL_START_YEAR,
    CONTEMPORARY_WAR_START_YEAR,
    ANALYSIS_NAME,
)

OUTPUT_DIR = get_analysis_output_dir(ANALYSIS_NAME)


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in [COL_COST_OF_WAR, COL_RECONSTRUCTION_COST]:
        if col in df.columns and df[col].dtype == object:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(",", "", regex=False), errors="coerce")
    if COL_GDP_CHANGE not in df.columns and "GDP_Change_%" in df.columns:
        df[COL_GDP_CHANGE] = pd.to_numeric(df["GDP_Change_%"], errors="coerce")
    return df


def _ensure_start_year(df: pd.DataFrame) -> pd.DataFrame:
    if COL_START_YEAR not in df.columns and "Start_Year" in df.columns:
        df = df.copy()
        df[COL_START_YEAR] = pd.to_numeric(df["Start_Year"], errors="coerce")
    return df


def chart_bar_ratio_by_conflict_type(df: pd.DataFrame) -> Path:
    """Wykres słupkowy: średni stosunek Reconstruction_to_War_Ratio wg Conflict_Type."""
    df = _ensure_columns(df)
    plot_df = df[[COL_COST_OF_WAR, COL_RECONSTRUCTION_COST, COL_CONFLICT_TYPE]].dropna(how="any")
    plot_df = plot_df[(plot_df[COL_COST_OF_WAR] > 0) & (plot_df[COL_RECONSTRUCTION_COST] > 0)]
    plot_df["ratio"] = plot_df[COL_RECONSTRUCTION_COST] / plot_df[COL_COST_OF_WAR]

    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych (koszt wojny / odbudowy)")
        out = OUTPUT_DIR / "chart_bar_ratio_by_conflict_type.png"
        save_figure(fig, out)
        return out

    by_type = plot_df.groupby(COL_CONFLICT_TYPE)["ratio"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = np.arange(len(by_type))
    bars = ax.bar(x_pos, by_type.values, color="steelblue", edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.2f}" for v in by_type.values], padding=3, fontsize=9)
    ax.axhline(1, color="red", linestyle="--", linewidth=1.5, alpha=0.8, label="Odbudowa = koszt wojny")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_type.index, rotation=25, ha="right")
    ax.set_xlabel("Typ konfliktu")
    ax.set_ylabel("Średni stosunek: koszt odbudowy / koszt wojny")
    ax.set_title(
        "Stosunek kosztu odbudowy do kosztu wojny wg typu konfliktu\n"
        "Teza: W których typach konfliktów odbudowa typowo przewyższa koszt wojny (ratio > 1)?"
    )
    r_min, r_max = by_type.min(), by_type.max()
    margin = max(0.1, (r_max - r_min) * 0.1)
    ax.set_ylim(max(0, r_min - margin), r_max + margin)
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_bar_ratio_by_conflict_type.png"
    save_figure(fig, out)
    return out


def chart_reconstruction_and_war_cost_contemporary_vs_old(df: pd.DataFrame) -> Path:
    """Dwa wykresy słupkowe: (1) koszt odbudowy — współczesne vs stare wojny; (2) koszt wojny — współczesne vs stare."""
    df = _ensure_columns(_ensure_start_year(df))
    need = [COL_COST_OF_WAR, COL_RECONSTRUCTION_COST, COL_START_YEAR]
    plot_df = df[[c for c in need if c in df.columns]].dropna(how="any")
    plot_df = plot_df[(plot_df[COL_COST_OF_WAR] > 0) & (plot_df[COL_RECONSTRUCTION_COST] > 0)]
    if COL_START_YEAR not in plot_df.columns or plot_df.empty:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        for ax in axes:
            ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_reconstruction_and_war_cost_contemporary_vs_old.png"
        save_figure(fig, out)
        return out

    plot_df["okres"] = np.where(
        plot_df[COL_START_YEAR] >= CONTEMPORARY_WAR_START_YEAR,
        f"Wojny współczesne\n(od {CONTEMPORARY_WAR_START_YEAR} r.)",
        f"Wojny starsze\n(przed {CONTEMPORARY_WAR_START_YEAR} r.)",
    )
    rec_by_period = plot_df.groupby("okres")[COL_RECONSTRUCTION_COST].mean()
    war_by_period = plot_df.groupby("okres")[COL_COST_OF_WAR].mean()
    order = [f"Wojny starsze\n(przed {CONTEMPORARY_WAR_START_YEAR} r.)", f"Wojny współczesne\n(od {CONTEMPORARY_WAR_START_YEAR} r.)"]
    order = [o for o in order if o in rec_by_period.index]
    rec_by_period = rec_by_period.reindex(order).dropna()
    war_by_period = war_by_period.reindex(order).dropna()

    base_key = order[0]
    base_rec = rec_by_period.loc[base_key] if base_key in rec_by_period.index else rec_by_period.iloc[0]
    base_war = war_by_period.loc[base_key] if base_key in war_by_period.index else war_by_period.iloc[0]
    rec_pct = (rec_by_period / base_rec * 100) if base_rec > 0 else rec_by_period * 0
    war_pct = (war_by_period / base_war * 100) if base_war > 0 else war_by_period * 0

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    def _pct_label(v: float) -> str:
        return f"{v:.2f}%" if abs(v - 100) < 10 else f"{v:.1f}%"

    x_pos = np.arange(len(rec_pct))
    bars1 = axes[0].bar(x_pos, rec_pct.values, color="coral", edgecolor="white")
    axes[0].bar_label(bars1, labels=[_pct_label(v) for v in rec_pct.values], padding=3, fontsize=9)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(rec_pct.index)
    axes[0].set_ylabel("Średni koszt odbudowy (% względem wojen starszych)")
    axes[0].set_title(
        "Koszt odbudowy: wojny współczesne vs starsze\n"
        "Teza: Czy koszt odbudowy był wyższy w wojnach współczesnych\nczy w starszych?"
    )
    r_lo, r_hi = rec_pct.min(), rec_pct.max()
    margin = max(2, (r_hi - r_lo) * 0.15)
    axes[0].set_ylim(max(0, r_lo - margin), r_hi + margin)
    axes[0].axhline(100, color="gray", linestyle="--", alpha=0.7, linewidth=1)
    axes[0].grid(True, alpha=0.3, axis="y")

    x_pos2 = np.arange(len(war_pct))
    bars2 = axes[1].bar(x_pos2, war_pct.values, color="steelblue", edgecolor="white")
    axes[1].bar_label(bars2, labels=[_pct_label(v) for v in war_pct.values], padding=3, fontsize=9)
    axes[1].set_xticks(x_pos2)
    axes[1].set_xticklabels(war_pct.index)
    axes[1].set_ylabel("Średni koszt wojny (% względem wojen starszych)")
    axes[1].set_title(
        "Koszt wojny: wojny współczesne vs starsze\n"
        "Teza: Czy koszt wojny był wyższy kiedyś\nczy w konfliktach współczesnych?"
    )
    w_lo, w_hi = war_pct.min(), war_pct.max()
    margin_w = max(2, (w_hi - w_lo) * 0.15)
    axes[1].set_ylim(max(0, w_lo - margin_w), w_hi + margin_w)
    axes[1].axhline(100, color="gray", linestyle="--", alpha=0.7, linewidth=1)
    axes[1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out = OUTPUT_DIR / "chart_reconstruction_and_war_cost_contemporary_vs_old.png"
    save_figure(fig, out)
    return out


def build_all_charts(df: pd.DataFrame) -> list[Path]:
    paths = []
    paths.append(chart_bar_ratio_by_conflict_type(df))
    paths.append(chart_reconstruction_and_war_cost_contemporary_vs_old(df))
    return paths
