# Comparative burstiness — permutation-corrected re-analysis

Tests whether belief clusters (±3-clause window) more than other
content topics, replacing the manuscript's raw burst-count odds-ratio
comparison (Model 4) with a permutation-null clustering score computed
identically across every category — controlling for two confounds the raw-OR
comparison doesn't handle: (1) `has_belief` aggregates 4 subtypes into a
union, which mechanically inflates apparent co-occurrence vs. a single flat
comparator; (2) categories have very different base rates, which distorts
logistic-regression OR comparisons even at identical true clustering
strength. See `../../POST_SUBMISSION_CORRECTIONS.md` #1 for the manuscript
passage this re-analyzes.

Fitting script: `sembel_comparative_burstiness.py`. Method: vectorized Monte
Carlo permutation (not a closed-form graph formula — simpler to audit, see
script docstring), 5000 permutations per (deposition,
category), corpus-level values are **sums of raw per-deposition statistics**
(not averaged per-deposition ratios — depositions range 4–385 clauses, an
unweighted average would let a thin deposition count as much as a large
one), bootstrapped (2000 reps, deposition-level resampling) for
the corpus CI.

## Validation gate

Independent recomputation (different RNG stream) agreed with the main computation within simulation noise (max 1.95 SE across 11 spot-checked deposition/category pairs) — see `validation_gate.csv`.

## Ranked results (all 9 real categories)

| Rank | Category | Type | Fold-enrichment [95% CI] | z [95% CI] | Holm p | Depositions (incl./excl. sparse) |
|---|---|---|---|---|---|---|
| 1 | `ct_rb` (generic_belief) | belief_subtype | 2.80 [2.24, 3.91] | 17.7 [13.5, 22.8] | 0.0000 | 66/735 |
| 2 | `ct_rb_th` (theological) | belief_subtype | 2.47 [1.90, 3.40] | 23.7 [17.9, 30.1] | 0.0000 | 53/748 |
| 3 | `ct_rb_st` (socio_theological) | belief_subtype | 2.32 [1.97, 2.92] | 23.5 [19.5, 27.8] | 0.0000 | 97/704 |
| 4 | `ct_rb_sm` (socio_moral) | belief_subtype | 2.28 [2.06, 2.53] | 25.4 [21.1, 30.1] | 0.0000 | 203/598 |
| 5 | `ct_ra` (religious_action) | comparator | 2.09 [1.92, 2.30] | 26.4 [22.0, 31.1] | 0.0000 | 197/604 |
| 6 | `ct_ms` (material_support) | comparator | 1.79 [1.64, 1.96] | 29.5 [25.3, 33.7] | 0.0000 | 228/573 |
| 7 | `has_belief` (belief_aggregate) | belief_aggregate | 1.67 [1.52, 1.91] | 34.7 [29.6, 40.4] | 0.0000 | 321/480 |
| 8 | `ct_ei` (encounter_interaction) | comparator | 1.47 [1.39, 1.57] | 22.5 [18.8, 26.4] | 0.0000 | 280/521 |
| 9 | `ct_sn` (social_network) | comparator | 1.30 [1.23, 1.38] | 18.8 [15.3, 22.6] | 0.0000 | 436/365 |
| 10 | `ct_st` (spatial_temporal) | comparator | 1.25 [1.20, 1.29] | 19.1 [15.7, 22.6] | 0.0000 | 439/362 |

## Does the "2 of 5 vs. 3 of 5" pattern survive the correction?

Manuscript's raw-OR comparison: `ct_ra` (OR=2.25) and `ct_ms` (OR=2.27) sat
inside belief's OR range (1.95–2.55); `ct_sn`/`ct_st`/`ct_ei` (OR 1.63–1.67)
sat below it. On this corrected metric: 0 of 5
comparators reach or exceed the lowest belief subtype's fold-enrichment
(2.28) — none do.
This does NOT cleanly reproduce the manuscript's 2-vs-3 split — see the full ranked table above for the actual pattern once base rate and aggregation are controlled.

## Is `has_belief`'s clustering an aggregation artifact?

`has_belief` fold-enrichment: **1.67**. Structural control
(random unions of 4 non-belief tags, 500/500 valid draws):
mean fold **1.40** (SD 0.28),
5th–95th percentile band [1.10, 2.01].
`has_belief` sits at the **81st percentile** of the structural
control's distribution; empirical `p_aggregation` (probability a random
union-of-4 non-belief tags clusters at least as strongly as `has_belief`
does) = **0.192**.

This is high enough that a substantial part of has_belief's apparent clustering is plausibly explainable by the union-of-4 construction alone, independent of belief content being special.

## Sparsity caveat

`ct_rb_th` (theological) and `ct_rb` (generic belief) are included in only
53 and
66 depositions respectively
(out of 801) after the min-k=2 exclusion — their CIs are visibly
wider than the other categories'. Don't read a narrow-looking point estimate
for these two as more certain than that sample size supports.

## Discourse mode, not topic?

If `ct_ra`/`ct_ms` (elaborated, explanatory content — describing an act, a
transaction) score closer to belief than `ct_sn`/`ct_st`/`ct_ei` (referential,
list-like content — naming a person, a place, a date) on this corrected
metric too, that favors a "clustering tracks discourse mode, not topic
identity" explanation over "belief is uniquely sticky" — see the ranked
table above (further discussion of this alternative reading is in an
internal working document, not included here).

## Files

- `comparative_burstiness_results.csv` — the ranked table above, full columns
- `comparative_burstiness_structural_draws.csv` — all 500 structural draws, individually
- `comparative_burstiness_structural_summary.csv` — the structural-control summary row
- `per_deposition_category_stats.csv` — raw per-(deposition, category) observed/null values, for audit
- `validation_gate.csv` — the independent-recomputation spot-check
