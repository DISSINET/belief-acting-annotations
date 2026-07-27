# Descriptive-figure methodology comparison

Figures under three normalization regimes (raw clause-pooled,
inverse-length-weighted, GLM-adjusted EMM), demonstrating why the
EMM/length-corrected figures at repo root are the right basis for
between-group comparison. Full methodology and per-figure discussion:
`../../descriptive.figures.readme.md`.

| Figures | What they show |
|---|---|
| `fig1_thematic_heatmap.png`, `fig1_ilw_thematic_heatmap.png`, `fig1_emm_thematic_heatmap.png` | CT distribution heatmap under each normalization. Material support flips sign entirely once length-corrected — raw z=-2.2 reads as suppressed; EMM z=+1.2 shows genuine elevation. `fig1_emm_thematic_heatmap.png` is a dendrogram layout of the same EMM data as `fig1_emm_popular_thematic_heatmap.png` at repo root, which uses a no-dendrogram layout. |
| `fig2_discursive_budget.png`, `fig2_ilw_discursive_budget.png`, `fig2_emm_discursive_budget.png` | Same comparison, discursive-budget form. Legal-procedural share: 41% raw vs. 22.6% length-corrected. `fig2_emm_discursive_budget.png` is a dendrogram-adjacent layout of the same data as `fig2_emm_popular_discursive_budget.png` at repo root. |
| `fig4_diverging_bars.png`, `fig4_ilw_diverging_bars.png` | Belief vs. suppressor-topic content. The raw/ILW "hydraulic near-parity" in Bologna LS (~1:1) becomes 2.5:1 once length-corrected (`fig4_emm_diverging_bars.png`, repo root). |
| `fig5_sex_slopes.png`, `fig5_ilw_sex_slopes.png` | Sex differences in content-topic rates. The length-corrected version (`fig5_emm_sex_slopes.png`, repo root) adds confidence intervals, revealing real uncertainty in Bologna LS that these point estimates don't show. |
| `fig6_distribution_summary.png`, `fig6_ilw_distribution_summary.png` | Per-deposition distributional shape (zero-inflation, skew) in raw counts and length-adjusted proportions respectively. Complementary to `fig6_emm_forest.png` (repo root, a model-adjusted between-group comparison) — the three figures show different properties of the data, not competing estimates of the same one. |

Belief-subtype composition is robust across all three normalization
methods (12.7% raw / 12.8% ILW / 15.3% EMM for Bologna LS female) — see
`fig3_emm_belief_composition.png` at repo root.

## Thumbnails: raw vs. ILW vs. EMM, side by side

| | Raw | ILW | EMM (canonical) |
|---|---|---|---|
| **Fig 1** (thematic heatmap) | <img src="fig1_thematic_heatmap.png" width="220"> | <img src="fig1_ilw_thematic_heatmap.png" width="220"> | <img src="fig1_emm_thematic_heatmap.png" width="220"> |
| **Fig 2** (discursive budget) | <img src="fig2_discursive_budget.png" width="220"> | <img src="fig2_ilw_discursive_budget.png" width="220"> | <img src="fig2_emm_discursive_budget.png" width="220"> |
| **Fig 4** (hydraulic competition) | <img src="fig4_diverging_bars.png" width="220"> | <img src="fig4_ilw_diverging_bars.png" width="220"> | <img src="../../fig4_emm_diverging_bars.png" width="220"> |
| **Fig 5** (sex differences) | <img src="fig5_sex_slopes.png" width="220"> | <img src="fig5_ilw_sex_slopes.png" width="220"> | <img src="../../fig5_emm_sex_slopes.png" width="220"> |
| **Fig 6** (per-deposition distributions) | <img src="fig6_distribution_summary.png" width="220"> | <img src="fig6_ilw_distribution_summary.png" width="220"> | <img src="../../fig6_emm_forest.png" width="220"> |

Fig 6's EMM column is the forest plot (`fig6_emm_forest.png`) — a
different chart type than the raw/ILW distribution-summary strips, shown
here for at-a-glance comparison, not because one replaces the other (see
`../../descriptive.figures.readme.md` for why).
