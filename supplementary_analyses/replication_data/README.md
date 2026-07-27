# Replication data — summary layer

Backs the "Validation" section in `../../README.md` and `../../REPLICATION.md`:
the full corpus (all 801 depositions) was independently re-extracted from
raw text with the same LLM model/prompt/settings, and the full model
sequence was re-fit, isolating the LLM extraction step as the only
varying factor. These files are the derived summary tables the reported
replication numbers come from, produced by
`generate_three_panels_replication.py` (a copy of the canonical
`generate_three_panels.py`, repointed at the replication data — see the
main project repo's `dh2026/full_corpus_replication_plan.md` for the full
phase-by-phase working log).

This is the summary layer, not the full re-extraction. The raw
re-extracted JSON files and the intermediate clause/deposition-level
pickles (`anaclauses_37-r1.pkl`, `df_full_37-r1.pkl`, etc., ~74MB total)
are not duplicated here to keep this repository lightweight — available
in the main project repository on request.

## Files

| File | Description |
|------|------|
| `frozen_demographics.csv` | Deposition-level `sex`/`register` lookup for all 801 depositions in the replication run (`deposition_code`, `sex`, `register`, `register_label`) — the institutional covariates frozen from canonical data (these are deposition-level facts independent of the LLM extraction, so freezing them doesn't compromise the replication). |
| `glm_model_details_hc3.csv` | Per-variable model-fitting diagnostics for the replication's GLM battery (distribution family, dispersion, AIC comparisons, length/register/sex coefficients and p-values, outlier counts, convergence, zero-inflation checks) — the full audit trail behind the three-panels comparison figure. |
| `glm_emms_with_cld_hc3.csv` | Estimated Marginal Means (EMM) with compact letter display (CLD) groupings per variable × register × sex cell — the length-standardized rates the panel figures visualize. |
| `panel1_predictions_heatmap.csv` | Panel 1 data: raw model-predicted rates per variable × register × sex cell. |
| `panel2_emm_heatmap.csv` | Panel 2 data: length-standardized EMM rates per cell (same structure as panel 1, length-adjusted). |
| `panel3_cld_heatmap.csv` | Panel 3 data: CLD group letters per cell (which register/sex cells are statistically indistinguishable from each other). |
| `3panels_glm_analysis_hc3_robust.pdf` | The rendered three-panel comparison figure these CSVs feed — predictions / EMM / CLD side by side, HC3 heteroscedasticity-robust standard errors throughout. |
