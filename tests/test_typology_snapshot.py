from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from build_typology_dashboard_snapshot import build_snapshot  # noqa: E402
from visualization.typology_snapshot import (  # noqa: E402
    SNAPSHOT_FILENAME,
    build_typology_dashboard_snapshot_html,
)


def test_build_snapshot_writes_expected_output_path(tmp_path: Path) -> None:
    output_path = build_snapshot(root=tmp_path)

    assert output_path == tmp_path / "outputs" / "final" / SNAPSHOT_FILENAME
    assert output_path.exists()


def test_snapshot_html_contains_required_sections_and_is_self_contained(tmp_path: Path) -> None:
    html = build_typology_dashboard_snapshot_html(root=ROOT)
    output_path = build_snapshot(root=tmp_path, source_root=ROOT)
    written_html = output_path.read_text(encoding="utf-8")

    assert written_html == html
    assert "<html" in html.lower()
    assert "Typology Dashboard Snapshot" in html
    assert "KPI Overview" in html
    assert "Typology Distribution Summary" in html
    assert "Field Map" in html
    assert "Typology Composition" in html
    assert "Selected Type Profile Summaries" in html
    assert "Institute Spotlight" in html
    assert "streamlit" not in html.lower()
    assert 'src="https://cdn.plot.ly' not in html.lower()
    assert 'src="http://cdn.plot.ly' not in html.lower()
    assert 'src="https://plot.ly' not in html.lower()
    assert "Plotly.newPlot" in html


def test_snapshot_html_gracefully_handles_empty_dashboard_frame(monkeypatch) -> None:
    empty_frame = pd.DataFrame(
        columns=[
            "institute_id",
            "institute_name",
            "total_docs",
            "dominant_domain",
            "regression_inclusion_status",
            "theory_typology",
            "theory_typology_confidence",
        ]
    )

    monkeypatch.setattr("visualization.typology_snapshot.load_typology_dashboard_bundle", lambda root: {})
    monkeypatch.setattr("visualization.typology_snapshot.build_typology_dashboard_frame", lambda bundle: empty_frame)
    monkeypatch.setattr(
        "visualization.typology_snapshot.build_typology_kpis",
        lambda frame: {
            "institutes": 0,
            "docs_total": 0,
            "low_volume_institutes": 0,
            "borderline_typologies": 0,
            "model_ready_institutes": 0,
            "top_typology": "NA",
        },
    )

    html = build_typology_dashboard_snapshot_html(root=ROOT)

    assert "Typology Dashboard Snapshot" in html
    assert "KPI Overview" in html
    assert "Typology Distribution Summary" in html
    assert "Field Map" in html
    assert "Typology Composition" in html
    assert "Selected Type Profile Summaries" in html
    assert "Institute Spotlight" in html
    assert "No typology dashboard data is available for this snapshot." in html
    assert "Plotly.newPlot" not in html
    assert "streamlit" not in html.lower()
