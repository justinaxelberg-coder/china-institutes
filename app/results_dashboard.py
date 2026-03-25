from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from visualization.typology_dashboard_charts import (
    DOMAIN_LABELS,
    DRILLDOWN_HEADER_COLUMNS,
    MEMBER_TABLE_COLUMNS,
    build_dominant_domain_composition_chart,
    build_institute_domain_salience_chart,
    build_institute_drilldown_summary,
    build_institute_vs_peer_comparison_chart,
    build_institute_within_domain_orientation_chart,
    build_typology_field_map,
    build_typology_kpis,
    build_typology_member_table,
    build_typology_profile_heatmap,
)
from visualization.typology_dashboard_data import (
    build_typology_dashboard_frame,
    load_typology_dashboard_bundle,
)

PANEL_INST_PATH = ROOT / "data" / "processed" / "panel_institute_master.csv"
PANEL_YEAR_PATH = ROOT / "data" / "processed" / "panel_institute_year_master.csv"
PANEL_INST_EMBEDDEDNESS_PATH = ROOT / "data" / "processed" / "panel_institute_master_embeddedness.csv"
PANEL_YEAR_EMBEDDEDNESS_PATH = ROOT / "data" / "processed" / "panel_institute_year_master_embeddedness.csv"
PANEL_MAP_PATH = ROOT / "data" / "processed" / "panel_institute_map.csv"
CI_MODEL_PATH = ROOT / "outputs" / "tables" / "confucius_panel_models.csv"
REGION_MODEL_PATH = ROOT / "outputs" / "tables" / "cooperation_axis_region_models.csv"
CI_CLOSURE_PATH = ROOT / "outputs" / "tables" / "confucius_closure_prepost_by_institute.csv"
WORDFISH_PATH = ROOT / "outputs" / "tables" / "institute_wordfish_confirmation_highsignal.csv"
WORDFISH_SUMMARY_PATH = ROOT / "outputs" / "tables" / "institute_wordfish_confirmation_highsignal_summary.txt"
SOURCE_MODEL_PATH = ROOT / "outputs" / "tables" / "source_type_models.csv"
SOURCE_DESC_PATH = ROOT / "outputs" / "tables" / "source_type_descriptives.csv"

SENSITIVE_FAMILY_SHARE_COLS = [
    "taiwan_cross_strait_share",
    "xinjiang_uyghur_falun_gong_share",
    "hong_kong_tiananmen_share",
    "rights_tiananmen_share",
    "censorship_academic_freedom_share",
]

SENSITIVE_FAMILY_LABELS = {
    "taiwan_cross_strait_share": "Taiwan / Cross-Strait",
    "xinjiang_uyghur_falun_gong_share": "Xinjiang / Uyghur / Falun Gong",
    "hong_kong_tiananmen_share": "Hong Kong / Tiananmen",
    "rights_tiananmen_share": "Rights / Tiananmen",
    "censorship_academic_freedom_share": "Censorship / Academic Freedom",
}

COUNTRY_CENTROIDS = {
    "Australia": (-25.0, 133.0),
    "Brazil": (-14.2, -51.9),
    "Canada": (56.1, -106.3),
    "Chile": (-35.7, -71.5),
    "China": (35.9, 104.2),
    "Denmark": (56.0, 10.0),
    "Ecuador": (-1.8, -78.2),
    "Europe": (50.8, 4.3),
    "France": (46.2, 2.2),
    "Germany": (51.2, 10.4),
    "Global": (46.2, 6.1),
    "Hong Kong": (22.3, 114.2),
    "India": (20.6, 78.9),
    "Italy": (41.9, 12.6),
    "Japan": (36.2, 138.3),
    "Latvia": (56.9, 24.6),
    "Mexico": (23.6, -102.6),
    "Netherlands": (52.1, 5.3),
    "New Zealand": (-41.3, 174.8),
    "Regional network": (50.8, 4.3),
    "Singapore": (1.35, 103.8),
    "South Africa": (-30.6, 22.9),
    "South Korea": (36.5, 127.9),
    "Sweden": (60.1, 18.6),
    "Taiwan": (23.7, 121.0),
    "United Kingdom": (55.0, -3.4),
    "United States": (39.8, -98.6),
}

COUNTRY_OVERRIDES = {
    "Chile / China": "Chile",
    "China / Global": "China",
    "China / United States": "China",
    "Ecuador / China": "Ecuador",
    "France / Hong Kong": "Hong Kong",
    "Hong Kong / United States": "Hong Kong",
    "Mexico / China": "Mexico",
    "United States / Africa-focused": "United States",
    "United States / China": "United States",
    "United States / Global": "United States",
}


