from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visualization.typology_dashboard_charts import (  # noqa: E402
    build_dominant_domain_composition_chart,
    build_institute_drilldown_summary,
    build_institute_vs_peer_comparison_chart,
    build_institute_within_domain_orientation_chart,
    build_typology_kpis,
    build_typology_member_table,
    build_typology_profile_heatmap,
)


def _sample_typology_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "institute_id": "alpha",
                "institute_name": "Alpha Institute",
                "region": "North America",
                "theory_typology": "security_hawks",
                "theory_typology_confidence": 0.83,
                "theory_typology_borderline": True,
                "theory_typology_borderline_badge": "Borderline",
                "low_volume_flag": True,
                "low_volume_badge": "Low volume",
                "regression_inclusion_status": "excluded_from_regression",
                "dominant_domain": "security_strategy",
                "dominant_domain_share": 0.61,
                "dominant_domain_borderline_flag": False,
                "dominant_domain_borderline_badge": "Clear",
                "cluster_label": "cluster_1_security_strategy_rival",
                "total_docs": 8,
                "parent_institution": "Alpha University",
                "institute_type_category": "academic center / institute",
                "security_strategy_salience_share": 0.61,
                "economy_trade_salience_share": 0.22,
                "science_technology_salience_share": 0.07,
                "environment_climate_salience_share": 0.04,
                "governance_law_salience_share": 0.03,
                "society_culture_salience_share": 0.03,
                "security_strategy_oriented_prop": 0.64,
                "security_strategy_rival_among_oriented": 0.91,
                "security_strategy_collaborator_among_oriented": 0.09,
                "economy_trade_oriented_prop": 0.44,
                "economy_trade_rival_among_oriented": 0.20,
                "economy_trade_collaborator_among_oriented": 0.80,
                "science_technology_oriented_prop": 0.18,
                "science_technology_rival_among_oriented": 0.40,
                "science_technology_collaborator_among_oriented": 0.60,
                "environment_climate_oriented_prop": 0.10,
                "environment_climate_rival_among_oriented": 0.35,
                "environment_climate_collaborator_among_oriented": 0.65,
                "governance_law_oriented_prop": 0.12,
                "governance_law_rival_among_oriented": 0.45,
                "governance_law_collaborator_among_oriented": 0.55,
                "society_culture_oriented_prop": 0.09,
                "society_culture_rival_among_oriented": 0.30,
                "society_culture_collaborator_among_oriented": 0.70,
                "overall_rival_among_oriented": 0.18,
                "overall_collaborator_among_oriented": 0.82,
            },
            {
                "institute_id": "beta",
                "institute_name": "Beta Institute",
                "region": "Europe",
                "theory_typology": "market_pragmatists",
                "theory_typology_confidence": 0.71,
                "theory_typology_borderline": False,
                "theory_typology_borderline_badge": "Clear",
                "low_volume_flag": False,
                "low_volume_badge": "Sufficient volume",
                "regression_inclusion_status": "included_in_regression",
                "dominant_domain": "economy_trade",
                "dominant_domain_share": 0.57,
                "dominant_domain_borderline_flag": True,
                "dominant_domain_borderline_badge": "Borderline",
                "cluster_label": "cluster_2_economy_trade_collaborator",
                "total_docs": 44,
                "parent_institution": "Beta University",
                "institute_type_category": "policy / think tank",
                "security_strategy_salience_share": 0.18,
                "economy_trade_salience_share": 0.57,
                "science_technology_salience_share": 0.08,
                "environment_climate_salience_share": 0.07,
                "governance_law_salience_share": 0.06,
                "society_culture_salience_share": 0.04,
                "security_strategy_oriented_prop": 0.21,
                "security_strategy_rival_among_oriented": 0.32,
                "security_strategy_collaborator_among_oriented": 0.68,
                "economy_trade_oriented_prop": 0.73,
                "economy_trade_rival_among_oriented": 0.24,
                "economy_trade_collaborator_among_oriented": 0.76,
                "science_technology_oriented_prop": 0.15,
                "science_technology_rival_among_oriented": 0.28,
                "science_technology_collaborator_among_oriented": 0.72,
                "environment_climate_oriented_prop": 0.12,
                "environment_climate_rival_among_oriented": 0.41,
                "environment_climate_collaborator_among_oriented": 0.59,
                "governance_law_oriented_prop": 0.11,
                "governance_law_rival_among_oriented": 0.36,
                "governance_law_collaborator_among_oriented": 0.64,
                "society_culture_oriented_prop": 0.10,
                "society_culture_rival_among_oriented": 0.33,
                "society_culture_collaborator_among_oriented": 0.67,
                "overall_rival_among_oriented": 0.61,
                "overall_collaborator_among_oriented": 0.39,
            },
            {
                "institute_id": "gamma",
                "institute_name": "Alpha Institute",
                "region": "Asia",
                "theory_typology": "security_hawks",
                "theory_typology_confidence": 0.67,
                "theory_typology_borderline": False,
                "theory_typology_borderline_badge": "Clear",
                "low_volume_flag": False,
                "low_volume_badge": "Sufficient volume",
                "regression_inclusion_status": "included_in_regression",
                "dominant_domain": "security_strategy",
                "dominant_domain_share": 0.48,
                "dominant_domain_borderline_flag": False,
                "dominant_domain_borderline_badge": "Clear",
                "cluster_label": "cluster_3_security_strategy_collaborator",
                "total_docs": 31,
                "parent_institution": "Gamma University",
                "institute_type_category": "academic center / institute",
                "security_strategy_salience_share": 0.48,
                "economy_trade_salience_share": 0.19,
                "science_technology_salience_share": 0.12,
                "environment_climate_salience_share": 0.08,
                "governance_law_salience_share": 0.07,
                "society_culture_salience_share": 0.06,
                "security_strategy_oriented_prop": 0.59,
                "security_strategy_rival_among_oriented": 0.26,
                "security_strategy_collaborator_among_oriented": 0.74,
                "economy_trade_oriented_prop": 0.33,
                "economy_trade_rival_among_oriented": 0.44,
                "economy_trade_collaborator_among_oriented": 0.56,
                "science_technology_oriented_prop": 0.22,
                "science_technology_rival_among_oriented": 0.38,
                "science_technology_collaborator_among_oriented": 0.62,
                "environment_climate_oriented_prop": 0.14,
                "environment_climate_rival_among_oriented": 0.35,
                "environment_climate_collaborator_among_oriented": 0.65,
                "governance_law_oriented_prop": 0.13,
                "governance_law_rival_among_oriented": 0.30,
                "governance_law_collaborator_among_oriented": 0.70,
                "society_culture_oriented_prop": 0.11,
                "society_culture_rival_among_oriented": 0.29,
                "society_culture_collaborator_among_oriented": 0.71,
                "overall_rival_among_oriented": 0.52,
                "overall_collaborator_among_oriented": 0.48,
            },
        ]
    )


