# Post-submission corrections

Four analyses run after the manuscript's submitted draft was finalized
(2026-07), refining or correcting specific claims. None change the
dataset in this repository — they are re-analyses of it, run outside this
repo (against a fuller internal working copy) and summarized here. Full
write-ups are available on request; this file gives the result and the
manuscript-text consequence for each.

None of the manuscript text itself has been edited to reflect these.
Anyone citing the claims listed below as "corrected" or "still holds as
originally stated" should check the current manuscript text against this
file first.

## 1. Model 4's clustering-exceptionalism claim: holds at the subtype level, not the aggregate level

**Original claim**: belief shows a "distinct, intensified clustering
dynamic" versus 5 comparator topics (religious action, material support,
social network, spatio-temporal, encounter-interaction), based on a raw
odds-ratio comparison.

**Problem found**: the comparison mixed two different relationship types
(comparators measured self->self; belief measured subtype->aggregate) and
never controlled for `has_belief` being a 4-way union of subtypes while
every comparator is a single flat tag.

**Corrected result**, via two independent methods (a permutation
fold-enrichment score, and a real GLMM self->self refit using the
manuscript's own archived Model-4 covariate skeleton; Spearman rank
correlation between the two methods: 0.939):

- **Subtype level: the claim survives and strengthens.** All 4 belief
  subtypes clear all 5 comparators cleanly in every method, with no
  overlap — a cleaner separation than the original raw-OR comparison
  showed.
- **Aggregate (`has_belief`) level — the claim as originally stated does
  not survive.** The aggregate ranks 7th of 10 categories tested in every
  method, statistically indistinguishable from a random union of 4
  unrelated flat tags (structural-control p=0.192).
- **Mechanism**: belief passages specialize in one subtype rather than
  blending (same-subtype burst OR averages ~3.0; cross-subtype ~1.2) — the
  aggregate's signal dilutes toward the weak cross-subtype end.
- Independently replicated on a from-scratch re-extraction of the corpus
  (see `REPLICATION.md`) — both the subtype-survives and
  aggregate-fails conclusions hold on new data.
- Untouched by this correction: the separate 94% deposition-level
  random-intercept variance-collapse finding — that result is about
  individual-vs-structural variance attribution, not about belief being
  more clustered than other topics, so it doesn't depend on the
  aggregate-exceptionalism claim either way.

**What this means for the manuscript's claim**: the submitted text states
"distinct, intensified clustering dynamic" without distinguishing subtype
from aggregate. Read that sentence as applying to the subtype level only
— the aggregate-level extension of the claim does not hold, per the
correction above.

**Code and full write-ups**: `supplementary_analyses/burst_saturation/`
— `sembel_comparative_burstiness.py` (fold-enrichment method) and
`sembel_self_burst_regression.py` (GLMM self→self method) for the
subtype/aggregate split above; `sembel_subtype_cross_burst.py` for the
same-subtype-vs-cross-subtype mechanism finding. See that folder's
`README.md` for which script backs which specific number.

## 2. Comparator-topic granularity — an irreducible limitation, not a further correction

The correction above controls for known aggregation mechanics and base
rate, but not for whether the comparator topics (religious action,
material support, social network, spatio-temporal, encounter-interaction)
have hidden internal facet-structure the coding scheme never captured —
only the belief category has a documented subcategory system in the
extraction prompt. This can't be resolved without re-annotating the
comparators at belief's own granularity, which is out of scope here.

**What this means for the manuscript's claim**: the #1 correction above
should be read alongside this limitation — the data cannot currently
distinguish belief being genuinely more internally differentiated from
belief simply having received more annotation attention than the other
topics.

**One specific version of this was tested and rejected**: raw
local co-occurrence data suggested the 3 comparator topics `sn`/`st`/`ei`
might be flat labels over one oscillating "circumstantial-detail"
register (they bridge into each other, r=0.09-0.10) — which would mean
their individually-measured self-clustering undercounts that register's
true persistence, the same dilution mechanism confirmed for `has_belief`.
Tested directly by porting both existing methods to a new `sn`∪`st`∪`ei`
union category: it ranks last of 11 categories on the permutation
fold-enrichment metric (lower than any of its 3 members individually,
0.2nd percentile of a random-3-tag-union control), and the controlled
cross-tag GLMM puts these three topics' mutual bridging (mean OR 1.04)
*below* belief's own cross-subtype bridging (mean OR 1.21). **This
specific hypothesis is rejected** — sn/st/ei don't blend into an
undercounted macro-mode any more than belief's own subtypes blend into
each other. `ms`/`ra` (the two comparators that actually matter for the
exceptionalism claim) were never implicated by this hypothesis regardless
— they show no bridging with anything. Net effect: strengthens confidence
in the subtype-exceptionalism claim rather than undermining it. Does
**not** resolve whether `ms`/`ra` specifically have their own hidden
internal facet-structure — that remains exactly as untestable as before.

