# Cross-topic local burst co-occurrence matrix

Answers a different question than `sembel_suppression_ranking.tex` (deposition-
proportion suppression strength): which topics tend to **accompany** belief
**locally** (nearby-clause co-occurrence, point-biserial correlation between a
topic's own clause-level indicator and every OTHER topic's local burst count),
at three window radii (+/-3, +/-5, +/-7 clauses, excluding the focal clause).
Full 17-topic-plus-aggregate matrix, not just belief-focused -- 18x18 per
radius.

No compositional/closure concerns here: burst counts are raw local-window
sums, not deposition-wide proportions, so they don't inherit the "fixed
denominator" issue that a proportion-based measure could raise.


## Window radius +/-3

**`has_belief`** (n=2208) -- top accompanying topics: `rb_st` (r=0.262), `rb_sm` (r=0.238), `rb_th` (r=0.222); most avoided: `sn` (r=-0.119), `ei` (r=-0.137), `st` (r=-0.150)
**`rb`** (n=360) -- top accompanying topics: `has_belief` (r=0.147), `rb_st` (r=0.038), `bs` (r=0.021); most avoided: `ms` (r=-0.036), `st` (r=-0.042), `ei` (r=-0.046)
**`rb_sm`** (n=866) -- top accompanying topics: `has_belief` (r=0.209), `lp` (r=0.048), `rb_st` (r=0.044); most avoided: `sn` (r=-0.075), `ei` (r=-0.082), `st` (r=-0.098)
**`rb_st`** (n=594) -- top accompanying topics: `has_belief` (r=0.256), `rb_sm` (r=0.049), `rb` (r=0.042); most avoided: `sn` (r=-0.062), `ei` (r=-0.072), `st` (r=-0.081)
**`rb_th`** (n=398) -- top accompanying topics: `has_belief` (r=0.237), `rb_st` (r=0.015), `ot` (r=0.010); most avoided: `ei` (r=-0.061), `st` (r=-0.062), `lp` (r=-0.064)

## Window radius +/-5

**`has_belief`** (n=2208) -- top accompanying topics: `rb_st` (r=0.278), `rb_sm` (r=0.239), `rb_th` (r=0.225); most avoided: `ms` (r=-0.120), `ei` (r=-0.148), `st` (r=-0.150)
**`rb`** (n=360) -- top accompanying topics: `has_belief` (r=0.148), `rb_st` (r=0.053), `bs` (r=0.024); most avoided: `ms` (r=-0.038), `st` (r=-0.041), `ei` (r=-0.048)
**`rb_sm`** (n=866) -- top accompanying topics: `has_belief` (r=0.192), `lp` (r=0.055), `rb_st` (r=0.050); most avoided: `sn` (r=-0.078), `ei` (r=-0.091), `st` (r=-0.100)
**`rb_st`** (n=594) -- top accompanying topics: `has_belief` (r=0.273), `rb_sm` (r=0.064), `rb` (r=0.061); most avoided: `ms` (r=-0.061), `ei` (r=-0.077), `st` (r=-0.080)
**`rb_th`** (n=398) -- top accompanying topics: `has_belief` (r=0.245), `rb_st` (r=0.022), `ot` (r=0.015); most avoided: `ms` (r=-0.060), `ei` (r=-0.065), `lp` (r=-0.066)

## Window radius +/-7

**`has_belief`** (n=2208) -- top accompanying topics: `rb_st` (r=0.280), `rb_sm` (r=0.241), `rb_th` (r=0.227); most avoided: `ms` (r=-0.126), `st` (r=-0.148), `ei` (r=-0.152)
**`rb`** (n=360) -- top accompanying topics: `has_belief` (r=0.147), `rb_st` (r=0.059), `bs` (r=0.024); most avoided: `st` (r=-0.039), `ms` (r=-0.041), `ei` (r=-0.049)
**`rb_sm`** (n=866) -- top accompanying topics: `has_belief` (r=0.178), `lp` (r=0.050), `rb_st` (r=0.049); most avoided: `sn` (r=-0.079), `ei` (r=-0.095), `st` (r=-0.102)
**`rb_st`** (n=594) -- top accompanying topics: `has_belief` (r=0.277), `rb` (r=0.071), `rb_sm` (r=0.071); most avoided: `ms` (r=-0.066), `st` (r=-0.077), `ei` (r=-0.080)
**`rb_th`** (n=398) -- top accompanying topics: `has_belief` (r=0.248), `rb_st` (r=0.029), `ot` (r=0.020); most avoided: `ms` (r=-0.063), `lp` (r=-0.065), `ei` (r=-0.066)

## Interpretation

**No topic positively accompanies belief locally, besides belief's own
subtypes.** Across all three radii, `has_belief`'s only positive
correlations are with its own 4 subtypes (0.16-0.28, mechanically expected
since they're its components) — every non-belief topic is at best
near-zero (`is`, `ea`, `bs`, `ot`: -0.01 to +0.02) or negative. There is no
"accompanying" topic in this corpus, contrary to what the suppression
framing alone might suggest by omission (it never actually tested for
positive co-occurrence, just measured negative deposition-proportion
association) — this null result for positive accompaniment is itself worth
having: belief-talk in these depositions is not characteristically paired
with any other specific topic, it is simply rarer wherever certain other
topics dominate.

**Stable across window size.** Rankings and magnitudes barely move between
+/-3, +/-5, and +/-7 — not a radius-sensitive artifact.

**Corroborates the suppression finding at the local scale too, but with a
different ranking than the log-odds regression.** `sn`, `ms`, `ei`, `st` are
consistently the four most-avoided topics locally, same four flagged by the
deposition-proportion regression (`sembel_suppression_ranking.tex`) — the
pattern is not just a deposition-proportion artifact. **But material
support is not the clear standout here**: at every radius, `st`
(spatio-temporal) and `ei` (encounter interaction) show correlations as
negative or more negative than `ms` (e.g. radius=7: `st`=-0.148, `ei`=-0.152,
`ms`=-0.126) — on this linear-correlation scale, material support is *not*
uniquely dominant the way it is on the log-odds scale (where it beat the
next-closest by ~7x). Same scale-dependency lesson as the has_belief
aggregate-vs-subtype magnitude question earlier in this thread: which topic
"suppresses hardest" depends on which scale you read the answer off of, and
that should be stated plainly rather than picking whichever number sounds
most dramatic. The log-odds finding survived real scrutiny (binned
dose-response, univariate-vs-joint check) and is not in question — but a
raw-correlation reader would rank spatio-temporal/encounter-interaction at
least as high as material support, not clearly behind it.

## Files

- `cross_topic_burst_matrix.csv` -- long format, all pairs x all radii
- `cross_topic_burst_matrix_r{3,5,7}.csv` -- wide topic x topic matrices, one per radius
- Fitting script: `sembel_cross_topic_burst_matrix.py`
- Motivating thread: `sembel_suppression_ranking.tex`, `slides.talk.issues.md` #7