def _backfill_dashboard_columns(
    frame: pd.DataFrame,
    *,
    required_cols: list[str],
    alias_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    alias_map = alias_map or {}
    out = frame.copy()
    for dest, source in alias_map.items():
        if dest not in out.columns and source in out.columns:
            out[dest] = out[source]

    for col in required_cols:
        if col in out.columns:
            continue
        if col in alias_map and alias_map[col] in out.columns:
            out[col] = out[alias_map[col]]
        elif col.endswith("_docs") or col == "total_docs":
            out[col] = 0
        else:
            out[col] = np.nan
    return out


def load_panel_frame_with_fallback(
    primary_path: Path,
    fallback_path: Path,
    *,
    required_cols: list[str],
    alias_map: dict[str, str] | None = None,
) -> pd.DataFrame:
    frame = pd.read_csv(primary_path)
    if set(required_cols).issubset(frame.columns):
        return frame

    if fallback_path.exists():
        fallback = pd.read_csv(fallback_path)
        if set(required_cols).issubset(fallback.columns):
            return fallback
        return _backfill_dashboard_columns(
            fallback,
            required_cols=required_cols,
            alias_map=alias_map,
        )

    return _backfill_dashboard_columns(
        frame,
        required_cols=required_cols,
        alias_map=alias_map,
    )


@st.cache_data(show_spinner=False)
def load_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, str],
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame | None,
    str | None,
]:
    inst = load_panel_frame_with_fallback(
        PANEL_INST_PATH,
        PANEL_INST_EMBEDDEDNESS_PATH,
        required_cols=[
            "institute_label",
            "country",
            "region",
            "parent_institution",
            "total_docs",
            "orientation_docs",
            "mean_embedding_score",
            "sensitive_curated_share",
            "sensitive_docs",
            "mean_dictionary_score",
        ],
        alias_map={
            "sensitive_curated_share": "sensitive_topic_share",
        },
    )
    year = load_panel_frame_with_fallback(
        PANEL_YEAR_PATH,
        PANEL_YEAR_EMBEDDEDNESS_PATH,
        required_cols=[
            "institute_label",
            "year",
            "region",
            "total_docs",
            "orientation_docs",
            "mean_embedding_score",
            "sensitive_curated_share",
        ],
        alias_map={
            "sensitive_curated_share": "sensitive_topic_share_x",
        },
    )
    ci_models = pd.read_csv(CI_MODEL_PATH)
    region_models = pd.read_csv(REGION_MODEL_PATH)
    closure = pd.read_csv(CI_CLOSURE_PATH)
    wordfish = pd.read_csv(WORDFISH_PATH) if WORDFISH_PATH.exists() else pd.DataFrame()
    source_models = pd.read_csv(SOURCE_MODEL_PATH) if SOURCE_MODEL_PATH.exists() else pd.DataFrame()
    source_desc = pd.read_csv(SOURCE_DESC_PATH) if SOURCE_DESC_PATH.exists() else pd.DataFrame()
    wordfish_summary: dict[str, str] = {}
    if WORDFISH_SUMMARY_PATH.exists():
        for line in WORDFISH_SUMMARY_PATH.read_text(encoding="utf-8").splitlines():
            if "=" in line:
                key, value = line.split("=", 1)
                wordfish_summary[key.strip()] = value.strip()

    if PANEL_MAP_PATH.exists():
        map_df = pd.read_csv(PANEL_MAP_PATH)
        keep_cols = [
            "institute_id",
            "resolved_ror_id",
            "resolved_ror_name",
            "ror_match_method",
            "ror_match_confidence",
            "ror_city",
            "ror_country_name",
            "ror_country_code",
            "ror_lat",
            "ror_lon",
        ]
        inst = inst.merge(map_df[keep_cols], on="institute_id", how="left")
    else:
        for col in [
            "resolved_ror_id",
            "resolved_ror_name",
            "ror_match_method",
            "ror_match_confidence",
            "ror_city",
            "ror_country_name",
            "ror_country_code",
            "ror_lat",
            "ror_lon",
        ]:
            inst[col] = np.nan

    for df in [inst, year]:
        df["ci_status"] = np.select(
            [
                df["confucius_institute_closed"].fillna("").astype(str).str.lower().eq("yes"),
                df["confucius_institute_present"].fillna("").astype(str).str.lower().eq("yes"),
            ],
            ["Closed", "Present"],
            default="None",
        )
    if not wordfish.empty:
        join_cols = [
            "institute_id",
            "ci_status",
            "confucius_institute_present",
            "confucius_institute_closed",
            "total_docs",
            "orientation_docs",
            "sensitive_curated_share",
        ]
        wordfish = wordfish.merge(inst[join_cols], on="institute_id", how="left")
    typology_frame: pd.DataFrame | None = None
    typology_error: str | None = None
    try:
        typology_frame = build_typology_dashboard_frame(load_typology_dashboard_bundle(ROOT))
    except Exception as exc:  # pragma: no cover - dashboard fallback path
        typology_error = str(exc)
    return (
        inst,
        year,
        ci_models,
        region_models,
        closure,
        wordfish,
        wordfish_summary,
        source_models,
        source_desc,
        typology_frame,
        typology_error,
    )


def _typology_option_label(frame: pd.DataFrame, institute_id: str) -> str:
    row = frame.loc[frame["institute_id"].eq(institute_id)].iloc[0]
    region = row.get("region")
    parent = row.get("parent_institution")
    extras = [value for value in [region, parent] if pd.notna(value) and str(value).strip()]
    suffix = " | ".join(str(value) for value in extras[:2])
    return f"{row['institute_name']} ({institute_id})" if not suffix else f"{row['institute_name']} ({institute_id}) - {suffix}"


def _render_typology_unavailable(message: str | None) -> None:
    st.warning("Typology data is unavailable. Legacy dashboard tabs remain fully accessible.")
    if message:
        st.info(f"Typology load error: {message}")


def weighted_average(frame: pd.DataFrame, value_col: str, weight_col: str) -> float:
    sub = frame.loc[frame[value_col].notna() & frame[weight_col].gt(0), [value_col, weight_col]].copy()
    if sub.empty:
        return np.nan
    return float(np.average(sub[value_col], weights=sub[weight_col]))


