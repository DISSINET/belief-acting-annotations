# Cross-subtype burst check: specialization vs. blending

Tests whether belief subtypes cluster with THEMSELVES specifically or with
belief generally. Motivated by a puzzle in
`self_burst_regression_results.md`: `has_belief`'s aggregate self-clustering
is consistently weaker than every individual subtype's self-clustering, in
both the regression and the permutation methods -- the opposite of the naive
expectation that an aggregate should inherit/amplify its parts' signals.

For each subtype DV, one joint model with all 4 subtype burst counts as
mutually-adjusted predictors + sex + register:

    {subtype} ~ burst_rb_th_count + burst_rb_st_count + burst_rb_sm_count +
                  burst_rb_count + sex + register + (1|deposition_code)

## Same-subtype vs. cross-subtype burst ORs

| DV | Same-subtype OR | Cross-subtype ORs (other 3) | Same/max-cross ratio |
|---|---|---|---|
| `ct_rb_th` (theological) | **2.61** | socio_theological=1.09, socio_moral=0.97, generic_belief=1.00 | 2.39x |
| `ct_rb_st` (socio_theological) | **2.98** | theological=1.13, socio_moral=1.50, generic_belief=1.37 | 1.98x |
| `ct_rb_sm` (socio_moral) | **3.11** | theological=1.10, socio_theological=1.51, generic_belief=1.35 | 2.06x |
| `ct_rb` (generic_belief) | **3.38** | theological=1.00, socio_theological=1.23, socio_moral=1.31 | 2.58x |

Mean same-subtype OR: **3.02**. Mean cross-subtype OR: **1.21**.

## Full results

```
      dv          dv_label      burst_column       burst_label  relationship  n_clauses  n_positive  fit_seconds  log_odds       se       p_value      or_  or_ci_low  or_ci_high
ct_rb_th       theological burst_rb_th_count       theological  same_subtype      27850         398    56.439359  0.958493 0.058311  1.028550e-60 2.607764   2.326130    2.923496
ct_rb_th       theological burst_rb_st_count socio_theological cross_subtype      27850         398    56.439359  0.088017 0.104815  4.010557e-01 1.092007   0.889215    1.341046
ct_rb_th       theological burst_rb_sm_count       socio_moral cross_subtype      27850         398    56.439359 -0.033999 0.124735  7.851812e-01 0.966572   0.756938    1.234265
ct_rb_th       theological    burst_rb_count    generic_belief cross_subtype      27850         398    56.439359 -0.003432 0.171303  9.840144e-01 0.996574   0.712354    1.394193
ct_rb_st socio_theological burst_rb_th_count       theological cross_subtype      27850         594    24.324504  0.123800 0.093039  1.833118e-01 1.131789   0.943128    1.358190
ct_rb_st socio_theological burst_rb_st_count socio_theological  same_subtype      27850         594    24.324504  1.090685 0.059158  6.669673e-76 2.976312   2.650469    3.342213
ct_rb_st socio_theological burst_rb_sm_count       socio_moral cross_subtype      27850         594    24.324504  0.405951 0.065928  7.391668e-10 1.500729   1.318816    1.707735
ct_rb_st socio_theological    burst_rb_count    generic_belief cross_subtype      27850         594    24.324504  0.315947 0.091626  5.643202e-04 1.371558   1.146097    1.641371
ct_rb_sm       socio_moral burst_rb_th_count       theological cross_subtype      27850         866    19.700503  0.098080 0.094737  3.005381e-01 1.103050   0.916125    1.328115
ct_rb_sm       socio_moral burst_rb_st_count socio_theological cross_subtype      27850         866    19.700503  0.410056 0.053028  1.051873e-14 1.506902   1.358149    1.671947
ct_rb_sm       socio_moral burst_rb_sm_count       socio_moral  same_subtype      27850         866    19.700503  1.133152 0.043100 2.396338e-152 3.105430   2.853878    3.379155
ct_rb_sm       socio_moral    burst_rb_count    generic_belief cross_subtype      27850         866    19.700503  0.296924 0.086264  5.773229e-04 1.345713   1.136383    1.593602
   ct_rb    generic_belief burst_rb_th_count       theological cross_subtype      27850         360    23.968546 -0.003174 0.141871  9.821526e-01 0.996831   0.754850    1.316384
   ct_rb    generic_belief burst_rb_st_count socio_theological cross_subtype      27850         360    23.968546  0.208420 0.085364  1.462413e-02 1.231731   1.041967    1.456054
   ct_rb    generic_belief burst_rb_sm_count       socio_moral cross_subtype      27850         360    23.968546  0.270199 0.096416  5.072182e-03 1.310225   1.084616    1.582762
   ct_rb    generic_belief    burst_rb_count    generic_belief  same_subtype      27850         360    23.968546  1.217709 0.081632  2.552670e-50 3.379435   2.879777    3.965787
```

## Interpretation

Same-subtype burst counts predict far more strongly than cross-subtype ones
-- consistent with the **specialization** story: passages tend to stay in
one belief register (a theological argument stays theological) rather than
blending all 4 subtypes together. This explains why `has_belief`'s aggregate
burst count under-performs every individual subtype's own burst count: the
aggregate signal is a mix of one strong same-subtype component and several
weak cross-subtype components, and averaging dilutes toward the weak end
rather than amplifying toward the strong one.

**Bears on the coding-scheme granularity question** (raised in an internal
working document, not included here): if cross-subtype burst counts predicted about as well as
same-subtype ones, that would suggest the 4 subtype labels are closer to
noise scattered over one real underlying "any belief" category. Instead,
the sharp same>>cross gap
is evidence the subtype boundaries track a real distinction in how these passages are organized,
not just where annotation effort happened to go. This validates belief's OWN
subtype coding internally -- it does **not** resolve Issue 2's separate
question of whether the comparator topics (`ct_ra`, `ct_ms`, etc.) have
comparable hidden facet-structure that was never subdivided; that remains
untestable from this data.

## A secondary finding: theological is an isolated island; the other three bridge

Not all cross-subtype pairs behave alike. `theological`'s three cross-subtype
ORs are all statistically indistinguishable from 1 (0.97-1.09, all p>0.4) --
essentially zero cross-bleed in either direction (see the `ct_rb_th` row
above, and the `burst_rb_th_count` cross-terms in the other three rows,
which are similarly null: 1.10, 1.13, 1.00). Theological content forms a
clean, isolated register: nearby theological clauses predict more
theological clauses and *nothing else*, and nearby other-subtype clauses do
not predict theological ones either.

The other three subtypes (`socio_theological`, `socio_moral`,
`generic_belief`) show real, if modest, mutual cross-prediction: OR
1.23-1.51, all but one significant at p<0.05. These three partially bridge
into each other locally; theological stands apart from all three.

Plausible substantive reading: `theological` is defined as purely
supernatural/metaphysical content, while the other three subtypes are all
more socially embedded (institutional efficacy, individual moral judgment,
undifferentiated belief-talk) -- the isolation may reflect a genuine
register distinction (abstract doctrinal argument vs. socially-embedded
belief-talk), not an annotation artifact. Not tested further here, but worth
noting if the subtype-level story is developed further in the manuscript or
talk.

## Files

- `subtype_cross_burst_results.csv` — all fits (4 DVs x 4 burst predictors each)
- Fitting script: `sembel_subtype_cross_burst.py`
- Motivating puzzle: `self_burst_regression_results.md`
- Cross-referenced: two internal working documents (manuscript-issues and
  known-issues tracking), not included here
