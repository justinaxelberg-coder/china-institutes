# Typology Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a polished typology-first Streamlit dashboard with institute drill-down and a standalone HTML snapshot for the within-domain typology analysis.

**Architecture:** Extend the existing Streamlit app rather than creating a second frontend. Add a typed data-loading and summary layer for the typology outputs, reuse shared Plotly chart builders across the live dashboard and the standalone HTML snapshot, and keep publication-derived views separate from secondary explanatory context.

**Tech Stack:** Python, Streamlit, Plotly, pandas, pytest, existing project smoke checks

---

## File Structure

### Existing files to modify

- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py`
  - Integrate the new typology-first navigation and views into the existing Streamlit app.
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/__init__.py`
  - Export any new reusable dashboard/snapshot helpers if needed.
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/smoke_check_project.py`
  - Add checks for the typology dashboard data contract and generated snapshot artifact if it becomes canonical.

### New files to create

- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_data.py`
  - Load, validate, and merge the typology dashboard sources into one institute-level frame.
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_charts.py`
  - Shared Plotly chart builders for overview, typology explorer, and institute drill-down.
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_snapshot.py`
  - HTML snapshot rendering helpers that reuse the dashboard summaries and charts.
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/build_typology_dashboard_snapshot.py`
  - CLI entrypoint that writes `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/final/typology_dashboard_snapshot.html`.
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_data.py`
  - Tests for file/column validation and merged-frame construction.
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_charts.py`
  - Tests for chart inputs and key layout labels.
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_snapshot.py`
  - Tests for standalone HTML generation and required sections.

## Required Dashboard Schema

The merged dashboard frame must preserve the fields needed by the spec-driven presentation layer.

### Required institute identity and sizing fields
- `institute_id`
- `institute_name`
- `total_docs`
- `dominant_domain`
- `dominant_domain_share`
- `dominant_domain_borderline_flag`
- `low_volume_flag`

### Required typology context fields
- `theory_typology`
- `theory_typology_confidence`
- `theory_typology_borderline`
- `cluster_label`
- `region`
- `parent_institution`
- `institute_type_category`
- `regression_inclusion_status`

### Required overview signal fields
- `security_signal`
- `economic_signal`

### Required institute profile fields
- domain salience shares
- within-domain rival shares
- within-domain collaborator shares
- within-domain oriented proportions
- within-domain rival-among-oriented proportions
- within-domain collaborator-among-oriented proportions

No task should drop or rename these fields without updating both tests and spec.

## Task 1: Build The Typology Dashboard Data Contract

**Files:**
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_data.py`
- Test: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_data.py`

- [ ] **Step 1: Write the failing data-contract tests**

Add tests for:
- missing required CSV file raises a project-specific error
- missing required columns raise a clear validation error
- merged frame contains one row per `institute_id`
- `regression_inclusion_status` is derived explicitly and not guessed in the app

Example test skeleton:

```python
from pathlib import Path

import pandas as pd
import pytest

from src.visualization.typology_dashboard_data import (
    TypologyDashboardDataError,
    load_typology_dashboard_bundle,
)


def test_load_typology_dashboard_bundle_requires_domain_profiles(tmp_path: Path) -> None:
    outputs = tmp_path / "outputs" / "tables"
    outputs.mkdir(parents=True)
    pd.DataFrame({"institute_id": ["a"]}).to_csv(outputs / "institute_typology_publication_matrix.csv", index=False)

    with pytest.raises(TypologyDashboardDataError, match="institute_domain_profiles.csv"):
        load_typology_dashboard_bundle(tmp_path)
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_data.py -v
```

Expected:
- FAIL because the module does not exist yet

- [ ] **Step 3: Implement the minimal data loader and validators**

Implement:
- `TypologyDashboardDataError`
- `load_typology_dashboard_bundle(root: Path) -> dict[str, pd.DataFrame]`
- `build_typology_dashboard_frame(bundle: dict[str, pd.DataFrame]) -> pd.DataFrame`

