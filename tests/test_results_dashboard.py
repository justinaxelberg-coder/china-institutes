from __future__ import annotations

import ast
import importlib.util
import importlib
import sys
from pathlib import Path
import builtins

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "app" / "results_dashboard.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("results_dashboard", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("results_dashboard", module)
    spec.loader.exec_module(module)
    return module


def test_load_panel_frame_prefers_embeddedness_when_primary_lacks_legacy_metrics(tmp_path: Path) -> None:
    module = _load_module()

    primary = tmp_path / "panel.csv"
    embedded = tmp_path / "panel_embedded.csv"

    pd.DataFrame(
        [
            {
                "institute_id": "alpha",
                "total_docs": 10,
            }
        ]
    ).to_csv(primary, index=False)

    pd.DataFrame(
        [
            {
                "institute_id": "alpha",
                "total_docs": 11,
                "orientation_docs": 7,
                "sensitive_curated_share": 0.12,
                "mean_embedding_score": -0.08,
            }
        ]
    ).to_csv(embedded, index=False)

    frame = module.load_panel_frame_with_fallback(
        primary,
        embedded,
        required_cols=["orientation_docs", "sensitive_curated_share", "mean_embedding_score"],
    )

    assert frame.loc[0, "total_docs"] == 11
    assert frame.loc[0, "orientation_docs"] == 7
    assert frame.loc[0, "sensitive_curated_share"] == 0.12
    assert frame.loc[0, "mean_embedding_score"] == -0.08


def test_load_panel_frame_backfills_aliases_and_defaults_when_fallback_missing(tmp_path: Path) -> None:
    module = _load_module()

    primary = tmp_path / "panel.csv"
    pd.DataFrame(
        [
            {
                "institute_id": "alpha",
                "total_docs": 10,
                "sensitive_topic_share": 0.04,
            }
        ]
    ).to_csv(primary, index=False)

    frame = module.load_panel_frame_with_fallback(
        primary,
        tmp_path / "missing.csv",
        required_cols=["orientation_docs", "sensitive_curated_share", "mean_embedding_score"],
        alias_map={"sensitive_curated_share": "sensitive_topic_share"},
    )

    assert "orientation_docs" in frame.columns
    assert "sensitive_curated_share" in frame.columns
    assert "mean_embedding_score" in frame.columns
    assert frame.loc[0, "orientation_docs"] == 0
    assert frame.loc[0, "sensitive_curated_share"] == 0.04
    assert np.isnan(frame.loc[0, "mean_embedding_score"])


def test_all_plotly_chart_calls_use_explicit_streamlit_keys() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    plotly_calls = []
    missing_key_lines = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "plotly_chart":
            continue
        plotly_calls.append(node.lineno)
        if not any(keyword.arg == "key" for keyword in node.keywords):
            missing_key_lines.append(node.lineno)

    assert plotly_calls, "Expected at least one plotly_chart call in the dashboard."
    assert not missing_key_lines, f"Missing explicit key= on plotly_chart calls at lines {missing_key_lines}"


def test_typology_dashboard_modules_do_not_require_matplotlib_on_import(monkeypatch) -> None:
    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name.startswith("matplotlib"):
            raise ModuleNotFoundError("No module named 'matplotlib'")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    for name in [
        "visualization",
        "visualization.typology_dashboard_charts",
        "visualization.typology_dashboard_data",
    ]:
        sys.modules.pop(name, None)

    importlib.import_module("visualization.typology_dashboard_charts")
    importlib.import_module("visualization.typology_dashboard_data")
