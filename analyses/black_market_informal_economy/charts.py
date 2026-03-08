"""
Wykresy: Czarny rynek i gospodarka nieformalna.
- Scatter: GDP_Change vs wzrost nieformalności (During − Pre), kolor = Black_Market_Activity_Level
- Bar: średni Currency_Black_Market_Rate_Gap_% wg Conflict_Type
- Boxplot: Informal_Economy_Size_During_War_% wg Conflict_Type
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

from config.settings import get_analysis_output_dir
from utils.plot_helpers import save_figure
from analyses.black_market_informal_economy.constants import (
    COL_GDP,
    COL_INFORMAL_PRE,
    COL_INFORMAL_DURING,
    COL_BLACK_MARKET_LEVEL,
    COL_CURRENCY_GAP,
    COL_CONFLICT_TYPE,
    COL_REGION,
    COL_START_YEAR,
    COL_PRIMARY_BLACK_MARKET_GOODS,
    COL_INFLATION,
    CONTEMPORARY_WAR_START_YEAR,
    BLACK_MARKET_LEVEL_ORDER,
    ANALYSIS_NAME,
)

OUTPUT_DIR = get_analysis_output_dir(ANALYSIS_NAME)


def _ensure_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for orig, new in [
        ("GDP_Change_%", COL_GDP),
        ("Informal_Economy_Size_Pre_War_%", COL_INFORMAL_PRE),
        ("Informal_Economy_Size_During_War_%", COL_INFORMAL_DURING),
        ("Currency_Black_Market_Rate_Gap_%", COL_CURRENCY_GAP),
        ("Inflation_Rate_%", COL_INFLATION),
    ]:
        if new not in df.columns and orig in df.columns:
            df[new] = pd.to_numeric(df[orig], errors="coerce")
    return df


def chart_scatter_gdp_vs_informality_growth(df: pd.DataFrame) -> Path:
    """
    Scatter: X = GDP_Change_%, Y = wzrost nieformalności (During − Pre w pp.),
    kolor = Black_Market_Activity_Level.
    """
    df = _ensure_columns(df)
    df["informality_growth_pp"] = df[COL_INFORMAL_DURING] - df[COL_INFORMAL_PRE]
    need = [COL_GDP, "informality_growth_pp", COL_BLACK_MARKET_LEVEL]
    plot_df = df[need].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_scatter_gdp_vs_informality_growth.png"
        save_figure(fig, out)
        return out

    by_level = plot_df.groupby(COL_BLACK_MARKET_LEVEL)[["informality_growth_pp", COL_GDP]].agg(["mean", "count"])
    by_level = by_level.reindex([l for l in BLACK_MARKET_LEVEL_ORDER if l in by_level.index])
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    x_pos = np.arange(len(by_level))
    w = 0.6
    bars1 = axes[0].bar(x_pos, by_level["informality_growth_pp"]["mean"].values, width=w, color="steelblue", edgecolor="white")
    axes[0].bar_label(bars1, labels=[f"{v:.3f}" for v in by_level["informality_growth_pp"]["mean"].values], padding=3, fontsize=8)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(by_level.index, rotation=20, ha="right")
    axes[0].set_ylabel("Średni wzrost nieformalności (p.p.)")
    axes[0].set_title("Wzrost nieformalności wg poziomu czarnego rynku\nTeza: Czy większy spadek PKB wiąże się\nz większym wzrostem nieformalności?")
    mn, mx = by_level["informality_growth_pp"]["mean"].min(), by_level["informality_growth_pp"]["mean"].max()
    axes[0].set_ylim(mn - 0.05, mx + 0.05)
    axes[0].grid(True, alpha=0.3, axis="y")

    bars2 = axes[1].bar(x_pos, by_level[COL_GDP]["mean"].values, width=w, color="coral", edgecolor="white")
    axes[1].bar_label(bars2, labels=[f"{v:.2f}%" for v in by_level[COL_GDP]["mean"].values], padding=3, fontsize=8)
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(by_level.index, rotation=20, ha="right")
    axes[1].set_ylabel("Średnia zmiana PKB (%)")
    axes[1].set_title("Zmiana PKB wg poziomu czarnego rynku\nTeza: Czy większy spadek PKB wiąże się\nz większym wzrostem nieformalności?")
    mn2, mx2 = by_level[COL_GDP]["mean"].min(), by_level[COL_GDP]["mean"].max()
    axes[1].set_ylim(mn2 - 0.2, mx2 + 0.2)
    axes[1].grid(True, alpha=0.3, axis="y")
    plt.suptitle("Czy większy spadek PKB = większy wzrost nieformalności?", y=1.02)
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_scatter_gdp_vs_informality_growth.png"
    save_figure(fig, out)
    return out


def chart_bar_currency_gap_by_conflict_type(df: pd.DataFrame) -> Path:
    """Bar: średni Currency_Black_Market_Rate_Gap_% wg Conflict_Type."""
    df = _ensure_columns(df)
    plot_df = df[[COL_CURRENCY_GAP, COL_CONFLICT_TYPE]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_bar_currency_gap_by_conflict_type.png"
        save_figure(fig, out)
        return out

    by_type = plot_df.groupby(COL_CONFLICT_TYPE)[COL_CURRENCY_GAP].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = np.arange(len(by_type))
    bars = ax.bar(x_pos, by_type.values, color="steelblue", edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in by_type.values], padding=3, fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_type.index, rotation=25, ha="right")
    ax.set_ylabel("Średnia luka kursu czarnorynkowego (%)")
    ax.set_xlabel("Typ konfliktu")
    ax.set_title("Luka kursu na czarnym rynku wg typu konfliktu\nTeza: Który typ konfliktu wiąże się z największą luką kursu walutowego na czarnym rynku?")
    v_min, v_max = by_type.min(), by_type.max()
    ax.set_ylim(v_min - 1, v_max + 1)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_bar_currency_gap_by_conflict_type.png"
    save_figure(fig, out)
    return out


def chart_bar_informal_during_by_conflict_type(df: pd.DataFrame) -> Path:
    """Wykres słupkowy: średnia Informal_Economy_Size_During_War_% wg Conflict_Type."""
    df = _ensure_columns(df)
    plot_df = df[[COL_INFORMAL_DURING, COL_CONFLICT_TYPE]].dropna(how="any")
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_bar_informal_during_by_conflict_type.png"
        save_figure(fig, out)
        return out

    by_type = plot_df.groupby(COL_CONFLICT_TYPE)[COL_INFORMAL_DURING].mean().sort_values(ascending=False)
    stats_informal = plot_df.groupby(COL_CONFLICT_TYPE)[COL_INFORMAL_DURING].agg(["mean", "median", "count"]).round(2)
    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = np.arange(len(by_type))
    bars = ax.bar(x_pos, by_type.values, color="steelblue", edgecolor="white")
    ax.bar_label(bars, labels=[f"{v:.2f}%" for v in by_type.values], padding=3, fontsize=9)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_type.index, rotation=25, ha="right")
    ax.set_xlabel("Typ konfliktu")
    ax.set_ylabel("Średni rozmiar gospodarki nieformalnej w trakcie wojny(%)")
    ax.set_title("Gospodarka nieformalna w trakcie konfliktu wg typu konfliktu\nTeza: Który typ konfliktu wiąże się z największym rozmiarem gospodarki nieformalnej w trakcie wojny?")
    m, M = by_type.min(), by_type.max()
    ax.set_ylim(m - 1, M + 1)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    out = OUTPUT_DIR / "chart_bar_informal_during_by_conflict_type.png"
    save_figure(fig, out)
    return out


def chart_black_market_level_by_region_and_period(df: pd.DataFrame) -> Path:
    """
    Wykres 1: Rozkład Black_Market_Activity_Level wg Regionu (słupki stosowane).
    Wykres 2: Średni „poziom” czarnego rynku wg regionu: wojny starsze (Start_Year < CONTEMPORARY_WAR_START_YEAR)
    vs współczesne (Start_Year >= CONTEMPORARY_WAR_START_YEAR) — czy we współczesnych wojnach level jest niższy?
    """
    need = [COL_BLACK_MARKET_LEVEL, COL_REGION]
    if COL_START_YEAR not in df.columns and "Start_Year" in df.columns:
        df = df.copy()
        df[COL_START_YEAR] = pd.to_numeric(df["Start_Year"], errors="coerce")
    plot_df = df[need + [COL_START_YEAR]] if COL_START_YEAR in df.columns else df[need].assign(**{COL_START_YEAR: np.nan})
    plot_df = plot_df.dropna(subset=need)
    if plot_df.empty:
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        for ax in axes:
            ax.set_title("Brak danych")
        out = OUTPUT_DIR / "chart_black_market_level_by_region_and_period.png"
        save_figure(fig, out)
        return out

    level_order = [l for l in BLACK_MARKET_LEVEL_ORDER if l in plot_df[COL_BLACK_MARKET_LEVEL].values]
    if not level_order:
        level_order = plot_df[COL_BLACK_MARKET_LEVEL].unique().tolist()

    fig, axes = plt.subplots(2, 1, figsize=(11, 9))

    cross = pd.crosstab(plot_df[COL_REGION], plot_df[COL_BLACK_MARKET_LEVEL], normalize="index") * 100
    for col in level_order:
        if col not in cross.columns:
            cross[col] = 0
    cross = cross.reindex(columns=level_order).fillna(0)
    cross = cross.loc[cross.sum(axis=1).sort_values(ascending=False).index]
    x = np.arange(len(cross))
    w = 0.2
    for i, col in enumerate(level_order):
        offset = (i - 1.5) * w
        axes[0].bar(x + offset, cross[col].values, width=w, label=col, color=["#2ecc71", "#f1c40f", "#e67e22", "#c0392b"][i % 4])
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(cross.index, rotation=25, ha="right")
    axes[0].set_ylabel("Odsetek obserwacji (%)")
    axes[0].set_xlabel("Region")
    axes[0].set_title("Rozkład poziomu czarnego rynku wg regionu\nTeza: Jak rozkłada się aktywność czarnego rynku (Low/Moderate/High/Dominant) w poszczególnych regionach?")
    axes[0].set_ylim(23.5, 26.5)
    axes[0].legend(loc="upper right", fontsize=8)
    axes[0].grid(True, alpha=0.3, axis="y")
   

    ordinal = {l: i + 1 for i, l in enumerate(level_order)}
    plot_df["level_ordinal"] = plot_df[COL_BLACK_MARKET_LEVEL].map(ordinal).fillna(1)
    plot_df["period"] = np.where(
        plot_df[COL_START_YEAR] >= CONTEMPORARY_WAR_START_YEAR,
        f"Konflikty od {CONTEMPORARY_WAR_START_YEAR} (współczesne)",
        f"Konflikty do {CONTEMPORARY_WAR_START_YEAR - 1} (starsze)",
    )
    period_df = plot_df[plot_df[COL_START_YEAR].notna()]
    if period_df.empty:
        axes[1].set_title("Brak danych z rokiem rozpoczęcia")
    else:
        by_region_period = period_df.groupby([COL_REGION, "period"])["level_ordinal"].mean().unstack(fill_value=0)
        col_order = [c for c in [f"Konflikty do {CONTEMPORARY_WAR_START_YEAR - 1} (starsze)", f"Konflikty od {CONTEMPORARY_WAR_START_YEAR} (współczesne)"] if c in by_region_period.columns]
        if not col_order:
            col_order = by_region_period.columns.tolist()
        by_region_period = by_region_period[col_order]
        by_region_period = by_region_period[(by_region_period > 0).all(axis=1)]
        by_region_period = by_region_period.reindex(by_region_period.sum(axis=1).sort_values(ascending=False).index)
        x = np.arange(len(by_region_period))
        n_cols = by_region_period.shape[1]
        w = 0.8 / max(n_cols, 1)
        colors_per = ["steelblue", "coral"]
        for i, col in enumerate(by_region_period.columns):
            offset = (i - (n_cols - 1) / 2) * w
            axes[1].bar(x + offset, by_region_period[col].values, width=w * 0.9, label=col, color=colors_per[i % 2])

        diff_cols = [c for c in by_region_period.columns if str(CONTEMPORARY_WAR_START_YEAR) in c]
        if len(by_region_period.columns) >= 2:
            d = by_region_period.iloc[:, 0] - by_region_period.iloc[:, 1]
        
        vals = by_region_period.values.flatten()
        vals = vals[np.isfinite(vals)]
        vals = vals[vals > 0]
        if len(vals) > 0:
            y_min, y_max = vals.min(), vals.max()
            span = max(0.2, y_max - y_min + 0.04)
            y_center = (y_min + y_max) / 2
            axes[1].set_ylim(y_center - span / 2, y_center + span / 2)
        else:
            axes[1].set_ylim(2.4, 2.55)
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(by_region_period.index, rotation=25, ha="right")
        axes[1].set_ylabel("Średni poziom czarnego rynku")
        axes[1].set_xlabel("Region")
        axes[1].set_title(f"Porównanie: wojny starsze vs od {CONTEMPORARY_WAR_START_YEAR}\nTeza: Czy we współczesnych wojnach (od {CONTEMPORARY_WAR_START_YEAR}) poziom czarnego rynku jest niższy niż w konfliktach starszych?")
        axes[1].legend(loc="upper right", fontsize=8)
        axes[1].grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out = OUTPUT_DIR / "chart_black_market_level_by_region_and_period.png"
    save_figure(fig, out)
    return out


def chart_black_market_goods_and_inflation(df: pd.DataFrame) -> Path:
    """
    Wykres 1: Jakimi towarami handluje się najczęściej na czarnym rynku (liczba obserwacji).
    Wykres 2: Średnia inflacja przy handlu danym towarem (korelacja inflacja ↔ towar na czarnym rynku).
    """
    df = _ensure_columns(df)
    goods_col = COL_PRIMARY_BLACK_MARKET_GOODS
    if goods_col not in df.columns:
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        for ax in axes:
            ax.set_title("Brak kolumny Primary_Black_Market_Goods")
        out = OUTPUT_DIR / "chart_black_market_goods_and_inflation.png"
        save_figure(fig, out)
        return out

    def split_goods(s):
        if pd.isna(s) or not isinstance(s, str):
            return []
        return [g.strip().lower() for g in s.split(",") if g.strip()]

    plot_df = df[[goods_col, COL_INFLATION]].copy()
    plot_df["good"] = plot_df[goods_col].apply(split_goods)
    exploded = plot_df.explode("good").dropna(subset=["good"])
    exploded = exploded[exploded["good"] != ""]
    if exploded.empty:
        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        for ax in axes:
            ax.set_title("Brak danych o towarach")
        out = OUTPUT_DIR / "chart_black_market_goods_and_inflation.png"
        save_figure(fig, out)
        return out

    exploded["good_label"] = exploded["good"].str.capitalize()
    counts = exploded["good_label"].value_counts()
    pct = (counts / counts.sum() * 100).sort_values(ascending=False)
    if COL_INFLATION in exploded.columns and exploded[COL_INFLATION].notna().any():
        inf_by_good = exploded.groupby("good_label")[COL_INFLATION].agg(["mean", "count"]).dropna(subset=["mean"])
        inf_by_good = inf_by_good[inf_by_good["count"] >= 10].sort_values("mean", ascending=False)

    fig, axes = plt.subplots(2, 1, figsize=(11, 8))

    x_pos = np.arange(len(pct))
    bars = axes[0].bar(x_pos, pct.values, color="steelblue", edgecolor="white")
    axes[0].bar_label(bars, labels=[f"{v:.2f}%" for v in pct.values], padding=3, fontsize=9)
    axes[0].set_xticks(x_pos)
    axes[0].set_xticklabels(pct.index, rotation=25, ha="right")
    axes[0].set_ylabel("Odsetek wystąpień (%)")
    axes[0].set_xlabel("Towar na czarnym rynku")
    axes[0].set_title("Częstotliwość handlu towarami na czarnym rynku\nTeza: Jakimi towarami handluje się najczęściej na czarnym rynku w kontekście konfliktów?")
    m0, M0 = pct.min(), pct.max()
    axes[0].set_ylim(m0 - 0.3, M0 + 0.3)
    axes[0].grid(True, alpha=0.3, axis="y")

    if COL_INFLATION in exploded.columns and exploded[COL_INFLATION].notna().any():
        inf_by_good = exploded.groupby("good_label")[COL_INFLATION].agg(["mean", "count"]).dropna(subset=["mean"])
        inf_by_good = inf_by_good[inf_by_good["count"] >= 10].sort_values("mean", ascending=False)
        if not inf_by_good.empty:
            x_pos2 = np.arange(len(inf_by_good))
            bars2 = axes[1].bar(x_pos2, inf_by_good["mean"].values, color="coral", edgecolor="white")
            axes[1].bar_label(bars2, labels=[f"{v:.2f}%" for v in inf_by_good["mean"].values], padding=3, fontsize=8)
            axes[1].set_xticks(x_pos2)
            axes[1].set_xticklabels(inf_by_good.index, rotation=25, ha="right")
            axes[1].set_ylabel("Średnia inflacja (%)")
            axes[1].set_xlabel("Towar na czarnym rynku")
            axes[1].set_title("Inflacja a towary na czarnym rynku\nTeza: Jaka jest korelacja między inflacją a handlem danymi towarami na czarnym rynku?")
            m, M = inf_by_good["mean"].min(), inf_by_good["mean"].max()
            axes[1].set_ylim(m - 0.15, M + 0.15)
            axes[1].grid(True, alpha=0.3, axis="y")
        else:
            axes[1].set_title("Za mało obserwacji z inflacją dla poszczególnych towarów")
    else:
        axes[1].set_title("Brak danych o inflacji")

    plt.tight_layout()
    out = OUTPUT_DIR / "chart_black_market_goods_and_inflation.png"
    save_figure(fig, out)
    return out


def build_all_charts(df: pd.DataFrame) -> list[Path]:
    paths = []
    paths.append(chart_scatter_gdp_vs_informality_growth(df))
    paths.append(chart_bar_currency_gap_by_conflict_type(df))
    paths.append(chart_bar_informal_during_by_conflict_type(df))
    paths.append(chart_black_market_level_by_region_and_period(df))
    paths.append(chart_black_market_goods_and_inflation(df))
    return paths
