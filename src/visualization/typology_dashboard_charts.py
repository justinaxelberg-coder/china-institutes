from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


DOMAIN_ORDER: tuple[str, ...] = (
    "security_strategy",
    "economy_trade",
    "science_technology",
    "environment_climate",
    "governance_law",
    "society_culture",
)

DOMAIN_LABELS: dict[str, str] = {
    "security_strategy": "Security & strategy",
    "economy_trade": "Economy & trade",
    "science_technology": "Science & technology",
    "environment_climate": "Environment & climate",
    "governance_law": "Governance & law",
    "society_culture": "Society & culture",
}

MEMBER_TABLE_COLUMNS: tuple[str, ...] = (
    "institute_id",
    "institute_name",
    "region",
    "dominant_domain",
    "theory_typology_confidence",
    "theory_typology_borderline",
    "low_volume_flag",
    "regression_inclusion_status",
)

DRILLDOWN_HEADER_COLUMNS: tuple[str, ...] = (
    "institute_name",
    "theory_typology",
    "cluster_label",
    "dominant_domain",
    "theory_typology_confidence",
    "theory_typology_borderline",
    "region",
    "total_docs",
    "parent_institution",
    "institute_type_category",
    "theory_typology_borderline_badge",
    "low_volume_badge",
    "regression_inclusion_status",
)


def _format_label(value: str) -> str:
    return DOMAIN_LABELS.get(value, str(value).replace("_", " ").title())


def _ordered_typologies(frame: pd.DataFrame) -> list[str]:
    counts = (
        frame["theory_typology"]
        .fillna("Unassigned")
        .value_counts()
        .sort_values(ascending=False)
    )
    return counts.index.tolist()


def _require_columns(frame: pd.DataFrame, columns: tuple[str, ...] | list[str], *, label: str) -> None:
    missing = sorted(col for col in columns if col not in frame.columns)
    if missing:
        raise ValueError(f"Missing {label} columns: {', '.join(missing)}")


def _resolve_institute_row(frame: pd.DataFrame, institute_id: str | None = None, institute_name: str | None = None) -> pd.Series:
    if institute_id is None and institute_name is None:
        raise ValueError("Provide institute_id or institute_name")
    if institute_id is not None:
        matches = frame.loc[frame["institute_id"].eq(institute_id)]
    else:
        matches = frame.loc[frame["institute_name"].eq(institute_name)]
        if len(matches) > 1:
            raise ValueError("Institute name is not unique; resolve the institute by institute_id")
    if matches.empty:
        raise ValueError("Requested institute was not found in the typology frame")
    return matches.iloc[0]


def build_typology_kpis(frame: pd.DataFrame) -> dict[str, Any]:
    _require_columns(
        frame,
        [
            "institute_id",
            "total_docs",
            "theory_typology",
            "theory_typology_borderline",
            "low_volume_flag",
            "regression_inclusion_status",
        ],
        label="typology KPI",
    )
    institutes = int(frame["institute_id"].nunique())
    docs_total = int(frame["total_docs"].fillna(0).sum())
    low_volume = int(frame["low_volume_flag"].fillna(False).sum())
    borderline = int(frame["theory_typology_borderline"].fillna(False).sum())
    ready = int(frame["regression_inclusion_status"].eq("included_in_regression").sum())
    top_typology = (
        frame["theory_typology"].mode(dropna=True).iloc[0]
        if frame["theory_typology"].dropna().any()
        else "NA"
    )
    return {
        "institutes": institutes,
        "docs_total": docs_total,
        "low_volume_institutes": low_volume,
        "borderline_typologies": borderline,
        "model_ready_institutes": ready,
        "top_typology": top_typology,
    }


def build_typology_field_map() -> pd.DataFrame:
    rows = [
        ("Explorer", "institute_name", "Institute", "Display name used in dashboard tables and drill-down."),
        ("Explorer", "region", "Region", "Region bucket carried from the typology model data."),
        ("Explorer", "dominant_domain", "Dominant domain", "Highest-salience issue domain for the institute."),
        ("Explorer", "theory_typology_confidence", "Typology confidence", "Confidence score attached to the theory-led typology."),
        ("Explorer", "theory_typology_borderline", "Borderline typology", "Marks institutes close to a typology decision boundary."),
        ("Explorer", "low_volume_flag", "Low volume", "Flags institutes with low document volume."),
        ("Explorer", "regression_inclusion_status", "Regression inclusion", "Derived model-readiness flag based on low volume."),
        ("Drill-down", "cluster_label", "Cluster label", "Cluster assignment used for robustness comparison."),
        ("Drill-down", "parent_institution", "Parent institution", "Top-level institution or university host."),
        ("Drill-down", "institute_type_category", "Institute type", "High-level institute category used in explanatory work."),
        ("Charts", "<domain>_salience_share", "Domain salience", "Share of institute documents assigned to each domain."),
        ("Charts", "<domain>_rival_among_oriented", "Within-domain rival share", "Rival share among oriented documents inside a domain."),
        ("Charts", "<domain>_collaborator_among_oriented", "Within-domain collaborator share", "Collaborator share among oriented documents inside a domain."),
    ]
    return pd.DataFrame(rows, columns=["section", "field", "label", "description"])


