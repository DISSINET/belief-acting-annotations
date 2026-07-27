# has_belief's self-to-self burst OR

The manuscript's headline belief burst-ORs (1.95-2.55) are subtype-burst-count
predicting the *aggregate* `has_belief` outcome (narrow predictor, broad union
outcome) — not the same kind of quantity as the five published comparator-topic
ORs (each topic's burst-count predicting *that same topic's own* recurrence,
true self→self). This script fits the true self→self logistic-regression model
for `has_belief` itself, via the same `BeliefContextModel`/pymer4 machinery the
manuscript itself used (not the permutation method — see
`comparative_burstiness_results.md` for that independent approach).

Three model specs per category, since the manuscript's own covariate choice
for its comparator "analogical burst models" is unrecorded (not archived in
the results workbook, prose doesn't clarify), and because a light spec risks
under-controlling relative to the manuscript's actual, heavily-adjusted
Model 4:

- **plain**: `{category} ~ {burst_count} + (1|deposition_code)`
- **adjusted**: `{category} ~ {burst_count} + sex + register + (1|deposition_code)`
- **fully_adjusted**: `{category} ~ {burst_count} + sex + register + nagiag +
  qr_tracked + log_clauses_len_std + has_nag_i_prop + [the other four
  comparator topics' `ct_*_prop`, excluding the category's own if it is
  itself one of the five comparators] + (1|deposition_code)` — the
  computationally heavy spec, added specifically to test whether the
  plain/adjusted ORs hold up once local discourse/agency structure and
  thematic competition from the other topics are controlled for (`nagiag`
  alone expands to ~9 dummy levels).

## The self→self OR

`has_belief`'s own self→self burst OR: **2.30** (plain), **2.28** (adjusted), **2.10** (fully_adjusted).

## Fit timing by spec

| Spec | Mean | Min | Max |
|---|---|---|---|
| adjusted | 20.0s | 11.4s | 41.5s |
| fully_adjusted | 960.0s | 204.2s | 4038.3s |
| m4_faithful | 3083.5s | 540.7s | 18037.4s |
| m4_joint | 724.9s | 724.9s | 724.9s |
| plain | 23.4s | 13.7s | 41.4s |

Confirms the heavier spec is indeed slower to fit.

## Full results

```
                  category             category_label         category_type     model_spec           burst_column  n_clauses  n_positive  converged  fit_seconds  n_covariates  log_odds       se   ci_low  ci_high      or_  or_ci_low  or_ci_high       p_value
                  ct_rb_th                theological        belief_subtype          plain      burst_rb_th_count      27850         398       True    41.426218             0  0.953373 0.054931 0.845710 1.061036 2.594445   2.329630    2.889363  1.784476e-67
                  ct_rb_th                theological        belief_subtype       adjusted      burst_rb_th_count      27850         398       True    41.459886             2  0.952634 0.054885 0.845061 1.060207 2.592530   2.328121    2.886968  1.749270e-67
                  ct_rb_th                theological        belief_subtype fully_adjusted      burst_rb_th_count      27850         398       True  4038.291163            11  1.175632 0.068025 1.042306 1.308958 3.240190   2.835749    3.702313  6.378076e-67
                  ct_rb_st          socio_theological        belief_subtype          plain      burst_rb_st_count      27850         594       True    25.082817             0  1.019564 0.055628 0.910536 1.128593 2.771987   2.485654    3.091303  4.916817e-75
                  ct_rb_st          socio_theological        belief_subtype       adjusted      burst_rb_st_count      27850         594       True    22.063314             2  1.016427 0.055070 0.908492 1.124363 2.763305   2.480578    3.078256  4.588821e-76
                  ct_rb_st          socio_theological        belief_subtype fully_adjusted      burst_rb_st_count      27850         594       True   502.820139            11  1.017490 0.053619 0.912398 1.122582 2.766243   2.490288    3.072777  2.681860e-80
                  ct_rb_sm                socio_moral        belief_subtype          plain      burst_rb_sm_count      27850         866       True    21.549090             0  1.109635 0.045253 1.020941 1.198330 3.033252   2.775805    3.314577 8.912127e-133
                  ct_rb_sm                socio_moral        belief_subtype       adjusted      burst_rb_sm_count      27850         866       True    16.770750             2  1.109518 0.045652 1.020041 1.198995 3.032897   2.773309    3.316783 1.795709e-130
                  ct_rb_sm                socio_moral        belief_subtype fully_adjusted      burst_rb_sm_count      27850         866       True   240.687618            11  0.993088 0.041391 0.911962 1.074214 2.699559   2.489203    2.927691 3.324625e-127
                     ct_rb             generic_belief        belief_subtype          plain         burst_rb_count      27850         360       True    25.998706             0  1.180770 0.078969 1.025993 1.335546 3.256880   2.789865    3.802072  1.504452e-50
                     ct_rb             generic_belief        belief_subtype       adjusted         burst_rb_count      27850         360       True    19.391188             2  1.182914 0.078587 1.028886 1.336942 3.263872   2.797948    3.807384  3.335902e-51
                     ct_rb             generic_belief        belief_subtype fully_adjusted         burst_rb_count      27850         360       True   538.733948            11  1.206679 0.081101 1.047725 1.365633 3.342366   2.851157    3.918203  4.525124e-50
                has_belief           belief_aggregate      belief_aggregate          plain burst_has_belief_count      27850        2208       True    21.819308             0  0.831408 0.025949 0.780550 0.882267 2.296550   2.182672    2.416371 2.981926e-225
                has_belief           belief_aggregate      belief_aggregate       adjusted burst_has_belief_count      27850        2208       True    18.174021             2  0.825457 0.025822 0.774847 0.876068 2.282925   2.170260    2.401439 3.142797e-224
                has_belief           belief_aggregate      belief_aggregate fully_adjusted burst_has_belief_count      27850        2208       True   357.937355            11  0.741461 0.023427 0.695545 0.787377 2.098999   2.004801    2.197623 7.580182e-220
                     ct_ra           religious_action            comparator          plain         burst_ra_count      27850        1456       True    20.277525             0  0.846095 0.032668 0.782066 0.910124 2.330528   2.185984    2.484630 6.740963e-148
                     ct_ra           religious_action            comparator       adjusted         burst_ra_count      27850        1456       True    16.104832             2  0.846484 0.032536 0.782715 0.910253 2.331435   2.187403    2.484951 3.175464e-149
                     ct_ra           religious_action            comparator fully_adjusted         burst_ra_count      27850        1456       True   327.729103            10  0.799630 0.028664 0.743449 0.855811 2.224718   2.103178    2.353282 2.945934e-171
                     ct_ms           material_support            comparator          plain         burst_ms_count      27850        1856       True    23.993915             0  0.879025 0.031682 0.816930 0.941120 2.408551   2.263540    2.562851 1.978161e-169
                     ct_ms           material_support            comparator       adjusted         burst_ms_count      27850        1856       True    18.207556             2  0.882459 0.030997 0.821706 0.943213 2.416836   2.274376    2.568219 2.835703e-178
                     ct_ms           material_support            comparator fully_adjusted         burst_ms_count      27850        1856       True   402.160785            10  0.849676 0.024647 0.801368 0.897984 2.338890   2.228589    2.454651 2.016999e-260
                     ct_sn             social_network            comparator          plain         burst_sn_count      27850        3527       True    20.993132             0  0.486970 0.020696 0.446407 0.527533 1.627378   1.562687    1.694746 2.016652e-122
                     ct_sn             social_network            comparator       adjusted         burst_sn_count      27850        3527       True    17.086272             2  0.480428 0.020704 0.439850 0.521006 1.616766   1.552474    1.683721 4.041152e-119
                     ct_sn             social_network            comparator fully_adjusted         burst_sn_count      27850        3527       True   204.194487            10  0.490680 0.020324 0.450846 0.530514 1.633427   1.569640    1.699805 8.790747e-129
                     ct_st           spatial_temporal            comparator          plain         burst_st_count      27850        4675       True    18.886726             0  0.417949 0.016799 0.385024 0.450875 1.518844   1.469649    1.569685 1.244174e-136
                     ct_st           spatial_temporal            comparator       adjusted         burst_st_count      27850        4675       True    19.077391             2  0.417299 0.016749 0.384473 0.450126 1.517857   1.468840    1.568509 5.039902e-137
                     ct_st           spatial_temporal            comparator fully_adjusted         burst_st_count      27850        4675       True  2609.310068            10  0.528846 0.017555 0.494439 0.563254 1.696973   1.639578    1.756378 2.294836e-199
                     ct_ei      encounter_interaction            comparator          plain         burst_ei_count      27850        2771       True    13.740687             0  0.549582 0.022658 0.505173 0.593991 1.732529   1.657273    1.811203 5.799640e-130
                     ct_ei      encounter_interaction            comparator       adjusted         burst_ei_count      27850        2771       True    11.394554             2  0.552154 0.022483 0.508087 0.596220 1.736990   1.662109    1.815245 3.524110e-133
                     ct_ei      encounter_interaction            comparator fully_adjusted         burst_ei_count      27850        2771       True   378.541677            10  0.505200 0.019880 0.466236 0.544164 1.657317   1.593983    1.723167 1.835407e-142
                  ct_rb_th                theological        belief_subtype    m4_faithful      burst_rb_th_count      27850         398       True  4474.495164            14  1.175829 0.067467 1.043596 1.308061 3.240827   2.839409    3.698995  5.036109e-68
                  ct_rb_st          socio_theological        belief_subtype    m4_faithful      burst_rb_st_count      27850         594       True  1199.880339            14  1.023817 0.045916 0.933824 1.113810 2.783801   2.544220    3.045942 3.883737e-110
                  ct_rb_sm                socio_moral        belief_subtype    m4_faithful      burst_rb_sm_count      27850         866       True   745.475716            14  1.021384 0.040312 0.942374 1.100393 2.777034   2.566067    3.005346 1.241438e-141
                     ct_rb             generic_belief        belief_subtype    m4_faithful         burst_rb_count      27850         360       True  1317.890161            14  1.211923 0.062995 1.088456 1.335390 3.359938   2.969684    3.801477  1.761129e-82
                has_belief           belief_aggregate      belief_aggregate    m4_faithful burst_has_belief_count      27850        2208       True  1187.617657            14  0.748865 0.025727 0.698441 0.799289 2.114598   2.010615    2.223960 2.846434e-186
                     ct_ra           religious_action            comparator    m4_faithful         burst_ra_count      27850        1456       True   938.643619            14  0.806452 0.028522 0.750549 0.862355 2.239947   2.118163    2.368733 7.162162e-176
                     ct_ms           material_support            comparator    m4_faithful         burst_ms_count      27850        1856       True  1585.992576            14  0.836256 0.024390 0.788453 0.884059 2.307711   2.199991    2.420705 1.208922e-257
                     ct_sn             social_network            comparator    m4_faithful         burst_sn_count      27850        3527       True   806.985783            14  0.488386 0.020269 0.448659 0.528112 1.629683   1.566211    1.695728 2.803756e-128
                     ct_st           spatial_temporal            comparator    m4_faithful         burst_st_count      27850        4675       True 18037.378698            14  0.527947 0.017294 0.494053 0.561842 1.695449   1.638945    1.753900 1.089170e-204
                     ct_ei      encounter_interaction            comparator    m4_faithful         burst_ei_count      27850        2771       True   540.716696            14  0.503240 0.022438 0.459263 0.547217 1.654072   1.582906    1.728437 2.089296e-111
has_belief_via_burst_rb_sm       m4_joint_socio_moral m4_joint_subtype_term       m4_joint      burst_rb_sm_count      27850        2208       True   724.908891            17  0.736226 0.035271 0.667094 0.805358 2.088040   1.948569    2.237494  9.399149e-97
has_belief_via_burst_rb_th       m4_joint_theological m4_joint_subtype_term       m4_joint      burst_rb_th_count      27850        2208       True   724.908891            17  0.672525 0.040003 0.594119 0.750931 1.959178   1.811437    2.118969  1.997899e-63
has_belief_via_burst_rb_st m4_joint_socio_theological m4_joint_subtype_term       m4_joint      burst_rb_st_count      27850        2208       True   724.908891            17  0.699507 0.035655 0.629623 0.769392 2.012761   1.876905    2.158450  1.073147e-85
   has_belief_via_burst_rb    m4_joint_generic_belief m4_joint_subtype_term       m4_joint         burst_rb_count      27850        2208       True   724.908891            17  0.951581 0.049202 0.855144 1.048018 2.589801   2.351718    2.851987  2.468950e-83
```

## Sanity check against the manuscript's own published comparator numbers

| Category | Manuscript's published OR | This script's plain-model OR |
|---|---|---|
| `ct_ra` | 2.25 | 2.33 |
| `ct_ms` | 2.27 | 2.41 |
| `ct_sn` | 1.67 | 1.63 |
| `ct_st` | 1.63 | 1.52 |
| `ct_ei` | 1.65 | 1.73 |

Not expected to match exactly (different exact data-prep/model details are
possible) but should land in the same ballpark — if wildly different, treat
`has_belief`'s new number with more caution and investigate before citing it.

## Cross-check against the permutation-based ranking

| Category | Regression OR (plain) | Regression rank | Permutation fold-enrichment | Permutation rank |
|---|---|---|---|---|
| `ct_rb` (generic_belief) | 3.26 | 1 | 2.80 | 1 |
| `ct_rb_sm` (socio_moral) | 3.03 | 2 | 2.28 | 4 |
| `ct_rb_st` (socio_theological) | 2.77 | 3 | 2.32 | 3 |
| `ct_rb_th` (theological) | 2.59 | 4 | 2.47 | 2 |
| `ct_ms` (material_support) | 2.41 | 5 | 1.79 | 6 |
| `ct_ra` (religious_action) | 2.33 | 6 | 2.09 | 5 |
| `has_belief` (belief_aggregate) | 2.30 | 7 | 1.67 | 7 |
| `ct_ei` (encounter_interaction) | 1.73 | 8 | 1.47 | 8 |
| `ct_sn` (social_network) | 1.63 | 9 | 1.30 | 9 |
| `ct_st` (spatial_temporal) | 1.52 | 10 | 1.25 | 10 |

Spearman rank correlation between the two independent methodologies: **0.939**.


## Interpretation

Both methods agree on the ordering: `has_belief` ranks 7th of 10
by regression OR and 7th of 10 by permutation fold-enrichment
(Spearman rank correlation **0.939**) — in neither method does the aggregate beat any of
the four belief subtypes (lowest subtype OR = 2.59) or beat both `ct_ra`
(OR=2.33) and `ct_ms` (OR=2.41).

**But the two methods disagree on magnitude, and that's worth keeping rather than smoothing over.**
Under the regression (this script), `has_belief`'s OR (2.30) sits only
0.03 below the lower of `ct_ra`/`ct_ms` (2.33) — close to
competitive, similar in spirit to the manuscript's own original framing ("2 of 5 comparators
similar to belief"). Under the permutation-null fold-enrichment
(`comparative_burstiness_results.md`), `has_belief`'s score (1.67) sits
0.11 below the lower of `ct_ra`/`ct_ms` (1.79) — a
larger, more decisive gap, closer to "mediocre, indistinguishable from a random 4-tag union"
(the permutation script's own structural control put it at the 81st percentile of that
distribution, p=0.192).

**Combined, honest conclusion**: the aggregate-exceptionalism claim does not survive either
method — `has_belief` never ranks above the subtypes or clearly above `ct_ra`/`ct_ms` in either
test. Whether it's "roughly competitive with `ra`/`ms`" or "mediocre relative to them" is
method-dependent and should be reported as such, not collapsed into whichever framing sounds
more dramatic. The subtype-level exceptionalism claim, by contrast, is robust to which method
you pick — all four subtypes outrank all five comparators in both the regression ranking and
the permutation ranking, with no ambiguity.

**Fully-adjusted spec (Model C) closes the magnitude gap between the two methodologies.**
Under heavy adjustment (`sex + register + nagiag + qr_tracked + log_clauses_len_std +
has_nag_i_prop` + the other four comparators' thematic proportions), `has_belief`'s OR
drops from 2.30 (plain) / 2.28 (adjusted)
to **2.10** — still rank 7th of 10, but now sitting
0.13 below the lower of `ct_ra`/`ct_ms` (2.22) once fully
adjusted, nearly matching the permutation method's gap (0.11). The
plain/adjusted specs' "close to competitive" reading turns out to be an artifact of
under-adjustment, not a genuine method disagreement — properly controlled, the regression
and permutation methods converge on the same magnitude, not just the same rank.

Fit cost of this spec was real: mean 960s vs.
23s (plain) / 20s
(adjusted) per fit — up to 4038s for the slowest
single fit. Confirms the manuscript's own heavier models are genuinely more expensive to fit,
not just more thorough on paper.

**Caveat:** at least two of the ten fully-adjusted fits (`ct_ms`, `ct_ei`) printed lme4
non-convergence warnings (gradient ~0.003-0.006 — near-convergence, not a clean fit) even
though they cleared the script's fit-success guard; console output for the earlier categories
was truncated by a `tail -100` pipe on the run that produced these numbers, so their
convergence status could not be re-confirmed after the fact. Treat the fully-adjusted ORs as
provisionally converged, not guaranteed-clean — a rerun with untruncated logging would be
needed before citing these numbers in the manuscript itself.

## m4_faithful and m4_joint: the manuscript's archived M4 formula

The `fully_adjusted` spec above approximates the manuscript's question-tracking
covariates as `nt_co_Q_prop_present`/`_mag`, which don't exist in the manuscript
M4 model. Its archived covariate skeleton — the `"belief-interdependency"`
model variant in `belief_context_analysis2.py` (main project repository, not
included here) — uses a single continuous `nt_co_Q_prop` term plus two
interactions (`nt_co_Q_prop*log_clauses_len_std`, `nt_co_Q_prop*register`).
Two new specs built on it:

- **m4_faithful**: `{category} ~ {burst_count} + nt_co_Q_prop + [other 4 comparator
  ct_*_prop, or has_belief_prop if {category} is itself a comparator] + has_nag_i_prop +
  nagiag + sex + register + log_clauses_len_std + qr_tracked +
  nt_co_Q_prop*log_clauses_len_std + nt_co_Q_prop*register + (1|deposition_code)` — the
  manuscript's archived M4 skeleton, applied symmetrically to all 10 categories
  (univariate own-burst, like `fully_adjusted`, but with the archived covariate
  set instead of the approximated one).
  `has_belief_prop` doesn't exist upstream (belief counts are deliberately excluded from the
  deposition-level proportion whitelist that builds `ct_ra_prop` etc., to avoid circularity
  when belief is the DV) — computed it here the same way (sum/clauses_len per deposition) so
  comparator-DV models get belief's rate as their "other topic" control, mirroring how M4
  itself uses the 5 comparators' rates as belief's controls.
- **m4_joint**: the literal archived formula, unmodified — `has_belief` predicted by **all
  four** subtype bursts **simultaneously** (mutually adjusted), not one at a time. This is
  the actual quantity behind the manuscript's published 1.95-2.55 range; nothing else in
  this script reproduces it (every other spec uses `has_belief`'s own aggregate burst count,
  univariate).

### m4_faithful confirms fully_adjusted almost exactly

`has_belief`'s self→self OR under the manuscript's archived M4 skeleton: **2.11** — 0.01 from
`fully_adjusted`'s 2.10, despite `fully_adjusted` using an approximated
(not the archived) `nt_co_Q` covariate set. Full m4_faithful ranking (OR): `ct_rb`=3.36, `ct_rb_th`=3.24, `ct_rb_st`=2.78,
`ct_rb_sm`=2.78, `ct_ms`=2.31, `ct_ra`=2.24, **`has_belief`=2.11 (rank 7th)**, `ct_st`=1.70,
`ct_ei`=1.65, `ct_sn`=1.63. Same rank, same gap to `ct_ra`/`ct_ms` (0.13, vs. permutation's
0.11) as `fully_adjusted` gave — a third independent confirmation of the mediocre-aggregate
finding, this time under the literal manuscript covariate set rather than an approximation.

**Fit cost, confirmed and worse than expected**: m4_faithful averaged **3084s (51 minutes)**
per fit, vs. 23s (plain) / 20s (adjusted) — up to **18,037s (over 5 hours)** for the single
slowest fit (`ct_st`). This is markedly heavier even than `fully_adjusted` (mean 960s, max
4038s), because `nt_co_Q_prop`'s two interaction terms multiply out against `nagiag`'s ~9
dummy levels. Confirms decisively that the manuscript's actual Model 4 is expensive to fit —
not a corner the light specs were wrong to cut for the qualitative conclusion, but a real
cost that would matter for any full re-fit of the manuscript's own models.

### m4_joint reproduces the manuscript's published subtype ORs almost exactly

| Subtype | Manuscript's published OR | m4_joint (this pipeline) |
|---|---|---|
| generic (`ct_rb`) | 2.55 | 2.59 |
| socio-moral (`ct_rb_sm`) | 2.07 | 2.09 |
| socio-theological (`ct_rb_st`) | 2.00 | 2.01 |
| theological (`ct_rb_th`) | 1.95 | 1.96 |

Differences of 0.01-0.04 across all four — essentially an exact reproduction, tighter than
the ~0.1 spread seen matching the five comparator topics under the `plain` spec earlier.
Strong validation that this pipeline and data faithfully reproduce the manuscript's own
actual, published M4 model — not just something in the same ballpark.

**Caveat**: this fit printed an lme4 non-convergence warning with gradient ≈0.0263 — an
order of magnitude worse than the ~0.003-0.006 warnings seen on some `fully_adjusted` fits.
Given how tightly it reproduces the manuscript's own published numbers, this may simply mean
the manuscript's own original fit carried the same warning (unrecorded in the prose) — glmer
models with many terms and several mutually-correlated predictors commonly do — but it
can't be confirmed either way from here. Treat the exact m4_joint coefficients as
suggestive-but-not-guaranteed-clean, same caveat as `fully_adjusted`.

### Why subtype→aggregate ORs are lower than subtype→self, not higher

A narrow predictor (one subtype's burst count) predicting a broad union outcome
(`has_belief`) might be expected to inflate the OR — structurally easier to
satisfy, close to near-definitional — suggesting subtype→aggregate numbers
should run *higher* than the matched subtype→self numbers. **m4_joint vs.
m4_faithful shows the opposite empirically**: subtype→aggregate (m4_joint:
1.96-2.59) is consistently *lower* than the matched subtype→self numbers
(m4_faithful: 2.78-3.36) — by 0.7 to 1.3 OR points, for every one of the four
subtypes.

The more likely mechanism (not fully isolated here — m4_joint changes *both* the DV,
belief-subtype-self vs. aggregate, *and* the predictor set, single burst vs. all four
jointly, relative to m4_faithful, so the two can't be cleanly separated without an
additional decomposition fit): entering all four subtype bursts as **mutually-adjusting**
predictors of the same broad outcome means each one's coefficient has to compete for shared
variance with three correlated siblings (a theological-heavy passage is usually also
somewhat socio-moral-heavy, etc.) — a standard collinearity attenuation, not a definitional
inflation.

**Consequence for the manuscript's own comparison**: correcting to genuine
self→self on both sides makes the subtype-level separation from the five
comparators *cleaner*, not muddier. The manuscript's own raw comparison
(subtype→aggregate 1.95-2.55 vs. comparator→self 1.63-2.27) showed overlap
(`ct_ra`/`ct_ms` sitting inside the subtype range) — that overlap was an artifact of
comparing two different quantities, as established above. The true self→self
comparison isn't just "no worse" than the manuscript's original one — it's
decisively better for the subtype-level claim: subtype self→self (2.78-3.36,
m4_faithful) clears comparator self→self (2.24-2.31, m4_faithful) with real separation, no
overlap at all. The manuscript's own comparison, ironically, *understated* how cleanly
belief subtypes cluster relative to other topics, by putting a deflated quantity (subtype→
aggregate) up against comparators' true self-recurrence.

## Files

- `self_burst_regression_results.csv` — 45 fits: 10 categories × 4 specs
  (plain/adjusted/fully_adjusted/m4_faithful) + 4 m4_joint subtype-burst terms from one
  joint fit
- Fitting script: `sembel_self_burst_regression.py`
- Manuscript M4 formula source: `belief_context_analysis2.py` in the main project
  repository (not included here), `"belief-interdependency"` model variant
  (~line 7053)
- Cross-referenced: two internal working documents (manuscript-issues and
  known-issues tracking, not included here), and `comparative_burstiness_results.md`