## 3. Model 2's "suppression" framing: saturation, not active competition

**Original claim**: material/social content "suppresses" or "competes
with" belief expression (`ct_ms_prop` OR~0.00).

**The coefficient itself is real** — checked against three candidate
artifacts (compositional-closure, multicollinearity, quasi-separation),
none hold up. **The causal-mechanism language does not hold up**:

- Raw (non-proportional) belief counts correlate weakly *positive* with
  every "suppressor" topic's raw count (r=0.02-0.12) — richer depositions
  have more of everything, including belief.
- What differs is scaling with deposition length: belief content scales
  weakly (r=0.39) while the suppressor topics scale strongly
  (r=0.70-0.86). Belief has a rough fixed ceiling per deposition; the
  other topics are elastic. Converting to proportions — the measure
  behind the original finding — mechanically turns that scaling
  difference into the observed negative association.
- A full local-burst co-occurrence check (18 topics x 3 window radii)
  found no topic positively accompanies belief locally either,
  consistent with saturation rather than active displacement. An
  asymmetric before/after split ruled out a hidden narrative-sequence
  effect too. Code and full write-ups:
  `supplementary_analyses/burst_saturation/sembel_cross_topic_burst_matrix.py`
  and `sembel_cross_topic_burst_asymmetric.py`.

**What this means for the manuscript's claim**: the submitted text
describes this as material/social content "suppressing" or "competing
with" belief expression. Read that language as saturation instead —
belief's *share* shrinks because everything else grows around a topic
that doesn't, not because other content actively displaces it. The
coefficients themselves are unaffected; only the mechanism-language is
superseded.

**Limitation of this correction: the evidence favors saturation but does
not exclude suppression.**

- Model 2's coefficient is a *deposition-level compositional* association
  (`ct_ms_prop` etc. are whole-deposition proportions, stamped identically
  onto every clause in that deposition) predicting a clause-level outcome
  — not a clause-by-clause sequential measure. Both the suppression and
  the saturation story predict exactly the same sign and magnitude for
  this coefficient: any topic whose raw count scales faster with
  deposition length than belief's does will mechanically produce a
  negative proportion coefficient against belief, whether or not any real
  interaction between the two topics exists. **The regression coefficient
  itself cannot adjudicate between the two stories** — everything
  discriminating comes from the auxiliary checks (raw-count correlation,
  length-scaling comparison, local-burst matrix), not from Model 2.
- The raw-count correlation (belief vs. suppressor topics, r=0.02-0.12)
  is weakly *positive*, which rules out a strong/absolute version of
  suppression, but "weakly positive" is close to null — a real local
  displacement effect could still exist and be masked by the length
  confound in this ecological correlation (structurally similar to a
  Simpson's-paradox risk: aggregate-level positive correlation doesn't
  guarantee no negative effect within depositions of matched length).
- The local clause-adjacency burst matrix (+/-3/5/7 clauses) only tests
  fine-grained, few-clause displacement. It cannot detect a coarser
  mechanism — e.g. an interrogation or notarial-recording session
  allocating whole *sections* of a deposition to one topic-register at a
  time (see the mode-switching story below) — which would leave no trace
  in a +/-7-clause window while still being a genuine displacement
  dynamic, just operating at a coarser grain than this check can see.
- Saturation and a coarse-grained institutional-allocation mechanism are
  not mutually exclusive, and neither is currently ruled in or out by the
  data checked so far.

**Plausible mechanisms for how saturation could actually operate** (this
direction is harder to construct concretely than suppression — an
attention/interrogation-mode-switching story for suppression is
intuitive; a substantive ceiling on belief specifically needs its own
explanation, not just "the math works out that way"):

