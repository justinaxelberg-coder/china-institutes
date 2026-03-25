# Current Retrieval and Corpus Summary

## Scope

This note describes only the retrieval and corpus layers that are currently doing the heavy lifting in the analysis. It deliberately focuses on the active production backbone and leaves out exploratory or legacy analytical layers.

## What Currently Does The Heavy Lifting

The present analysis is driven mainly by two retrieval streams:

1. attributed **indexed publications** from the OpenAlex-based retrieval path
2. a smaller attributed **grey-literature** stream from institute websites and official publication pages

The main typology and within-domain orientation analysis are estimated from the **core publication corpus** built from those sources.

A separate policy-document corpus is still retained, but it is not the main driver of the current publication-derived typology.

## Retrieval Backbone

The current production corpus is assembled from three attributed source files:

- `data/interim/openalex_attributed.csv`
- `data/interim/grey_attributed.csv`
- `data/interim/dimensions_policy_attributed.csv`

In the current workflow:

- indexed publications contribute `title + abstract` text
- grey literature contributes parsed page text when available, otherwise page title
- policy documents are exported separately rather than folded into the main publication corpus

Cross-source duplicates are removed by normalized title within institute, with preference order:

1. indexed
2. grey
3. policy_document

The `probable` corpus excludes anything already included in `core`.

## Corpus Structure

- Core corpus: **9,438** documents across **86** institutes
- Probable corpus: **6,961** documents
- Full publication corpus: **16,399** documents across **90** institutes
- Separate policy corpus: **941** rows
- Year coverage in the full publication corpus: **2000-2026**

Source composition:

- Core corpus: indexed=9,082, grey=356
- Probable corpus: indexed=6,952, grey=9
- Full publication corpus: indexed=16,034, grey=365

This means the heavy lifting is still overwhelmingly being done by the indexed publication layer, with grey literature acting as a useful but much smaller supplement.

## What Actually Enters The Current Analysis

The current typology/orientation rewrite is grounded in the **core publication corpus**, not the full union.

- Core documents entering the paragraph layer: **9,438**
- Paragraph rows written for the current domain/orientation layer: **9,026**
- Documents represented in the paragraph layer: **9,026**
- Review-like paragraphs flagged: **325**

Current dominant paragraph-domain counts:

- society_culture: 1,953
- security_strategy: 1,949
- economy_trade: 1,161
- governance_law: 805
- science_technology: 644
- environment_climate: 299
- unclassified: 2,215

So, in practical terms, the current analysis is being carried mainly by the core indexed corpus, with smaller support from grey literature, and then pushed through the paragraph-level domain and orientation pipeline.

## What Is Supporting Rather Than Driving

- The `probable` corpus broadens descriptive coverage but is not the conservative analytical base.
- The separate policy corpus is preserved for policy-facing outputs and contextual work, but it is not the backbone of the current typology.
- Exploratory topic-modeling layers are not the main retrieval/corpus engine for the current analysis.

## Largest Institutes In The Core Analytical Corpus

- China Institute: 847
- Center for Chinese Studies: 687
- China Policy Institute / CPI Analysis: 581
- Stanford Center on China's Economy and Institutions: 456
- Australia-China Relations Institute: 395
- Penn Project on the Future of U.S.-China Relations: 356
- Centre d'Études Français sur la Chine Contemporaine (CEFC): 347
- University of Oxford China Centre: 262
- Durham China Centre: 237
- Nordic Institute of Asian Studies: 235

## Bottom Line

The current analytical heavy lifting is being done by a conservative core corpus built mainly from attributed OpenAlex indexed publications, supplemented by a smaller grey-literature stream, deduplicated across sources, and then carried into the paragraph-level domain/orientation pipeline. The probable corpus and policy corpus remain useful, but they are not the primary engines of the present publication-derived analysis.