Required source files:
- `institute_typology_publication_matrix.csv`
- `institute_domain_profiles.csv`
- `institute_typology_theory_led.csv`
- `institute_typology_clustered.csv`
- `institute_typology_model_data.csv`

Optional source:
- `institute_typology_group_summary.csv`

Derived fields should include:
- `regression_inclusion_status`
- human-readable boolean badges for `low_volume_flag`, `theory_typology_borderline`, and `dominant_domain_borderline_flag`

The merged frame must preserve at least:
- `total_docs`
- `dominant_domain`
- `dominant_domain_borderline_flag`
- `cluster_label`
- `parent_institution`
- `institute_type_category`
- `region`

- [ ] **Step 4: Run the data-contract tests again**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_data.py -v
```

Expected:
- PASS

- [ ] **Step 5: Commit the data-contract layer**

```bash
git add /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_data.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_data.py
git commit -m "feat: add typology dashboard data contract"
```

## Task 2: Add Reusable Typology Charts And Streamlit Views

**Files:**
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_charts.py`
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py`
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/__init__.py`
- Test: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_charts.py`

- [ ] **Step 1: Write the failing chart and dashboard tests**

Add tests for:
- overview chart builders return Plotly figures with the expected titles
- typology explorer chart consumes within-domain rival/collaborator columns from `institute_domain_profiles.csv`
- institute drill-down summary preserves borderline and low-volume badges

Example assertion:

```python
def test_typology_field_map_has_expected_axes(sample_dashboard_frame):
    fig = build_typology_field_map(sample_dashboard_frame)
    assert fig.layout.xaxis.title.text == "Security signal"
    assert fig.layout.yaxis.title.text == "Economic / STI signal"
```

- [ ] **Step 2: Run the new tests to verify they fail**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_charts.py -v
```

Expected:
- FAIL because the chart module and dashboard integration do not exist yet

- [ ] **Step 3: Implement reusable chart builders**

Add shared builders for:
- KPI-ready typology summaries
- typology field map
- dominant-domain composition chart
- typology profile heatmap or matrix
- institute domain salience chart
- institute within-domain rival/collaborator chart
- institute-vs-peer comparison chart

The Typology Explorer must include a member table with at least:
- `institute_name`
- `region`
- `dominant_domain`
- `theory_typology_confidence`
- `theory_typology_borderline`
- `low_volume_flag`
- `regression_inclusion_status`

The Institute Drill-Down header must include at least:
- `institute_name`
- `theory_typology`
- `cluster_label`
- `dominant_domain`
- `theory_typology_confidence`
- `theory_typology_borderline`
- `region`
- `total_docs`
- `parent_institution`
- `institute_type_category`

Keep data shaping in `typology_dashboard_data.py` and chart rendering in `typology_dashboard_charts.py`.

- [ ] **Step 4: Integrate a new typology-first section into the Streamlit app**

Modify `app/results_dashboard.py` so the new dashboard includes:
- Overview
- Typology Explorer
- Institute Drill-Down

Integration rules:
- preserve existing tabs rather than deleting them
- make typology the leading section for the meeting-facing flow
- keep regressions and older robustness tabs secondary

- [ ] **Step 5: Run the chart tests**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_charts.py -v
```

Expected:
- PASS

- [ ] **Step 6: Smoke-run the Streamlit entrypoint**

Run:

```bash
python -m compileall -q /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_charts.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_data.py
```

Expected:
- no syntax errors

- [ ] **Step 7: Commit the dashboard UI layer**

```bash
git add /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/__init__.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_dashboard_charts.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_charts.py
git commit -m "feat: add typology dashboard views"
```

## Task 3: Build The Standalone HTML Snapshot

**Files:**
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_snapshot.py`
- Create: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/build_typology_dashboard_snapshot.py`
- Test: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_snapshot.py`

- [ ] **Step 1: Write the failing snapshot tests**

Add tests for:
- builder writes `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/final/typology_dashboard_snapshot.html`
- generated HTML contains:
  - title / heading
  - KPI section
  - typology distribution section
  - field map section
  - typology composition section
  - selected type profile summary section
  - institute spotlight section
