from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


class TypologyDashboardDataError(ValueError):
    """Raised when the typology dashboard data contract is broken."""


_TABLE_FILENAMES: dict[str, str] = {
    "publication_matrix": "institute_typology_publication_matrix.csv",
    "domain_profiles": "institute_domain_profiles.csv",
    "theory_led": "institute_typology_theory_led.csv",
    "clustered": "institute_typology_clustered.csv",
    "model_data": "institute_typology_model_data.csv",
}

_OPTIONAL_TABLE_FILENAMES: dict[str, str] = {
    "group_summary": "institute_typology_group_summary.csv",
}

_DOMAIN_NAMES: tuple[str, ...] = (
    "security_strategy",
    "economy_trade",
    "science_technology",
    "environment_climate",
    "governance_law",
    "society_culture",
)


def _tables_dir(root: Path) -> Path:
    root = Path(root)
    preferred = root / "outputs" / "tables"
    if preferred.exists():
        return preferred
    if (root / _TABLE_FILENAMES["publication_matrix"]).exists():
        return root
    return preferred


def _missing_columns(frame: pd.DataFrame, required: Iterable[str]) -> list[str]:
    return sorted(col for col in required if col not in frame.columns)


def _require_columns(frame: pd.DataFrame, required: Iterable[str], *, label: str) -> None:
    missing = _missing_columns(frame, required)
    if missing:
        raise TypologyDashboardDataError(f"Missing {label} columns: {', '.join(missing)}")


def _require_unique_institute_ids(frame: pd.DataFrame, *, label: str) -> None:
    if frame["institute_id"].duplicated().any():
        duplicated = frame.loc[frame["institute_id"].duplicated(), "institute_id"].tolist()
        preview = ", ".join(map(str, duplicated[:5]))
        raise TypologyDashboardDataError(f"Duplicate institute_id values in {label}: {preview}")


def _require_non_null_columns(frame: pd.DataFrame, columns: Iterable[str], *, label: str) -> None:
    null_columns = [col for col in columns if col in frame.columns and frame[col].isna().any()]
    if null_columns:
        raise TypologyDashboardDataError(
            f"{', '.join(sorted(null_columns))} contains null values in {label}"
        )


def _load_csv(path: Path, *, label: str) -> pd.DataFrame:
    try:
        return pd.read_csv(path)
    except FileNotFoundError as exc:  # pragma: no cover - guarded by caller
        raise TypologyDashboardDataError(f"Missing required typology dashboard file: {path.name}") from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise TypologyDashboardDataError(f"Failed to read typology dashboard file {path.name}: {exc}") from exc


def _load_required_frame(tables_dir: Path, key: str) -> pd.DataFrame:
    filename = _TABLE_FILENAMES[key]
    path = tables_dir / filename
    if not path.exists():
        raise TypologyDashboardDataError(f"Missing required typology dashboard file: {filename}")
    return _load_csv(path, label=key)


def load_typology_dashboard_bundle(root: Path) -> dict[str, pd.DataFrame]:
    tables_dir = _tables_dir(Path(root))
    bundle = {key: _load_required_frame(tables_dir, key) for key in _TABLE_FILENAMES}
    for key, filename in _OPTIONAL_TABLE_FILENAMES.items():
        path = tables_dir / filename
        if path.exists():
            bundle[key] = _load_csv(path, label=key)
    return bundle


def _merge_on_institute_id(left: pd.DataFrame, right: pd.DataFrame, *, label: str) -> pd.DataFrame:
    merged = left.merge(right, on="institute_id", how="inner", validate="one_to_one")
    if len(merged) != len(left) or len(merged) != len(right):
        raise TypologyDashboardDataError(f"Institute_id mismatch while merging {label}")
    return merged


def _badge(flag: pd.Series, *, true_label: str, false_label: str) -> pd.Series:
    return flag.map({True: true_label, False: false_label})


def _status(flag: pd.Series) -> pd.Series:
    return flag.map({True: "excluded_from_regression", False: "included_in_regression"})