def build_region_year(frame: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (region, year), sub in frame.groupby(["region", "year"], dropna=False):
        rows.append(
            {
                "region": region,
                "year": year,
                "orientation_weighted": weighted_average(sub, "mean_embedding_score", "orientation_docs"),
                "sensitive_share_weighted": weighted_average(sub, "sensitive_curated_share", "total_docs"),
                "docs_total": int(sub["total_docs"].sum()),
                "institutes": int(sub["institute_id"].nunique()),
            }
        )
    return pd.DataFrame(rows).sort_values(["region", "year"])


def filter_institutes(inst: pd.DataFrame, *, min_docs: int, regions: list[str], ci_statuses: list[str], search_text: str) -> pd.DataFrame:
    out = inst.copy()
    out = out.loc[out["total_docs"] >= min_docs]
    if regions:
        out = out.loc[out["region"].isin(regions)]
    if ci_statuses:
        out = out.loc[out["ci_status"].isin(ci_statuses)]
    if search_text.strip():
        patt = search_text.strip().lower()
        out = out.loc[
            out["institute_label"].fillna("").str.lower().str.contains(patt)
            | out["parent_institution"].fillna("").str.lower().str.contains(patt)
            | out["country"].fillna("").str.lower().str.contains(patt)
        ]
    return out.copy()


def _base_country(country: str) -> str:
    if pd.isna(country):
        return "Global"
    country = str(country).strip()
    if country in COUNTRY_OVERRIDES:
        return COUNTRY_OVERRIDES[country]
    if country in COUNTRY_CENTROIDS:
        return country
    if " / " in country:
        first = country.split(" / ")[0].strip()
        if first in COUNTRY_CENTROIDS:
            return first
    return "Global"


def _jitter_offsets(n: int, radius: float) -> list[tuple[float, float]]:
    if n <= 1:
        return [(0.0, 0.0)]
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return [(float(radius * np.sin(a)), float(radius * np.cos(a))) for a in angles]


def institute_geo_frame(filtered: pd.DataFrame) -> pd.DataFrame:
    geo = filtered.copy()
    geo["map_country"] = geo["country"].map(_base_country)
    geo["base_lat"] = geo["ror_lat"]
    geo["base_lon"] = geo["ror_lon"]
    geo["map_source"] = np.where(geo["ror_lat"].notna() & geo["ror_lon"].notna(), "ROR", "Country fallback")

    fallback_mask = geo["base_lat"].isna() | geo["base_lon"].isna()
    geo.loc[fallback_mask, ["base_lat", "base_lon"]] = geo.loc[fallback_mask, "map_country"].map(COUNTRY_CENTROIDS).apply(pd.Series)
    geo["location_label"] = np.where(
        geo["map_source"].eq("ROR"),
        np.where(geo["ror_city"].fillna("").eq(""), geo["map_country"], geo["ror_city"].fillna("")),
        geo["map_country"],
    )
    geo["location_key"] = np.where(
        geo["map_source"].eq("ROR"),
        geo["base_lat"].round(4).astype(str) + "|" + geo["base_lon"].round(4).astype(str),
        "country::" + geo["map_country"].astype(str),
    )
    geo["location_rank"] = geo.groupby("location_key").cumcount()
    geo["location_count"] = geo.groupby("location_key")["institute_id"].transform("size")
    jitter_lat = []
    jitter_lon = []
    for _, sub in geo.groupby("location_key", sort=False):
        radius = 0.25 if sub["map_source"].iloc[0] == "ROR" else (2.0 if int(sub["location_count"].iloc[0]) <= 4 else 3.0)
        offsets = _jitter_offsets(int(sub["location_count"].iloc[0]), radius=radius)
        rank_to_offset = {rank: offsets[rank] for rank in range(len(offsets))}
        for rank in sub["location_rank"]:
            dlat, dlon = rank_to_offset[int(rank)]
            jitter_lat.append(dlat)
            jitter_lon.append(dlon)
    geo["map_lat"] = geo["base_lat"] + np.array(jitter_lat)
    geo["map_lon"] = geo["base_lon"] + np.array(jitter_lon)
    return geo


def institute_world_map(filtered: pd.DataFrame, color_mode: str = "Orientation") -> go.Figure:
    geo = institute_geo_frame(filtered)
    color_col = "mean_embedding_score" if color_mode == "Orientation" else "region"
    color_kwargs = (
        {
            "color_continuous_scale": [
                [0.0, "#2166ac"],
                [0.5, "#f7f7f7"],
                [1.0, "#b2182b"],
            ],
            "color_continuous_midpoint": 0.0,
        }
        if color_mode == "Orientation"
        else {}
    )
    fig = px.scatter_geo(
        geo,
        lat="map_lat",
        lon="map_lon",
        size="total_docs",
        color=color_col,
        symbol="ci_status",
        hover_name="institute_label",
        hover_data={
            "country": True,
            "region": True,
            "parent_institution": True,
            "total_docs": True,
            "orientation_docs": True,
            "mean_embedding_score": ":.3f",
            "sensitive_curated_share": ":.3f",
            "map_source": True,
            "ror_city": True,
            "resolved_ror_name": True,
            "map_country": False,
            "map_lat": False,
            "map_lon": False,
        },
        projection="natural earth",
        title="Global Distribution of Research Centres",
        size_max=28,
        **color_kwargs,
    )
    fig.update_geos(
        showland=True,
        landcolor="#f7f4ea",
        showcountries=True,
        countrycolor="#9aa3a8",
        showocean=True,
        oceancolor="#dceaf7",
        lataxis_showgrid=True,
        lonaxis_showgrid=True,
    )
    if color_mode == "Orientation":
        fig.update_coloraxes(
            colorbar_title_text="Orientation score",
            cmin=min(-0.25, float(geo["mean_embedding_score"].min(skipna=True))),
            cmax=max(0.25, float(geo["mean_embedding_score"].max(skipna=True))),
        )
    fig.update_layout(height=650, legend_title_text="")
    return fig


def institute_scatter(filtered: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        filtered,
        x="mean_embedding_score",
        y="sensitive_curated_share",
        size="total_docs",
        color="region",
        symbol="ci_status",
        hover_name="institute_label",
        hover_data={
            "country": True,
            "parent_institution": True,
            "total_docs": True,
            "orientation_docs": True,
            "sensitive_docs": True,
            "mean_dictionary_score": ":.3f",
            "mean_embedding_score": ":.3f",
            "sensitive_curated_share": ":.3f",
            "ci_status": True,
        },
        title="Institute Landscape: Cooperation-Hawkishness vs Sensitive-Issue Share",
        labels={
            "mean_embedding_score": "Embedding orientation score (lower = more cooperative)",
            "sensitive_curated_share": "Curated sensitive-topic share",
        },
        size_max=40,
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(height=620, legend_title_text="")
    return fig


def ranking_chart(filtered: pd.DataFrame, top_n: int, ascending: bool) -> go.Figure:
    plot_df = (
        filtered.loc[filtered["orientation_docs"] >= 20, ["institute_label", "mean_embedding_score", "orientation_docs", "region", "ci_status"]]
        .sort_values("mean_embedding_score", ascending=ascending)
        .head(top_n)
        .sort_values("mean_embedding_score", ascending=True)
    )
    title = "Most Cooperative Institutes" if ascending else "Most Hawkish Institutes"
    fig = px.bar(
        plot_df,
        x="mean_embedding_score",
        y="institute_label",
        color="region",
        orientation="h",
        hover_data={"orientation_docs": True, "ci_status": True},
        title=title,
        labels={"mean_embedding_score": "Embedding orientation score", "institute_label": ""},
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(height=650, showlegend=False)
    return fig


def sensitive_family_chart(filtered: pd.DataFrame, mode: str) -> go.Figure:
    if mode == "Region":
        grp = (
            filtered.groupby("region", dropna=False)[SENSITIVE_FAMILY_SHARE_COLS]
            .mean()
            .reset_index()
            .rename(columns={"region": "group"})
        )
        title = "Sensitive-Issue Composition by Region"
    else:
        grp = (
            filtered.sort_values("sensitive_curated_share", ascending=False)
            .head(20)[["institute_label"] + SENSITIVE_FAMILY_SHARE_COLS]
            .rename(columns={"institute_label": "group"})
        )
        title = "Sensitive-Issue Composition for Top 20 Institutes by Sensitive Share"

    long = grp.melt(id_vars="group", value_vars=SENSITIVE_FAMILY_SHARE_COLS, var_name="family", value_name="share")
    long["family"] = long["family"].map(SENSITIVE_FAMILY_LABELS)
    fig = px.bar(
        long,
        x="group",
        y="share",
        color="family",
        title=title,
        labels={"group": "", "share": "Average share"},
    )
    fig.update_layout(height=560, xaxis_tickangle=-35, legend_title_text="")
    return fig


def region_trend_charts(region_year: pd.DataFrame, regions: list[str]) -> tuple[go.Figure, go.Figure]:
    data = region_year.copy()
    if regions:
        data = data.loc[data["region"].isin(regions)]

    orient = px.line(
        data,
        x="year",
        y="orientation_weighted",
        color="region",
        markers=True,
        title="Weighted Regional Trend: Cooperation-Hawkishness Axis",
        labels={"orientation_weighted": "Weighted embedding score", "year": ""},
    )
    orient.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)
    orient.update_layout(height=420, legend_title_text="")

    sensitive = px.line(
        data,
        x="year",
        y="sensitive_share_weighted",
        color="region",
        markers=True,
        title="Weighted Regional Trend: Sensitive-Issue Share",
        labels={"sensitive_share_weighted": "Weighted sensitive-topic share", "year": ""},
    )
    sensitive.update_layout(height=420, legend_title_text="")
    return orient, sensitive


def institute_trend_chart(year_df: pd.DataFrame, selected_institutes: list[str]) -> go.Figure:
    sub = year_df.loc[year_df["institute_label"].isin(selected_institutes) & year_df["mean_embedding_score"].notna()]
    fig = px.line(
        sub,
        x="year",
        y="mean_embedding_score",
        color="institute_label",
        markers=True,
        title="Institute-Year Trend on the Cooperation-Hawkishness Axis",
        labels={"mean_embedding_score": "Embedding score", "year": "", "institute_label": ""},
    )
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(height=500, legend_title_text="")
    return fig


def filter_wordfish(wordfish: pd.DataFrame, *, min_docs: int, regions: list[str], ci_statuses: list[str], search_text: str) -> pd.DataFrame:
    if wordfish.empty:
        return wordfish.copy()
    out = wordfish.copy()
    out = out.loc[out["total_docs"].fillna(0) >= min_docs]
    if regions:
        out = out.loc[out["region"].isin(regions)]
    if ci_statuses and "ci_status" in out.columns:
        out = out.loc[out["ci_status"].isin(ci_statuses)]
    if search_text.strip():
        patt = search_text.strip().lower()
        out = out.loc[
            out["institute_label"].fillna("").str.lower().str.contains(patt)
            | out["parent_institution"].fillna("").str.lower().str.contains(patt)
            | out["country"].fillna("").str.lower().str.contains(patt)
        ]
    return out.copy()


def wordfish_scatter(wordfish: pd.DataFrame) -> go.Figure:
    plot_df = wordfish.loc[wordfish["n_docs"] >= 10].copy()
    fig = px.scatter(
        plot_df,
        x="mean_embedding_score",
        y="wordfish_score",
        size="n_docs",
        color="region",
        symbol="ci_status" if "ci_status" in plot_df.columns else None,
        hover_name="institute_label",
        hover_data={
            "country": True,
            "parent_institution": True,
            "n_docs": True,
            "total_docs": True,
            "mean_dictionary_score": ":.3f",
            "mean_embedding_score": ":.3f",
            "wordfish_score": ":.3f",
            "sensitive_share": ":.3f",
        },
        title="Wordfish vs Embedding on the High-Signal Institute Slice",
        labels={
            "mean_embedding_score": "Embedding orientation score",
            "wordfish_score": "Wordfish score",
        },
        size_max=38,
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(height=560, legend_title_text="")
    return fig


def wordfish_gap_chart(wordfish: pd.DataFrame, top_n: int = 15) -> go.Figure:
    plot_df = wordfish.loc[wordfish["n_docs"] >= 10].copy()
    plot_df["abs_gap"] = (plot_df["wordfish_score"] - plot_df["mean_embedding_score"]).abs()
    plot_df = plot_df.sort_values("abs_gap", ascending=False).head(top_n).sort_values("wordfish_embedding_gap")
    fig = px.bar(
        plot_df,
        x="wordfish_embedding_gap",
        y="institute_label",
        color="region",
        orientation="h",
        hover_data={
            "n_docs": True,
            "wordfish_score": ":.3f",
            "mean_embedding_score": ":.3f",
            "mean_dictionary_score": ":.3f",
        },
        title="Largest Wordfish vs Embedding Gaps",
        labels={"wordfish_embedding_gap": "Wordfish - Embedding gap", "institute_label": ""},
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(height=560, showlegend=False)
    return fig


def coefficient_plot(models: pd.DataFrame, terms: list[str], title: str, label_map: dict[str, str] | None = None) -> go.Figure:
    sub = models.loc[models["term"].isin(terms)].copy()
    sub["label"] = sub["term"].str.replace("region\\[", "", regex=True).str.replace("\\]", "", regex=True)
    if label_map:
        sub["label"] = sub["term"].map(label_map).fillna(sub["label"])
    sub["model_label"] = sub["model"].map(
        {
            "region_year": "Region + Year",
            "region_year_source_type": "Region + Year + Source Mix + Type",
            "broad_panel_controls": "Broad Panel Controls",
            "closure_only_institute_fe": "Closure FE",
            "source_region_year_type": "Source + Region + Year + Type",
            "source_region_year_type_lpm": "Source + Region + Year + Type",
        }
    ).fillna(sub["model"])

    fig = go.Figure()
    for model_label, grp in sub.groupby("model_label", dropna=False):
        fig.add_trace(
            go.Scatter(
                x=grp["estimate"],
                y=grp["label"],
                mode="markers",
                error_x=dict(
                    type="data",
                    symmetric=False,
                    array=grp["ci_high"] - grp["estimate"],
                    arrayminus=grp["estimate"] - grp["ci_low"],
                ),
                name=model_label,
                marker=dict(size=10),
            )
        )
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(title=title, height=420, xaxis_title="Coefficient", yaxis_title="")
    return fig


def source_descriptive_chart(source_desc: pd.DataFrame) -> go.Figure:
    plot_df = source_desc.copy()
    fig = px.bar(
        plot_df,
        x="source_type",
        y="docs_total",
        color="source_type",
        hover_data={
            "orientation_docs": True,
            "mean_embedding_score": ":.3f",
            "mean_dictionary_score": ":.3f",
            "sensitive_share": ":.3f",
            "mean_tokens": ":,.1f",
        },
        title="Corpus Composition by Source Type",
        labels={"source_type": "", "docs_total": "Documents"},
    )
    fig.update_layout(height=420, showlegend=False)
    return fig


def closure_small_multiples(closure: pd.DataFrame) -> go.Figure:
    plot_df = closure.copy()
    plot_df = plot_df.melt(
        id_vars=["institute_label"],
        value_vars=["orientation_diff_post_minus_pre", "sensitive_diff_post_minus_pre"],
        var_name="metric",
        value_name="diff",
    )
    plot_df["metric"] = plot_df["metric"].map(
        {
            "orientation_diff_post_minus_pre": "Orientation change (post - pre)",
            "sensitive_diff_post_minus_pre": "Sensitive share change (post - pre)",
        }
    )
    fig = px.bar(
        plot_df,
        x="diff",
        y="institute_label",
        color="metric",
        barmode="group",
        orientation="h",
        title="Closure Cases: Pre/Post Changes by Institute",
        labels={"diff": "Change", "institute_label": ""},
    )
    fig.add_vline(x=0, line_dash="dash", line_color="gray", opacity=0.6)
    fig.update_layout(height=520, legend_title_text="")
    return fig


def main() -> None:
    st.set_page_config(page_title="China Institutes Results Dashboard", layout="wide")
    st.title("China Institutes Results Dashboard")
    st.caption("Interactive exploration of institute orientation, sensitive-topic prevalence, and Confucius Institute results.")

    inst, year, ci_models, region_models, closure, wordfish, wordfish_summary, source_models, source_desc, typology_frame, typology_error = load_data()
    region_year = build_region_year(year)

    with st.sidebar:
        st.header("Filters")
        min_docs = st.slider("Minimum institute total documents", min_value=1, max_value=int(inst["total_docs"].max()), value=20, step=1)
        all_regions = sorted(inst["region"].dropna().unique().tolist())
        selected_regions = st.multiselect("Regions", all_regions, default=all_regions)
        selected_ci = st.multiselect("Confucius Institute status", ["None", "Present", "Closed"], default=["None", "Present", "Closed"])
        search_text = st.text_input("Search institute / parent / country", value="")
        top_n = st.slider("Ranking size", min_value=5, max_value=30, value=15, step=1)

    filtered = filter_institutes(inst, min_docs=min_docs, regions=selected_regions, ci_statuses=selected_ci, search_text=search_text)
    wordfish_filtered = filter_wordfish(wordfish, min_docs=min_docs, regions=selected_regions, ci_statuses=selected_ci, search_text=search_text)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Institutes in view", f"{len(filtered)}")
    c2.metric("Docs in view", f"{int(filtered['total_docs'].sum()):,}")
    c3.metric("Mean orientation", f"{filtered['mean_embedding_score'].mean():.3f}" if not filtered.empty else "NA")
    c4.metric("Mean sensitive share", f"{filtered['sensitive_curated_share'].mean():.3f}" if not filtered.empty else "NA")

    tabs = st.tabs(
        [
            "Overview",
            "Typology Explorer",
            "Institute Drill-Down",
            "World Map",
            "Field Map",
            "Rankings",
            "Trends",
            "Sensitive Topics",
            "Source Types",
            "Wordfish",
            "Confucius Institutes",
        ]
    )

    with tabs[0]:
        if typology_frame is None:
            _render_typology_unavailable(typology_error)
        else:
            kpis = build_typology_kpis(typology_frame)
            st.caption("Typology-first briefing view for meetings: start with the institutional mix, then move into members and drill-downs.")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Institutes", f"{kpis['institutes']:,}")
            m2.metric("Documents", f"{kpis['docs_total']:,}")
            m3.metric("Model-ready", f"{kpis['model_ready_institutes']:,}")
            m4.metric("Borderline typologies", f"{kpis['borderline_typologies']:,}")
            m5.metric("Low-volume institutes", f"{kpis['low_volume_institutes']:,}")

            left, right = st.columns([1.2, 1.0])
            left.plotly_chart(
                build_dominant_domain_composition_chart(typology_frame),
                use_container_width=True,
                key="overview_dominant_domain_composition_chart",
            )
            right.plotly_chart(
                build_typology_profile_heatmap(typology_frame),
                use_container_width=True,
                key="overview_typology_profile_heatmap",
            )

            st.dataframe(build_typology_field_map(), use_container_width=True, hide_index=True)

    with tabs[1]:
        if typology_frame is None:
            _render_typology_unavailable(typology_error)
        else:
            explorer_cols = st.columns(4)
            typology_options = ["All"] + sorted(typology_frame["theory_typology"].dropna().unique().tolist())
            domain_options = ["All"] + [domain for domain in DOMAIN_LABELS if domain in typology_frame["dominant_domain"].dropna().unique().tolist()]
            region_options = ["All"] + sorted(typology_frame["region"].dropna().unique().tolist())

            selected_typology = explorer_cols[0].selectbox("Typology", typology_options, key="typology_explorer_typology")
            selected_domain = explorer_cols[1].selectbox(
                "Dominant domain",
                domain_options,
                key="typology_explorer_domain",
                format_func=lambda value: "All" if value == "All" else DOMAIN_LABELS.get(value, value),
            )
            selected_region = explorer_cols[2].selectbox("Region", region_options, key="typology_explorer_region")
            typology_search = explorer_cols[3].text_input("Find institute", value="", key="typology_explorer_search")

            member_table = build_typology_member_table(
                typology_frame,
                typology=selected_typology,
                dominant_domain=selected_domain,
                region=selected_region,
                search_text=typology_search,
            )
            member_display = member_table.copy()
            if not member_display.empty:
                member_display["dominant_domain"] = member_display["dominant_domain"].map(
                    lambda value: DOMAIN_LABELS.get(value, value)
                )
                member_display["theory_typology_confidence"] = member_display["theory_typology_confidence"].map(
                    lambda value: f"{float(value):.3f}" if pd.notna(value) else "NA"
                )

            explorer_options = member_table["institute_id"].tolist()
            if not explorer_options:
                explorer_options = typology_frame.sort_values(["institute_name", "institute_id"])["institute_id"].tolist()
            explorer_pick = st.selectbox(
                "Highlighted institute",
                options=explorer_options,
                key="typology_explorer_highlight",
                format_func=lambda institute_id: _typology_option_label(typology_frame, institute_id),
            )

            if explorer_pick:
                left, right = st.columns(2)
                left.plotly_chart(
                    build_institute_domain_salience_chart(typology_frame, institute_id=explorer_pick),
                    use_container_width=True,
                    key="typology_explorer_domain_salience_chart",
                )
                right.plotly_chart(
                    build_institute_within_domain_orientation_chart(typology_frame, institute_id=explorer_pick),
                    use_container_width=True,
                    key="typology_explorer_orientation_chart",
                )

            display_columns = [column for column in MEMBER_TABLE_COLUMNS if column != "institute_id"]
            st.dataframe(
                member_display.loc[:, display_columns],
                use_container_width=True,
                hide_index=True,
            )

    with tabs[2]:
        if typology_frame is None:
            _render_typology_unavailable(typology_error)
        else:
            drilldown_ids = typology_frame.sort_values(["institute_name", "institute_id"])["institute_id"].tolist()
            selected_id = st.selectbox(
                "Institute",
                drilldown_ids,
                key="typology_drilldown_institute",
                format_func=lambda institute_id: _typology_option_label(typology_frame, institute_id),
            )
            summary = build_institute_drilldown_summary(typology_frame, institute_id=selected_id)

            st.subheader(str(summary["institute_name"]))
            header_left, header_mid, header_right = st.columns(3)
            header_left.metric("Typology", str(summary["theory_typology"]).replace("_", " ").title())
            header_left.caption(f"Confidence: {float(summary['theory_typology_confidence']):.3f}")
            header_mid.metric("Dominant domain", DOMAIN_LABELS.get(str(summary["dominant_domain"]), str(summary["dominant_domain"])))
            header_mid.caption(f"Cluster: {summary['cluster_label']}")
            header_right.metric("Documents", f"{int(summary['total_docs']):,}")
            header_right.caption(f"Region: {summary['region']}")

            summary_display = pd.DataFrame(
                [
                    {
                        "field": column,
                        "value": DOMAIN_LABELS.get(str(value), value) if column == "dominant_domain" else value,
                    }
                    for column, value in summary.items()
                    if column in DRILLDOWN_HEADER_COLUMNS
                ]
            )
            st.dataframe(summary_display, use_container_width=True, hide_index=True)

            left, right = st.columns(2)
            left.plotly_chart(
                build_institute_domain_salience_chart(typology_frame, institute_id=selected_id),
                use_container_width=True,
                key="drilldown_domain_salience_chart",
            )
            right.plotly_chart(
                build_institute_within_domain_orientation_chart(typology_frame, institute_id=selected_id),
                use_container_width=True,
                key="drilldown_orientation_chart",
            )
            st.plotly_chart(
                build_institute_vs_peer_comparison_chart(typology_frame, institute_id=selected_id),
                use_container_width=True,
                key="drilldown_peer_comparison_chart",
            )

    with tabs[3]:
        color_mode = st.radio("Map coloring", ["Orientation", "Region"], horizontal=True)
        geo = institute_geo_frame(filtered)
        st.plotly_chart(
            institute_world_map(filtered, color_mode=color_mode),
            use_container_width=True,
            key="world_map_chart",
        )
        ror_count = int(geo["map_source"].eq("ROR").sum())
        fallback_count = int(geo["map_source"].eq("Country fallback").sum())
        st.caption(
            f"Map uses parent-institution coordinates from ROR where available ({ror_count} institutes) and country-level fallback centroids otherwise ({fallback_count} institutes). Small offsets separate overlapping points. Lower scores are more cooperative; higher scores are more hawkish."
        )
        st.dataframe(
            geo[
                [
                    "institute_label",
                    "country",
                    "region",
                    "map_source",
                    "ror_city",
                    "ci_status",
                    "total_docs",
                    "mean_embedding_score",
                    "sensitive_curated_share",
                ]
            ].sort_values(["country", "institute_label"]),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[4]:
        st.plotly_chart(
            institute_scatter(filtered),
            use_container_width=True,
            key="field_map_scatter_chart",
        )
        st.dataframe(
            filtered[
                [
                    "institute_label",
                    "country",
                    "region",
                    "ci_status",
                    "total_docs",
                    "orientation_docs",
                    "mean_embedding_score",
                    "sensitive_curated_share",
                ]
            ].sort_values("mean_embedding_score", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    with tabs[5]:
        left, right = st.columns(2)
        left.plotly_chart(
            ranking_chart(filtered, top_n=top_n, ascending=True),
            use_container_width=True,
            key="rankings_cooperative_chart",
        )
        right.plotly_chart(
            ranking_chart(filtered, top_n=top_n, ascending=False),
            use_container_width=True,
            key="rankings_hawkish_chart",
        )

    with tabs[6]:
        orient_fig, sens_fig = region_trend_charts(region_year, selected_regions)
        st.plotly_chart(
            orient_fig,
            use_container_width=True,
            key="trends_region_orientation_chart",
        )
        st.plotly_chart(
            sens_fig,
            use_container_width=True,
            key="trends_region_sensitive_chart",
        )

        available_institutes = filtered.loc[filtered["orientation_docs"] >= 20, "institute_label"].sort_values().tolist()
        default_institutes = available_institutes[: min(5, len(available_institutes))]
        picked = st.multiselect("Institute drilldown", available_institutes, default=default_institutes)
        if picked:
            st.plotly_chart(
                institute_trend_chart(year, picked),
                use_container_width=True,
                key="trends_institute_drilldown_chart",
            )

    with tabs[7]:
        mode = st.radio("Composition view", ["Region", "Institute"], horizontal=True)
        st.plotly_chart(
            sensitive_family_chart(filtered, mode=mode),
            use_container_width=True,
            key="sensitive_family_chart",
        )

    with tabs[8]:
        if source_models.empty or source_desc.empty:
            st.info("Source-type model outputs are not available.")
        else:
            st.caption(
                "Baseline source type is indexed. Embedding results are estimated on orientation-eligible documents; sensitive-topic results are estimated on the full corpus."
            )
            left, right = st.columns(2)
            left.plotly_chart(
                coefficient_plot(
                    source_models.loc[source_models["outcome"] == "embedding_score"],
                    terms=["source_policy", "source_grey"],
                    title="Source-Type Effects on the Cooperation-Hawkishness Axis",
                    label_map={"source_policy": "Policy documents", "source_grey": "Grey literature"},
                ),
                use_container_width=True,
                key="source_types_embedding_coefficients_chart",
            )
            right.plotly_chart(
                coefficient_plot(
                    source_models.loc[source_models["outcome"] == "sensitive_flag_num"],
                    terms=["source_policy", "source_grey"],
                    title="Source-Type Effects on Sensitive-Issue Prevalence",
                    label_map={"source_policy": "Policy documents", "source_grey": "Grey literature"},
                ),
                use_container_width=True,
                key="source_types_sensitive_coefficients_chart",
            )
            st.plotly_chart(
                source_descriptive_chart(source_desc),
                use_container_width=True,
                key="source_types_descriptive_chart",
            )
            st.dataframe(source_desc, use_container_width=True, hide_index=True)

    with tabs[9]:
        if wordfish_filtered.empty:
            st.info("No Wordfish robustness rows available for the current filters.")
        else:
            m1, m2, m3 = st.columns(3)
            m1.metric("Wordfish institutes in view", f"{len(wordfish_filtered)}")
            m2.metric("High-signal docs in view", f"{int(wordfish_filtered['n_docs'].sum()):,}")
            corr_filtered = wordfish_filtered.loc[wordfish_filtered["n_docs"] >= 10, "wordfish_score"].corr(
                wordfish_filtered.loc[wordfish_filtered["n_docs"] >= 10, "mean_embedding_score"]
            )
            m3.metric("Wordfish vs embedding r", f"{corr_filtered:.3f}" if pd.notna(corr_filtered) else "NA")

            st.caption(
                "Wordfish is shown here only as a limited robustness check on a high-signal institute slice: English, orientation-eligible, dictionary-matched, and either modern-policy or sensitive-topic documents. The broad corpus Wordfish fit did not recover the main axis cleanly."
            )
            if wordfish_summary:
                st.caption(
                    "High-signal summary: "
                    f"{wordfish_summary.get('rows', 'NA')} institute rows, "
                    f"{wordfish_summary.get('filtered_rows_n_docs_ge_10', 'NA')} with n_docs >= 10, "
                    f"filtered corr(wordfish, embedding) = {wordfish_summary.get('corr_filtered_wordfish_embedding', 'NA')}."
                )

            left, right = st.columns(2)
            left.plotly_chart(
                wordfish_scatter(wordfish_filtered),
                use_container_width=True,
                key="wordfish_scatter_chart",
            )
            right.plotly_chart(
                wordfish_gap_chart(wordfish_filtered, top_n=top_n),
                use_container_width=True,
                key="wordfish_gap_chart",
            )
            st.dataframe(
                wordfish_filtered[
                    [
                        "institute_label",
                        "country",
                        "region",
                        "n_docs",
                        "total_docs",
                        "mean_embedding_score",
                        "mean_dictionary_score",
                        "wordfish_score",
                        "wordfish_embedding_gap",
                    ]
                ].sort_values("wordfish_score", ascending=False),
                use_container_width=True,
                hide_index=True,
            )

    with tabs[10]:
        st.plotly_chart(
            coefficient_plot(
                ci_models.loc[ci_models["outcome"] == "sensitive_curated_share"],
                terms=["ci_present", "ci_closed", "post_ci_closure", "years_since_ci_closure"],
                title="Confucius Institute Models: Sensitive-Topic Share",
            ),
            use_container_width=True,
            key="confucius_sensitive_coefficients_chart",
        )
        st.plotly_chart(
            coefficient_plot(
                ci_models.loc[ci_models["outcome"] == "mean_embedding_score"],
                terms=["ci_present", "ci_closed", "post_ci_closure", "years_since_ci_closure"],
                title="Confucius Institute Models: Cooperation-Hawkishness Axis",
            ),
            use_container_width=True,
            key="confucius_orientation_coefficients_chart",
        )
        st.plotly_chart(
            closure_small_multiples(closure),
            use_container_width=True,
            key="confucius_closure_small_multiples_chart",
        )
        st.dataframe(
            closure[
                [
                    "institute_label",
                    "ci_closure_year",
                    "orientation_diff_post_minus_pre",
                    "sensitive_diff_post_minus_pre",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")
    st.markdown(
        "Run locally with `streamlit run app/results_dashboard.py` from the project root."
    )


if __name__ == "__main__":
    main()
