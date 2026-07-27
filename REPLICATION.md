# Full-corpus replication

**Question**: do this dataset's reported statistical findings reproduce if
all 801 depositions are re-extracted from scratch with the same LLM
model/prompt/settings, then run through the same consolidation and
statistical pipeline? **Answer: yes**, throughout.

This validation was run outside this repository (it needed a full second
LLM extraction pass and a parallel copy of the analysis pipeline); this
file summarizes the result. The derived summary tables the numbers below
come from are included in `supplementary_analyses/replication_data/` (deposition-level
covariates, GLM model diagnostics, EMM/CLD tables, the rendered
three-panel comparison figure — see `supplementary_analyses/replication_data/README.md`). The
raw re-extracted JSON files and intermediate clause/deposition-level
pickles (~74MB) are not duplicated here to keep this repository
lightweight. Full methodology and working log live in the project's
internal `dh2026/full_corpus_replication_plan.md` and
`dh2026/replication_summary.md` — not included here, but available on
request.

## What was done

| Phase | What | Result |
|---|---|---|
| A | Re-extract all 801 depositions (same model/prompt, Anthropic Batch API) | 801/801 valid, 2 depositions needed a split-and-combine fix for silent under-extraction |
| B | Consolidate to clause-level and deposition-level dataframes | Exact column parity (184/184, 41/41) vs. this repo's data; clause counts within 0.2% |
| C | Model 1 (register + sex baseline) + three-panels (CT/NT x register x sex) | Both replicate; Model 1 verified byte-close (~0.02 log-odds) against this repo's own archived results |
| D | Model sets 2-4 (progressively adding topic, agency/length/questioning, burst/clustering predictors) | All replicate — same sign, same significance, close magnitude, at every step |
| E | The Model-4 clustering-claim correction (see `POST_SUBMISSION_CORRECTIONS.md` #1) | Both the confirmed (subtype) and retracted (aggregate) parts replicate |

## Headline numbers

**Model 1 (baseline)** — this repo's data vs. replication:

| Effect | This repo's OR (p) | Replication OR (p) |
|---|---|---|
| register1 (Bologna vs Toulouse) | 1.67 (.003) | 1.62 (.006) |
| register2 (Bologna-LS vs Toulouse) | 2.18 (<.001) | 2.21 (<.001) |
| sex=male (vs female) | 0.50 (<.001) | 0.54 (<.001) |

**Models 2-4** — same pattern at every step, e.g. Model 4: register2 OR
0.96 -> 0.90 (both n.s.), sexm OR 0.76 -> 0.73 (both p<.001); the full
7-level `nagiag` categorical and all four burst-count terms replicate
closely too.

**Model 4 clustering-claim correction (self->self burst regression)**:

| | this repo's data | replication |
|---|---|---|
| 4 belief subtypes (OR range) | 2.78-3.36 | 2.65-3.29 |
| 5 comparator topics (OR range) | 1.63-2.31 | 1.62-2.27 |
| `has_belief` aggregate | 2.11 (rank 7/10) | 2.17 (rank 7/10) |

Subtypes clear comparators cleanly in both datasets, no overlap either
time. The aggregate stays mediocre in both — same conclusion, same rank,
independent of which extraction run grounds it. See
`POST_SUBMISSION_CORRECTIONS.md` #1 for what this means for the
manuscript's clustering claim.

## What this establishes

The LLM extraction step was isolated as the only varying factor
throughout (same prompt, same model, same settings; institutional
covariates — sex, register, etc. — held fixed rather than re-derived,
since they're not a function of the extraction). Every statistical
conclusion this dataset's models produce reproduces on independently
re-extracted data. No sign flips, no significance-threshold crossings,
anywhere in the chain.

## What's not covered

- The permutation-based fold-enrichment correction and the same-subtype-
  vs-cross-subtype dilution check (see `POST_SUBMISSION_CORRECTIONS.md`
  #1) were not re-run on replication data — only the GLMM-regression side
  of that correction was replicated.
- The gender-mechanism test (`POST_SUBMISSION_CORRECTIONS.md` #4) and the
  saturation-mechanism analysis (#3) were not re-run on replication data
  either — both are analyses of this repo's own data, not yet
  cross-checked against an independent extraction.
