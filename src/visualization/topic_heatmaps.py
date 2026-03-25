"""
visualization/topic_heatmaps.py
================================
Topic × institute heatmap visualisations with optional dendrograms.

Functions
---------
    plot_topic_institute_heatmap(pivot_df, ...)
        BERTopic / thematic topics (rows) × institutes (columns).
    plot_sensitive_topic_heatmap(coverage_df, topic_names, ...)
        Sensitive topics × institutes, colour = mention proportion.

Dependencies: matplotlib, seaborn, scipy (for dendrograms), pandas.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.cluster import hierarchy
from scipy.spatial.distance import pdist

_ROOT    = Path(__file__).resolve().parents[2]
_FIG_DIR = _ROOT / "outputs" / "figures"
_FIG_DIR.mkdir(parents=True, exist_ok=True)

try:
    import seaborn as sns
    _SNS = True
except ImportError:
    _SNS = False


def _resolve_save(save_path: str | Path | None, default_name: str) -> Path:
    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return _FIG_DIR / default_name


def _cluster_order(matrix: np.ndarray, axis: int = 0) -> list[int]:
    """Return row (axis=0) or column (axis=1) indices in hierarchical cluster order."""
    data = matrix if axis == 0 else matrix.T
    data = np.nan_to_num(data)
    if data.shape[0] < 2:
        return list(range(data.shape[0]))
    dist   = pdist(data, metric="euclidean")
    link   = hierarchy.linkage(dist, method="ward")
    leaves = hierarchy.leaves_list(hierarchy.optimal_leaf_ordering(link, dist))
    return list(leaves)


def plot_topic_institute_heatmap(
    pivot_df:    pd.DataFrame,
    value_label: str              = "Share of documents (%)",
    title:       str              = "Thematic Topic Coverage by Institute",
    cmap:        str              = "YlOrRd",
    figsize:     tuple[int, int]  = (16, 8),
    cluster:     bool             = True,
    fmt:         str              = ".1f",
    scale_pct:   bool             = True,
    save_path:   str | Path | None = None,
    show:        bool             = False,
    dpi:         int              = 300,
) -> Path:
    """
    Heatmap of topic prevalence: rows = topics, columns = institutes.

    Parameters
    ----------
    pivot_df   : DataFrame with topics as index, institute IDs as columns,
                 values = proportion [0, 1] or share [0, 100]
    value_label: colour bar label
    title      : plot title
    cmap       : matplotlib colour map
    figsize    : (width, height) inches
    cluster    : whether to apply hierarchical clustering to both axes
    fmt        : cell annotation format (e.g. ".1f" for 1 decimal)
    scale_pct  : if True and values ≤ 1, multiply by 100 for display
    save_path  : output path; defaults to outputs/figures/
    show       : whether to call plt.show()
    dpi        : output resolution

    Returns
    -------
    Path to saved figure.
    """
    df = pivot_df.copy().astype(float)
    if scale_pct and df.values.max() <= 1.0 + 1e-6:
        df = df * 100

    mat = df.values
    row_labels = list(df.index.astype(str))
    col_labels = list(df.columns.astype(str))

    if cluster and len(row_labels) > 1 and len(col_labels) > 1:
        row_ord = _cluster_order(mat, axis=0)
        col_ord = _cluster_order(mat, axis=1)
        mat        = mat[np.ix_(row_ord, col_ord)]
        row_labels = [row_labels[i] for i in row_ord]
        col_labels = [col_labels[i] for i in col_ord]

    if _SNS:
        fig, ax = plt.subplots(figsize=figsize)
        sns.heatmap(
            pd.DataFrame(mat, index=row_labels, columns=col_labels),
            ax=ax, cmap=cmap, annot=len(row_labels) <= 20,
            fmt=fmt, linewidths=0.3, linecolor="white",
            cbar_kws={"label": value_label, "shrink": 0.6},
        )
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=7)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0,  fontsize=7)
        ax.set_title(title, fontsize=10, pad=12)
    else:
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(mat, aspect="auto", cmap=cmap)
        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(row_labels)))
        ax.set_yticklabels(row_labels, fontsize=7)
        fig.colorbar(im, ax=ax, label=value_label, shrink=0.6)
        ax.set_title(title, fontsize=10)

    plt.tight_layout()
    out = _resolve_save(save_path, "topic_institute_heatmap.pdf")
    fig.savefig(out, dpi=dpi, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
    return out


def plot_sensitive_topic_heatmap(
    coverage_df:  pd.DataFrame,
    topic_names:  list[str] | None = None,
    inst_col:     str              = "institute_id",
    value_suffix: str              = "_proportion",
    title:        str              = "Sensitive Topic Coverage by Institute (%)",
    cmap:         str              = "Reds",
    figsize:      tuple[int, int]  = (16, 7),
    cluster:      bool             = True,
    save_path:    str | Path | None = None,
    show:         bool             = False,
    dpi:          int              = 300,
) -> Path:
    """
    Heatmap of sensitive topic mention proportions: topics × institutes.

    Parameters
    ----------
    coverage_df  : output of sensitive_topics.coverage_metrics.compute_coverage()
    topic_names  : list of topic slugs; auto-detected from ``_proportion`` columns
    inst_col     : institute identifier column
    value_suffix : suffix pattern used to find value columns
    title        : plot title
    cmap         : matplotlib colour map (default: "Reds")
    figsize      : (width, height) inches
    cluster      : apply hierarchical clustering to both axes
    save_path    : output path
    show         : whether to call plt.show()
    dpi          : output resolution

    Returns
    -------
    Path to saved figure.
    """
    if topic_names is None:
        topic_names = [
            c.replace(value_suffix, "")
            for c in coverage_df.columns
            if c.endswith(value_suffix) and c != f"total_docs{value_suffix}"
        ]
    if not topic_names:
        raise ValueError(f"No '{value_suffix}' columns found in coverage_df.")

    prop_cols = [f"{t}{value_suffix}" for t in topic_names
                 if f"{t}{value_suffix}" in coverage_df.columns]

    pivot = (
        coverage_df.set_index(inst_col)[prop_cols]
        .rename(columns=lambda c: c.replace(value_suffix, ""))
        .T   # topics as rows, institutes as columns
    )
    pivot = pivot.fillna(0) * 100   # to percentage

    return plot_topic_institute_heatmap(
        pivot_df    = pivot,
        value_label = "Mention rate (%)",
        title       = title,
        cmap        = cmap,
        figsize     = figsize,
        cluster     = cluster,
        fmt         = ".1f",
        scale_pct   = False,
        save_path   = save_path or str(_FIG_DIR / "sensitive_topic_heatmap.pdf"),
        show        = show,
        dpi         = dpi,
    )