def build_dominant_domain_composition_chart(frame: pd.DataFrame) -> go.Figure:
    _require_columns(frame, ["theory_typology", "dominant_domain", "institute_id"], label="composition chart")
    plot_df = (
        frame.assign(
            theory_typology=frame["theory_typology"].fillna("Unassigned"),
            dominant_domain_label=frame["dominant_domain"].map(_format_label),
        )
        .groupby(["theory_typology", "dominant_domain_label"], observed=True)["institute_id"]
        .nunique()
        .reset_index(name="n_institutes")
    )
    typology_order = _ordered_typologies(frame)
    plot_df["theory_typology"] = pd.Categorical(plot_df["theory_typology"], categories=typology_order, ordered=True)
    fig = px.bar(
        plot_df.sort_values(["theory_typology", "dominant_domain_label"]),
        x="theory_typology",
        y="n_institutes",
        color="dominant_domain_label",
        title="Dominant Domain Composition by Typology",
        labels={"theory_typology": "", "n_institutes": "Institutes", "dominant_domain_label": "Dominant domain"},
    )
    fig.update_layout(barmode="stack", legend_title_text="", height=430)
    return fig


def build_typology_profile_heatmap(frame: pd.DataFrame) -> go.Figure:
    salience_cols = [f"{domain}_salience_share" for domain in DOMAIN_ORDER]
    _require_columns(frame, ["theory_typology", *salience_cols], label="profile heatmap")
    plot_df = frame[["theory_typology", *salience_cols]].copy()
    plot_df["theory_typology"] = plot_df["theory_typology"].fillna("Unassigned")
    grouped = (
        plot_df.groupby("theory_typology", observed=True)[salience_cols]
        .mean()
        .reindex(_ordered_typologies(plot_df))
    )
    heatmap = go.Heatmap(
        z=grouped.values,
        x=[_format_label(col.removesuffix("_salience_share")) for col in grouped.columns],
        y=grouped.index.tolist(),
        colorscale="Blues",
        zmin=0.0,
        zmax=max(float(grouped.max().max()), 0.01),
        colorbar={"title": "Mean share"},
        hovertemplate="Typology=%{y}<br>Domain=%{x}<br>Mean share=%{z:.2f}<extra></extra>",
    )
    fig = go.Figure(data=[heatmap])
    fig.update_layout(title="Typology Profile Matrix", height=430, xaxis_title="", yaxis_title="")
    return fig


def build_institute_domain_salience_chart(frame: pd.DataFrame, *, institute_id: str | None = None, institute_name: str | None = None) -> go.Figure:
    salience_cols = [f"{domain}_salience_share" for domain in DOMAIN_ORDER]
    _require_columns(frame, ["institute_id", "institute_name", *salience_cols], label="salience chart")
    row = _resolve_institute_row(frame, institute_id=institute_id, institute_name=institute_name)
    plot_df = pd.DataFrame(
        {
            "domain": [_format_label(domain) for domain in DOMAIN_ORDER],
            "salience_share": [float(row.get(f"{domain}_salience_share", 0.0) or 0.0) for domain in DOMAIN_ORDER],
        }
    )
    fig = px.bar(
        plot_df,
        x="domain",
        y="salience_share",
        title=f"Domain Salience: {row['institute_name']}",
        labels={"domain": "", "salience_share": "Share of documents"},
    )
    fig.update_layout(showlegend=False, height=360)
    return fig


