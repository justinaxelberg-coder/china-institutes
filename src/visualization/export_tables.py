"""
visualization/export_tables.py
================================
Publication-ready table export (CSV + LaTeX).

Functions
---------
    export_main_results_table(institute_df, ...)
        Institute scores, ranks, confidence intervals — one row per institute.
    export_method_comparison_table(correlation_dict, ...)
        Cross-method Pearson/Spearman matrix as LaTeX table.
    export_sensitive_coverage_table(coverage_df, ...)
        Sensitive topic coverage proportions — institutes × topics.

Dependencies: pandas, numpy.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

_ROOT    = Path(__file__).resolve().parents[2]
_TAB_DIR = _ROOT / "outputs" / "tables"
_TAB_DIR.mkdir(parents=True, exist_ok=True)


def _resolve(save_path: str | Path | None, default_name: str) -> Path:
    if save_path:
        p = Path(save_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    return _TAB_DIR / default_name


# ── Main results table ────────────────────────────────────────────────────────

def export_main_results_table(
    institute_df: pd.DataFrame,
    score_col:    str              = "composite_score",
    ci_lower_col: str | None       = None,
    ci_upper_col: str | None       = None,
    label_col:    str              = "institute_id",
    extra_cols:   list[str]        = (),
    save_csv:     str | Path | None = None,
    save_latex:   str | Path | None = None,
    caption:      str              = "Institute Positions on the Cooperation–Hawkishness Spectrum",
    label:        str              = "tab:institute_scores",
) -> dict[str, Path]:
    """
    Export institute scores table in CSV and LaTeX format.

    The table is sorted by composite_score (most hawkish first) and includes
    rank, institute label, score, CI, total_docs, and any extra columns.

    Parameters
    ----------
    institute_df : institute-level DataFrame
    score_col    : primary score column
    ci_lower_col : lower CI column; auto-detected as {score_col}_ci_lower
    ci_upper_col : upper CI column; auto-detected as {score_col}_ci_upper
    label_col    : institute label column (display name)
    extra_cols   : additional columns to include (e.g. cluster_label)
    save_csv     : CSV output path; defaults to outputs/tables/
    save_latex   : LaTeX output path; defaults to outputs/tables/
    caption      : LaTeX table caption
    label        : LaTeX table label

    Returns
    -------
    {"csv": Path, "latex": Path}
    """
    lo_col = ci_lower_col or f"{score_col}_ci_lower"
    hi_col = ci_upper_col or f"{score_col}_ci_upper"

    df = institute_df.sort_values(score_col, ascending=False).copy().reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))

    base_cols = ["rank", label_col, "total_docs", score_col]
    if lo_col in df.columns and hi_col in df.columns:
        df["95%_CI"] = df.apply(
            lambda r: f"[{r[lo_col]:.3f}, {r[hi_col]:.3f}]", axis=1
        )
        base_cols.append("95%_CI")
    base_cols += [c for c in extra_cols if c in df.columns]

    out_df = df[[c for c in base_cols if c in df.columns]].copy()
    out_df[score_col] = out_df[score_col].round(3)

    # CSV
    csv_path = _resolve(save_csv, "institute_scores.csv")
    out_df.to_csv(csv_path, index=False)

    # LaTeX
    latex_path = _resolve(save_latex, "institute_scores.tex")
    col_format = "r" + "l" + "r" * (len(out_df.columns) - 2)
    latex_str  = out_df.to_latex(
        index=False, escape=True, column_format=col_format,
        caption=caption, label=label,
        float_format="%.3f",
    )
    latex_path.write_text(latex_str, encoding="utf-8")

    return {"csv": csv_path, "latex": latex_path}


# ── Method comparison table ────────────────────────────────────────────────────

def export_method_comparison_table(
    correlation_dict: dict[str, pd.DataFrame],
    save_csv:         str | Path | None = None,
    save_latex:       str | Path | None = None,
    caption:          str = "Cross-Method Pearson Correlations (Institute-Level Means)",
    label:            str = "tab:method_correlations",
) -> dict[str, Path]:
    """
    Export the cross-method correlation matrix.

    Parameters
    ----------
    correlation_dict : output of aggregation.validation.method_correlation_matrix();
                       must have "pearson" key (also uses "pearson_p" if present)
    save_csv / save_latex : output paths
    caption, label : LaTeX table metadata

    Returns
    -------
    {"csv": Path, "latex": Path}
    """
    r_mat = correlation_dict["pearson"]
    p_mat = correlation_dict.get("pearson_p")

    # Format: r value with significance stars
    def _fmt(r: float, p: float | None) -> str:
        if np.isnan(r):
            return "—"
        s = f"{r:.3f}"
        if p is not None and not np.isnan(p):
            if p < 0.001: s += "***"
            elif p < 0.01: s += "**"
            elif p < 0.05: s += "*"
        return s

    display = r_mat.copy().astype(object)
    for i, ri in enumerate(r_mat.index):
        for j, ci in enumerate(r_mat.columns):
            p = float(p_mat.iloc[i, j]) if p_mat is not None else None
            display.iloc[i, j] = _fmt(float(r_mat.iloc[i, j]), p)

    csv_path = _resolve(save_csv, "method_correlations.csv")
    display.to_csv(csv_path)

    latex_path = _resolve(save_latex, "method_correlations.tex")
    col_fmt   = "l" + "c" * len(display.columns)
    latex_str = (
        "% Significance: *** p<0.001  ** p<0.01  * p<0.05\n" +
        display.to_latex(
            escape=True, column_format=col_fmt,
            caption=caption, label=label,
        )
    )
    latex_path.write_text(latex_str, encoding="utf-8")
    return {"csv": csv_path, "latex": latex_path}


# ── Sensitive topic coverage table ────────────────────────────────────────────

def export_sensitive_coverage_table(
    coverage_df:  pd.DataFrame,
    topic_names:  list[str] | None = None,
    inst_col:     str              = "institute_id",
    value_suffix: str              = "_proportion",
    pct:          bool             = True,
    save_csv:     str | Path | None = None,
    save_latex:   str | Path | None = None,
    caption:      str = "Sensitive Topic Coverage by Institute (% of documents mentioning topic)",
    label:        str = "tab:sensitive_coverage",
    top_n:        int | None       = None,
) -> dict[str, Path]:
    """
    Export sensitive topic coverage matrix: institutes × topics.

    Parameters
    ----------
    coverage_df  : output of sensitive_topics.coverage_metrics.compute_coverage()
    topic_names  : list of topic slugs; auto-detected from _proportion columns
    inst_col     : institute identifier column
    value_suffix : column suffix pattern for proportion columns
    pct          : if True, multiply values by 100 and format as %.1f
    save_csv / save_latex : output paths
    caption, label        : LaTeX table metadata
    top_n        : if set, only include the top_n institutes by sensitive_topic_index

    Returns
    -------
    {"csv": Path, "latex": Path}
    """
    if topic_names is None:
        topic_names = [
            c.replace(value_suffix, "")
            for c in coverage_df.columns
            if c.endswith(value_suffix) and c != f"total_docs{value_suffix}"
        ]

    prop_cols = {t: f"{t}{value_suffix}" for t in topic_names
                 if f"{t}{value_suffix}" in coverage_df.columns}

    df = coverage_df.copy()
    if top_n and "sensitive_topic_index" in df.columns:
        df = df.nlargest(top_n, "sensitive_topic_index")

    df = df.set_index(inst_col)[list(prop_cols.values())].copy()
    df.columns = [t.replace("_", " ").title() for t in prop_cols.keys()]

    if pct:
        df = (df * 100).round(1)

    df = df.sort_values(df.columns.tolist()[0], ascending=False)

    csv_path = _resolve(save_csv, "sensitive_topic_coverage.csv")
    df.to_csv(csv_path)

    latex_path = _resolve(save_latex, "sensitive_topic_coverage.tex")
    col_fmt   = "l" + "r" * len(df.columns)
    latex_str = df.to_latex(
        escape=True, column_format=col_fmt,
        caption=caption, label=label,
        float_format="%.1f",
    )
    latex_path.write_text(latex_str, encoding="utf-8")
    return {"csv": csv_path, "latex": latex_path}
