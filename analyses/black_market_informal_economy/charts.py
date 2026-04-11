"""
Wykresy: Czarny rynek i gospodarka nieformalna.
- GDP / nieformalność wg poziomu czarnego rynku, luka kursu i nieformalność wg typu konfliktu
- Porównanie nieformalności przed vs w trakcie oraz wzrost (During - Pre) wg regionu i długości konfliktu
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
    COL_REGION,
    COL_START_YEAR,
    COL_END_YEAR,
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


def _add_informality_and_duration(df: pd.DataFrame) -> pd.DataFrame:
    """Wzrost nieformalności (During - Pre) oraz szacowana długość konfliktu w latach."""
    df = _ensure_columns(df)
    out = df.copy()
    out["informality_growth_pp"] = out[COL_INFORMAL_DURING] - out[COL_INFORMAL_PRE]
    if COL_START_YEAR in out.columns and COL_END_YEAR in out.columns:
        sy = pd.to_numeric(out[COL_START_YEAR], errors="coerce")
        ey = pd.to_numeric(out[COL_END_YEAR], errors="coerce")
        dur = ey - sy + 1
        out["war_duration_years"] = dur.where((dur >= 1) & sy.notna() & ey.notna(), np.nan)
    else:
        out["war_duration_years"] = np.nan
    return out


def chart_informal_pre_vs_during_by_region(df: pd.DataFrame) -> Path:
    """
    Min / max udziału gospodarki nieformalnej: przed wojną vs w trakcie, wg regionu.
    (Średnie w tym zbiorze są do siebie bardzo zbliżone. Ekstrema pokazują faktyczny rozrzut obserwacji.)
    """
    df = _add_informality_and_duration(df)
    need = [COL_REGION, COL_INFORMAL_PRE, COL_INFORMAL_DURING]
    plot_df = df[need].dropna(how="any")
    out = OUTPUT_DIR / "chart_informal_pre_vs_during_by_region.png"
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        save_figure(fig, out)
        return out

    ag = plot_df.groupby(COL_REGION, observed=True)[[COL_INFORMAL_PRE, COL_INFORMAL_DURING]].agg(["min", "max"])
    ag = ag.sort_values((COL_INFORMAL_DURING, "max"), ascending=False)
    x = np.arange(len(ag))
    w = 0.18
    offs = [-1.5 * w, -0.5 * w, 0.5 * w, 1.5 * w]
    fig, ax = plt.subplots(figsize=(12, 5))
    pre_min = ag[(COL_INFORMAL_PRE, "min")].values
    pre_max = ag[(COL_INFORMAL_PRE, "max")].values
    dur_min = ag[(COL_INFORMAL_DURING, "min")].values
    dur_max = ag[(COL_INFORMAL_DURING, "max")].values
    ax.bar(x + offs[0], pre_min, width=w, label="Przed - min (%)", color="#aed6f1", edgecolor="white")
    ax.bar(x + offs[1], pre_max, width=w, label="Przed - max (%)", color="#1f618d", edgecolor="white")
    ax.bar(x + offs[2], dur_min, width=w, label="W trakcie - min (%)", color="#f5b7b1", edgecolor="white")
    ax.bar(x + offs[3], dur_max, width=w, label="W trakcie - max (%)", color="#c0392b", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(ag.index, rotation=28, ha="right")
    ax.set_ylabel("Udział gospodarki nieformalnej (%) - min / max w regionie")
    ax.set_xlabel("Region")
    ax.set_title(
        "Gospodarka nieformalna: przed vs w trakcie - zakres (min-max) wg regionu\n"
        "Średnie były mało rozróżniające. Wykres pokazuje skalę rozrzutu obserwacji w każdym regionie."
    )
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    ax.grid(True, alpha=0.3, axis="y")
    y0 = float(np.nanmin([pre_min.min(), dur_min.min()]))
    y1 = float(np.nanmax([pre_max.max(), dur_max.max()]))
    pad = (y1 - y0) * 0.04 + 1.0
    ax.set_ylim(max(0, y0 - pad), y1 + pad)
    plt.tight_layout()
    save_figure(fig, out)
    return out


def chart_informality_growth_by_region(df: pd.DataFrame) -> Path:
    """Min i max wzrostu nieformalności (During - Pre, p.p.) wg regionu."""
    df = _add_informality_and_duration(df)
    need = [COL_REGION, "informality_growth_pp"]
    plot_df = df[need].dropna(how="any")
    out = OUTPUT_DIR / "chart_informality_growth_by_region.png"
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        save_figure(fig, out)
        return out

    by_reg = plot_df.groupby(COL_REGION, observed=True)["informality_growth_pp"].agg(["min", "max", "mean"])
    by_reg = by_reg.sort_values("max", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = np.arange(len(by_reg))
    w = 0.36
    bars_lo = ax.bar(x_pos - w / 2, by_reg["min"].values, width=w, label="Min (p.p.)", color="#5dade2", edgecolor="white")
    bars_hi = ax.bar(x_pos + w / 2, by_reg["max"].values, width=w, label="Max (p.p.)", color="#2874a6", edgecolor="white")
    ax.scatter(x_pos, by_reg["mean"].values, color="#f39c12", s=36, zorder=3, label="Średnia", marker="D", edgecolors="white", linewidths=0.6)
    ax.bar_label(bars_lo, labels=[f"{v:.1f}" for v in by_reg["min"].values], padding=2, fontsize=7)
    ax.bar_label(bars_hi, labels=[f"{v:.1f}" for v in by_reg["max"].values], padding=2, fontsize=7)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_reg.index, rotation=25, ha="right")
    ax.set_ylabel("Wzrost nieformalności (During - Pre), p.p.")
    ax.set_xlabel("Region")
    ax.set_title(
        "Wzrost nieformalności wg regionu - minimum, maksimum i średnia\n"
        "Ekstrema pokazują skalę możliwych wartości, średnie pozostają zbliżone między regionami."
    )
    y0, y1 = float(by_reg["min"].min()), float(by_reg["max"].max())
    pad = max(1.0, (y1 - y0) * 0.03)
    ax.set_ylim(y0 - pad, y1 + pad)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    save_figure(fig, out)
    return out


def chart_informality_growth_by_war_duration(df: pd.DataFrame) -> Path:
    """Min / max / średnia wzrostu nieformalności wg przedziału długości konfliktu (Start_Year … End_Year, inkluzywnie)."""
    df = _add_informality_and_duration(df)
    need = ["war_duration_years", "informality_growth_pp"]
    plot_df = df[need].dropna(how="any")
    out = OUTPUT_DIR / "chart_informality_growth_by_war_duration.png"
    if plot_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych")
        save_figure(fig, out)
        return out

    bins = [0, 2, 5, 10, 25, 50, 200]
    labels = ["1-2 lata", "3-5 lat", "6-10 lat", "11-25 lat", "26-50 lat", "51+ lat"]
    plot_df = plot_df.copy()
    plot_df["duration_bin"] = pd.cut(
        plot_df["war_duration_years"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True,
    )
    by_bin = plot_df.groupby("duration_bin", observed=True)["informality_growth_pp"].agg(["min", "max", "mean", "count"])
    by_bin = by_bin[by_bin["count"] > 0].dropna(how="any")
    if by_bin.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_title("Brak danych po przypisaniu przedziałów")
        save_figure(fig, out)
        return out

    fig, ax = plt.subplots(figsize=(10, 5))
    x_pos = np.arange(len(by_bin))
    w = 0.36
    bars_lo = ax.bar(x_pos - w / 2, by_bin["min"].values, width=w, label="Min (p.p.)", color="#76d7c4", edgecolor="white")
    bars_hi = ax.bar(x_pos + w / 2, by_bin["max"].values, width=w, label="Max (p.p.)", color="#117864", edgecolor="white")
    ax.scatter(x_pos, by_bin["mean"].values, color="#f39c12", s=34, zorder=3, label="Średnia", marker="D", edgecolors="white", linewidths=0.6)
    ax.bar_label(bars_lo, labels=[f"{v:.1f}" for v in by_bin["min"].values], padding=2, fontsize=7)
    ax.bar_label(
        bars_hi,
        padding=2,
        fontsize=7,
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(by_bin.index.astype(str), rotation=15, ha="right")
    ax.set_ylabel("Wzrost nieformalności (During - Pre), p.p.")
    ax.set_xlabel("Szacowana długość konfliktu (lata)")
    ax.set_title(
        "Wzrost nieformalności a długość wojny - min, max i średnia w przedziale\n"
        "Średnie były zbliżone, zakres (min-max) pokazuje rozpiętość obserwacji w każdej grupie."
    )
    y0, y1 = float(by_bin["min"].min()), float(by_bin["max"].max())
    pad = max(1.0, (y1 - y0) * 0.03)
    ax.set_ylim(y0 - pad, y1 + pad)
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    save_figure(fig, out)
    return out


def chart_scatter_gdp_vs_informality_growth(df: pd.DataFrame) -> Path:
    """
    Scatter: X = GDP_Change_%, Y = wzrost nieformalności (During - Pre w pp.),
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



