# Statistical Output Figures

This directory contains visualization files for the primary outcome
(`has_belief`) across the four-model progressive GLMM sequence, from the
January 29, 2026 canonical model run. Per-subtype (`ct_rb`, `ct_rb.sm`,
`ct_rb.st`, `ct_rb.th`) breakdowns and the intermediate models' random-effects
diagnostics are not included here — the aggregate progression is what the
manuscript's headline finding (the M1→M4 variance-collapse result) reports
on; full per-subtype output is available in the main project repository.

## Files

### Fixed-effects visualizations, `has_belief` across all four models

- `has_belief_null_coefs_20260129_121753.png` / `has_belief_null_emmeans_20260129_121753.png` — Model 1 (null): random effects only, no fixed effects
- `has_belief_thematic-context_coefs_20260129_121753.png` / `has_belief_thematic-context_emmeans_20260129_121753.png` — Model 2: adds content-topic proportions
- `has_belief_procedural-dynamics_coefs_20260129_121753.png` / `has_belief_procedural-dynamics_emmeans_20260129_121753.png` — Model 3: adds discourse agency (nagiag) and question tracking
- `has_belief_burst-has-belief_coefs_20260129_121753.png` / `has_belief_burst-has-belief_emmeans_20260129_121753.png` — Model 4: adds local burst/clustering variables

**Coefficient plots** (`*_coefs_*.png`): regression coefficients (log-odds) with 95% CIs. Positive = increased log-odds; CI not crossing zero = significant at α=0.05.

**Estimated marginal means** (`*_emmeans_*.png`): predicted probabilities for categorical predictor levels, holding other variables constant — more interpretable than raw log-odds.

### Random-effects diagnostics, `has_belief` at each of the four models

- `model_001_has_belief_ranef_caterpillar_20260129_121753.pdf`, `model_001_has_belief_ranef_histogram_20260129_121753.png`, `model_001_has_belief_ranef_vs_size_20260129_121753.png` — Model 1
- `model_006_has_belief_ranef_*` — Model 2
- `model_011_has_belief_ranef_*` — Model 3
- `model_016_has_belief_ranef_*` — Model 4

**Caterpillar plots** (`*_ranef_caterpillar_*.pdf`): random intercept deviations per deposition, sorted by magnitude — shows between-deposition variability and identifies unusually high/low-baseline depositions.

**Histograms** (`*_ranef_histogram_*.png`): distribution of random intercept deviations across all depositions — should approximate normal; skew/heavy tails suggest model misspecification.

**Random effects vs. deposition size** (`*_ranef_vs_size_*.png`): scatterplot of random effects against deposition length — should show no systematic relationship; a pattern would indicate confounding with the length asymmetry problem (Bologna LS ~4x shorter than Toulouse/Bologna).

Comparing the histogram/vs-size plots across models 001→006→011→016 is what the manuscript's headline variance-collapse finding visualizes directly: deposition-level random-intercept variance for `has_belief` drops as thematic, procedural, and burst predictors are progressively added.

### Cross-model summary

- `effect_sizes_heatmap_20260129_121753.png` — standardized effect sizes across all models and predictors, for quick comparison of relative predictor importance.

## Interpreting results

- **Coefficient direction/magnitude**: positive = increases log-odds; exponentiate for odds ratios (coefficient 0.5 → OR = exp(0.5) = 1.65, a 65% increase in odds).
- **Significance**: 95% CI not crossing zero indicates p < 0.05.
- **Random effects**: larger variance = more between-deposition heterogeneity; small depositions shrink toward the overall mean.

For detailed model specifications, coefficients, and goodness-of-fit statistics across all models (including the subtype outcomes not visualized here), see `../all_models_results_20260129_121753.xlsx`.

## Technical details

Figures generated in Python (matplotlib/seaborn, coefficient/emmeans plots)
and R (ggplot2, random-effects diagnostics). Models fitted via `pymer4`
(Python wrapper for R's `lme4`). All models include `(1|deposition_code)`
to account for within-deposition clustering of clauses.
