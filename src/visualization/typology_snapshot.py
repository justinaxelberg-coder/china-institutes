from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import plotly.io as pio

from visualization.typology_dashboard_charts import (
    DOMAIN_LABELS,
    build_dominant_domain_composition_chart,
    build_institute_domain_salience_chart,
    build_institute_drilldown_summary,
    build_institute_vs_peer_comparison_chart,
    build_typology_field_map,
    build_typology_kpis,
    build_typology_profile_heatmap,
)
from visualization.typology_dashboard_data import (
    build_typology_dashboard_frame,
    load_typology_dashboard_bundle,
)


SNAPSHOT_FILENAME = "typology_dashboard_snapshot.html"


def _format_int(value: int | float) -> str:
    return f"{int(value):,}"


def _format_pct(value: float | int) -> str:
    return f"{float(value) * 100:.1f}%"


def _field(value: object) -> str:
    if value is None or pd.isna(value):
        return "NA"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _build_typology_distribution_summary(frame: pd.DataFrame) -> pd.DataFrame:
    summary = (
        frame.assign(
            theory_typology=frame["theory_typology"].fillna("Unassigned"),
            model_ready=frame["regression_inclusion_status"].eq("included_in_regression"),
        )
        .groupby("theory_typology", observed=True)
        .agg(
            institutes=("institute_id", "nunique"),
            docs_total=("total_docs", "sum"),
            median_docs=("total_docs", "median"),
            model_ready_institutes=("model_ready", "sum"),
            dominant_domain=("dominant_domain", lambda values: values.mode().iloc[0] if not values.mode().empty else "NA"),
        )
        .reset_index()
        .sort_values(["institutes", "docs_total", "theory_typology"], ascending=[False, False, True])
        .reset_index(drop=True)
    )
    summary["share_of_institutes"] = summary["institutes"] / max(int(frame["institute_id"].nunique()), 1)
    summary["dominant_domain"] = summary["dominant_domain"].map(lambda value: DOMAIN_LABELS.get(value, str(value)))
    return summary[
        [
            "theory_typology",
            "institutes",
            "share_of_institutes",
            "model_ready_institutes",
            "docs_total",
            "median_docs",
            "dominant_domain",
        ]
    ]


def _build_type_profile_summaries(frame: pd.DataFrame, limit: int = 3) -> list[dict[str, str]]:
    summary = _build_typology_distribution_summary(frame).head(limit)
    cards: list[dict[str, str]] = []
    for row in summary.itertuples(index=False):
        subset = frame.loc[frame["theory_typology"].fillna("Unassigned").eq(row.theory_typology)]
        top_institute = (
            subset.sort_values(["total_docs", "institute_name"], ascending=[False, True])
            .iloc[0]["institute_name"]
            if not subset.empty
            else "NA"
        )
        cards.append(
            {
                "title": str(row.theory_typology),
                "body": (
                    f"{_format_int(row.institutes)} institutes account for {_format_pct(row.share_of_institutes)} "
                    f"of the dashboard frame. The typical dominant domain is {row.dominant_domain}, "
                    f"with {_format_int(row.model_ready_institutes)} model-ready institutes and "
                    f"{_format_int(row.docs_total)} total documents. Spotlight institute: {top_institute}."
                ),
            }
        )
    return cards


def _select_spotlight_institute(frame: pd.DataFrame) -> str | None:
    if frame.empty:
        return None
    ready = frame.loc[frame["regression_inclusion_status"].eq("included_in_regression")].copy()
    candidates = ready if not ready.empty else frame.copy()
    ordered = candidates.sort_values(
        ["total_docs", "theory_typology_confidence", "institute_name"],
        ascending=[False, False, True],
    )
    if ordered.empty:
        return None
    return str(ordered.iloc[0]["institute_id"])


def _plotly_fragment(figure: object, *, include_js: bool, div_id: str) -> str:
    return pio.to_html(
        figure,
        include_plotlyjs=True if include_js else False,
        full_html=False,
        config={"displayModeBar": False, "responsive": True},
        div_id=div_id,
    )


