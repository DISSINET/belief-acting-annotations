# Asymmetric (before/after) cross-topic local co-occurrence

Follow-up to `cross_topic_burst_matrix_results.md` (symmetric +/-w window,
found no topic positively accompanies belief, stable across radii). Splits
each topic's local burst count into BEFORE (w clauses immediately
preceding the focal clause) and AFTER (w clauses immediately following),
to check for a narrative-sequence effect a symmetric window would cancel
out or dilute.


## Window radius 3 (before/after, 3 clauses each direction)

**`has_belief`** (n=2208) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `st` | -0.141 | -0.099 | -0.042 |
| `ea` | -0.009 | 0.029 | -0.038 |
| `rb` | 0.111 | 0.149 | -0.038 |
| `lp` | -0.036 | -0.005 | -0.031 |
| `rb_sm` | 0.195 | 0.175 | +0.020 |

**`rb`** (n=360) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `has_belief` | 0.141 | 0.104 | +0.037 |
| `rb_st` | 0.050 | 0.013 | +0.037 |
| `rb_sm` | 0.021 | 0.001 | +0.020 |
| `rb_th` | 0.007 | -0.009 | +0.015 |
| `sn` | -0.031 | -0.017 | -0.013 |

**`rb_sm`** (n=866) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `ea` | 0.010 | 0.054 | -0.044 |
| `lp` | 0.024 | 0.053 | -0.029 |
| `st` | -0.091 | -0.065 | -0.027 |
| `ra` | -0.022 | 0.001 | -0.023 |
| `rb_st` | 0.026 | 0.047 | -0.021 |

**`rb_st`** (n=594) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `rb` | 0.014 | 0.052 | -0.038 |
| `rb_sm` | 0.050 | 0.027 | +0.024 |
| `st` | -0.075 | -0.053 | -0.022 |
| `ea` | -0.015 | -0.001 | -0.014 |
| `sn` | -0.055 | -0.044 | -0.011 |

**`rb_th`** (n=398) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `st` | -0.058 | -0.040 | -0.018 |
| `rb` | -0.010 | 0.007 | -0.017 |
| `lp` | -0.057 | -0.047 | -0.009 |
| `is` | -0.020 | -0.012 | -0.008 |
| `rb_st` | 0.016 | 0.008 | +0.007 |


## Window radius 5 (before/after, 5 clauses each direction)

**`has_belief`** (n=2208) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `st` | -0.143 | -0.098 | -0.045 |
| `rb` | 0.119 | 0.155 | -0.037 |
| `ea` | -0.006 | 0.028 | -0.033 |
| `lp` | -0.028 | -0.004 | -0.025 |
| `rb_sm` | 0.197 | 0.174 | +0.023 |

**`rb`** (n=360) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `has_belief` | 0.143 | 0.107 | +0.036 |
| `rb_st` | 0.062 | 0.028 | +0.034 |
| `rb_sm` | 0.027 | 0.002 | +0.025 |
| `bs` | 0.028 | 0.012 | +0.017 |
| `st` | -0.041 | -0.025 | -0.016 |

**`rb_sm`** (n=866) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `ea` | 0.015 | 0.054 | -0.040 |
| `st` | -0.094 | -0.067 | -0.027 |
| `is` | 0.035 | 0.010 | +0.025 |
| `lp` | 0.033 | 0.056 | -0.023 |
| `rb` | 0.001 | 0.024 | -0.023 |

**`rb_st`** (n=594) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `rb` | 0.031 | 0.066 | -0.036 |
| `st` | -0.078 | -0.051 | -0.026 |
| `rb_sm` | 0.059 | 0.040 | +0.018 |
| `ra` | -0.000 | -0.018 | +0.017 |
| `sn` | -0.055 | -0.039 | -0.016 |

**`rb_th`** (n=398) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `st` | -0.056 | -0.039 | -0.017 |
| `lp` | -0.061 | -0.048 | -0.013 |
| `rb` | -0.006 | 0.007 | -0.013 |
| `rb_st` | 0.023 | 0.014 | +0.010 |
| `ra` | -0.028 | -0.019 | -0.009 |


## Window radius 7 (before/after, 7 clauses each direction)

**`has_belief`** (n=2208) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `st` | -0.141 | -0.099 | -0.042 |
| `ea` | -0.006 | 0.025 | -0.031 |
| `rb` | 0.125 | 0.154 | -0.029 |
| `lp` | -0.025 | -0.004 | -0.020 |
| `rb_sm` | 0.197 | 0.177 | +0.020 |

**`rb`** (n=360) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `has_belief` | 0.139 | 0.110 | +0.029 |
| `rb_sm` | 0.031 | 0.005 | +0.026 |
| `rb_st` | 0.062 | 0.038 | +0.023 |
| `bs` | 0.028 | 0.012 | +0.016 |
| `st` | -0.039 | -0.024 | -0.015 |

**`rb_sm`** (n=866) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `ea` | 0.012 | 0.049 | -0.036 |
| `is` | 0.032 | 0.007 | +0.025 |
| `st` | -0.096 | -0.070 | -0.025 |
| `rb` | 0.002 | 0.024 | -0.022 |
| `lp` | 0.030 | 0.050 | -0.020 |

**`rb_st`** (n=594) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `st` | -0.076 | -0.049 | -0.028 |
| `rb` | 0.044 | 0.068 | -0.024 |
| `ra` | 0.002 | -0.018 | +0.019 |
| `sn` | -0.052 | -0.039 | -0.014 |
| `bs` | 0.020 | 0.008 | +0.012 |

**`rb_th`** (n=398) -- top 5 by |before-after| divergence:

| context | before r | after r | before-after |
|---|---|---|---|
| `lp` | -0.060 | -0.046 | -0.014 |
| `st` | -0.053 | -0.039 | -0.014 |
| `rb_st` | 0.031 | 0.017 | +0.014 |
| `ra` | -0.025 | -0.015 | -0.010 |
| `rb` | -0.003 | 0.005 | -0.009 |


## Interpretation

**Null confirmed.** Max |before-after| divergence across every belief
target and all 3 radii is ~0.045 (`rb_sm` vs. `ea`, radius 5) -- well below
any meaningful threshold. No context topic shows a real directional/
sequential asymmetry. The symmetric result (`cross_topic_burst_matrix_results.md`)
wasn't hiding a narrative-sequence effect -- the null (belief has no
thematic companion topic in this corpus) is robust to this alternative
lens too, not an artifact of window symmetry.

**Two small, consistent-across-radii patterns, worth having in reserve but
not strong enough to build a claim on**:
- `ea` (emotional/affective): consistently leans *after* belief clauses more
  than before (e.g. `has_belief`: before -0.006 to -0.009, after +0.025 to
  +0.029, all 3 radii) -- plausible narrative read: state the belief, then
  an emotional reaction, not the reverse.
- `st` (spatio-temporal): consistently more negative *before* belief clauses
  than after (`has_belief`: before -0.14, after -0.10, all 3 radii) --
  plausible read: scene-setting content recedes once already inside a
  belief-heavy passage.

Both effects are small (~0.03-0.05 magnitude) and directionally stable, but
this is descriptive pattern-noticing, not a tested/confirmed finding --
would need a proper sequential model to treat as more than a footnote.

## Files

- `cross_topic_burst_asymmetric.csv` -- long format, all pairs x radii x direction
- Fitting script: `sembel_cross_topic_burst_asymmetric.py`
- Motivating result: `cross_topic_burst_matrix_results.md`
