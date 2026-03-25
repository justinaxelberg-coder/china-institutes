from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from visualization.typology_dashboard_data import (  # noqa: E402
    TypologyDashboardDataError,
    build_typology_dashboard_frame,
    load_typology_dashboard_bundle,
)


def test_load_typology_dashboard_bundle_requires_all_required_files(tmp_path: Path) -> None:
    tables = tmp_path / "outputs" / "tables"
    tables.mkdir(parents=True)
    pd.DataFrame({"institute_id": ["a"]}).to_csv(
        tables / "institute_typology_publication_matrix.csv",
        index=False,
    )

    with pytest.raises(TypologyDashboardDataError, match="institute_domain_profiles.csv"):
        load_typology_dashboard_bundle(tmp_path)


def test_build_typology_dashboard_frame_rejects_missing_required_columns() -> None:
    bundle = load_typology_dashboard_bundle(ROOT)
    bundle["model_data"] = bundle["model_data"].drop(columns=["region"])

    with pytest.raises(TypologyDashboardDataError, match="region"):
        build_typology_dashboard_frame(bundle)


def test_build_typology_dashboard_frame_preserves_one_row_per_institute_id() -> None:
    bundle = load_typology_dashboard_bundle(ROOT)

    frame = build_typology_dashboard_frame(bundle)

    assert frame["institute_id"].is_unique
    assert len(frame) == len(bundle["model_data"])
    required_columns = {
        "institute_id",
        "institute_name",
        "total_docs",
        "dominant_domain",
        "dominant_domain_share",
        "dominant_domain_borderline_flag",
        "low_volume_flag",
        "theory_typology",
        "theory_typology_confidence",
        "theory_typology_borderline",
        "cluster_label",
        "region",
        "parent_institution",
        "institute_type_category",
        "regression_inclusion_status",
        "security_signal",
        "economic_signal",
        "low_volume_badge",
        "theory_typology_borderline_badge",
        "dominant_domain_borderline_badge",
    }
    assert required_columns.issubset(frame.columns)


def test_regression_inclusion_status_is_derived_from_low_volume_flag() -> None:
    bundle = load_typology_dashboard_bundle(ROOT)
    frame = build_typology_dashboard_frame(bundle)

    included_borderline = frame.loc[
        (~frame["low_volume_flag"].fillna(False)) & (frame["theory_typology_borderline"].fillna(False)),
        "regression_inclusion_status",
    ].unique()
    excluded_low_volume = frame.loc[
        frame["low_volume_flag"].fillna(False),
        "regression_inclusion_status",
    ].unique()

    assert set(included_borderline) == {"included_in_regression"}
    assert set(excluded_low_volume) == {"excluded_from_regression"}
    assert frame.loc[frame["low_volume_flag"], "low_volume_badge"].eq("Low volume").all()
    assert frame.loc[~frame["low_volume_flag"], "low_volume_badge"].eq("Sufficient volume").all()
    assert frame.loc[frame["theory_typology_borderline"], "theory_typology_borderline_badge"].eq("Borderline").all()
    assert frame.loc[~frame["theory_typology_borderline"], "theory_typology_borderline_badge"].eq("Clear").all()
    assert frame.loc[frame["dominant_domain_borderline_flag"], "dominant_domain_borderline_badge"].eq("Borderline").all()
    assert frame.loc[~frame["dominant_domain_borderline_flag"], "dominant_domain_borderline_badge"].eq("Clear").all()


def test_build_typology_dashboard_frame_rejects_null_required_flags() -> None:
    bundle = load_typology_dashboard_bundle(ROOT)
    bundle["model_data"] = bundle["model_data"].copy()
    bundle["model_data"]["low_volume_flag"] = bundle["model_data"]["low_volume_flag"].astype("object")
    bundle["model_data"].loc[bundle["model_data"].index[0], "low_volume_flag"] = pd.NA

    with pytest.raises(TypologyDashboardDataError, match="low_volume_flag.*null"):
        build_typology_dashboard_frame(bundle)


def test_build_typology_dashboard_frame_rejects_cross_table_field_mismatch() -> None:
    bundle = load_typology_dashboard_bundle(ROOT)
    bundle["theory_led"] = bundle["theory_led"].copy()
    bundle["theory_led"].loc[bundle["theory_led"].index[0], "institute_name"] = "Incorrect Institute Name"

    with pytest.raises(TypologyDashboardDataError, match="institute_name.*mismatch"):
        build_typology_dashboard_frame(bundle)