def test_overview_chart_builders_return_plotly_figures_with_expected_titles() -> None:
    frame = _sample_typology_frame()

    composition = build_dominant_domain_composition_chart(frame)
    heatmap = build_typology_profile_heatmap(frame)

    assert isinstance(composition, go.Figure)
    assert isinstance(heatmap, go.Figure)
    assert composition.layout.title.text == "Dominant Domain Composition by Typology"
    assert heatmap.layout.title.text == "Typology Profile Matrix"


def test_institute_within_domain_orientation_chart_uses_within_domain_columns() -> None:
    frame = _sample_typology_frame()

    fig = build_institute_within_domain_orientation_chart(frame, institute_id="alpha")

    assert isinstance(fig, go.Figure)
    values = dict(zip(fig.data[0].x, fig.data[0].y, strict=False))
    assert values["Rival share"] == 0.91
    assert values["Collaborator share"] == 0.09
    assert values["Rival share"] != frame.loc[0, "overall_rival_among_oriented"]
    assert values["Collaborator share"] != frame.loc[0, "overall_collaborator_among_oriented"]


def test_institute_drilldown_summary_preserves_borderline_and_low_volume_badges() -> None:
    frame = _sample_typology_frame()

    summary = build_institute_drilldown_summary(frame, institute_id="alpha")

    assert summary["institute_name"] == "Alpha Institute"
    assert summary["theory_typology_borderline_badge"] == "Borderline"
    assert summary["low_volume_badge"] == "Low volume"
    assert summary["regression_inclusion_status"] == "excluded_from_regression"


def test_build_typology_kpis_summarizes_counts_and_docs() -> None:
    frame = _sample_typology_frame()

    kpis = build_typology_kpis(frame)

    assert kpis["institutes"] == 3
    assert kpis["docs_total"] == 83
    assert kpis["low_volume_institutes"] == 1
    assert kpis["borderline_typologies"] == 1
    assert kpis["model_ready_institutes"] == 2
    assert kpis["top_typology"] == "security_hawks"


def test_build_typology_member_table_retains_institute_id_for_safe_selection() -> None:
    frame = _sample_typology_frame()

    member_table = build_typology_member_table(frame, typology="security_hawks")

    assert "institute_id" in member_table.columns
    assert member_table["institute_id"].tolist() == ["alpha", "gamma"]
    assert member_table["institute_name"].tolist() == ["Alpha Institute", "Alpha Institute"]


def test_build_institute_vs_peer_comparison_chart_uses_selected_id_with_duplicate_names() -> None:
    frame = _sample_typology_frame()

    fig = build_institute_vs_peer_comparison_chart(frame, institute_id="gamma")

    assert isinstance(fig, go.Figure)
    assert fig.layout.title.text == "Institute vs Peer Typology Profile: Alpha Institute"
    institute_trace = fig.data[0]
    values = dict(zip(institute_trace.x, institute_trace.y, strict=False))
    assert values["Security & strategy"] == 0.48
    assert values["Economy & trade"] == 0.19


def test_drilldown_summary_prefers_id_when_names_are_non_unique() -> None:
    frame = _sample_typology_frame()

    summary = build_institute_drilldown_summary(frame, institute_id="gamma")

    assert summary["parent_institution"] == "Gamma University"
    assert summary["total_docs"] == 31


def test_drilldown_summary_rejects_ambiguous_name_lookup() -> None:
    frame = _sample_typology_frame()

    with pytest.raises(ValueError, match="not unique"):
        build_institute_drilldown_summary(frame, institute_name="Alpha Institute")
