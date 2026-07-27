# Burst/saturation-mechanism analyses

Backs two corrections in `../../POST_SUBMISSION_CORRECTIONS.md`: the
Model 4 aggregate-vs-subtype clustering-claim correction (#1) and the
suppression→saturation reframing of Model 2's material/social-content
finding (#3). The manuscript's own supplementary materials narrate these
corrections in prose; this folder includes the actual analysis code and
write-ups behind them, not just the summary.

**Not standalone-runnable as-is**: these scripts take `--pickle`/
`--dep-pickle` arguments pointing at this project's full clause-level and
deposition-level dataframes (`anaclauses.pickle`, `anadepositions_plus.pickle`)
— not included in this public repo (see `clauses.csv`/`depositions.csv`
for the tabular equivalents this repo does ship). Included here so the
methodology is fully inspectable and auditable, not to be re-run without
the full project repository. All were originally run with
`conda run -n pymer python <script>.py` (needs `pymer4`/R `lme4` — see
`../../README.md`'s Statistical Software section).

## Which script backs which claim

| Script | Backs | Method |
|---|---|---|
| `sembel_comparative_burstiness.py` | Model 4 correction (#1) | Permutation-based fold-enrichment: does belief cluster with itself more than 5 comparator topics do, correcting for the union-of-4-subtypes aggregation mechanics the manuscript's original comparison didn't control for |
| `sembel_self_burst_regression.py` | Model 4 correction (#1) | Independent GLMM self→self burst regression using the manuscript's own archived Model 4 covariate skeleton — a second, methodologically distinct check that converges with the fold-enrichment result (Spearman rank correlation 0.939 between the two) |
| `sembel_subtype_cross_burst.py` | Model 4 correction (#1), the *why* | Same-subtype-vs-cross-subtype burst check — explains why the aggregate `has_belief` measure fails where the 4 individual subtypes succeed: belief passages specialize in one subtype rather than blending, diluting the aggregate's burst signal toward the weak end |
| `sembel_cross_topic_burst_matrix.py` | Suppression→saturation reframing (#3) | Full 18-topic × 3-window-radius local burst co-occurrence matrix — no topic positively accompanies belief locally, consistent with saturation (a fixed ceiling) rather than active clause-by-clause displacement |
| `sembel_cross_topic_burst_asymmetric.py` | Suppression→saturation reframing (#3) | Asymmetric before/after split — rules out a hidden narrative-sequence effect as an alternative explanation for the local co-occurrence pattern above |

## Files

Each script's paired `*_results.md` is the actual write-up (numbers,
methodology detail, verdict) — read those, not just this index, before
citing any specific figure from these corrections.
