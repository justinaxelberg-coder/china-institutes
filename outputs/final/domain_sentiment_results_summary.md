# Domain and Orientation Methodology With Brief Results Summary

## Purpose

This note summarizes the current production methodology for domain identification and orientation scoring, followed by a short summary of the current results. It reflects the active paragraph-level domain/orientation pipeline rather than older one-axis framing outputs.

## 1. Domain Methodology

The current production workflow identifies domains in two steps.

First, the pipeline applies a rule-based China-studies thematic taxonomy. That underlying taxonomy has 15 themes, including foreign policy, trade and political economy, domestic politics, security and military affairs, Taiwan, Hong Kong, Xinjiang/Tibet, technology, environment, history and culture, Global South and regional activity, media and influence operations, society and demographics, health science, and law and institutions.

Second, those 15 themes are collapsed upward into 6 broader analytical domains used in the current typology:

- security_strategy
- economy_trade
- science_technology
- environment_climate
- governance_law
- society_culture

The key methodological shift is that the current system works at the paragraph level rather than assigning one label to an entire document. Documents from the core corpus are segmented into paragraphs, the paragraphs are scored against the thematic taxonomy, and those theme scores are then aggregated into broad-domain weights.

In practice, this means a paragraph can load partly onto more than one domain rather than being forced into a single topic bucket. If no domain accumulates enough score, the paragraph is left as `unclassified`.

The domain layer is therefore not a BERTopic-style latent topic model. It is a controlled, production-facing domain identification system built from the thematic taxonomy plus broad-domain cue terms and a series of cleanup rules to reduce false positives, especially around science/technology versus education, governance, and bibliographic noise.

## 2. Orientation Methodology

The current orientation layer is not generic positive/negative sentiment analysis. Instead, it asks a more specific question: when a paragraph discusses China in a given domain, does it frame China more as a `rival` or more as a `collaborator`?

These are scored as separate dimensions rather than as opposite ends of a single line. That matters because a document or institute can be collaborative in one domain and rivalrous in another, and some passages contain both kinds of language.

At the paragraph level, the orientation scorer uses:

- lexicon-based matching for rival and collaborator cues
- paragraph body text rather than title text
- density-normalized scoring
- a minimum paragraph-length threshold
- suppression of review-like and metadata-thin rows

The remaining domain salience not allocated to rival or collaborator is treated as `neutral`, which is best understood as neutral/analytic residual rather than as a separate positive sentiment class.

The paragraph-level output is then aggregated upward to the document and institute levels, producing within-domain shares such as `security_strategy_rival_share`, `economy_trade_collaborator_share`, and `science_technology_collaborator_share`.

## 3. Brief Results Summary

The current paragraph-level production layer contains **9,026** scored paragraphs. Of these, **325** are flagged as review-like or bibliographic-style rows.

### Domain distribution

- Unclassified: 2,215
- Society & culture: 1,953
- Security & strategy: 1,949
- Economy & trade: 1,161
- Governance & law: 805
- Science, technology & education: 644
- Environment & climate: 299

The largest broad domains at the paragraph level are currently society/culture and security/strategy, followed by economy/trade. Environment/climate is smaller but now clearly visible as its own domain rather than being buried inside political economy.

### Orientation distribution

- Neutral / analytic: 7,810
- Collaborator only: 819
- Rival only: 259
- Collaborator leaning: 56
- Balanced mixed: 49
- Rival leaning: 33

The most important overall pattern is that the corpus is still mostly neutral/analytic in tone, which is what we would expect from a publication corpus. Within the non-neutral share, collaborator language is more common than rival language, but mixed and rivalrous passages clearly exist and are substantial enough to support a typology richer than a single engagement-threat axis.

### Institute-level typology

- Institutes in the current typology frame: **84**
- Low-volume institutes excluded from modeling: **18**
- Institutes entering the current regression sample: **66**

- broad_neutral_analysts: 19
- security_hawks: 18
- low_volume_unassigned: 18
- economic_or_sti_pragmatists: 14
- selective_engagers: 10
- dual_track_institutes: 5

Taken together, these results support the core substantive point of the rewrite: institutes do not line up neatly on a single spectrum from engagement to threat. Instead, they differ in how they distribute attention across domains and in how they orient toward China within those domains.

### Brief model read

The current regression layer remains secondary to the publication-derived typology and should be read associationally rather than causally. Its main value at this stage is to show that the within-domain outcomes can be modeled as distinct dependent variables rather than collapsed into one overall index.

Among the current continuous models, the strongest retained associations are concentrated in security-rival and security-collaborator outcomes, which is consistent with the broader finding that security remains one of the most structuring domains in the corpus.