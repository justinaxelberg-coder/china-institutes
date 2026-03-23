# Domain-Specific China Orientation Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current one-axis framing interpretation with a paragraph-level, domain-specific institute typology built from publication text and delivered in controlled sprints.

**Architecture:** The rewrite will preserve the existing pipeline shape where possible, but introduce a new paragraph-level scoring layer between cleaned corpus text and institute-level framing outputs. Broad domains, rival/collaborator orientation, and institute typology outputs will be added incrementally so each sprint produces inspectable artifacts before the next begins.

**Tech Stack:** Python, pandas, YAML configs, existing `src/analysis/*` scaffold, project CSV outputs, pytest

---

## File Structure

### Core measurement files

- Create: `src/analysis/paragraphs.py`
  - Segment cleaned documents into paragraphs and preserve paragraph-document links.
- Create: `src/analysis/domain_profiles.py`
  - Collapse existing thematic signals or apply a domain classifier to paragraphs and normalize broad-domain weights.
- Create: `src/analysis/orientation.py`
  - Score `rival` and `collaborator` orientation independently at paragraph level and compute neutral residuals.
- Create: `src/analysis/typology.py`
  - Build theory-led profile assignment helpers and data-led clustering utilities.

### Pipeline scripts

- Create: `src/08b_score_domain_orientations.py`
  - Run paragraph segmentation, domain scoring, orientation scoring, and document aggregation.
- Create: `src/08c_build_institute_typology.py`
  - Build institute-level profile matrices and typology outputs.
- Modify: `run_analysis.py`
  - Wire the new scripts into the main analysis flow without breaking the rest of the pipeline.

### Config

- Create: `config/analysis/domain_schema.yaml`
  - Define the five broad domains and thematic collapse rules.
- Create: `config/analysis/orientation_lexicon.yaml`
  - Define rival and collaborator terms, weights, and normalization settings.
- Modify: `config/analysis/scaffold.yaml`
  - Add paths and thresholds for the new scoring outputs.

### Outputs

- Create: `data/processed/corpus_paragraphs_scored.csv`
- Create: `data/processed/corpus_domain_orientation_scored.csv`
- Create: `outputs/tables/institute_domain_profiles.csv`
- Create: `outputs/tables/institute_typology_theory_led.csv`
- Create: `outputs/tables/institute_typology_clustered.csv`
- Create: `outputs/tables/institute_typology_validation.csv`

### Validation and tests

- Create: `tests/test_paragraphs.py`
- Create: `tests/test_domain_profiles.py`
- Create: `tests/test_orientation.py`
- Create: `tests/test_typology.py`
- Modify: validation sampling scripts if a paragraph-level review packet is added in Sprint 3 or 4.

## Sprint Plan

### Task 1: Sprint 1 - Domain Scaffold

**Files:**
- Create: `config/analysis/domain_schema.yaml`
- Create: `src/analysis/paragraphs.py`
- Create: `src/analysis/domain_profiles.py`
- Create: `tests/test_paragraphs.py`
- Create: `tests/test_domain_profiles.py`

- [ ] **Step 1: Write the failing paragraph segmentation tests**

Test cases:
- a single document with clean paragraph breaks preserves order and document IDs
- empty and near-empty paragraphs are dropped or normalized consistently
- paragraph outputs can be re-aggregated to the original document

- [ ] **Step 2: Run the paragraph tests to verify they fail**

Run: `pytest tests/test_paragraphs.py -v`
Expected: FAIL because paragraph utilities do not exist yet

- [ ] **Step 3: Write the failing domain profile tests**

Test cases:
- a paragraph with mixed thematic signals receives fractional weights across broad domains
- broad-domain weights normalize as expected
- broad-domain mapping stays stable for simple controlled inputs

- [ ] **Step 4: Run the domain profile tests to verify they fail**

Run: `pytest tests/test_domain_profiles.py -v`
Expected: FAIL because domain scoring utilities do not exist yet

- [ ] **Step 5: Implement paragraph segmentation**

