"""
Wykresy: Regiony i typy konfliktów najbardziej dotknięte ubóstwem i brakiem bezpieczeństwa żywnościowego.
- Boxplot: Extreme_Poverty / Food_Insecurity vs Region lub Conflict_Type
- Bar: ranking regionów (złożony wskaźnik)
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from pathlib import Path

from config.settings import get_analysis_output_dir
from utils.plot_helpers import save_figure
from analyses.poverty_and_food_insecurity.constants import (
    COL_EXTREME_POVERTY,
    COL_FOOD_INSECURITY,
    COL_HOUSEHOLDS_POVERTY,
    COL_CONFLICT_TYPE,
    COL_REGION,
    ANALYSIS_NAME,
)

OUTPUT_DIR = get_analysis_output_dir(ANALYSIS_NAME)


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if COL_EXTREME_POVERTY not in df.columns and "Extreme_Poverty_Rate_%" in df.columns:
        df[COL_EXTREME_POVERTY] = pd.to_numeric(df["Extreme_Poverty_Rate_%"], errors="coerce")
    if COL_FOOD_INSECURITY not in df.columns and "Food_Insecurity_Rate_%" in df.columns:
        df[COL_FOOD_INSECURITY] = pd.to_numeric(df["Food_Insecurity_Rate_%"], errors="coerce")
    if COL_HOUSEHOLDS_POVERTY not in df.columns and "Households_Fallen_Into_Poverty_Estimate" in df.columns:
        df[COL_HOUSEHOLDS_POVERTY] = pd.to_numeric(df["Households_Fallen_Into_Poverty_Estimate"], errors="coerce")
    return df


def chart_boxplot_food_insecurity_by_region(df: pd.DataFrame) -> Path:
    """Boxplot: Food_Insecurity_Rate vs Region — porównanie rozkładów."""
    df = _ensure_columns(df)
    plot_df = df[[COL_FOOD_INSECURITY, COL_REGION]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_food_insecurity_by_region.png"
        save_figure(fig, out)
        return out

    order = plot_df.groupby(COL_REGION)[COL_FOOD_INSECURITY].median().sort_values(ascending=False).index.tolist()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=plot_df, x=COL_REGION, y=COL_FOOD_INSECURITY, order=order, hue=COL_REGION, legend=False, palette="muted", ax=ax)
    ax.set_xlabel("Region")
    ax.set_ylabel("Wskaźnik braku bezpieczeństwa żywnościowego (%)")
    ax.set_title("Brak bezpieczeństwa żywnościowego wg regionu\nTeza: Które regiony mają najwyższy poziom braku bezpieczeństwa żywnościowego?")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_food_insecurity_by_region.png"
    save_figure(fig, out)
    return out


def chart_boxplot_extreme_poverty_by_conflict_type(df: pd.DataFrame) -> Path:
    """Boxplot: Extreme_Poverty_Rate vs Conflict_Type."""
    df = _ensure_columns(df)
    plot_df = df[[COL_EXTREME_POVERTY, COL_CONFLICT_TYPE]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_extreme_poverty_by_conflict_type.png"
        save_figure(fig, out)
        return out

    order = plot_df.groupby(COL_CONFLICT_TYPE)[COL_EXTREME_POVERTY].median().sort_values(ascending=False).index.tolist()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.boxplot(data=plot_df, x=COL_CONFLICT_TYPE, y=COL_EXTREME_POVERTY, order=order, hue=COL_CONFLICT_TYPE, legend=False, palette="muted", ax=ax)
    ax.set_xlabel("Typ konfliktu")
    ax.set_ylabel("Wskaźnik skrajnego ubóstwa (%)")
    ax.set_title("Skrajne ubóstwo wg typu konfliktu\nTeza: Który typ konfliktu wiąże się z najwyższym skrajnym ubóstwem?")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_extreme_poverty_by_conflict_type.png"
    save_figure(fig, out)
    return out


def chart_bar_region_ranking(df: pd.DataFrame) -> Path:
    """
    Bar: ranking regionów po złożonym wskaźniku (średnia z normalizowanych:
    ubóstwo skrajne + brak bezpieczeństwa żywnościowego + liczba gospodarstw wpadających w ubóstwo).
    """
    df = _ensure_columns(df)
    need = [COL_EXTREME_POVERTY, COL_FOOD_INSECURITY, COL_HOUSEHOLDS_POVERTY, COL_REGION]
    plot_df = df[need].dropna(how="any")
    if plot_df.empty or len(plot_df) < 2:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_region_vulnerability_ranking.png"
        save_figure(fig, out)
        return out

    for c in [COL_EXTREME_POVERTY, COL_FOOD_INSECURITY, COL_HOUSEHOLDS_POVERTY]:
        mn, mx = plot_df[c].min(), plot_df[c].max()
        if mx > mn:
            plot_df[f"{c}_n"] = (plot_df[c] - mn) / (mx - mn)
        else:
            plot_df[f"{c}_n"] = 0.5
    plot_df["composite"] = (plot_df[f"{COL_EXTREME_POVERTY}_n"] + plot_df[f"{COL_FOOD_INSECURITY}_n"] + plot_df[f"{COL_HOUSEHOLDS_POVERTY}_n"]) / 3

    by_region = plot_df.groupby(COL_REGION)["composite"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = np.arange(len(by_region))
    bars = ax.bar(x_pos, by_region.values, color="coral", edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.2f}" for v in by_region.values], padding=3, fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_region.index, rotation=25, ha="right")
    ax.set_ylabel("Złożony wskaźnik (0–1) - \nubóstwo skrajne, brak bezpieczeństwa żywnościowego,\nliczba gospodarstw wpadających w ubóstwo")
    ax.set_xlabel("Region")
    ax.set_title("Ranking regionów najbardziej dotkniętych ubóstwem i brakiem bezpieczeństwa żywnościowego\nTeza: Które regiony są najbardziej dotknięte (złożony wskaźnik: ubóstwo, głód, gospodarstwa w ubóstwie)?")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_region_vulnerability_ranking.png"
    save_figure(fig, out)
    return out


def build_all_charts(df: pd.DataFrame) -> list[Path]:
    paths = []
    paths.append(chart_boxplot_food_insecurity_by_region(df))
    paths.append(chart_boxplot_extreme_poverty_by_conflict_type(df))
    paths.append(chart_bar_region_ranking(df))
    return paths