def build_institute_within_domain_orientation_chart(
    frame: pd.DataFrame,
    *,
    institute_id: str | None = None,
    institute_name: str | None = None,
) -> go.Figure:
    _require_columns(
        frame,
        ["institute_id", "institute_name", "dominant_domain", *[f"{domain}_rival_among_oriented" for domain in DOMAIN_ORDER], *[f"{domain}_collaborator_among_oriented" for domain in DOMAIN_ORDER]],
        label="within-domain orientation chart",
    )
    row = _resolve_institute_row(frame, institute_id=institute_id, institute_name=institute_name)
    domain = str(row["dominant_domain"])
    rival_value = float(row.get(f"{domain}_rival_among_oriented", 0.0) or 0.0)
    collaborator_value = float(row.get(f"{domain}_collaborator_among_oriented", 0.0) or 0.0)
    fig = go.Figure(
        data=[
            go.Bar(
                x=["Rival share", "Collaborator share"],
                y=[rival_value, collaborator_value],
                marker_color=["#b22222", "#2a6f97"],
                hovertemplate="%{x}: %{y:.2f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        title=f"Within-Domain Rival vs Collaborator: {row['institute_name']}",
        xaxis_title="",
        yaxis_title="Share among oriented documents",
        height=340,
    )
    fig.add_annotation(
        x=0.5,
        y=max(rival_value, collaborator_value),
        yshift=18,
        showarrow=False,
        text=f"Dominant domain: {_format_label(domain)}",
    )
    return fig


def build_institute_vs_peer_comparison_chart(
    frame: pd.DataFrame,
    *,
    institute_id: str | None = None,
    institute_name: str | None = None,
) -> go.Figure:
    salience_cols = [f"{domain}_salience_share" for domain in DOMAIN_ORDER]
    _require_columns(frame, ["institute_id", "institute_name", "theory_typology", *salience_cols], label="peer comparison chart")
    row = _resolve_institute_row(frame, institute_id=institute_id, institute_name=institute_name)
    peers = frame.loc[frame["theory_typology"].eq(row["theory_typology"])]
    peer_means = peers[salience_cols].mean().fillna(0.0)
    institute_values = [float(row.get(col, 0.0) or 0.0) for col in salience_cols]
    fig = go.Figure()
    fig.add_bar(
        name=row["institute_name"],
        x=[_format_label(domain) for domain in DOMAIN_ORDER],
        y=institute_values,
        marker_color="#16324f",
    )
    fig.add_bar(
        name=f"Peer mean ({row['theory_typology']})",
        x=[_format_label(domain) for domain in DOMAIN_ORDER],
        y=[float(peer_means[col]) for col in salience_cols],
        marker_color="#9db4c0",
    )
    fig.update_layout(
        title=f"Institute vs Peer Typology Profile: {row['institute_name']}",
        barmode="group",
        xaxis_title="",
        yaxis_title="Domain salience share",
        height=380,
        legend_title_text="",
    )
    return fig


def build_typology_member_table(
    frame: pd.DataFrame,
    *,
    typology: str | None = None,
    dominant_domain: str | None = None,
    region: str | None = None,
    search_text: str = "",
) -> pd.DataFrame:
    _require_columns(frame, ["theory_typology", "dominant_domain", "region", *MEMBER_TABLE_COLUMNS], label="member table")
    out = frame.copy()
    if typology and typology != "All":
        out = out.loc[out["theory_typology"].eq(typology)]
    if dominant_domain and dominant_domain != "All":
        out = out.loc[out["dominant_domain"].eq(dominant_domain)]
    if region and region != "All":
        out = out.loc[out["region"].eq(region)]
    query = search_text.strip().lower()
    if query:
        out = out.loc[out["institute_name"].fillna("").str.lower().str.contains(query)]
    out = out.loc[:, MEMBER_TABLE_COLUMNS].copy()
    return out.sort_values(["institute_name", "institute_id"]).reset_index(drop=True)


def build_institute_drilldown_summary(
    frame: pd.DataFrame,
    *,
    institute_id: str | None = None,
    institute_name: str | None = None,
) -> dict[str, Any]:
    _require_columns(frame, ["institute_id", "institute_name", *DRILLDOWN_HEADER_COLUMNS[1:]], label="drill-down summary")
    row = _resolve_institute_row(frame, institute_id=institute_id, institute_name=institute_name)
    return {column: row.get(column) for column in DRILLDOWN_HEADER_COLUMNS}


__all__ = [
    "DOMAIN_LABELS",
    "DOMAIN_ORDER",
    "DRILLDOWN_HEADER_COLUMNS",
    "MEMBER_TABLE_COLUMNS",
    "build_dominant_domain_composition_chart",
    "build_institute_domain_salience_chart",
    "build_institute_drilldown_summary",
    "build_institute_vs_peer_comparison_chart",
    "build_institute_within_domain_orientation_chart",
    "build_typology_field_map",
    "build_typology_kpis",
    "build_typology_member_table",
    "build_typology_profile_heatmap",
]
