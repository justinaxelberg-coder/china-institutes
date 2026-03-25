"""
visualization/temporal_trends.py
==================================
Longitudinal change plots for scores and topic trends.

Functions
---------
    plot_institute_trends(temporal_df, score_col, ...)
        Line plot: annual mean score per institute, with LOWESS smoothing.
    plot_topic_trends(temporal_df, ...)
        Multi-panel line chart: one panel per topic, one line per institute.

Dependencies: matplotlib, seaborn, pandas, numpy.
Optional: statsmodels (for LOWESS smoothing).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_ROOT    = Path(__file__).resolve().parents[2]
_FIG_DIR = _ROOT / "outputs" / "figures"
_FIG_DIR.mkdir(parents=True, exist_ok=True)

try:
    import seaborn as sns
    sns.set_theme(style="whitegrid", font_scale=0.85)
    _SNS = True
except ImportError:
    _SNS = False

try:
    from statsmodels.nonparametric.smoothers_lowess import lowess as _lowess_fn
    _LOWESS = True
except ImportError:
    _LOWESS = False


def _resolve_save(save_path: str | Path | None, default_name: str) -> Path:
    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return _FIG_DIR / default_name


def _rolling_mean(years: np.ndarray, values: np.ndarray, window: int = 3) -> np.ndarray:
    """Simple rolling mean as LOWESS fallback."""
    s = pd.Series(values, index=years)
    return s.rolling(window, min_periods=1, center=True).mean().values


def plot_institute_trends(
    temporal_df:      pd.DataFrame,
    score_col:        str              = "score",
    year_col:         str              = "year",
    institute_col:    str              = "institute_id",
    highlight:        list[str]        = (),
    n_highlight:      int              = 8,
    smooth:           bool             = True,
    title:            str              = "Institute Score Trends Over Time",
    figsize:          tuple[int, int]  = (13, 7),
    save_path:        str | Path | None = None,
    show:             bool             = False,
    dpi:              int              = 300,
) -> Path:
    """
    Line plot of annual mean score per institute.

    Parameters
    ----------
    temporal_df   : long-format DataFrame with year, institute_id, score columns
    score_col     : score column name (e.g. "score", "composite_score")
    year_col      : year column name
    institute_col : institute identifier column
    highlight     : specific institutes to draw in bold; if empty, picks top/bottom n
    n_highlight   : number of most-extreme institutes to highlight (if highlight empty)
    smooth        : apply LOWESS / rolling smoothing to lines
    title         : plot title
    figsize       : (width, height) inches
    save_path     : output path; defaults to outputs/figures/
    show          : whether to call plt.show()
    dpi           : output resolution

    Returns
    -------
    Path to saved figure.
    """
    df = temporal_df.dropna(subset=[year_col, score_col]).copy()
    df[year_col]  = df[year_col].astype(int)
    df[score_col] = pd.to_numeric(df[score_col], errors="coerce")

    # Annual mean per institute
    annual = (df.groupby([institute_col, year_col])[score_col]
                .mean().reset_index())

    all_insts = annual[institute_col].unique().tolist()

    # Choose institutes to highlight
    if not highlight:
        inst_means = annual.groupby(institute_col)[score_col].mean()
        top = inst_means.nlargest(n_highlight // 2).index.tolist()
        bot = inst_means.nsmallest(n_highlight // 2).index.tolist()
        highlight = list(set(top + bot))

    cmap = plt.get_cmap("tab20")

    fig, ax = plt.subplots(figsize=figsize)

    for i, inst in enumerate(all_insts):
        sub   = annual[annual[institute_col] == inst].sort_values(year_col)
        years = sub[year_col].values
        vals  = sub[score_col].values
        if len(years) < 2:
            continue
        is_hl = inst in highlight
        color = cmap(highlight.index(inst) / max(len(highlight) - 1, 1)) if is_hl else "lightgrey"
        lw    = 1.5 if is_hl else 0.4
        alpha = 0.9 if is_hl else 0.3
        zord  = 3 if is_hl else 1

        if smooth and len(years) >= 3:
            if _LOWESS:
                smoothed = _lowess_fn(vals, years, frac=0.6, return_sorted=False)
            else:
                smoothed = _rolling_mean(years, vals)
            ax.plot(years, smoothed, color=color, linewidth=lw, alpha=alpha, zorder=zord)
        else:
            ax.plot(years, vals, color=color, linewidth=lw, alpha=alpha, zorder=zord)

        if is_hl:
            ax.text(years[-1] + 0.1, float(vals[-1]), inst,
                    fontsize=6, color=color, va="center")

    ax.axhline(0, color="black", linewidth=0.6, linestyle="--", alpha=0.4)
    ax.set_xlabel(year_col, fontsize=9)
    ax.set_ylabel(f"{score_col}  (−1 cooperative ↔ +1 hawkish)", fontsize=9)
    ax.set_title(title, fontsize=10, pad=10)

    plt.tight_layout()
    out = _resolve_save(save_path, "institute_score_trends.pdf")
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return out


def plot_topic_trends(
    temporal_df:   pd.DataFrame,
    topic_col:     str              = "topic",
    year_col:      str              = "year",
    value_col:     str              = "proportion",
    institute_col: str              = "institute_id",
    topics:        list[str] | None = None,
    n_cols:        int              = 3,
    title:         str              = "Sensitive Topic Coverage Over Time",
    figsize:       tuple[int, int]  = (15, 10),
    save_path:     str | Path | None = None,
    show:          bool             = False,
    dpi:           int              = 300,
) -> Path:
    """
    Multi-panel chart: one panel per topic, one line per institute.

    Parameters
    ----------
    temporal_df   : long-format from sensitive_topics.coverage_metrics.coverage_temporal()
    topic_col     : column name for topic
    year_col      : column name for year
    value_col     : column name for proportion (y-axis)
    institute_col : column name for institute
    topics        : specific topics to plot; defaults to all
    n_cols        : number of subplot columns
    title         : overall figure title
    figsize       : (width, height) inches
    save_path     : output path
    show          : whether to call plt.show()
    dpi           : output resolution

    Returns
    -------
    Path to saved figure.
    """
    df = temporal_df.dropna(subset=[year_col, value_col]).copy()
    df[year_col]  = df[year_col].astype(int)
    df[value_col] = pd.to_numeric(df[value_col], errors="coerce")

    topics_list = topics or sorted(df[topic_col].unique().tolist())
    n_topics    = len(topics_list)
    n_rows      = int(np.ceil(n_topics / n_cols))

    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize,
                              sharex=False, sharey=True)
    axes_flat = axes.flatten() if n_topics > 1 else [axes]

    all_insts = df[institute_col].unique().tolist()
    cmap      = plt.get_cmap("tab20")

    for ax_idx, topic in enumerate(topics_list):
        ax    = axes_flat[ax_idx]
        sub   = df[df[topic_col] == topic]
        for i, inst in enumerate(all_insts):
            isub  = sub[sub[institute_col] == inst].sort_values(year_col)
            if len(isub) < 2:
                continue
            ax.plot(isub[year_col].values, isub[value_col].values,
                    color=cmap(i / max(len(all_insts) - 1, 1)),
                    linewidth=0.7, alpha=0.5)
        ax.set_title(topic.replace("_", " ").title(), fontsize=8)
        ax.set_xlabel("")
        ax.tick_params(axis="both", labelsize=6)

    # Hide unused panels
    for ax in axes_flat[n_topics:]:
        ax.set_visible(False)

    fig.suptitle(title, fontsize=10, y=1.01)
    fig.text(0.5, -0.01, "Year", ha="center", fontsize=9)
    fig.text(-0.01, 0.5, value_col.replace("_", " ").title(),
             va="center", rotation="vertical", fontsize=9)
    plt.tight_layout()

    out = _resolve_save(save_path, "topic_coverage_trends.pdf")
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return out