def _table_html(frame: pd.DataFrame, *, formatters: dict[str, object] | None = None) -> str:
    display = frame.copy()
    if formatters:
        for column, formatter in formatters.items():
            if column in display.columns:
                display[column] = display[column].map(formatter)
    headers = "".join(f"<th>{escape(str(column).replace('_', ' ').title())}</th>" for column in display.columns)
    rows = []
    for record in display.to_dict(orient="records"):
        cells = "".join(f"<td>{escape(_field(value))}</td>" for value in record.values())
        rows.append(f"<tr>{cells}</tr>")
    body = "".join(rows)
    return f"<table><thead><tr>{headers}</tr></thead><tbody>{body}</tbody></table>"


def _empty_state_html(message: str) -> str:
    return f"<div class='empty-state'><p>{escape(message)}</p></div>"


def build_typology_dashboard_snapshot_html(root: Path) -> str:
    bundle = load_typology_dashboard_bundle(Path(root))
    frame = build_typology_dashboard_frame(bundle)
    kpis = build_typology_kpis(frame)
    distribution = _build_typology_distribution_summary(frame)
    field_map = build_typology_field_map()
    spotlight_id = _select_spotlight_institute(frame)
    has_data = not frame.empty and spotlight_id is not None
    no_data_message = "No typology dashboard data is available for this snapshot."

    if has_data:
        spotlight = build_institute_drilldown_summary(frame, institute_id=spotlight_id)
        figures = [
            _plotly_fragment(
                build_dominant_domain_composition_chart(frame),
                include_js=True,
                div_id="typology-composition-chart",
            ),
            _plotly_fragment(
                build_typology_profile_heatmap(frame),
                include_js=False,
                div_id="typology-profile-heatmap",
            ),
            _plotly_fragment(
                build_institute_domain_salience_chart(frame, institute_id=spotlight_id),
                include_js=False,
                div_id="spotlight-salience-chart",
            ),
            _plotly_fragment(
                build_institute_vs_peer_comparison_chart(frame, institute_id=spotlight_id),
                include_js=False,
                div_id="spotlight-peer-chart",
            ),
        ]
    else:
        spotlight = {}
        figures = []

    kpi_cards = [
        ("Institutes", _format_int(kpis["institutes"])),
        ("Documents", _format_int(kpis["docs_total"])),
        ("Low-volume institutes", _format_int(kpis["low_volume_institutes"])),
        ("Borderline typologies", _format_int(kpis["borderline_typologies"])),
        ("Model-ready institutes", _format_int(kpis["model_ready_institutes"])),
        ("Largest typology", escape(str(kpis["top_typology"]))),
    ]
    kpi_html = "".join(
        f"<article class='kpi-card'><h3>{label}</h3><p>{value}</p></article>"
        for label, value in kpi_cards
    )

    profile_summaries = _build_type_profile_summaries(frame)
    profile_cards = (
        "".join(
            f"<article class='profile-card'><h3>{escape(card['title'])}</h3><p>{escape(card['body'])}</p></article>"
            for card in profile_summaries
        )
        if profile_summaries
        else _empty_state_html(no_data_message)
    )
    spotlight_rows = "".join(
        f"<tr><th>{escape(key.replace('_', ' ').title())}</th><td>{escape(_field(value))}</td></tr>"
        for key, value in spotlight.items()
    )

    distribution_table = (
        _table_html(
            distribution.rename(columns={"theory_typology": "typology"}),
            formatters={
                "share_of_institutes": _format_pct,
                "median_docs": lambda value: f"{float(value):.1f}",
                "docs_total": _format_int,
                "institutes": _format_int,
                "model_ready_institutes": _format_int,
            },
        )
        if not distribution.empty
        else _empty_state_html(no_data_message)
    )
    field_map_table = _table_html(field_map)
    composition_section = (
        f"<div class='chart-grid'>{figures[0]}{figures[1]}</div>"
        if has_data
        else _empty_state_html(no_data_message)
    )
    spotlight_section = (
        f"""
      <div class="spotlight-layout">
        <div class="spotlight-card">
          <table>
            <tbody>{spotlight_rows}</tbody>
          </table>
        </div>
        <div class="chart-grid">
          {figures[2]}
          {figures[3]}
        </div>
      </div>
"""
        if has_data
        else _empty_state_html(no_data_message)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Typology Dashboard Snapshot</title>
  <style>
    :root {{
      --bg: #f6f3ea;
      --ink: #1f2933;
      --muted: #52606d;
      --card: #fffdf8;
      --line: #d9d0bf;
      --accent: #8c3b2a;
      --accent-soft: #efe2cf;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(140, 59, 42, 0.10), transparent 28%),
        linear-gradient(180deg, #fbf8f1 0%, var(--bg) 100%);
    }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px 72px; }}
    header {{ margin-bottom: 28px; }}
    h1, h2, h3 {{ margin: 0 0 12px; line-height: 1.15; }}
    p {{ margin: 0 0 12px; color: var(--muted); }}
    section {{
      background: rgba(255, 253, 248, 0.92);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 22px;
      margin-top: 18px;
      box-shadow: 0 18px 40px rgba(72, 52, 20, 0.08);
    }}
    .kpi-grid, .profile-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 14px;
    }}
    .kpi-card, .profile-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
    }}
    .kpi-card p {{
      color: var(--accent);
      font-size: 1.8rem;
      font-weight: 700;
      margin: 0;
    }}
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    thead th {{
      background: var(--accent-soft);
      color: var(--ink);
    }}
    .spotlight-layout {{
      display: grid;
      grid-template-columns: minmax(260px, 340px) 1fr;
      gap: 16px;
      align-items: start;
    }}
    .spotlight-card {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
    }}
    .empty-state {{
      background: var(--card);
      border: 1px dashed var(--line);
      border-radius: 14px;
      padding: 20px;
    }}
    @media (max-width: 860px) {{
      .spotlight-layout {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Typology Dashboard Snapshot</h1>
      <p>Standalone HTML report generated from the typology dashboard data and Plotly chart builders.</p>
    </header>

    <section aria-labelledby="kpi-overview">
      <h2 id="kpi-overview">KPI Overview</h2>
      <div class="kpi-grid">{kpi_html}</div>
    </section>

    <section aria-labelledby="typology-distribution-summary">
      <h2 id="typology-distribution-summary">Typology Distribution Summary</h2>
      <p>Counts and document volume by theory-led typology, using the dashboard frame as the reporting base.</p>
      {distribution_table}
    </section>

    <section aria-labelledby="field-map">
      <h2 id="field-map">Field Map</h2>
      <p>Reference guide for the main fields surfaced in the snapshot and the broader dashboard.</p>
      {field_map_table}
    </section>

    <section aria-labelledby="typology-composition">
      <h2 id="typology-composition">Typology Composition</h2>
      {composition_section}
    </section>

    <section aria-labelledby="selected-type-profile-summaries">
      <h2 id="selected-type-profile-summaries">Selected Type Profile Summaries</h2>
      <div class="profile-grid">{profile_cards}</div>
    </section>

    <section aria-labelledby="institute-spotlight">
      <h2 id="institute-spotlight">Institute Spotlight</h2>
      <p>The spotlight prioritizes model-ready institutes with the largest document volume.</p>
      {spotlight_section}
    </section>
  </main>
</body>
</html>
"""


def write_typology_dashboard_snapshot(
    *,
    root: Path,
    output_path: Path | None = None,
) -> Path:
    html = build_typology_dashboard_snapshot_html(root=root)
    destination = output_path or (Path(root) / "outputs" / "final" / SNAPSHOT_FILENAME)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8")
    return destination


__all__ = [
    "SNAPSHOT_FILENAME",
    "build_typology_dashboard_snapshot_html",
    "write_typology_dashboard_snapshot",
]
