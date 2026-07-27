# GLM Length-Adjustment Methodology

Simple proportions (`count / clauses_len`) are biased when deposition
lengths vary substantially across registers. Bologna LS depositions have
a median of 9–12 clauses versus 42–47 for Toulouse and Bologna non-LS.
Length adjustment rescales each deposition's count to what it would be at
the **reference length** (L_ref = 34.77, the corpus mean of `clauses_len`).

## Files

| File | Description |
|------|--------------|
| `3panels_glm_analysis_hc3_robust.pdf` | Three-panel GLM comparison (predictions / EMM / compact letter display), HC3-robust standard errors — the canonical run, matching `../replication_data/`'s equivalent for direct comparison |
| `glm_emms_with_cld_hc3.csv` | Estimated marginal means with CLD groupings per variable × register × sex cell |
| `glm_model_details_hc3.csv` | Per-variable model-fitting diagnostics (distribution, dispersion, AIC comparisons, coefficients) |
| `panel1_predictions_heatmap.csv` | Panel 1 data: raw model-predicted rates |
| `panel2_emm_heatmap.csv` | Panel 2 data: length-standardized EMM rates |
| `panel3_cld_heatmap.csv` | Panel 3 data: CLD group letters (which register/sex cells are statistically indistinguishable) |

## Adjustment formula

```
adjusted_i = count_i × (L_ref / clauses_len_i) ^ β_length
```

`β_length` is estimated per variable from a GLM (Negative Binomial or Poisson with HC3
robust standard errors) that regresses the count on log(clauses_len) plus register and
sex dummies. Three competing specifications are fitted and the lowest-AIC model is chosen:

| Model type | Formula | β_length |
|------------|---------|----------|
| `offset` | log(count) ~ register + sex + offset(log(len)) | Fixed at 1.0 (strict proportionality) |
| `predictor` | log(count) ~ log(len) + register + sex | Freely estimated |
| `predictor+int` | log(count) ~ log(len) × register × sex | Freely estimated (group-specific slopes) |

When β = 1.0 (offset model selected), the adjustment reduces to simple rescaling:
`adjusted_i = count_i × L_ref / clauses_len_i`.

Selected β_length values, illustrating the range across content topics:

| Variable | Full label | β_length | Length model |
|----------|-----------|-----------|--------------|
| `ct_lp` | Legal / procedural | 0.30 | predictor+int |
| `ct_rb` | Religious belief (aggregate) | 0.61 | predictor+int |
| `ct_rb.st` | Religious belief — socio-theological | 1.00 | offset |
| `ct_rb.sm` | Religious belief — socio-moral | 1.00 | offset |
| `ct_rb.th` | Religious belief — theological | 1.67 | predictor |
| `ct_ei` | Encounter / interaction | 1.53 | predictor+int |

This is the same length-scaling logic behind the EMM descriptive figures
at repo root — see `../../descriptive.figures.readme.md` for the full
methodology comparison (raw vs. inverse-length-weighted vs. EMM).

## Corpus metadata

- 801 depositions, 27,850 clauses, reference length L_ref = 34.77 clauses
- Register distribution: Toulouse/Parnac (192), Bologna non-LS (207), Bologna LS (402)

## Generation

Produced by `generate_length_adjusted_depositions_with_nag.py` (not
included in this repo — the per-deposition, per-topic×agency adjusted
counts and their full model diagnostics are audit-depth intermediate
output; this folder ships the aggregate comparison (the PDF and its 5
backing CSVs above) that the analysis actually reports on).