def _validate_shared_fields(
    base: pd.DataFrame,
    other: pd.DataFrame,
    *,
    label: str,
    columns: Iterable[str],
) -> None:
    shared = [col for col in columns if col in base.columns and col in other.columns]
    for column in shared:
        comparison = base[["institute_id", column]].merge(
            other[["institute_id", column]],
            on="institute_id",
            how="inner",
            suffixes=("_base", "_other"),
            validate="one_to_one",
        )
        left_values = comparison[f"{column}_base"].astype("object").where(comparison[f"{column}_base"].notna(), "__NULL__")
        right_values = comparison[f"{column}_other"].astype("object").where(comparison[f"{column}_other"].notna(), "__NULL__")
        mismatch = comparison[left_values != right_values]
        if not mismatch.empty:
            preview = mismatch.loc[:, "institute_id"].astype(str).head(5).tolist()
            raise TypologyDashboardDataError(
                f"{column} mismatch across tables in {label}: institute_id(s) {', '.join(preview)}"
            )


def build_typology_dashboard_frame(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame:
    required_keys = set(_TABLE_FILENAMES)
    missing_keys = sorted(required_keys - set(bundle))
    if missing_keys:
        raise TypologyDashboardDataError(f"Missing typology dashboard bundle keys: {', '.join(missing_keys)}")

    publication = bundle["publication_matrix"].copy()
    domain_profiles = bundle["domain_profiles"].copy()
    theory_led = bundle["theory_led"].copy()
    clustered = bundle["clustered"].copy()
    model_data = bundle["model_data"].copy()

    publication_required = {
        "institute_id",
        "institute_name",
        "total_docs",
        "dominant_domain",
        "dominant_domain_share",
        "dominant_domain_borderline_flag",
        "low_volume_flag",
    }
    publication_required.update(f"{domain}_salience_share" for domain in _DOMAIN_NAMES)
    publication_required.update(f"{domain}_rival_prop" for domain in _DOMAIN_NAMES)
    publication_required.update(f"{domain}_collaborator_prop" for domain in _DOMAIN_NAMES)
    _require_columns(publication, publication_required, label="publication matrix")
    _require_unique_institute_ids(publication, label="publication matrix")
    _require_non_null_columns(
        publication,
        ["low_volume_flag", "dominant_domain_borderline_flag"],
        label="publication matrix",
    )

    domain_required = {
        "institute_id",
        "institute_name",
        "dominant_domain",
        "low_volume_flag",
    }
    domain_required.update(f"{domain}_oriented_prop" for domain in _DOMAIN_NAMES)
    domain_required.update(f"{domain}_rival_among_oriented" for domain in _DOMAIN_NAMES)
    domain_required.update(f"{domain}_collaborator_among_oriented" for domain in _DOMAIN_NAMES)
    _require_columns(domain_profiles, domain_required, label="domain profiles")
    _require_unique_institute_ids(domain_profiles, label="domain profiles")
    _require_non_null_columns(
        domain_profiles,
        ["low_volume_flag"],
        label="domain profiles",
    )

    theory_required = {
        "institute_id",
        "institute_name",
        "low_volume_flag",
        "theory_typology",
        "theory_typology_confidence",
        "theory_typology_borderline",
        "security_signal",
        "economic_signal",
    }
    _require_columns(theory_led, theory_required, label="theory-led typology")
    _require_unique_institute_ids(theory_led, label="theory-led typology")
    _require_non_null_columns(
        theory_led,
        ["low_volume_flag", "theory_typology_borderline"],
        label="theory-led typology",
    )

    cluster_required = {
        "institute_id",
        "cluster_label",
    }
    _require_columns(clustered, cluster_required, label="clustered typology")
    _require_unique_institute_ids(clustered, label="clustered typology")
    _require_non_null_columns(
        clustered,
        ["low_volume_flag", "dominant_domain_borderline_flag"],
        label="clustered typology",
    )

    model_required = {
        "institute_id",
        "institute_name",
        "low_volume_flag",
        "region",
        "parent_institution",
        "institute_type_category",
    }
    _require_columns(model_data, model_required, label="model data")
    _require_unique_institute_ids(model_data, label="model data")
    _require_non_null_columns(
        model_data,
        ["low_volume_flag"],
        label="model data",
    )

    publication_ids = set(publication["institute_id"])
    for label, frame in {
        "domain profiles": domain_profiles,
        "theory-led typology": theory_led,
        "clustered typology": clustered,
        "model data": model_data,
    }.items():
        frame_ids = set(frame["institute_id"])
        if frame_ids != publication_ids:
            missing = sorted(publication_ids - frame_ids)
            extra = sorted(frame_ids - publication_ids)
            parts = []
            if missing:
                parts.append(f"missing {len(missing)} ids")
            if extra:
                parts.append(f"unexpected {len(extra)} ids")
            raise TypologyDashboardDataError(f"Institute_id mismatch in {label}: {', '.join(parts)}")

    _validate_shared_fields(
        publication,
        domain_profiles,
        label="domain profiles",
        columns=["institute_name", "dominant_domain", "low_volume_flag"],
    )
    _validate_shared_fields(
        publication,
        theory_led,
        label="theory-led typology",
        columns=["institute_name", "dominant_domain", "low_volume_flag"],
    )
    _validate_shared_fields(
        publication,
        clustered,
        label="clustered typology",
        columns=["institute_name", "dominant_domain", "low_volume_flag"],
    )
    _validate_shared_fields(
        publication,
        model_data,
        label="model data",
        columns=["institute_name", "low_volume_flag"],
    )

    frame = publication[
        [
            "institute_id",
            "institute_name",
            "total_docs",
            "dominant_domain",
            "dominant_domain_share",
            "dominant_domain_borderline_flag",
            "low_volume_flag",
            *[f"{domain}_salience_share" for domain in _DOMAIN_NAMES],
            *[f"{domain}_rival_prop" for domain in _DOMAIN_NAMES],
            *[f"{domain}_collaborator_prop" for domain in _DOMAIN_NAMES],
        ]
    ].copy()

    frame = _merge_on_institute_id(
        frame,
        domain_profiles[
            [
                "institute_id",
                *[f"{domain}_oriented_prop" for domain in _DOMAIN_NAMES],
                *[f"{domain}_rival_among_oriented" for domain in _DOMAIN_NAMES],
                *[f"{domain}_collaborator_among_oriented" for domain in _DOMAIN_NAMES],
            ]
        ].copy(),
        label="domain profiles",
    )

    frame = _merge_on_institute_id(
        frame,
        theory_led[
            [
                "institute_id",
                "theory_typology",
                "theory_typology_confidence",
                "theory_typology_borderline",
                "security_signal",
                "economic_signal",
            ]
        ].copy(),
        label="theory-led typology",
    )

    frame = _merge_on_institute_id(
        frame,
        clustered[["institute_id", "cluster_label"]].copy(),
        label="clustered typology",
    )

    frame = _merge_on_institute_id(
        frame,
        model_data[
            [
                "institute_id",
                "region",
                "parent_institution",
                "institute_type_category",
            ]
        ].copy(),
        label="model data",
    )

    _require_non_null_columns(
        frame,
        ["low_volume_flag", "theory_typology_borderline", "dominant_domain_borderline_flag"],
        label="merged typology dashboard frame",
    )
    frame["regression_inclusion_status"] = _status(frame["low_volume_flag"])
    frame["low_volume_badge"] = _badge(frame["low_volume_flag"], true_label="Low volume", false_label="Sufficient volume")
    frame["theory_typology_borderline_badge"] = _badge(
        frame["theory_typology_borderline"],
        true_label="Borderline",
        false_label="Clear",
    )
    frame["dominant_domain_borderline_badge"] = _badge(
        frame["dominant_domain_borderline_flag"],
        true_label="Borderline",
        false_label="Clear",
    )

    ordered_columns = [
        "institute_id",
        "institute_name",
        "total_docs",
        "dominant_domain",
        "dominant_domain_share",
        "dominant_domain_borderline_flag",
        "dominant_domain_borderline_badge",
        "low_volume_flag",
        "low_volume_badge",
        "regression_inclusion_status",
        "theory_typology",
        "theory_typology_confidence",
        "theory_typology_borderline",
        "theory_typology_borderline_badge",
        "cluster_label",
        "region",
        "parent_institution",
        "institute_type_category",
        "security_signal",
        "economic_signal",
        *[f"{domain}_salience_share" for domain in _DOMAIN_NAMES],
        *[f"{domain}_rival_prop" for domain in _DOMAIN_NAMES],
        *[f"{domain}_collaborator_prop" for domain in _DOMAIN_NAMES],
        *[f"{domain}_oriented_prop" for domain in _DOMAIN_NAMES],
        *[f"{domain}_rival_among_oriented" for domain in _DOMAIN_NAMES],
        *[f"{domain}_collaborator_among_oriented" for domain in _DOMAIN_NAMES],
    ]

    remaining = [col for col in frame.columns if col not in ordered_columns]
    return frame[ordered_columns + remaining].sort_values(["institute_name", "institute_id"]).reset_index(drop=True)