Implementation target:
- `src/analysis/paragraphs.py`

Requirements:
- preserve `doc_id`, `institute_id`, and paragraph order
- expose configurable minimum paragraph length
- avoid changing the source document text used elsewhere in the pipeline

- [ ] **Step 6: Implement the broad-domain scoring layer**

Implementation targets:
- `config/analysis/domain_schema.yaml`
- `src/analysis/domain_profiles.py`

Requirements:
- map existing thematic structure into the five approved domains
- support fractional paragraph weights
- normalize paragraph-domain weights for aggregation

- [ ] **Step 7: Run Sprint 1 tests**

Run: `pytest tests/test_paragraphs.py tests/test_domain_profiles.py -v`
Expected: PASS

- [ ] **Step 8: Produce a Sprint 1 inspection artifact**

Run a limited scoring pass and write:
- `data/processed/corpus_paragraphs_scored.csv`

Inspection questions:
- are paragraph counts plausible?
- do mixed paragraphs receive sensible multi-domain allocations?
- are the five domains adequately populated?

- [ ] **Step 9: Run smoke verification for changed code**

Run:
- `python -m compileall -q src/analysis/paragraphs.py src/analysis/domain_profiles.py`
- `python scripts/smoke_check_project.py`

- [ ] **Step 10: Pause for user review before Sprint 2**

Acceptance gate:
- user approves the domain scaffold outputs before orientation work starts

### Task 2: Sprint 2 - Orientation Layer

**Files:**
- Create: `config/analysis/orientation_lexicon.yaml`
- Create: `src/analysis/orientation.py`
- Create: `src/08b_score_domain_orientations.py`
- Modify: `config/analysis/scaffold.yaml`
- Create: `tests/test_orientation.py`

- [ ] **Step 1: Write the failing orientation tests**

Test cases:
- rival and collaborator are independently scoreable for the same paragraph
- residual neutral share is computed from remaining salience
- paragraphs with domain salience but weak orientation are mostly neutral

- [ ] **Step 2: Run the orientation tests to verify they fail**

Run: `pytest tests/test_orientation.py -v`
Expected: FAIL because orientation utilities do not exist yet

- [ ] **Step 3: Implement the rival/collaborator orientation scorer**

Implementation target:
- `src/analysis/orientation.py`

Requirements:
- independent rival and collaborator scores
- no forced opposition
- domain-aware allocation support for paragraph-level aggregation

- [ ] **Step 4: Implement the pipeline runner for paragraph-domain-orientation scoring**

Implementation target:
- `src/08b_score_domain_orientations.py`

Requirements:
- read cleaned corpus
- segment into paragraphs
- score domains
- score orientations
- write paragraph and document outputs

- [ ] **Step 5: Update scaffold config and output contracts**

Implementation target:
- `config/analysis/scaffold.yaml`

Requirements:
- add new paths and thresholds without breaking downstream compatibility unnecessarily

- [ ] **Step 6: Run Sprint 2 tests**

Run: `pytest tests/test_orientation.py -v`
Expected: PASS

- [ ] **Step 7: Produce Sprint 2 inspection artifacts**

Write:
- `data/processed/corpus_domain_orientation_scored.csv`

Inspection questions:
- do paragraphs show meaningful coexisting rival and collaborator signals?
- does neutral residual look like a genuine remainder rather than noise?
- do document-level aggregates read plausibly in hand checks?

- [ ] **Step 8: Run smoke verification for changed code**

Run:
- `python -m compileall -q src/analysis/orientation.py src/08b_score_domain_orientations.py`
- `python scripts/smoke_check_project.py`

- [ ] **Step 9: Pause for user review before Sprint 3**

Acceptance gate:
- user approves orientation behavior before institute typology work begins

### Task 3: Sprint 3 - Institute Profiles and Typology

