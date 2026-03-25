# Typology Dashboard Design

## Purpose

This spec defines a polished exploratory dashboard for the China institutes typology rewrite. The dashboard is intended first as a meeting-facing exploration surface for March 30, 2026, and second as an internal analysis tool for institute and typology inspection.

The dashboard should foreground:

- publication-derived typology groups
- institute-level drill-down
- within-domain rival versus collaborator orientation

The dashboard should not foreground regression results in the first pass. Those remain secondary and should not dominate the landing experience.

## Core Design Goal

The dashboard should help a viewer answer three questions quickly:

1. What ideal-typical groups exist in the corpus?
2. What makes each group substantively different?
3. Where does a given institute sit within that landscape?

The design should preserve the paper architecture:

- publication-only measurement and typology first
- explanatory metadata later and clearly separated

## Delivery Shape

The first implementation should deliver two related outputs:

### 1. Live dashboard

An interactive Streamlit dashboard integrated into the existing app surface in [app/results_dashboard.py](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py).

This is the primary exploratory tool for the meeting and later analysis.

### 2. Standalone HTML snapshot

A polished exportable HTML summary generated from the same typology outputs.

This is not a full interactive replacement for the Streamlit app. It is a portable narrative snapshot that preserves:

- headline typology metrics
- the main charts
- representative institute views

It should be suitable for circulation after the meeting or for colleagues who cannot run the app locally.

## Existing App Constraint

The project already has a Streamlit dashboard in [app/results_dashboard.py](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py).

The new work should extend that app rather than create a disconnected second application. The typology dashboard can be introduced as:

- a new top-level section or tab inside the existing dashboard
- or a refactored navigation structure if needed for clarity

The implementation should follow existing Streamlit and Plotly patterns already present in the app.

## Dashboard Information Architecture

The dashboard should have three main views.

### View 1: Overview

This is the meeting-facing landing view.

It should include:

- a KPI strip with:
  - institutes covered
  - model-ready institutes
  - low-volume institutes
  - borderline typology cases
- typology cards:
  - theory-led type name
  - institute count
  - share of all institutes
  - mean confidence
  - low-volume and borderline counts
- one primary field map:
  - institutes plotted on `security_signal` versus `economic_signal`
  - color by theory typology
  - size by `total_docs`
- one composition chart:
  - dominant domain composition within each theory type

The overview should be readable in under a minute and should avoid dense control panels above the fold.

### View 2: Typology Explorer

This view should support comparison across theory-led groups.

It should include:

- a typology selector
- a group summary panel for the selected type
- a heatmap or matrix-style chart showing the selected type's average:
  - domain salience
  - within-domain rival orientation
  - within-domain collaborator orientation
- a member table with:
  - institute name
  - region
  - dominant domain
  - typology confidence
  - borderline flag
  - low-volume flag
  - regression inclusion status
- an optional within-type scatter view so variation among members remains visible

The key requirement is that sentiment remains within-domain, not collapsed to one overall score.

### View 3: Institute Drill-Down

This view should allow focused inspection of one institute.

It should include:

- a profile header:
  - institute name
  - theory-led typology
  - cluster label if available
  - dominant domain
  - confidence
  - borderline status
  - region
  - total docs
- a domain salience profile chart
- a within-domain orientation chart:
  - rival versus collaborator by domain
- a peer comparison:
  - institute values versus theory-type average
- compact metadata context:
  - parent institution
  - institute type category
  - model inclusion status

This page should be designed for discussion of concrete cases during the meeting.

## Sentiment And Orientation Logic

The dashboard must present sentiment as domain-specific orientation, not as a single overall polarity.

This means:

- sentiment is shown within domains as `rival` versus `collaborator`
- `neutral` remains secondary and is used mainly for context or audit
- no chart should imply that institutes sit on a single engagement-threat line

The visual framing should reinforce the substantive claim:

- institutes can be collaborative in one domain and rivalrous in another

## Data Sources

The dashboard should read from the frozen typology outputs and should not recompute analytical results in the app layer.

Primary inputs:

- [institute_typology_publication_matrix.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_publication_matrix.csv)
- [institute_domain_profiles.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_domain_profiles.csv)
- [institute_typology_theory_led.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_theory_led.csv)
- [institute_typology_clustered.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_clustered.csv)
- [institute_typology_model_data.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_model_data.csv)
- [institute_typology_group_summary.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_group_summary.csv)

The app should build one merged cached frame keyed by `institute_id`.

The standalone HTML snapshot should be generated from the same merged data contract.