1. **Belief as a bounded procedural checklist, other content as an open
   list.** If belief is elicited via a small, roughly fixed set of
   standard credal/inquisitorial questions ("did you believe the heretics
   were good men," "did you adore them," etc.), that checklist is
   answerable in a handful of clauses regardless of deposition length —
   once asked and answered, the topic is procedurally closed. Social/
   material content (who was met, when, what was given or received) has
   no equivalent closure condition: each additional named person, meeting,
   or transaction is a new discrete fact, and the list of possible facts
   is effectively open-ended. Longer depositions accumulate more facts of
   the open-list kind; the checklist kind stays roughly constant size.
2. **Belief as a durative state-predicate, other content as episodic
   counts.** "I believed X" is a single state asserted once (perhaps with
   a start/end date or a retraction), not a countable series of events.
   "I met him, gave him bread, saw him again in Lent" is a series of
   discrete episodes that multiplies with more testimony. A state
   predicate doesn't accumulate additional instances just because the
   surrounding testimony grows; an episodic list does.
3. **Evidentiary sufficiency threshold.** Canon-law procedure needs one
   clear, on-record admission of heretical belief to establish the legal
   fact of heresy — once met, further belief-statements have diminishing
   procedural value and the notary/inquisitor has no institutional reason
   to keep eliciting more. Naming additional accomplices, places, and
   transactions retains prosecutorial/intelligence value indefinitely
   (each new name is actionable), so there's no equivalent point of
   "enough" for the social/material side.
4. **Deponent self-protective ceiling.** Any admission of past belief is
   self-incriminating; a deponent has an incentive to concede the minimal
   sufficient admission and stop elaborating (more detail only adds
   culpability). Naming other people's involvement, movements, and
   transactions is comparatively lower-risk to elaborate on (sometimes
   even self-exculpatory, or currying favor by informing) — a strategic,
   not institutional, source of asymmetric ceilings.
5. **Linguistic compressibility.** Belief content is expressible
   compactly ("credidit quod...") independent of how much has actually
   been believed; material/social content requires one clause per
   discrete action or fact by the extraction scheme's own segmentation
   rules. The same underlying amount of "content" produces far fewer
   belief clauses than material/social clauses simply as a function of
   how compressible each domain is to narrate, regardless of production
   ceilings or interrogation strategy.

**The mode-switching alternative the reader's intuition supplies**: when
an inquisitorial session is in a material/social-investigation mode
(establishing who supported the movement, financially or logistically),
the inquisitor may simply not ask belief-probing questions during that
stretch — a real attention-allocation effect operating at the level of a
whole interrogation phase, not individual clauses. This is a genuine
suppression mechanism, coarser-grained than anything the local-burst
matrix could detect.

**Tested directly, and it overturns pure saturation as the whole
story.** A `detail_run_len_so_far` covariate (consecutive
immediately-preceding clauses tagged with any of Model 2's own 5
suppressor topics, defined for every clause — no censoring needed even
for the 43% of depositions with zero belief clauses) fit as
`has_belief ~ log1p(detail_run_len_so_far) + sex + register +
log_clauses_len_std + (1|deposition_code)` — `log_clauses_len_std`
specifically absorbs the already-known length/saturation effect, so this
tests whatever's left on top of it.

**Result: log-odds=-1.60, OR=0.20 [0.17, 0.24], p=1.5e-80** — large,
robust, and it survives controlling for overall deposition length.
Confirmed monotonic in a binned dose-response table (12.0%→2.3%→0.44%→0%
across run-length bins 0/1-3/4-10/11-25), holding separately in all three
registers. Ruled out the obvious confound (long detail-runs just proxying
for "later in the deposition," where belief might be front-loaded):
`corr` with relative sequence-position = 0.034 (near-zero), and adding
that position as a covariate leaves the effect essentially unchanged
(OR=0.197) while position itself points the *opposite* direction (belief
slightly *more* likely later).

**Revised picture**: saturation (belief's count doesn't scale with
overall length) and a real coarse-grained persistence effect coexist —
not competing explanations, both true. "Suppresses"/"crowds out" is still
wrong as a description of fine-grained, clause-by-clause dynamics (that
null result stands), but at the passage/session grain, something
functionally suppression-like is real.

**"Whose persistence this is" tested directly.**
Checked whether long detail-runs (and, for the first time, belief-runs)
stay within a single sustained question, using new-question events
(`NT in {"co.iq","co.ro"}`) as boundary markers — a method whose known
biases (over-splitting at nested tangents, missing reversion to an
earlier question) work *against* finding containment. Result: **both**
detail-runs and belief-runs mostly stay within one question (weighted
boundary rate 4.3% detail, 2.1% belief — far under what "many separate
short questions" would predict). A secondary, sparse `qr`-based check
(real per-question ids, ~10% coverage) corroborates this for detail-runs
directly.

**Correction, via a register-stratified check prompted by a
Simpson's-paradox concern**: the "belief is more contained than detail"
comparison above does not survive register-stratification and is
retracted. Question-marking rate itself differs sharply by register
(Toulouse 4.9%, Bologna 7.2%, Bologna LS only 2.3% of clauses) — so
"does a run span a new question" is mechanically easier to detect in
Toulouse/Bologna and harder in Bologna LS regardless of real content
differences. Recomputed directly from the saved run-level data:
detail-run containment holds up fine in every register (Toulouse
4.8-7.4%, Bologna 3.4-11.1%, Bologna LS 2.2-9.5%, all well under 15% —
Bologna-main shows the *most* boundary-crossing, not Bologna LS). But
belief-runs are 27% Bologna-LS by count vs. only 13% for detail-runs, and
Bologna LS's belief-runs show a literal 0/390 boundary rate — an artifact
of that register barely having tracked-question data at all, not
evidence belief is exceptionally single-question-bound there. **In
Toulouse — the register with the most balanced data for both — belief
(6.0%/4.3%) and detail (4.8%/5.5%) look about the same**, not
belief-more-contained. The pooled asymmetry was a register-mix artifact.

**What survives**: both detail-runs and belief-runs still clearly stay
mostly within one question in every register checked (nothing approaches
the ~50%+ rate "many separate short questions" would predict), and
belief-runs never show *more* boundary-spanning than detail-runs
anywhere in the breakdown. **Best-supported reading, unchanged**: a
generic structural fact about how question-answer exchanges are
organized (whichever topic the currently-open question is about locally
excludes the other, symmetric in both directions), not a belief-specific
institutional-avoidance effect. Coarse-grained persistence is still real
and confirmed; this still resolves *why* in favor of the
generic-coherence explanation over the inquisitor-agenda one. Full
detail:
`outputs_sembel/run_question_alignment/run_question_alignment_results.md`
(internal working repo).

**Robustness check**: both findings above were run pooling
the 5 suppressor topics into one union; rerunning both checks on each of
`ms`/`sn`/`st`/`ei`/`ra` individually confirms both replicate topic-by-topic
(persistence OR 0.12-0.42, all p<5e-6; containment rate 0.5-4.1%, same
range as the pooled result). Bonus: persistence strength splits along the
same sn/st/ei-vs-ms/ra line already found for local topic-bridging
(§2's sub-check) — and `ms`, the single strongest *static* compositional
suppressor, has the *weakest* coarse *persistence* effect of the five,
one more instance of ranking depending on which scale you read it from.
Full detail: `outputs_sembel/detail_topic_breakdown/detail_topic_breakdown_results.md`
(internal working repo).

**What this means for the manuscript's claim, revised**: the "Thematic
Saturation" framing (§3 above) is not the complete picture either — both
a fixed-ceiling/length-scaling effect *and* a genuine coarse-grained
persistence effect are evidenced, and the latter is best attributed to
generic question-answer topical coherence rather than belief-specific
institutional avoidance. The most accurate description going forward:
belief has a rough ceiling that doesn't scale with length, and
independently, once a passage settles into non-belief content it
measurably tends to stay there for the duration of that question — not
"suppresses" alone, "merely saturates" alone, or an unqualified
inquisitor-avoidance framing.

## 4. Sex effect mechanism: sharper than "unclear," still not fully resolved

**Original claim**: the manuscript names three candidate explanations for
"female deponents show more belief expression" (institutional handling,
deponent self-expression, content-crowding) and concludes "it is unclear."

**Corrected result**:

- **Content-crowding: partially confirmed.** The sex odds ratio
  attenuates substantially once thematic content is added as a control,
  but a significant residual gap remains — a real, partial contributor,
  not the whole story.
- **Institutional handling vs. deponent self-expression: two independent,
  convergent tests, both null on the interaction term.** If institutional
  handling drove the gap, it should concentrate in inquisitor-voiced or
  question-elicited content specifically. Two different operationalizations
  of that split (whose voice frames the clause; whether the clause answers
  a tracked question) both found no significant interaction, with point
  estimates running opposite to what the institutional-handling story
  predicts. Not a full falsification given the p-values, but a materially
  more informative state than "unclear" — the gap looks fairly uniform
  across elicitation context.

**What this means for the manuscript's claim**: the submitted text
describes the sex-effect mechanism as "unclear." A sharper conclusion is
now available — content-crowding is a confirmed partial contributor, and
the data leans (without full statistical confirmation) against a narrow
institutional-handling story specifically.