- HTML output is self-contained and does not require Streamlit

Example assertion:

```python
def test_build_typology_dashboard_snapshot_writes_required_sections(tmp_path: Path) -> None:
    out = tmp_path / "snapshot.html"
    build_typology_dashboard_snapshot(sample_dashboard_frame, out)
    html = out.read_text(encoding="utf-8")
    assert "Typology Overview" in html
    assert "Institute Spotlight" in html
```

- [ ] **Step 2: Run the snapshot tests to verify they fail**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_snapshot.py -v
```

Expected:
- FAIL because the snapshot builder does not exist yet

- [ ] **Step 3: Implement the snapshot renderer and CLI**

Implementation requirements:
- reuse summary and chart builders from the dashboard layer where practical
- emit a real standalone HTML file to `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/final/typology_dashboard_snapshot.html`
- embed Plotly output in the HTML rather than linking to a running app
- include:
  - KPI block
  - typology distribution summary
  - field map
  - typology composition chart
  - selected type profile summaries
  - institute spotlight

- [ ] **Step 4: Run the snapshot tests**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_snapshot.py -v
```

Expected:
- PASS

- [ ] **Step 5: Build the snapshot once manually**

Run:

```bash
python /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/build_typology_dashboard_snapshot.py
```

Expected:
- writes `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/final/typology_dashboard_snapshot.html`

- [ ] **Step 6: Commit the snapshot layer**

```bash
git add /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src/visualization/typology_snapshot.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/build_typology_dashboard_snapshot.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_snapshot.py
git commit -m "feat: add typology dashboard html snapshot"
```

## Task 4: Verification, Smoke Checks, And Final Polish

**Files:**
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/smoke_check_project.py`
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_within_domain_results_packet.py` if needed only for overlapping helper imports
- Modify: `/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py`

- [ ] **Step 1: Add smoke checks for the new dashboard contract**

Extend smoke checks to verify:
- required typology dashboard source files exist
- required columns for dashboard rendering exist
- snapshot output exists after it has been built if the snapshot becomes canonical
- one sample merged frame still exposes the required presentation schema for the live dashboard views

- [ ] **Step 2: Run focused tests for the new dashboard stack**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_data.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_dashboard_charts.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_snapshot.py -v
```

Expected:
- PASS

- [ ] **Step 3: Run the broader existing verification set**

Run:

```bash
pytest /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_typology_exports.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_within_domain_results_packet.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/tests/test_explanatory_models.py -v
python -m compileall -q /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/src /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/run_analysis.py
python /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/smoke_check_project.py
```

Expected:
- tests pass
- compile step succeeds
- smoke checks pass

- [ ] **Step 4: Perform manual dashboard inspection**

Run locally:

```bash
streamlit run /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py
```

Manual checks:
- overview tells the typology story quickly
- typology explorer remains readable on a laptop screen
- institute drill-down clearly shows within-domain rival versus collaborator orientation
- low-volume and borderline badges are visible and honest
- snapshot HTML opens directly in a browser and shows the expected sections

- [ ] **Step 5: Commit the verification and polish pass**

```bash
git add /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/scripts/smoke_check_project.py /Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py
git commit -m "test: verify typology dashboard outputs"
```

## Execution Notes

- Keep publication-derived presentation separate from explanatory context in the UI.
- Do not reintroduce a single overall China sentiment axis as the headline.
- Prefer small helper functions over adding more complexity directly into `app/results_dashboard.py`.
- If `app/results_dashboard.py` becomes unwieldy, move logic into `src/visualization/` helpers rather than growing the Streamlit file indefinitely.

## Final Verification Checklist

- [ ] New data-contract tests pass
- [ ] New chart tests pass
- [ ] New snapshot tests pass
- [ ] Existing typology-related tests still pass
- [ ] `python -m compileall -q ...` passes
- [ ] `python scripts/smoke_check_project.py` passes
- [ ] `outputs/final/typology_dashboard_snapshot.html` is generated
- [ ] Streamlit dashboard renders the new typology-first views cleanly