**Files:**
- Create: `src/analysis/typology.py`
- Create: `src/08c_build_institute_typology.py`
- Create: `tests/test_typology.py`
- Create: `outputs/tables/institute_domain_profiles.csv`
- Create: `outputs/tables/institute_typology_theory_led.csv`
- Create: `outputs/tables/institute_typology_clustered.csv`

- [ ] **Step 1: Write the failing typology tests**

Test cases:
- institute aggregation preserves domain and orientation shares
- theory-led assignment behaves correctly on synthetic institute profiles
- cluster helper produces stable outputs on toy data

- [ ] **Step 2: Run the typology tests to verify they fail**

Run: `pytest tests/test_typology.py -v`
Expected: FAIL because typology utilities do not exist yet

- [ ] **Step 3: Implement institute-level aggregation**

Implementation targets:
- `src/analysis/typology.py`
- `src/08c_build_institute_typology.py`

Requirements:
- aggregate paragraph/document scores to institute matrices
- write auditable profile tables
- flag low-volume institutes where necessary

- [ ] **Step 4: Implement theory-led type assignment**

Requirements:
- use transparent thresholds or rule-based assignment
- keep labels provisional and editable
- expose diagnostics for borderline cases

- [ ] **Step 5: Implement data-led clustering**

Requirements:
- cluster on the same profile matrix
- record chosen clustering settings
- write outputs that are easy to compare with theory-led types

- [ ] **Step 6: Run Sprint 3 tests**

Run: `pytest tests/test_typology.py -v`
Expected: PASS

- [ ] **Step 7: Produce Sprint 3 inspection artifacts**

Write:
- `outputs/tables/institute_domain_profiles.csv`
- `outputs/tables/institute_typology_theory_led.csv`
- `outputs/tables/institute_typology_clustered.csv`

Inspection questions:
- are the resulting ideal types interpretable?
- do theory-led and clustered structures broadly converge?
- which institutes appear mixed or borderline?

- [ ] **Step 8: Add validation support for the new typology**

Requirements:
- generate a targeted review queue for borderline institute assignments
- prepare paragraph-level examples for manual inspection

- [ ] **Step 9: Run smoke verification for changed code**

Run:
- `python -m compileall -q src/analysis/typology.py src/08c_build_institute_typology.py`
- `python scripts/smoke_check_project.py`

- [ ] **Step 10: Pause for user review before Sprint 4**

Acceptance gate:
- user approves the typology outputs before explanatory modeling starts

### Task 4: Sprint 4 - Explanatory Models and Paper-Ready Outputs

**Files:**
- Modify or create modeling scripts under `src/`
- Modify export scripts as needed
- Create paper-facing summaries under `outputs/final/`

- [ ] **Step 1: Identify the explanatory modeling target**

Choose one or more:
- type membership
- domain shares
- orientation shares

- [ ] **Step 2: Write or adapt modeling tests where practical**

Requirements:
- protect expected input schema
- verify modeling prep does not drop key covariates silently

- [ ] **Step 3: Implement explanatory model prep**

Requirements:
- merge institute profiles with curated institute metadata
- document covariate availability and missingness

- [ ] **Step 4: Implement the main explanatory models**

Requirements:
- preserve a publication-only typology
- use metadata only as explanatory variables
- export model-ready tables and summary results

- [ ] **Step 5: Produce paper-ready artifacts**

Write:
- results tables
- typology summaries
- dashboard-ready exports
- memo summarizing substantive findings

- [ ] **Step 6: Run end-to-end verification**

Run:
- targeted pytest suite for the new modules
- `python -m compileall -q src scripts run_analysis.py`
- `python scripts/smoke_check_project.py`

- [ ] **Step 7: Pause for publication-oriented review**

Acceptance gate:
- user confirms the outputs support the intended paper argument before broader polishing

## Execution Notes

- This workspace is currently not a git repository, so commit steps are intentionally omitted from the task flow.
- Each sprint should be treated as a checkpointed delivery. Do not automatically begin the next sprint without user approval.
- Preserve backward compatibility where feasible, but prefer explicit new outputs over silently overloading old one-axis files.
