"""
visualization/spectrum_plots.py
================================
Institute positioning plots on the cooperation–hawkishness spectrum.

Functions
---------
    plot_institute_spectrum(institute_df, score_col, ...)
        Lollipop / dot chart: institutes on y-axis, score on x-axis,
        coloured by cluster. Error bars show 95% CI.
    plot_2d_map(institute_df, x_col, y_col, ...)
        Scatter plot: x = composite score, y = sensitive topic intensity.
        Point size ∝ document count.

Dependencies: matplotlib, seaborn, pandas, numpy.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")   # non-interactive backend for script use
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

_ROOT       = Path(__file__).resolve().parents[2]
_FIG_DIR    = _ROOT / "outputs" / "figures"
_FIG_DIR.mkdir(parents=True, exist_ok=True)

try:
    import seaborn as sns
    sns.set_theme(style="whitegrid", font_scale=0.85)
    _SNS = True
except ImportError:
    _SNS = False

_PALETTE = "RdYlBu_r"   # diverging: red=hawkish, blue=cooperative


def _resolve_save(save_path: str | Path | None, default_name: str) -> Path:
    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return _FIG_DIR / default_name


def plot_institute_spectrum(
    institute_df: pd.DataFrame,
    score_col:    str              = "composite_score",
    ci_lower_col: str | None       = None,
    ci_upper_col: str | None       = None,
    label_col:    str              = "institute_id",
    cluster_col:  str | None       = "cluster_label",
    title:        str              = "Institute Positions on the Cooperation–Hawkishness Spectrum",
    figsize:      tuple[int, int]  = (10, 12),
    save_path:    str | Path | None = None,
    show:         bool             = False,
    dpi:          int              = 300,
) -> Path:
    """
    Horizontal lollipop chart of institute scores on the spectrum.

    Parameters
    ----------
    institute_df : institute-level DataFrame with score and (optionally) CI columns
    score_col    : column for the main score (x-axis)
    ci_lower_col : column for lower CI bound; auto-detected as {score_col}_ci_lower
    ci_upper_col : column for upper CI bound; auto-detected as {score_col}_ci_upper
    label_col    : column for institute labels (y-axis)
    cluster_col  : optional column for colour coding
    title        : plot title
    figsize      : (width, height) in inches
    save_path    : full path to save figure; defaults to outputs/figures/
    show         : whether to call plt.show()
    dpi          : output resolution

    Returns
    -------
    Path to saved figure.
    """
    if score_col not in institute_df.columns:
        raise ValueError(f"Column '{score_col}' not found.")

    df = institute_df.sort_values(score_col, ascending=True).reset_index(drop=True)

    # Auto-detect CI columns
    lo_col = ci_lower_col or f"{score_col}_ci_lower"
    hi_col = ci_upper_col or f"{score_col}_ci_upper"
    has_ci = (lo_col in df.columns) and (hi_col in df.columns)

    scores = df[score_col].values
    labels = df[label_col].astype(str).values
    n      = len(df)

    # Colour by cluster or continuous score
    if cluster_col and cluster_col in df.columns:
        clusters  = df[cluster_col].astype(str)
        uniq      = clusters.unique()
        cmap      = plt.get_cmap("tab10")
        color_map = {c: cmap(i / max(len(uniq) - 1, 1)) for i, c in enumerate(uniq)}
        colors    = [color_map[c] for c in clusters]
    else:
        cmap      = plt.get_cmap(_PALETTE)
        norm      = plt.Normalize(scores.min(), scores.max())
        colors    = [cmap(norm(s)) for s in scores]
        color_map = None

    fig, ax = plt.subplots(figsize=figsize)

    y_pos = np.arange(n)
    ax.hlines(y_pos, 0, scores, colors="lightgrey", linewidth=0.8, zorder=1)
    ax.scatter(scores, y_pos, c=colors, s=60, zorder=3, edgecolors="white", linewidth=0.5)

    if has_ci:
        lo = (scores - df[lo_col].values).clip(0)
        hi = (df[hi_col].values - scores).clip(0)
        ax.errorbar(scores, y_pos, xerr=[lo, hi],
                    fmt="none", ecolor="grey", elinewidth=0.8, capsize=2, zorder=2)

    ax.axvline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_xlabel("Score  (−1 = cooperative  ·  +1 = hawkish/security)", fontsize=9)
    ax.set_title(title, fontsize=10, pad=10)
    ax.set_xlim(-1.15, 1.15)

    # Pole annotations
    ax.text(-1.12, -0.8, "← Cooperative", fontsize=7, color="steelblue", va="bottom")
    ax.text( 0.90, -0.8, "Hawkish →",    fontsize=7, color="tomato",    va="bottom")

    # Legend for clusters
    if color_map:
        handles = [mpatches.Patch(color=c, label=lbl) for lbl, c in color_map.items()]
        ax.legend(handles=handles, title="Cluster", fontsize=7, title_fontsize=7,
                  loc="lower right", framealpha=0.8)

    plt.tight_layout()
    out = _resolve_save(save_path, "spectrum_lollipop.pdf")
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return out


def plot_2d_map(
    institute_df:      pd.DataFrame,
    x_col:             str              = "composite_score",
    y_col:             str              = "sensitive_topic_index",
    size_col:          str | None       = "total_docs",
    label_col:         str              = "institute_id",
    cluster_col:       str | None       = "cluster_label",
    title:             str              = "Institute Map: Spectrum × Sensitive Topic Intensity",
    figsize:           tuple[int, int]  = (11, 8),
    annotate_outliers: int              = 5,
    save_path:         str | Path | None = None,
    show:              bool             = False,
    dpi:               int              = 300,
) -> Path:
    """
    Scatter plot: x = cooperation/security score, y = sensitive topic intensity.
    Point size ∝ document count. Annotates the most extreme institutes.
    """
    for col in (x_col, y_col):
        if col not in institute_df.columns:
            raise ValueError(f"Column '{col}' not found.")

    df = institute_df.dropna(subset=[x_col, y_col]).reset_index(drop=True)

    x      = df[x_col].values
    y      = df[y_col].values
    labels = df[label_col].astype(str).values
    sizes  = (df[size_col].clip(lower=10).values * 1.5
              if size_col and size_col in df.columns
              else np.full(len(df), 60))

    if cluster_col and cluster_col in df.columns:
        clusters = df[cluster_col].astype(str)
        uniq     = clusters.unique()
        cmap     = plt.get_cmap("tab10")
        colors   = [cmap(list(uniq).index(c) / max(len(uniq) - 1, 1)) for c in clusters]
    else:
        cmap   = plt.get_cmap(_PALETTE)
        norm   = plt.Normalize(x.min(), x.max())
        colors = [cmap(norm(xi)) for xi in x]

    fig, ax = plt.subplots(figsize=figsize)

    sc = ax.scatter(x, y, c=colors, s=sizes, alpha=0.75,
                    edgecolors="white", linewidth=0.5, zorder=3)

    # Quadrant lines
    ax.axvline(0, color="grey", linewidth=0.6, linestyle="--", alpha=0.5)
    ax.axhline(float(np.median(y)), color="grey", linewidth=0.6, linestyle="--", alpha=0.5)

    # Annotate top outliers by combined extremity
    extremity = np.abs(x) + np.abs(y - float(np.mean(y)))
    top_n     = np.argsort(extremity)[::-1][:annotate_outliers]
    for idx in top_n:
        ax.annotate(
            labels[idx], (x[idx], y[idx]),
            textcoords="offset points", xytext=(5, 3),
            fontsize=6.5, alpha=0.9,
            arrowprops=dict(arrowstyle="-", color="grey", lw=0.5),
        )

    ax.set_xlabel(f"{x_col}  (−1 cooperative ↔ +1 hawkish)", fontsize=9)
    ax.set_ylabel(f"{y_col}", fontsize=9)
    ax.set_title(title, fontsize=10, pad=10)

    # Size legend
    if size_col and size_col in df.columns:
        for doc_n in [50, 200, 500]:
            ax.scatter([], [], s=doc_n * 1.5, color="grey", alpha=0.5,
                       label=f"{doc_n} docs", edgecolors="white")
        ax.legend(title="Document count", fontsize=7, title_fontsize=7,
                  loc="upper left", framealpha=0.8)

    plt.tight_layout()
    out = _resolve_save(save_path, "spectrum_2d_map.pdf")
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return out
