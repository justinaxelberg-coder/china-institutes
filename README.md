# China Institutes

This repository contains the current working bundle for the China-focused institutes project, including:

- processed corpus files
- institute-level typology outputs
- a Streamlit dashboard for exploratory analysis
- a static HTML dashboard snapshot
- short `.docx` and `.md` summary documents

## Dashboard

The main live dashboard is:

- `app/results_dashboard.py`

To run it locally from the repository root:

```bash
streamlit run app/results_dashboard.py
```

The dashboard is organized around:

- typology overview
- typology-group exploration
- institute drill-down
- supporting legacy views for maps, rankings, trends, source types, Wordfish, and Confucius Institute models

## Public Sharing

For a simple public link that non-technical users can open directly, the recommended setup is:

- deploy the dashboard on Streamlit Community Cloud
- keep the included HTML snapshot as a backup share artifact

### Deploy On Streamlit Community Cloud

1. Push the latest repository state to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create a new app from this repository.
4. Set the main file path to:
   - `app/results_dashboard.py`
5. Deploy the app and share the resulting public URL.

The repository already includes the deployment files Streamlit Cloud needs:

- `requirements.txt`
- `.streamlit/config.toml`

If someone prefers a static artifact instead of the live app, use the HTML snapshot below.

## Shareable Snapshot

A static HTML snapshot is included here:

- `outputs/final/typology_dashboard_snapshot.html`

This is useful for quick circulation when you want a portable dashboard-style artifact without running Streamlit.

## Included Summaries

Two short reference documents are included in both `.md` and `.docx` form:

- `outputs/final/retrieval_and_corpus_summary.docx`
- `outputs/final/domain_sentiment_results_summary.docx`

They cover:

- the current retrieval and corpus backbone doing the analytical heavy lifting
- the current domain-identification and rival/collaborator orientation methodology
- a short results summary from the present typology pipeline

## Main Data Used By The Dashboard

The dashboard reads primarily from:

- `data/processed/panel_institute_master.csv`
- `data/processed/panel_institute_year_master.csv`
- `data/processed/panel_institute_master_embeddedness.csv`
- `data/processed/panel_institute_year_master_embeddedness.csv`
- `outputs/tables/institute_typology_publication_matrix.csv`
- `outputs/tables/institute_domain_profiles.csv`
- `outputs/tables/institute_typology_theory_led.csv`
- `outputs/tables/institute_typology_clustered.csv`
- `outputs/tables/institute_typology_model_data.csv`
- `outputs/final/china_institutes_typology_dataset.csv`

## Current Scope

The present analytical heavy lifting is being done by:

- the attributed indexed-publication corpus
- a smaller attributed grey-literature layer
- the paragraph-level domain and within-domain orientation pipeline

Exploratory topic-modeling layers remain useful for supplementary work, but they are not the main engine of the current publication-derived typology.
