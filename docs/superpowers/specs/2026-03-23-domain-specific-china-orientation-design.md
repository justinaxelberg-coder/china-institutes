# Domain-Specific China Orientation Redesign

## Purpose

This spec defines a rewrite of the current China framing layer for the institutes corpus. The current single-axis interpretation is too blunt for the underlying research problem. Institutes do not sort cleanly from "cooperative" to "security-focused," because many combine collaboration, rivalry, and neutral analytic treatment across different issue areas. The redesign introduces a domain-specific, paragraph-level measurement framework that is better aligned with the substantive claim the paper aims to make.

The primary intended output is an academic argument suitable for venues such as *Research Policy*, *Quantitative Science Studies*, or *Minerva*. The dashboard remains a secondary output for exploration and presentation.

## Research Problem

The project asks how China-focused institutes position China in their published output. The old framing layer pushes this into a one-dimensional spectrum, which obscures at least three realities:

1. Institutes often discuss economic, scientific, or social cooperation while simultaneously framing China as a strategic rival or threat.
2. Institutes often publish mixed texts in which different paragraphs take different orientations.
3. Institutes may be comparable not because they occupy points on a single line, but because they cluster into distinct publication profiles.

The paper's substantive aim is therefore:

> China-focused institutes do not sort neatly along a single engagement-threat continuum. Instead, they cluster into a small number of ideal-typical publication profiles defined by their domain emphases and their orientations toward China within those domains. Those profiles are partly explainable by institutional characteristics.

## Core Design Choice

The redesign replaces the single-axis model with a two-layer profile:

- domain salience
- domain-specific orientation

### Domains

The main specification uses five broad analytical domains:

- `security_strategy`
- `economy_trade`
- `science_technology`
- `governance_law`
- `society_culture`

These are broad enough to be stable and interpretable, but not so broad that important differences disappear. A three-domain collapse will be used later as a robustness check.

### Orientations

Within each domain, the redesign scores three orientation states:

- `rival`
- `collaborator`
- `neutral_residual`

`rival` and `collaborator` are scored independently, not as opposite ends of one axis. `neutral_residual` is not directly lexicon-scored; it is the remaining domain-salient material not strongly allocated to either rival or collaborator.

## Unit of Analysis

The paper's main unit of analysis is the institute.

The measurement layer, however, operates at the paragraph level so that the system can capture mixed domain-orientation combinations within the same document. Paragraphs are preferred to fixed-length windows because they are more interpretable, more defensible for manual validation, and more likely to preserve discrete argumentative moves.

The aggregation path is:

- paragraph -> document
- document -> institute

## Measurement Model

### Step 1: Paragraph segmentation

Each text in the validated corpus is segmented into paragraphs. Paragraphs that are too short or too noisy can be dropped or merged under a configurable minimum-content rule.

### Step 2: Fractional domain assignment

Each paragraph receives fractional weights across the five broad domains. Domain weights may come from a collapse of the existing thematic classifier or a revised domain-level classifier, but the output contract must be the same:

- weights are continuous
- multiple domains can be active for the same paragraph
- paragraph domain weights are normalized so that each paragraph contributes proportionally rather than exclusively

This allows a paragraph to count as partly `science_technology` and partly `security_strategy`, for example.

### Step 3: Independent orientation scoring

Each paragraph receives separate `rival` and `collaborator` scores. These are independent rather than opposite. A paragraph may score on both if it expresses mixed or ambivalent positioning.

The orientation layer should be designed to reflect stance toward China, not merely topic area. For example:

- STI cooperation language should not automatically imply collaborator orientation if the paragraph simultaneously frames China as a strategic competitor
- security discussion should not automatically imply rival orientation if the paragraph is analytic or managerial rather than adversarial

### Step 4: Neutral residual

For each paragraph-domain allocation, `neutral_residual` is computed as the portion of salience not strongly allocated to rival or collaborator. This avoids the need for a separate noisy lexicon for "neutrality."

### Step 5: Institute profile aggregation

Paragraph scores are aggregated up to document and institute levels to create:

- domain salience shares by institute
- domain-specific rival shares
- domain-specific collaborator shares
- domain-specific neutral residual shares

The result is a publication-only profile for each institute.

## Expected Variable Schema

The main institute matrix should include:

- `security_strategy_share`
- `economy_trade_share`
- `science_technology_share`
- `governance_law_share`
- `society_culture_share`

And, for each domain, three orientation shares such as:

- `security_strategy_rival_share`
- `security_strategy_collaborator_share`
- `security_strategy_neutral_share`

Equivalent variables should exist for each remaining domain.

The document-level and paragraph-level artifacts should preserve intermediate scores so the measurement pipeline remains auditable.

## Typology Strategy

The typology will be built from publication data only.

Two approaches will be tested:

### Theory-led typology

Define a small set of ideal types from the literature and substantive expectations. Candidate examples include:

- `security_hawks`
- `selective_engagers`
- `economic_or_sti_pragmatists`
- `dual_track_institutes`
- `broad_neutral_analysts`

These labels are provisional and should only survive if the data support them.

### Data-led typology

Cluster institutes using the domain-orientation matrix. The point is not to let clustering replace interpretation, but to test whether the publication corpus naturally recovers similar groupings.

### Comparison logic

The paper should compare:

- whether the theory-led and data-led structures broadly converge
- which solution is more stable and interpretable
- where the data challenge the initial theoretical expectations

## Explanatory Analysis

The typology itself will be derived only from publications. Institute metadata will not be used to define the types.

Once the typology is established, the project will estimate explanatory models using institute characteristics such as:

- location / region
- organization type
- parent institution type
- Chinese funding presence
- coauthorship with China
- participation ties
- Confucius Institute presence or closure
- other existing registry covariates already curated in the project

This preserves a clean causal sequence:

- publications define the outcome
- metadata help explain the outcome

## Validation Strategy

Validation must move from document-only review toward paragraph-aware review.

The validation framework should include:

- paragraph-level coding samples for domain assignment
- paragraph-level coding samples for rival vs collaborator orientation
- review of mixed paragraphs and borderline residual cases
- institute-level profile sanity checks using hand-read examples

Core tests:

- domain assignment validity
- rival/collaborator precision
- stability of institute profiles under alternative aggregation choices
- robustness to collapsing five domains to three
- comparison of paragraph-level and whole-document alternatives

## Outputs

The redesign should produce:

- paragraph-level scored corpus
- document-level aggregated orientation profiles
- institute-level domain-orientation matrix
- theory-led type assignments
- data-led cluster assignments
- explanatory regression tables
- dashboard-ready exports and summaries

The old one-axis interpretation should be retired from headline presentation once the new framework is validated.

## Risks and Guardrails

### Risk 1: Overly sparse profiles

Some institutes may have too few paragraphs in some domains for stable shares.

Guardrail:
- enforce minimum-volume rules for some typology and clustering steps
- report uncertainty or low-coverage flags

### Risk 2: Orientation lexicons bleed into domain detection

If domain and orientation vocabularies are not kept distinct, the model may collapse topic and stance.

Guardrail:
- separate domain detection logic from orientation logic
- validate failure modes explicitly

### Risk 3: Clusters are unstable or uninterpretable

Guardrail:
- compare multiple clustering specifications
- prefer theory-led interpretation if cluster structure is weak

### Risk 4: The paper becomes a methods note

Guardrail:
- keep the framing of the paper centered on the substantive finding that institutes exhibit ideal-typical domain-specific profiles
- present the measurement redesign as the necessary tool that makes that finding visible

## Delivery Strategy

The rewrite should be delivered in gated sprints so the user can maintain control over scope and inspect outputs before moving on.

### Sprint 1: Domain Scaffold

Goal:
- define the five-domain mapping and paragraph segmentation layer
- produce auditable paragraph-level domain weights

### Sprint 2: Orientation Layer

Goal:
- add rival and collaborator scoring at paragraph level
- compute neutral residuals and document-level aggregates

### Sprint 3: Institute Profiles and Typology

Goal:
- build institute matrices
- generate theory-led and data-led type assignments
- test stability and interpretability

### Sprint 4: Explanatory Models and Paper-Ready Outputs

Goal:
- run regressions on typology membership or profile dimensions
- produce tables, figures, dashboard exports, and a results memo

## Definition of Success

This redesign is successful if it allows the project to make a stronger substantive claim than the old axis could support:

- institutes are not well-described by a single cooperative-security line
- institutes exhibit distinct, interpretable, domain-specific publication profiles
- those profiles can be related to institutional characteristics in a disciplined way

## Out of Scope for This Rewrite

- institute-year dynamic modeling as the main paper design
- using metadata directly to construct the typology
- replacing the transparent scoring system with a fully latent or opaque model as the headline method

These may remain future extensions, but they are not required to answer the current research question.