### Source Authority

The dashboard should treat the data files as authoritative for different presentation layers.

- [institute_typology_publication_matrix.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_publication_matrix.csv):
  - top-line corpus volume
  - dominant domain
  - salience shares
  - meeting-facing headline metrics
- [institute_domain_profiles.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_domain_profiles.csv):
  - within-domain orientation charts
  - `*_oriented_prop`
  - `*_rival_among_oriented`
  - `*_collaborator_among_oriented`
  - `*_rival_prop` and `*_collaborator_prop`
- [institute_typology_theory_led.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_theory_led.csv):
  - theory-led type labels
  - confidence
  - borderline flags
- [institute_typology_clustered.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_clustered.csv):
  - cluster labels for secondary context
- [institute_typology_model_data.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_model_data.csv):
  - institute metadata and regression inclusion context
- [institute_typology_group_summary.csv](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/tables/institute_typology_group_summary.csv):
  - group-level summary tables when already materialized

## Data Guardrails

The dashboard should fail loudly when required data files or required columns are missing.

Required safeguards:

- explicit file existence checks
- explicit required-column checks
- no silent zero-filling of missing typology or orientation columns
- clear badges for:
  - `low_volume_flag`
  - `theory_typology_borderline`
  - `dominant_domain_borderline_flag`

These uncertainty signals should be visible in both the live dashboard and the HTML snapshot.

## Navigation And Interaction

The interaction model should stay lightweight.

Recommended controls:

- sidebar or header filters for:
  - region
  - theory typology
  - dominant domain
  - minimum document count
  - include/exclude low-volume institutes
  - include/exclude borderline institutes
- institute search box
- typology selector for the explorer page

The dashboard should default to a sensible initial state rather than a blank canvas.

## Standalone HTML Snapshot

The snapshot should be a generated artifact rather than an exported Streamlit app.

It should be implemented as a report builder that writes a standalone `.html` file containing:

- top-line KPI panel
- typology distribution summary
- the field map chart
- one typology composition chart
- selected type profile summaries
- a compact institute spotlight section

Plotly charts can remain embedded for lightweight client-side interactivity, but the snapshot should not depend on a running Streamlit server.

The canonical HTML output should be:

- [typology_dashboard_snapshot.html](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/outputs/final/typology_dashboard_snapshot.html)

## Recommended Implementation Boundaries

The implementation should be split into focused responsibilities.

### App layer

- extend [app/results_dashboard.py](/Users/administrador/Downloads/china_institutes_pipeline_v9_1_china_filter/app/results_dashboard.py)
- or split reusable typology dashboard helpers into `src/visualization/` if the current app file becomes unwieldy

### Data preparation helpers

Create small reusable functions for:

- loading and validating typology dashboard sources
- building merged institute frames
- computing typology summary tables needed only for presentation

### HTML export layer

Add a dedicated builder script under `scripts/` and supporting rendering helpers under `src/visualization/`.

The export path should stay clearly separate from the Streamlit view logic even if both share chart-building helpers.

## Out Of Scope For First Pass

The following should remain out of scope unless they are trivial once the main dashboard works:

- embedding full regression exploration as a main tab
- map-heavy geographic storytelling
- advanced crossfilter linking across many charts
- institute-year temporal storytelling
- browser-side state persistence
- a second frontend stack

The first pass should be polished, not maximal.

## Testing And Verification

The implementation should include lightweight but real verification.

### Required checks

- tests for dashboard data loading and validation
- tests for summary builders used by the dashboard
- tests for standalone HTML generation
- compile check for changed modules
- smoke checks extended to include required typology dashboard outputs if new generated artifacts become canonical

### Manual verification

Before calling the work complete, verify:

- the overview reads cleanly on desktop
- the typology explorer can compare groups without visual clutter
- the institute drill-down highlights within-domain rival versus collaborator orientation correctly
- the HTML snapshot opens as a self-contained file and renders the expected sections

## Success Criteria

The first dashboard pass is successful if:

- the landing view tells a clear typology story in under a minute
- the typology explorer makes group differences legible
- the institute drill-down supports case discussion in the meeting
- sentiment is shown within-domain rather than as one global polarity
- the same analytical layer can be shared as a standalone HTML snapshot

## Planning Guidance

The implementation plan should treat this as one dashboard project with two coordinated surfaces:

- Streamlit exploratory dashboard
- standalone HTML report builder

The plan should sequence the work so the live dashboard becomes usable first, then reuse those same presentation helpers for the HTML snapshot wherever possible.