def chart_black_market_level_by_region_and_period(df: pd.DataFrame) -> Path:
    """
    Wykres 1: Rozkład Black_Market_Activity_Level wg Regionu.
    Wykres 2: Średni „poziom” czarnego rynku wg regionu: wojny starsze (Start_Year < CONTEMPORARY_WAR_START_YEAR)
    vs współczesne (Start_Year >= CONTEMPORARY_WAR_START_YEAR) - czy we współczesnych wojnach level jest niższy?
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
    2x2: częstość globalnie; częstość wg regionu (słupki grupowane: region - towary);
    inflacja globalnie; inflacja wg regionu i towaru (słupki grupowane).
    """
    df = _ensure_columns(df)
    goods_col = COL_PRIMARY_BLACK_MARKET_GOODS
    out = OUTPUT_DIR / "chart_black_market_goods_and_inflation.png"
    top_n_regional_goods = 12
    min_count_inflation_cell = 10

    def split_goods(s):
        if pd.isna(s) or not isinstance(s, str):
            return []
        return [g.strip().lower() for g in s.split(",") if g.strip()]

    def empty_grid(msg: str) -> None:
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        for ax in axes.flat:
            ax.set_title(msg)
            ax.axis("off")
        plt.tight_layout()
        save_figure(fig, out)

    if goods_col not in df.columns:
        empty_grid("Brak kolumny Primary_Black_Market_Goods")
        return out

    use_cols = [goods_col, COL_INFLATION]
    if COL_REGION in df.columns:
        use_cols.append(COL_REGION)
    plot_df = df[use_cols].copy()
    plot_df["good"] = plot_df[goods_col].apply(split_goods)
    exploded = plot_df.explode("good").dropna(subset=["good"])
    exploded = exploded[exploded["good"] != ""]
    if exploded.empty:
        empty_grid("Brak danych o towarach")
        return out

    exploded["good_label"] = exploded["good"].str.capitalize()
    counts = exploded["good_label"].value_counts()
    pct = (counts / counts.sum() * 100).sort_values(ascending=False)
    top_goods = pct.head(top_n_regional_goods).index.tolist()
    exp_top = exploded[exploded["good_label"].isin(top_goods)].copy()
    good_colors = plt.cm.tab20(np.linspace(0, 1, max(len(top_goods), 1)))

    regions_ordered = []
    if COL_REGION in exp_top.columns and exp_top[COL_REGION].notna().any():
        regions_ordered = (
            exp_top.groupby(COL_REGION, observed=False)
            .size()
            .sort_values(ascending=False)
            .index.tolist()
        )

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    ax_tl, ax_tr, ax_bl, ax_br = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    x_pos = np.arange(len(pct))
    bars = ax_tl.bar(x_pos, pct.values, color="steelblue", edgecolor="white")
    ax_tl.bar_label(bars, labels=[f"{v:.2f}%" for v in pct.values], padding=3, fontsize=8)
    ax_tl.set_xticks(x_pos)
    ax_tl.set_xticklabels(pct.index, rotation=25, ha="right", fontsize=8)
    ax_tl.set_ylabel("Odsetek wystąpień (%)")
    ax_tl.set_xlabel("Towar na czarnym rynku")
    ax_tl.set_title(
        "Częstotliwość handlu towarami (cały zbiór)\n"
        "Teza: Jakimi towarami handluje się najczęściej na czarnym rynku?"
    )
    m0, M0 = pct.min(), pct.max()
    ax_tl.set_ylim(max(0, m0 - 0.5), M0 + 0.5)
    ax_tl.grid(True, alpha=0.3, axis="y")

    if regions_ordered:
        mat_freq = np.zeros((len(regions_ordered), len(top_goods)))
        for i, reg in enumerate(regions_ordered):
            sub = exp_top[exp_top[COL_REGION] == reg]
            if sub.empty:
                continue
            vc = sub["good_label"].value_counts(normalize=True) * 100
            for j, g in enumerate(top_goods):
                mat_freq[i, j] = float(vc.get(g, 0.0))
        n_reg = len(regions_ordered)
        n_g = len(top_goods)
        x_reg = np.arange(n_reg)
        bar_w = 0.82 / max(n_g, 1)
        for j, gname in enumerate(top_goods):
            off = (j - (n_g - 1) / 2) * bar_w
            ax_tr.bar(
                x_reg + off,
                mat_freq[:, j],
                width=bar_w * 0.92,
                label=gname,
                color=good_colors[j % len(good_colors)],
                edgecolor="white",
                linewidth=0.35,
            )
        ax_tr.set_xticks(x_reg)
        ax_tr.set_xticklabels(regions_ordered, rotation=22, ha="right", fontsize=9)
        ax_tr.set_xlabel("Region")
        ax_tr.set_ylabel("% w obrębie regionu (wśród top towarów)")
        ax_tr.set_title(
            "Częstotliwość towarów według regionu - słupki per towar\n"
            f"Każdy region: udział towaru wśród wystąpień z top {len(top_goods)} towarów (wiersz ≈ 100 %)."
        )
        ax_tr.legend(
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            fontsize=6,
            title="Towar",
            title_fontsize=7,
        )
        ax_tr.grid(True, alpha=0.3, axis="y")
        ax_tr.set_ylim(0, max(float(mat_freq.max()) * 1.08, 1.0))
    else:
        ax_tr.set_title("Brak kolumny Region - brak podziału geograficznego")
        ax_tr.axis("off")

    if COL_INFLATION in exploded.columns and exploded[COL_INFLATION].notna().any():
        inf_by_good = (
            exploded.groupby("good_label", observed=False)[COL_INFLATION]
            .agg(["mean", "count"])
            .dropna(subset=["mean"])
        )
        inf_by_good = inf_by_good[inf_by_good["count"] >= min_count_inflation_cell].sort_values("mean", ascending=False)
        if not inf_by_good.empty:
            x_pos2 = np.arange(len(inf_by_good))
            bars2 = ax_bl.bar(x_pos2, inf_by_good["mean"].values, color="coral", edgecolor="white")
            ax_bl.bar_label(bars2, labels=[f"{v:.2f}%" for v in inf_by_good["mean"].values], padding=3, fontsize=7)
            ax_bl.set_xticks(x_pos2)
            ax_bl.set_xticklabels(inf_by_good.index, rotation=25, ha="right", fontsize=8)
            ax_bl.set_ylabel("Średnia inflacja (%)")
            ax_bl.set_xlabel("Towar na czarnym rynku")
            ax_bl.set_title(
                "Średnia inflacja przy wystąpieniu towaru (cały zbiór)\n"
                "Teza: Związek inflacji z handlem danym towarem (tylko towary z n ≥ "
                f"{min_count_inflation_cell})."
            )
            m, M = inf_by_good["mean"].min(), inf_by_good["mean"].max()
            ax_bl.set_ylim(m - 0.2, M + 0.2)
            ax_bl.grid(True, alpha=0.3, axis="y")
        else:
            ax_bl.set_title("Za mało obserwacji z inflacją dla poszczególnych towarów")
            ax_bl.axis("off")
    else:
        ax_bl.set_title("Brak danych o inflacji")
        ax_bl.axis("off")

    if (
        regions_ordered
        and COL_INFLATION in exp_top.columns
        and exp_top[COL_INFLATION].notna().any()
    ):
        agg_rg = (
            exp_top.groupby([COL_REGION, "good_label"], observed=False)[COL_INFLATION]
            .agg(["mean", "count"])
        )
        means = agg_rg["mean"].where(agg_rg["count"] >= min_count_inflation_cell)
        pivot_inf = means.unstack(fill_value=np.nan)
        pivot_inf = pivot_inf.reindex(index=regions_ordered, columns=top_goods)
        mat_inf = pivot_inf.to_numpy(dtype=float)
        valid = np.isfinite(mat_inf)
        heights = np.where(valid, mat_inf, 0.0)
        if not valid.any():
            ax_br.set_title(
                f"Brak danych (region x towar, n ≥ {min_count_inflation_cell})"
            )
            ax_br.axis("off")
        else:
            n_reg = len(regions_ordered)
            n_g = len(top_goods)
            x_reg = np.arange(n_reg)
            bar_w = 0.82 / max(n_g, 1)
            for j, gname in enumerate(top_goods):
                off = (j - (n_g - 1) / 2) * bar_w
                ax_br.bar(
                    x_reg + off,
                    heights[:, j],
                    width=bar_w * 0.92,
                    label=gname,
                    color=good_colors[j % len(good_colors)],
                    edgecolor="white",
                    linewidth=0.35,
                )
            ax_br.set_xticks(x_reg)
            ax_br.set_xticklabels(regions_ordered, rotation=22, ha="right", fontsize=9)
            ax_br.set_xlabel("Region")
            ax_br.set_ylabel("Średnia inflacja (%)")
            ax_br.set_title(
                "Średnia inflacja według regionu i towaru - słupki per towar\n"
                f"Brak słupka (wys. 0) = n < {min_count_inflation_cell} lub brak pary region-towar."
            )
            ax_br.legend(
                bbox_to_anchor=(1.02, 1),
                loc="upper left",
                fontsize=6,
                title="Towar",
                title_fontsize=7,
            )
            ax_br.grid(True, alpha=0.3, axis="y")
            hi = float(np.nanmax(mat_inf))
            lo = float(np.nanmin(mat_inf[np.isfinite(mat_inf)]))
            pad = max(0.15, (hi - lo) * 0.08) if hi > lo else 1.0
            ax_br.set_ylim(max(0, lo - pad), hi + pad)
    else:
        ax_br.set_title("Brak danych do wykresu inflacji wg regionu")
        ax_br.axis("off")

    plt.tight_layout(rect=[0, 0, 0.83, 1])
    save_figure(fig, out)
    return out


def build_all_charts(df: pd.DataFrame) -> list[Path]:
    paths = []
    paths.append(chart_scatter_gdp_vs_informality_growth(df))
    paths.append(chart_informal_pre_vs_during_by_region(df))
    paths.append(chart_informality_growth_by_region(df))
    paths.append(chart_informality_growth_by_war_duration(df))
    paths.append(chart_black_market_level_by_region_and_period(df))
    paths.append(chart_black_market_goods_and_inflation(df))
    return paths
